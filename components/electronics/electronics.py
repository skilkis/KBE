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
