#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" battery.py is a file which automatically generates a battery part depending on parametric input of battery weight,
or battery capacity. Utilize the parameter `show_primitives` for debugging.
"""

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# TODO All necessary comments and documentation

# Other Modules
from user import *
from definitions import *
from directories import *

__all__ = ["Battery", "show_primitives"]

# TODO change show_primitives to be inside class definition and protected variable
# TODO remove error message since it is already handled by a validator

# A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
show_primitives = False  # type: bool


class Battery(Component):

    __initargs__ = ["sizing_target", "sizing_value"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'batteryIII.png')

    sizing_target = Input('capacity', validator=val.OneOf(["capacity", "weight"]))
    # TODO link this to custom validator function
    sizing_value = Input(10000000.0, validator=val.Positive())
    max_width = Input(0.15, validator=val.Positive())
    max_height = Input(0.1, validator=val.Positive())  # Suggested to use a wider-battery, max_height = max_width / 2 for fuselage aerodynamics
    # position = Input(Position(Point(0, 0, 0)))
    label = Input('LiPo Battery')

    @Attribute
    def component_type(self):
        return 'battery'

    @Attribute
    def weight(self):
        """ Total mass of the battery

        :return: Mass in SI kilogram
        :rtype: float
        """
        return self.total_energy / self.constants['energy_density']

    @Attribute
    def center_of_gravity(self):
        """ Location of the battery center of gravity w.r.t the origin

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        return self.internal_shape.cog

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
    def width(self):
        return self.max_width

    @Attribute
    def length(self):
        length = self.volume / self.battery_profile.area
        return length

    @Attribute
    def height(self):
        return self.max_height

    @Attribute
    def bbox_intern(self):
        self.battery.bbox.color = MyColors.deep_green
        return self.battery.bbox

    @Attribute(private=True)
    def minimum_capacity(self):
        return self.constants['minimum_volume'] * self.constants['energy_volume']

    @Attribute(private=True)
    def minimum_weight(self):
        return self.minimum_capacity / self.constants['energy_density']

    @Attribute(private=True)
    def radius(self):
        """Defines the radius in a way that prevents the battery_profile from self-destructing.

        :rtype: float
        """
        min_dimension = min(self.width, self.height)
        return min_dimension / 2.0


    @Attribute(private=True)
    def type_errormsg(self):
        error_str = "%s is not a valid weight_target. Valid inputs: 'weight', 'capacity'" % self.sizing_target
        raise TypeError(error_str)

    # --- Output Solid: -----------------------------------------------------------------------------------------------

    @Part
    def internal_shape(self):
        return TranslatedShape(shape_in=self.battery_import, displacement=Vector(self.position.x,
                                                                                 self.position.y,
                                                                                 (self.height / 2.0) + self.position.z),
                               color=MyColors.battery,
                               transparency=0.7)

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=show_primitives)
    def rectangle(self):
        return RectangularFace(width=self.max_width, length=self.max_height,
                               position=YOZ)

    @Part(in_tree=show_primitives)
    def battery_profile(self):
        return FilletedFace(built_from=self.rectangle, radius=self.radius)


    @Part(in_tree=show_primitives)
    def battery_import(self):
        return ExtrudedSolid(face_in=self.battery_profile, distance=self.length, direction='x')

if __name__ == '__main__':
    from parapy.gui import display

    obj = Battery()
    display(obj, background_image=False)
