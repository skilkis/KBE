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
from definitions import *


# TODO Make sure that excel read and things are top level program features (not buried within the tree)

class UAV(DesignInput):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')



#     @Attribute
#     def wing_loading(self):
#         return self.params.wingpowerloading.designpoint['wing_loading']
#
    @Part
    def params(self):
        return ParameterGenerator(label="Design Parameters")
#
#     @Part
#     def wing(self):
#         return Wing(WS_pt=self.wing_loading, position=translate(XOY, 'x', 0.1))
#
#     @Part
#     def stabilizer(self):
#         return VerticalStabilizer(position=translate(self.wing.position, 'x', 0.2))
#
#     @Part
#     def stability(self):
#         return ScissorPlot(x_cg=self.cg.x,
#                            x_ac=self.wing.wing.aerodynamic_center.x,
#                            x_lemac=self.wing.wing.lemac.x,
#                            mac=self.wing.wing.mac_length,
#                            AR=12,
#                            e=0.8,
#                            AR_h=5.0, # TODO Make this a derived input based on wing AR
#                            e_h=0.8,
#                            Cl_w=self.wing.lift_coef_control,
#                            C_mac=self.wing.controllability_c_m,
#                            Cla_w=self.wing.lift_coef_vs_alpha,
#                            delta_xcg=0.3,
#                            configuration='canard')
# #  TODO make relation for AR_h, and add dynamic validator.
#
#     #TODO make this from MAC to MAC
#     @Part
#     def stabilizer_h(self):
#         return HorizontalStabilizer(position=translate(self.wing.position,
#                                                        'x', self.stability.lhc * self.wing.wing.mac_length),
#                                     S_req=self.wing.s_req * self.stability.shs_req)
#
#     @Part
#     def fuselage(self):
#         return Fuselage(compartment_type=['motor', 'container', 'container', 'tail'],
#                         sizing_parts=[self.motor, [self.stabilizer_h, self.camera], [self.battery, self.wing, self.stabilizer], None])
#
#     @Part
#     def motor(self):
#         return Motor(integration='puller', position=translate(self.camera.position, 'x', -1, 'z', self.cg.z / 2.0))
#
#     @Part
#     def center_of_gravity(self):
#         return VisualCG(self.cg, self.weights['mtow'])
#
#     @Part
#     def propeller(self):
#         return Propeller(self.motor)
#
#     @Attribute
#     def configuration(self):
#         return self.params.configuration
#
#     @Attribute
#     def mtow(self):
#         return self.weight_and_balance()['WEIGHTS']['mtow']
#
#     @Attribute(private=True)
#     # TODO finish this validator attribute (make it private)
#     def mtow_validator(self):
#         return 1
#
#
#     # @Attribute
#
#     @Attribute
#     def payload(self):
#         return self.params.weightestimator.weight_payload
#
#     @Attribute
#     def battery_capacity(self):
#         return self.sizing_value
#
#     @Part
#     def battery(self):
#         return Battery(position=translate(XOY, 'x', -0.1))
#
#     # @Part
#     # def battery_test(self):
#     #     return Battery(position=Position(self.cg))
#
#     @Part
#     def camera(self):
#         return EOIR(target_weight=self.payload, position=translate(XOY, 'x', -0.3))
#
#     # TODO Add a nice bar-graph that shows performance, power consumption, drag, etc in the GUI with boxes!

    @Attribute
    def cg(self):
        print self.weight_and_balance()['CG']
        return self.weight_and_balance()['CG']

    @Attribute
    def weights(self):
        return self.weight_and_balance()['WEIGHTS']

    @Attribute
    def parasite_drag(self):
        """ Utilizes Raymer's Equivalent skin-friction drag method to compute Zero-Lift Drag. The utilized value used
        for the skin_friction_coef is taken from subsonic, light propeller aircraft

        http://www.fzt.haw-hamburg.de/pers/Scholz/HOOU/AircraftDesign_13_Drag.pdf

        :return: Zero-Lift Drag Coefficient
        :rtype: Float
        """
        # TODO Incorporate drag estimation into the knowledge base
        skin_friction_coef = 0.0055
        area_dict = self.sum_area()
        reference_area = area_dict['REFERENCE']
        wetted_area = area_dict['WETTED']['total']
        if wetted_area and reference_area is not 0:
            parasite_drag = skin_friction_coef * (wetted_area / reference_area)
        else:
            parasite_drag = None
        return parasite_drag

    @Attribute
    def areas(self):
        return self.sum_area()

    def weight_and_balance(self):
        """ Retrieves all relevant parameters from children with `weight` and `center_of_gravity` attributes and then
        calculates the center of gravity w.r.t the origin Point(0, 0, 0)

        :return: A dictionary of component weights as well as the center of gravity fieldnames = 'WEIGHTS', 'CG'
        :rtype: dict
        """

        children = self.get_children()

        # Creating dummy lists to store all weights and respective c.g. locations
        weight = []
        cg = []

        # Defining the structure of the weight_dictionary
        weight_dict = {'WEIGHTS': {'wing': 0.0,
                                   'fuselage': 0.0,
                                   'vt': 0.0,
                                   'ht': 0.0,
                                   'payload': 0.0,
                                   'prop': 0.0,
                                   'battery': 0.0,
                                   'electronics': 0.0,
                                   'misc': 0.0},
                       'CG': Point(0, 0, 0)}

        for _child in children:
            if hasattr(_child, 'weight') and hasattr(_child, 'center_of_gravity'):
                weight.append(_child.getslot('weight'))
                cg.append(_child.getslot('center_of_gravity'))

                if _child.getslot('component_type') == 'wing':
                    weight_dict['WEIGHTS']['wing'] = weight_dict['WEIGHTS']['wing'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'fuselage':
                    weight_dict['WEIGHTS']['fuselage'] = weight_dict['WEIGHTS']['fuselage'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'vt':
                    weight_dict['WEIGHTS']['vt'] = weight_dict['WEIGHTS']['vt'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'ht':
                    weight_dict['WEIGHTS']['ht'] = weight_dict['WEIGHTS']['ht'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'payload':
                    weight_dict['WEIGHTS']['payload'] = weight_dict['WEIGHTS']['payload'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'prop':
                    weight_dict['WEIGHTS']['prop'] = weight_dict['WEIGHTS']['prop'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'battery':
                    weight_dict['WEIGHTS']['battery'] = weight_dict['WEIGHTS']['battery'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'electronics':
                    weight_dict['WEIGHTS']['electronics'] = weight_dict['WEIGHTS']['electronics'] + \
                                                            (_child.getslot('weight'))

                else:
                    weight_dict['WEIGHTS']['misc'] = weight_dict['WEIGHTS']['misc'] + _child.getslot('weight')
                    print Warning("%s does not have an Attribute 'component_type'"
                                  "it was thus added to the 'misc' category in the weight_dictionary" % _child)

        total_weight = sum(weight)
        weight_dict['WEIGHTS']['mtow'] = total_weight

        # CG calculation through a weighted average utilizing list comprehension
        if len(weight) and len(cg) is not 0:
            cg_x = sum([weight[i] * cg[i].x for i in range(0, len(weight))]) / total_weight
            cg_y = sum([weight[i] * cg[i].y for i in range(0, len(weight))]) / total_weight
            cg_z = sum([weight[i] * cg[i].z for i in range(0, len(weight))]) / total_weight

            weight_dict['CG'] = Point(cg_x, cg_y, cg_z)

        return weight_dict

    def sum_area(self):
        """ Retrieves all wetted surface areas of instantiated children that have the attributes `wetted_area` and
        `planform_area` which are defined by the class `ExternalBody`. This class

        :return: A dictionary of wetted surface and reference area with the fieldnames: 'WETTED' and 'REFERENCE'
        """
        children = self.get_children()

        areas = []
        area_dict = {'WETTED': {'wing': 0,
                                'fuselage': 0,
                                'vt': 0,
                                'ht': 0,
                                'misc': 0,
                                'total': 0},
                     'REFERENCE': 0}

        for _child in children:
            if hasattr(_child, 'wetted_area') and hasattr(_child, 'planform_area'):
                areas.append(_child.wetted_area)

                if _child.getslot('surface_type') == 'wing':
                    area_dict['WETTED']['wing'] = area_dict['WETTED']['wing'] + _child.wetted_area
                    area_dict['REFERENCE'] = area_dict['REFERENCE'] + _child.planform_area

                elif _child.getslot('surface_type') == 'fuselage':
                    area_dict['WETTED']['fuselage'] = area_dict['WETTED']['fuselage'] + _child.wetted_area

                elif _child.getslot('surface_type') == 'vt':
                    area_dict['WETTED']['vt'] = area_dict['WETTED']['vt'] + _child.wetted_area

                elif _child.getslot('surface_type') == 'vt':
                    area_dict['WETTED']['vt'] = area_dict['WETTED']['vt'] + _child.wetted_area

                elif _child.getslot('surface_type') == 'ht':
                    area_dict['WETTED']['ht'] = area_dict['WETTED']['ht'] + _child.wetted_area

                else:
                    area_dict['WETTED']['misc'] = area_dict['WETTED']['misc'] + _child.wetted_area
                    print Warning("%s does not have an Attribute 'surface_type'"
                                  "it was thus added to the 'misc' category in the area_dictionary" % _child)
        area_dict['WETTED']['total'] = sum(areas)

        return area_dict

    # def validate_geometry(self):
    #     children = self.get_children()
    #     x_loc_max = 0
    #     x_loc_min = 0
    #     index_first = 0
    #     index_last = 0
    #     for _child in children:
    #         if hasattr(_child, 'internal_shape') and getslot(_child, 'component_type') != 'motor':
    #             # Above is the identification of a Motor
    #             current_corners = _child.internal_shape.bbox.corners
    #             if current_corners[1].x > x_loc_max:
    #                 x_loc_max = current_corners[1].x
    #             elif current_corners[0].x < x_loc_min:
    #                 x_loc_min = current_corners[0].x
    #     return x_loc_min, x_loc_max


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
