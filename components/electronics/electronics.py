#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Required Modules
from parapy.core import *
from parapy.geom import *
from definitions import *
from directories import *
from flightcontroller import FlightController
from speedcontroller import SpeedController
from components import Motor
from collections import Iterable

__author__ = "Nelson Johnson"
__all__ = ["Electronics"]


class Electronics(Component):
    """  This class will instantiate the flight controller and speed_controller(s) and place them on top of one another.

    :returns: ParaPy Geometry of the electronics
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'electronics.png')

    #  If multiple motors put in, give [] within input parentheses
    motor_in = Input(Motor())

    label = Input('Electronics')

    @Attribute
    def component_type(self):
        """ This attribute names the component 'electronics' for electronics.

        :return: String with electronics component name
        :rtype: str
        """
        return 'electronics'

    @Attribute
    def weight(self):
        """ Total mass of the electronics components

        :return: Mass in SI kilograms
        :rtype: float
        """
        return self.flight_controller.weight + self.speed_controller.weight

    @Attribute
    def amp_req(self):
        """ This is the required amperage for the engine(s).

        :return: Complete Amp draw from the engine(s) in SI Amps
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
        """ This is used to determine the number of engines from the input motor_in.

        :return: Number of Engines
        :rtype: int
        """
        length = 1
        if isinstance(self.motor_in, Iterable):
            length = len(self.motor_in)
        return length

    @Part
    def flight_controller(self):
        """ This an instantiation of the flight controller. It takes only the position input.

        :return: Flight controller geometry
        :rtype: TranslatedShape
        """
        return FlightController(position=self.position)

    @Part
    def speed_controller(self):
        """ This an instantiation of the speed controller class. It requires the amp draw and the number of engines and
        position as input.

        :return: Speed Controller(s) Geometry
        :rtype: Box
        """
        return SpeedController(position=self.position,
                               amp_recc=self.amp_req,
                               num_engines=self.number_engines)

    @Attribute
    def box_length(self):
        """ This returns the length of the flight controller box for calculations.

        :return: Flight Controller Length
        :rtype: float
        """
        return self.flight_controller.l_navio

    @Attribute
    def elec_joiner(self):
        """ This joins the ESC's together through a series of Fuse operations to be able to present a
        single `internal_shape` required for the fuselage frame sizing.

        :return: ParaPy Fused Boxes
        :rtype: Fused
        """
        parts_in = [self.speed_controller.esc_joiner, self.flight_controller.solid]
        if self.number_engines > 1:
            shape_in = parts_in[0]
            for i in range(0, self.number_engines - 1):
                new_part = Fused(shape_in=shape_in, tool=parts_in[i+1])
                shape_in = new_part
            shape_out = shape_in
        else:
            shape_out = parts_in[0]
        return shape_out

    @Attribute
    def center_of_gravity(self):
        """ This attribute finds the center of gravities of the separate ESCs, then finds the combined C.G.

          :return: ParaPy Point
          :rtype: Point
          """
        cogs = [self.speed_controller.center_of_gravity, self.flight_controller.center_of_gravity]
        weights = [self.speed_controller.weight, self.flight_controller.weight]

        # CG calculation through a weighted average utilizing list comprehension
        cg_x = sum([weights[i] * cogs[i].x for i in range(0, len(weights))]) / self.weight
        cg_y = sum([weights[i] * cogs[i].y for i in range(0, len(weights))]) / self.weight
        cg_z = sum([weights[i] * cogs[i].z for i in range(0, len(weights))]) / self.weight

        return Point(cg_x, cg_y, cg_z)

    @Part
    def internal_shape(self):
        """ This is creating a box for the fuselage frames. This is used to get around ParaPy errors.

        :return: Speed Controller(s) bounded box
        :rtype: ScaledShape
        """
        return ScaledShape(shape_in=self.elec_joiner, reference_point=self.speed_controller.center_of_gravity, factor=1, transparency=0.7)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Electronics()
    display(obj)
