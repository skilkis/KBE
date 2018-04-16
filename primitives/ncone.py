#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *
from primitives import *


class FCone(GeomBase):

    support_frame = Input(FFrame(width=1.0, height=0.5))
    direction = Input('x', validator=val.OneOf(["x", "x_"]))
    slenderness_ratio = Input(0.5, validator=val.Positive())  # nose-cone length / fuselage_length
    fuselage_length = Input(3.0, validator=val.Positive())

    @Attribute
    def build_direction(self):
        value = (-1 if self.direction == 'x' else 1)
        return value

    @Attribute
    def length(self):
        return self.fuselage_length * self.slenderness_ratio

    @Attribute
    def tip_point(self):
        return Point(self.build_direction*self.length, 0, 0)

    @Attribute
    def guides(self):
        start_frame = self.support_frame
        points = start_frame.spline_points

        frame_curve = self.support_frame.frame
        frame_curve_split = SplitCurve(curve_in=frame_curve, tool=points[1]).edges

        v_curve = InterpolatedCurve(points=[points[0], self.tip_point, points[2]])
        v_curve_split = SplitCurve(curve_in=v_curve, tool=self.tip_point).edges

        h_curve = InterpolatedCurve(points=[points[1], self.tip_point, points[3]])
        h_curve_split = SplitCurve(curve_in=h_curve, tool=self.tip_point).edges

        return {'f_curve': frame_curve_split, 'v_curve': v_curve_split, 'h_curve': h_curve_split}

    @Attribute
    def nose_side_guide(self):
        start_frame = self.support_frame
        points = start_frame.spline_points
        return FittedCurve(points=[points[1], self.tip_point, points[3]])

    @Attribute
    def nose_frame(self):
        start_frame = self.support_frame
        points = start_frame.spline_points
        return SplitCurve(curve_in=start_frame.frame, tool=points[1])

    @Attribute
    def test_access(self):
        return self.guides['f_curve'][0]

    @Attribute(private=True)
    def type_errormsg(self):
        error_str = "%s is not a valid type. Valid inputs: 'nose', 'tail'" % self.direction
        raise TypeError(error_str)

    # @Part
    # def nose_top_guide_split(self):
    #     return SplitCurve(curve_in=self.nose_guides[0], tool=self.tip_point)
    #
    # @Part
    # def nose_side_guide_split(self):
    #     return SplitCurve(curve_in=self.nose_guides[1], tool=self.tip_point)
    #
    @Part
    def filled_test(self):
        return FilledSurface(curves=[self.guides['f_curve'][1], self.guides['v_curve'][1],
                                     self.guides['h_curve'][0]])

    @Part
    def filled_test_2(self):
        return FilledSurface(curves=[self.guides['f_curve'][0].reversed, self.guides['v_curve'][0].reversed,
                                     self.guides['h_curve'][0].reversed])

if __name__ == '__main__':
    from parapy.gui import display

    obj = FCone()
    display(obj)