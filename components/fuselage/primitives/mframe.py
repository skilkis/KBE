#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

#TODO Allow this to work with any input position

__author__ = ["Şan Kılkış"]
__all__ = ["MFrame"]


class MFrame(GeomBase):
    """MFrame (Motor-Frame) is a class which utilizes a scaled 'unit curve' to define a motor-mount cross-section
    that can fit a user-input 'motor_diameter'. Furthermore, to facilitate utilization of this class in batch mode,
    the location of the cross-sections can be with the input `position`.

    :param motor_diameter: Internal usable diameter of the motor mount
    :type motor_diameter: float

    :param position: Position of the cross-section in 3D space.
    :type position: Position(Point)
    """

    __initargs__ = ["motor_diameter", "position"]

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    motor_diameter = Input(0.5, validator=val.Positive())
    position = Input(Position(Point(0, 0, 0)))  # Added to remove highlighted syntax errors

    @Attribute(in_tree=True)
    def spline_points(self):
        """Defines the control points of the fuselage frame, this can be utilized to later fit a spline across all
        cross-sections of the fuselage
        """

        start = self.curve.start
        mid = self.curve.midpoint
        end = self.curve.end
        mid_reflected = Point(mid[0], -mid[1], mid[2]).translate(y=2.0 * self.position.y)

        return [start, mid, end, mid_reflected]

    @Attribute
    def motor_radius(self):
        return self.motor_diameter / 2.0

    @Attribute(private=True)
    def curvepoints(self):
        """Defines the points utilized to construct the shape of the motor-mount cross-section. If a different shape
        is required these points can be edited as long as a unit-circle (radius = 1) can still fit inside the
        cross-section at the origin.
        """
        return [Point(0, 0, -self.motor_radius), Point(0, self.motor_radius, 0), Point(0, 0, self.motor_radius)]

    # --- Output Frame: -----------------------------------------------------------------------------------------------

    @Part
    def curve(self):
        return TranslatedCurve(curve_in=self.unit_hcircle_import,
                               displacement=Vector(self.position.x, self.position.y, self.position.z))

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=__show_primitives)
    def unit_hcircle_import(self):
        return Arc3P(point1=self.curvepoints[0], point2=self.curvepoints[1], point3=self.curvepoints[2])

if __name__ == '__main__':
    from parapy.gui import display

    obj = MFrame()
    display(obj, view='left')
