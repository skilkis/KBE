#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

# Required Modules
from fframe import *
from directories import *
from math import sqrt

__author__ = ["Şan Kılkış"]
__all__ = ["FCone"]


class FCone(GeomBase):


    # TODO cleanup init args and inputs, write documentation
    __initargs__ = ["support_frame", "side_tangent", "top_tangent", "direction", "tip_point_z"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'cone.png')

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    support_frame = Input(FFrame(width=1.0, height=0.5))  #
    side_tangent = Input(Vector(-0.88, -0.65, 0))
    top_tangent = Input(Vector(0.8851351164623547, 0, 0.46533410105554684))
    direction = Input('x_', validator=val.OneOf(["x", "x_"]))
    slenderness_ratio = Input(1, validator=val.Range(0, 1.5))  # Nose-cone length / frame diagonal
    transparency = Input(None)

    @Attribute
    def length(self):
        diagonal = sqrt((self.support_frame.height ** 2) + (self.support_frame.width ** 2))
        return self.slenderness_ratio * diagonal

    @Attribute
    def build_direction(self):
        value = (-1 if self.direction == 'x_' else 1)
        return value

    @Attribute
    def side_tangent_reflected(self):
        x = self.side_tangent.x
        y = self.side_tangent.y
        z = self.side_tangent.z
        return Vector(x, -y, z)

    @Attribute
    def tip_point(self):
        support_position = self.support_frame.position
        support_mid_point = self.support_frame.spline_points[1]
        # delta_z = self.build_direction * (self.side_tangent.z / self.side_tangent.x) * self.length
        return Point(support_position.x + (self.build_direction * self.length),
                     support_position.y, support_mid_point.z)

    @Attribute
    def guides(self):
        start_frame = self.support_frame
        points = start_frame.spline_points

        frame_curve = self.support_frame.curve
        frame_curve_split = SplitCurve(curve_in=frame_curve, tool=points[1]).edges

        v_curve = InterpolatedCurve(points=[points[0], self.tip_point, points[2]],
                                    tangents=[Vector(self.build_direction, 0, 0),  # Bottom forced Horizontal
                                              Vector(0, 0, 1),  # Mid-Point Vector (Forced z+ from sign convention)
                                              self.top_tangent])
        v_curve_split = SplitCurve(curve_in=v_curve, tool=self.tip_point).edges

        h_curve = InterpolatedCurve(points=[points[1], self.tip_point, points[3]],
                                    tangents=[self.side_tangent,
                                              Vector(0, -1, 0),  # Mid-Point Vector (Forced y-)
                                              self.side_tangent_reflected])
        h_curve_split = SplitCurve(curve_in=h_curve, tool=self.tip_point).edges

        return {'f_curve': frame_curve_split, 'v_curve': v_curve_split, 'h_curve': h_curve_split}

    # --- Output Surface: ---------------------------------------------------------------------------------------------

    @Part
    def cone(self):
        return SewnShell([self.cone_right, self.cone_left], transparency=self.transparency)

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=__show_primitives)
    def filled_top(self):
        return FilledSurface(curves=[self.guides['f_curve'][1], self.guides['v_curve'][1].reversed,
                                     self.guides['h_curve'][0].reversed])

    @Part(in_tree=__show_primitives)
    def filled_bot(self):
        return FilledSurface(curves=[self.guides['h_curve'][0], self.guides['v_curve'][0].reversed,
                                     self.guides['f_curve'][0]])
    @Part(in_tree=__show_primitives)
    def cone_right(self):
        return SewnShell([self.filled_top, self.filled_bot])

    @Part(in_tree=__show_primitives)
    def cone_left(self):
        return MirroredShape(shape_in=self.cone_right,
                             reference_point=self.position,
                             vector1=self.position.Vx_,
                             vector2=self.position.Vz)

if __name__ == '__main__':
    from parapy.gui import display

    obj = FCone()
    display(obj)
