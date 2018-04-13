#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" battery.py is a file which automatically generates a battery part depending on parametric input of battery weight,
 """

# Required ParaPy Modules
from parapy.core import *
from parapy.geom import *

# TODO All necessary comments and documentation

# Other Modules
from directories import *


class Battery(GeomBase):

    __initargs__ = ["sizing_target", "sizing_value"]

    sizing_target = Input('capacity')
    sizing_value = Input(10000000)
    max_width = Input(0.05)
    max_height = Input(0.025)  # Suggested to use a wider-battery, max_height = max_width / 2 for fuselage aerodynamics

    @Attribute
    def constants(self):
        mydict = {
            'energy_density': (1.8*(10**6)),    # MJ/kg From WikiPedia https://en.wikipedia.org/wiki/Energy_density
            'energy_volume': (4.32*(10**9)),    # MJ/m^3
            'minimum_volume': 0.000015          # m^3

        }
        return mydict

    @Attribute
    def total_energy(self):
        if self.sizing_target == 'weight':
            e_bat = self.sizing_value * self.constants['energy_density']
            # Code to put a minimum weight to not break the code with div by zero
            if self.sizing_value < self.minimum_weight:
                raise ZeroDivisionError('%s [kg] results in a battery size that is too small to manufacture,'
                                        ' please change it to at least %s [kg]' % (self.sizing_value,
                                                                                   self.minimum_weight))
            else:
                return e_bat
        elif self.sizing_target == 'capacity':
            # Code to put a minimum size of capacity to not break the code with div by zero
            e_bat = self.sizing_value
            if self.sizing_value < self.minimum_capacity:
                raise ZeroDivisionError('%s [MJ] results in a battery size that is too small to manufacture,'
                                        ' please change it to at least %s [MJ]' % (self.sizing_value,
                                                                                   self.minimum_capacity))
            else:
                return e_bat
        else:
            return self.type_errormsg

    @Attribute
    def volume(self):
        return self.total_energy / self.constants['energy_volume']


    @Attribute
    def weight(self):
        return self.total_energy / self.constants['energy_volume']


    @Attribute
    def cg_x(self):
        return self.battery_scaled.cog[0]

    @Attribute(private=True)
    def minimum_capacity(self):
        return self.constants['minimum_volume'] * self.constants['energy_volume']

    @Attribute(private=True)
    def minimum_weight(self):
        return self.minimum_capacity / self.constants['energy_density']

    @Attribute(private=True)
    def type_errormsg(self):
        error_str = "%s is not a valid weight_target. Valid inputs: 'weight', 'capacity'" % self.sizing_target
        raise TypeError(error_str)

    @Attribute
    def width(self):
        return self.max_width

    @Attribute(private=True)
    def length_initial(self):
        length = self.volume / (self.width * self.height)
        return length

    @Attribute
    def length(self):
        updated_value = self.scaling_ratio * self.length_initial
        return updated_value

    @Attribute
    def height(self):
        return self.max_height


    @Attribute(private=True)
    def chamfer(self):
        e1, e2, e3, e4 = self.battery_import.top_face.edges
        d = (self.max_width + self.max_height) / 20.0
        cham_dict = {'edges': (e1, e3), 'distance': d}
        return cham_dict

    @Attribute(private=True)
    def scaling_ratio(self):
        required_length = self.volume / self.battery_chamfer.faces[1].area
        scaling_ratio = required_length / self.length_initial
        return scaling_ratio

    @Part
    def battery_import(self):
        return Box(self.max_width, self.length_initial, self.max_height, hidden=True)

    @Part
    def battery_chamfer(self):
        return ChamferedSolid(self.battery_import,
                              distance=self.chamfer['distance'],
                              edge_table=self.chamfer['edges'],
                              hidden=True)

    @Part
    def battery_transformed(self):
        return TransformedShape(shape_in=self.battery_chamfer,
                                from_position=XOY,
                                to_position=translate(rotate90(XOY, 'z_'), 'x_', self.max_width / 2.0),
                                hidden=True)
    @Part
    def battery_scaled(self):
        return ScaledShape(shape_in=self.battery_transformed,
                           reference_point=XOY,
                           factor=[self.scaling_ratio, 1.0, 1.0],
                           transparency=0.5)

    @Part
    def center_of_gravity(self):
        return Sphere(radius=0.01,
                      position=self.battery_scaled.cog, color='red')


if __name__ == '__main__':
    from parapy.gui import display

    obj = Battery()
    display(obj)
