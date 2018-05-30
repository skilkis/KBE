#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Required Modules
from parapy.core import *
from parapy.geom import *
from definitions import *
from flightcontroller import FlightController
from speedcontroller import SpeedController
from components import Motor
from collections import Iterable

#  TODO CONNECT THIS CODE TO MAIN!!!

__author__ = "Nelson Johnson"
__all__ = ["Electronics"]


class Electronics(Component):
    """  This code will estimate the mass and create the geometry of the avionics
    :returns: ParaPy Geometry of the ESC(s)
    """
    # TODO The following input will work if tuple list or set. CONNECT WITH MAIN!!!!!!!!!!!!!!!!!!!!!!!
    motor_in = Input([Motor(), Motor()])

    @Attribute
    def component_type(self):
        """ This attribute names the component 'electronics' for electronics.
        :return: str
        :rtype: str
        """
        return 'electronics'

    @Attribute
    def weight(self):
        """ Total mass of the component

        :return: Mass in SI kilogram
        :rtype: float
        """
        return self.flight_controller.weight + self.speed_controller.weight

#  TODO overwrite weight and CG
#  TODO Make sure this is correct below.
#  TODO Fix internal shape

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
        weight_dict = {'WEIGHTS': {'flight_controller': 0.0,
                                   'speed_controller': 0.0},
                       'CG': Point(0, 0, 0)}

        for _child in children:
            if hasattr(_child, 'weight') and hasattr(_child, 'center_of_gravity'):
                weight.append(_child.getslot('weight'))
                cg.append(_child.getslot('center_of_gravity'))

                if _child.getslot('component_type') == 'flight_controller':
                    weight_dict['WEIGHTS']['flight_controller'] = weight_dict['WEIGHTS']['flight_controller'] +\
                                                                  (_child.getslot('flight_controller'))
                if _child.getslot('component_type') == 'speed_controller':
                    weight_dict['WEIGHTS']['speed_controller'] = weight_dict['WEIGHTS']['speed_controller'] +\
                                                                  (_child.getslot('speed_controller'))

        total_weight = sum(weight)
        weight_dict['WEIGHTS']['Combined'] = total_weight

        # CG calculation through a weighted average utilizing list comprehension
        if len(weight) and len(cg) is not 0:
            cg_x = sum([weight[i] * cg[i].x for i in range(0, len(weight))]) / total_weight
            cg_y = sum([weight[i] * cg[i].y for i in range(0, len(weight))]) / total_weight
            cg_z = sum([weight[i] * cg[i].z for i in range(0, len(weight))]) / total_weight

            weight_dict['CG'] = Point(cg_x, cg_y, cg_z)

        return weight_dict

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity w.r.t the origin

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        return self.weight_and_balance()


    @Attribute
    def amp_req(self):
        """ This is the required amperage for the engine(s).
        :return: Complete Amp draw from the engine(s)
        :rtype: float
        """
        amp_req = 0
        if self.number_engines == 1 and not isinstance(self.motor_in, Iterable):
            amp_req = self.motor_in.specs['esc_recommendation']
        else:
            for i in self.motor_in:
                amp_req = amp_req + i.specs['esc_recommendation']
        return amp_req

    @Attribute
    def number_engines(self):
        """ This is used to determine the number of engines.
        :return: Number of Engines
        :rtype: int
        """
        length = 1
        # length = len(self.motor_in) if type(self.motor_in) is tuple or list else 0
        if isinstance(self.motor_in, Iterable):
            length = len(self.motor_in)
        return length

    @Part
    def flight_controller(self):
        """ This an instantiation of the flight controller. It takes no inputs.
        :return: Flight controller geometry
        :rtype: TranslatedShape
        """
        return FlightController()

    @Part
    def speed_controller(self):
        """ This an instantiation of the speed controller class. It requires the amp draw and the number of engines as
        input.
        :return: Speed Controller(s) Geometry
        :rtype: Box
        """
        return SpeedController(amp_recc=self.amp_req,
                               num_engines=self.number_engines)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Electronics()
    display(obj)
