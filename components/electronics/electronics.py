#  This code will estimate the mass and create the geometry of the avionics


from parapy.core import *
from parapy.geom import *
from definitions import *
from flightcontroller import FlightController
from speedcontroller import SpeedController
from components import Motor

#  This code will make a couple Flight controllers
__author__ = "Nelson Johnson"
__all__ = ["Electronics"]


class Electronics(Component):

    #  TODO CONNECT THIS CODE TO MAIN!!!
    motor_in = Input((Motor(), Motor()))    #  The following input will work if tuple list or set.

    @Attribute
    def amp_req(self):
        #  This is the required amperage for both engines.
        amp_req = 0
        if self.number_engines == 1:
            amp_req = self.motor_in.specs['esc_recommendation']
        else:
            for i in self.motor_in:
                amp_req = amp_req + i.specs['esc_recommendation']
        return amp_req

    @Attribute
    def number_engines(self):
        length = 1
        # length = len(self.motor_in) if type(self.motor_in) is tuple or list else 0
        if isinstance(self.motor_in, (tuple, list, set)):
            length = len(self.motor_in)
        return length

    @Part
    def flight_controller(self):
        #  Flight Controller takes no inputs.
        return FlightController()

    @Part
    def speed_controller(self):
        #  Speed controller takes inputs continuous amp draw and number of engines.
        return SpeedController(amp_recc = self.amp_req,
                               num_engines = self.number_engines)

if __name__ == '__main__':
    from parapy.gui import display

    obj = Electronics()
    display(obj)