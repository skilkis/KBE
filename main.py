# -*- coding: utf-8 -*-
# from components import Battery
""" Explanation of Main File Here


@author: Şan Kılkış & Nelson Johnson
@version: 1.0
"""

# TODO Add explanation of main file here

from design import *
from parapy.core import *
from parapy.geom import *
from components import *
from directories import *


# TODO Make sure that excel read and things are top level program features (not buried within the tree)

class UAV(Base):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')

    sizing_target = Input('weight')
    sizing_value = Input(1.25)

    @Attribute
    def wing_loading(self):
        return self.params.wingpowerloading.designpoint['wing_loading']

    @Part
    def params(self):
        return ParameterGenerator(label="Design Parameters")

    @Part
    def wing(self):
        return Wing(WS_pt=self.wing_loading, position=translate(XOY, 'x', self.cg.x + 0.1))

    @Part
    def stabilizer(self):
        return VerticalStabilizer(position=translate(self.wing.position, 'x', 0.2))

    @Part
    def stabilizer_h(self):
        return HorizontalStabilizer(position=translate(self.wing.position, 'x', -0.4))

    @Part
    def fuselage(self):
        return Fuselage(compartment_type=['motor', 'container', 'container', 'container', 'tail'],
                        sizing_parts=[self.motor, [self.stabilizer_h, self.camera], self.battery, [self.wing, self.stabilizer], None])

    @Part
    def motor(self):
        return Motor(integration='puller', position=translate(XOY, 'x', -0.3))

    @Part
    def propeller(self):
        return Propeller(self.motor)



    @Attribute
    def configuration(self):
        return self.params.configuration

    @Attribute
    def mtow(self):
        return self.weight_and_balance()['WEIGHTS']['MTOW']

    # @Attribute

    @Attribute
    def payload(self):
        return self.params.weightestimator.weight_payload

    @Attribute
    def battery_capacity(self):
        return self.sizing_value

    @Part
    def battery(self):
        return Battery(position=translate(XOY, 'x', -0.1))

    # @Part
    # def battery_test(self):
    #     return Battery(position=Position(self.cg))

    @Part
    def camera(self):
        return EOIR(target_weight=self.payload, position=translate(XOY, 'x', -0.3))

    # TODO Add a nice bar-graph that shows performance, power consumption, drag, etc in the GUI with boxes!

    @Attribute
    def cg(self):
        return self.weight_and_balance()['CG']

    # @Attribute
    # def motor_loc(self):
    #     if self.motor
    #     return self.motor_location()

    def weight_and_balance(self):
        """ Retrieves all relevant parameters from children with `weight` and `center_of_gravity` attributes and then
        calculates the center of gravity w.r.t the origin Point(0, 0, 0)

        :return: A dictionary of component weights as well as the center of gravity fieldnames = `WEIGHTS`, `CG`
        :rtype: dict
        """

        children = self.get_children()
        weight = []
        cg = []
        weight_dict = {'WEIGHTS': {},
                       'CG': Point(0, 0, 0)}
        for _child in children:
            if hasattr(_child, 'weight') and hasattr(_child, 'center_of_gravity'):
                weight_dict['WEIGHTS'][_child.label] = _child.getslot('weight')
                weight.append(_child.getslot('weight'))
                cg.append(_child.getslot('center_of_gravity'))

        total_weight = sum(weight)
        weight_dict['WEIGHTS']['MTOW'] = total_weight

        # CG calculation through a weighted average utilizing list comprehension
        cg_x = sum([weight[i] * cg[i].x for i in range(0, len(weight))]) / total_weight
        cg_y = sum([weight[i] * cg[i].y for i in range(0, len(weight))]) / total_weight
        cg_z = sum([weight[i] * cg[i].z for i in range(0, len(weight))]) / total_weight

        weight_dict['CG'] = Point(cg_x, cg_y, cg_z)

        return weight_dict

    def validate_geometry(self):
        children = self.get_children()
        x_loc_max = 0
        x_loc_min = 0
        for _child in children:
            if hasattr(_child, 'internal_shape') and getslot(_child, 'component_type') != 'motor':  # Identification of a Motor
                current_corners = _child.internal_shape.bbox.corners
                if current_corners[1].x > x_loc_max:
                    x_loc_max = current_corners[1].x
                elif current_corners[0].x < x_loc_min:
                    x_loc_min = current_corners[0].x
        return x_loc_min, x_loc_max


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
