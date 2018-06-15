#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Required Modules
from parapy.core import *
from parapy.geom import *
from definitions import *
from directories import *


__author__ = ["Nelson Johnson"]
__all__ = ["FlightController"]


class FlightController(Component):
    """ This class will create the Navio2 flight controller geometry. The dimensions are at https://emlid.com/navio/ .

    :returns: ParaPy Geometry of the flight computer

    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'chip.png')

    #: Navio 2 Flight computer dimensions are below. Source: https://emlid.com/navio/
    @Attribute
    def l_navio(self):
        """ The 65mm length of the Flight Computer is the longest dimension and is to be oriented parallel with the x
         axis.

        :return: ParaPy Flight Controller Length
        :rtype: float
        """
        return 0.065

    #: :type: float
    @Attribute
    def w_navio(self):
        """ The 55mm width is to be oriented parallel with the y axis.

        :return: ParaPy Flight Controller Width
        :rtype: float
        """
        return 0.055

    @Attribute
    def h_navio(self):
        """ The flight controller height is to be oriented parallel with the y axis. This height was assumed from their
        figure.

        :return: ParaPy Flight Controller height
        :rtype: float
        """
        return 0.017

    @Part
    def flightcontroller_offset(self):
        """ This creates the geometry of the flight controller. FOR BOX FUNCTION: Width is x direction, length is
        y direction, height is z direction.

        :return: ParaPy Flight Controller Geometry
        :rtype: Box
        """
        return Box(width=self.l_navio,
                   length=self.w_navio,
                   height=self.h_navio,
                   color='green',
                   hidden=True)

    @Part
    def solid(self):
        """ This shifts the shape to the correct place with respect to the local axis system.

        :return: ParaPy Flight Controller Geometry
        :rtype: TranslatedShape
        """
        return TranslatedShape(shape_in=self.flightcontroller_offset,
                               displacement=Vector(0, -self.w_navio*0.5, 0),
                               transparency=0.7,
                               color='green')

    @Attribute
    def flight_controller_power(self):
        """ This attribute estimates the Navio2 flight computer power. It is found by multiplying the average voltage
        (5V), by the average current (150mA). Source: https://emlid.com/navio/

        :return: Flight Computer Power
        :rtype: float
        """
        return 0.15*5

    @Attribute
    def component_type(self):
        """ This attribute names the component 'flightcontroller' for flight controller.

        :return: String with flightcontroller's component name
        :rtype: str
        """
        return 'flightcontroller'

    @Attribute
    def center_of_gravity(self):
        """ This attribute returns the COG of the flight controller.

        :return: ParaPy Point
        :rtype: ParaPy Point
        """
        return self.solid.cog

    @Attribute
    def weight(self):
        """ The mass of the Navio2 flight computer is 23 grams.

        :return: Navio2 Mass
        :rtype: float
        """
        return 0.023

    @Part
    def internal_shape(self):
        """ This obtains a bounding box of the flight controller to size the fuselage frames.

        :return: Navio2 Shape
        :rtype: ScaledShape
        """
        return ScaledShape(shape_in=self.solid, reference_point=self.solid.cog, factor=1,
                           transparency=0.7, hidden=True)

    @Attribute
    def label(self):
        """ This labels the flight controller 'Avionics'

        :return: Avionics Label
        :rtype: str
        """
        return 'Avionics'


if __name__ == '__main__':
    from parapy.gui import display

    obj = FlightController()
    display(obj)
