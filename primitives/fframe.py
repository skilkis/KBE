#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

__all__ = ["FFrame", "show_primitives"]

show_primitives = False


class FFrame(GeomBase):
    """FFrame (Fuselage-Frame) is a class which utilizes a scaled 'unit curve' to define a fuselage cross-section
    that can fit a user-input `width` and `height`. Furthermore, to facilitate utilization of this class in batch mode,
    the location of the cross-sections on to x-axis can be supplied with the parameter position=Translate

    :param width: Internal usable width of the fuselage
    :type width: float

    :param height: Internal usable height of the fuselage
    :type height: float

    :param x_loc: Position of the cross-section on the x-axis
    :type x_loc: float
    """

    __initargs__ = ["width", "height", "position"]

    width = Input(1.0)
    height = Input(0.5)
    position = Input(Position(Point(0, 0, 0)))  # Added to remove highlighted syntax errors


    @Attribute(in_tree=True)
    def spline_points(self):
        """Defines the control points of the fuselage frame, this can be utilized to later fit a spline across all
        cross-sections of the fuselage
        """
        return [self.frame.point1, self.frame.midpoint, self.frame.point2]

    @Attribute(private=True)
    def framepoints(self):
        """Defines the points utilized to construct the shape of the cross-section. If a different shape, is required
        these points can be edited as long as a unit-square can still fit inside the cross-section
        """
        return [Point(0, 0, -0.05), Point(0, 0.8, 0.15), Point(0, 0, 0.6)]

    @Attribute(private=True)
    def tangents(self):
        return [Vector(0, 1, 0), Vector(0, 0, 1), Vector(0, -1, 0)]

    # --- Output Frame: -----------------------------------------------------------------------------------------------

    @Part
    def frame(self):
        return TranslatedCurve(curve_in=self.unit_curve, displacement=Vector(self.position.x, 0, self.position.z))

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=show_primitives)
    def unit_curve_import(self):
        return InterpolatedCurve(points=self.framepoints,
                                 tangents=self.tangents)

    @Part(in_tree=show_primitives)
    def unit_curve(self):
        return ScaledCurve(curve_in=self.unit_curve_import,
                           reference_point=YOZ, factor=(1, self.width, self.height * 2.0))

    @Part(in_tree=show_primitives)
    def visualize_bounds(self):
        return Rectangle(width=self.width, length=self.height,
                         position=translate(YOZ, 'y', self.height / 2.0),
                         color='red')


if __name__ == '__main__':
    from parapy.gui import display

    obj = FFrame()
    display(obj, view='left')
