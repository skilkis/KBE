#  This code will estimate the mass and create the geometry of the avionics


from parapy.core import *
from parapy.geom import *
from definitions import *

#  This code will make a couple Flight controllers
__author__ = ["Nelson Johnson"]
__all__ = ["FlightController"]


class FlightController(Component):


    #  Navio 2 Flight computer dimensions
    l_navio = 0.065     #  65mm Length. This longest dimesion is to be oriented parallell with the x axis.
    w_navio = 0.025     #  55mm Width
    h_navio = 0.017     #  17mm height assumed.

    @Part
    def flightcontroller_offset(self):
        #  This creates the geometery of the flight conrtoller.
        #  FOR BOX FUNCTION: Width is x direction, length is y direction, height is z direction.
        return Box(width = self.l_navio,
                   length = self.w_navio,
                   height = self.h_navio,
                   color = 'green',
                   hidden = True)
    @Part
    def flightcontroller(self):
        #  This shifts the shape to the correct place with respect to the local axis system.
        return TranslatedShape(shape_in=self.flightcontroller_offset,
                               displacement = Vector(0,-self.w_navio*0.5,0),
                               transparency = 0.7,
                               color = 'Green')

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
        return 'electronics'

    @Attribute
    def center_of_gravity(self):
        return self.flightcontroller.cog
    @Attribute
    def weight(self):
        #  The weight of the navio2 flight computer is 23 grams.
        return 0.023
    @Attribute
    def internal_shape(self):
        return self.flightcontroller.bbox
    @Attribute
    def label(self):
        return 'Avionics'







if __name__ == '__main__':
    from parapy.gui import display

    obj = FlightController()
    display(obj)