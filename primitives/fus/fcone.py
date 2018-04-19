#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

# Required Modules
from fframe import *
from directories import *

__all__ = ["FCone"]


class FCone(GeomBase):

    __initargs__ = ["support_frame", "direction", "slenderness_ratio", "fuselage_length", "tip_point_z"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'cone.png')

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    support_frame = Input(FFrame(width=1.0, height=0.5))  #
    tangents = Input()
    vector1 = Input(Vector(-1, 0, 0))
    vector2 = Input(Vector(0.8851351164623547, 0, 0.46533410105554684))
    direction = Input('x', validator=val.OneOf(["x", "x_"]))
    slenderness_ratio = Input(0.1, validator=val.Positive())  # nose-cone length / fuselage_length
    fuselage_length = Input(1.0, validator=val.Positive())

    @Attribute
    def length(self):
        return self.fuselage_length * self.slenderness_ratio

    @Attribute
    def cog(self):
        return self.cone.cog

    @Attribute
    def build_direction(self):
        value = (-1 if self.direction == 'x' else 1)
        return value

    @Attribute
    def tip_point(self):
        support_position = self.support_frame.position
        support_mid_point = self.support_frame.spline_points[1]
        return Point(support_position.x + (self.build_direction * self.length),
                     support_position.y, support_mid_point.z)

    @Attribute
    def guides(self):
        start_frame = self.support_frame
        points = start_frame.spline_points

        frame_curve = self.support_frame.frame
        frame_curve_split = SplitCurve(curve_in=frame_curve, tool=points[1]).edges

        v_curve = InterpolatedCurve(points=[points[0], self.tip_point, points[2]],
                                    tangents=[self.vector1,
                                              Vector(0, 0, 1),
                                              self.vector2])
        v_curve_split = SplitCurve(curve_in=v_curve, tool=self.tip_point).edges

        h_curve = FittedCurve(points=[points[1], self.tip_point, points[3]])
        h_curve_split = SplitCurve(curve_in=h_curve, tool=self.tip_point).edges

        return {'f_curve': frame_curve_split, 'v_curve': v_curve_split, 'h_curve': h_curve_split}

    # --- Output Surface: ---------------------------------------------------------------------------------------------

    @Part
    def fused_left(self):
        return FusedShell(shape_in=self.filled_top, tool=self.filled_bot)

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=__show_primitives)
    def filled_top(self):
        return FilledSurface(curves=[self.guides['f_curve'][1], self.guides['v_curve'][1].reversed,
                                     self.guides['h_curve'][0].reversed])

    @Part(in_tree=__show_primitives)
    def filled_bot(self):
        return FilledSurface(curves=[self.guides['h_curve'][0], self.guides['v_curve'][0].reversed,
                                     self.guides['f_curve'][0]])


if __name__ == '__main__':
    from parapy.gui import display

    obj = FCone()
    display(obj)
