#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

__all__ = ["MFrame", "show_primitives"]

show_primitives = False


class MFrame(GeomBase):
    """MFrame (Motor-Frame) is a class which utilizes a scaled 'unit curve' to define a motor-mount cross-section
    that can fit a user-input 'radius'. Furthermore, to facilitate utilization of this class in batch mode,
    the location of the cross-sections on the XZ plane can be supplied with the parameter position=Translate

    :param radius: Internal usable radius of the motor mount
    :type radius: float
    """

    __initargs__ = ["motor_radius", "position"]

    motor_radius = Input(0.5, validator=val.Positive())
    position = Input(Position(Point(0, 0, 0)))  # Added to remove highlighted syntax errors


    @Attribute(in_tree=True)
    def spline_points(self):
        """Defines the control points of the fuselage frame, this can be utilized to later fit a spline across all
        cross-sections of the fuselage
        """

        start = self.frame.start
        mid = self.frame.midpoint
        end = self.frame.end
        mid_reflected = Point(mid[0], -mid[1], mid[2])

        return [start, mid, end, mid_reflected]

    @Attribute(private=True)
    def framepoints(self):
        """Defines the points utilized to construct the shape of the cross-section. If a different shape is required
        these points can be edited as long as a unit-rectangle (1 x 0.5) can still fit inside the cross-section
        """
        return [Point(0, 0, -self.motor_radius), Point(0, self.motor_radius, 0), Point(0, 0, self.motor_radius)]

    # --- Output Frame: -----------------------------------------------------------------------------------------------

    @Part
    def frame(self):
        return TranslatedCurve(curve_in=self.unit_hcircle_import,
                               displacement=Vector(self.position.x, 0, self.position.z))

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=show_primitives)
    def unit_hcircle_import(self):
        return Arc3P(point1=self.framepoints[0], point2=self.framepoints[1], point3=self.framepoints[2])

if __name__ == '__main__':
    from parapy.gui import display

    obj = MFrame()
    display(obj, view='left')
