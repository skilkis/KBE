#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

# Required Modules
from primitives.fus import *
from user import *

__all__ = ["Fuselage"]


class Fuselage(GeomBase):

    widths = Input([0.5, 0.8, 0.8, 0.5])
    heights = Input([0.2, 0.4, 0.4, 0.3])
    boom_length = Input(4.0)
    x_locs = Input([0, 1, 2, 3])
    z_locs = Input([0, 0, 0, 0])

    @Attribute
    def frame_grabber(self):
        frames = [i.frame for i in self.frame_builder]
        frames.append(self.motor.frame)
        return frames

    @Attribute
    def current_pos(self):
        self.position = translate(self.position, 'x', 10)
        return self.position

    @Attribute
    def weird_pos(self):
        return self.frame_grabber[-1].position.x / 2.0  # What the hell is going on here? this number comes out doubled

    @Part
    def frame_builder(self):
        return FFrame(quantify=len(self.widths), width=self.widths[child.index],
                      height=self.heights[child.index],
                      position=translate(self.position, 'x', self.x_locs[child.index], 'z', self.z_locs[child.index]))

    @Part
    def motor(self):
        return MFrame(motor_radius=0.2, position=translate(self.position, 'x', 4))

    @Part
    def surface(self):
        return LoftedSurface(profiles=self.frame_grabber)

    @Part
    def surface2(self):
        return LoftedSurface(profiles=[self.frame_grabber[-1], self.boom.frame])

    # @Part
    # def boom(self):
    #     return FFrame(width=0.1, height=0.1,
    #                   position=translate(self.position,
    #                                      'x', (self.frame_grabber[-1].frame.position.x / 2.0) + self.boom_length,
    #                                      'z', self.frame_grabber[-1].frame.position.z))

    # @Part
    # def half_fuselage(self):
    #     return FusedShell(shape_in=self.surface, tool=self.surface2)

    @Part
    def nosecone(self):
        return FCone(support_frame=self.frame_builder[0], color=MyColors.light_grey)

    # @Part
    # def tailcone(self):
    #     return FCone(support_frame=self.boom, direction='x_')

    @Part
    def tailcone_2(self):
        return FCone(support_frame=self.motor, direction='x_')

    # @Part
    # def nose_reference(self):
    #     return Point(-0.5, 0, 0)
    #
    # @Attribute
    # def nose_top_guide(self):
    #     start_frame = self.frame_builder[0]
    #     points = start_frame.spline_points
    #     return FittedCurve(points=[points[0], self.nose_reference, points[2]])
    #
    # @Attribute
    # def nose_side_guide(self):
    #     start_frame = self.frame_builder[0]
    #     points = start_frame.spline_points
    #     return FittedCurve(points=[points[1], self.nose_reference, points[3]])
    #
    # @Attribute
    # def nose_frame(self):
    #     start_frame = self.frame_builder[0]
    #     points = start_frame.spline_points
    #     return SplitCurve(curve_in=start_frame.frame, tool=points[1])
    #
    # @Part
    # def nose_top_guide_split(self):
    #     return SplitCurve(curve_in=self.nose_top_guide, tool=self.nose_reference)
    #
    # @Part
    # def nose_side_guide_split(self):
    #     return SplitCurve(curve_in=self.nose_side_guide, tool=self.nose_reference)
    #
    # @Part
    # def filled_test(self):
    #     return FilledSurface(curves=[self.nose_frame.edges[1], self.nose_top_guide_split.edges[1],
    #                                  self.nose_side_guide_split.edges[0]])

    @Part
    def fuselage(self):
        return MirroredShape(shape_in=self.half_fuselage, reference_point=YOZ,
                               vector1=Vector(1, 0, 0),
                               vector2=Vector(0, 0, 1),
                               color=MyColors.light_grey)

    @Part
    def end_fuselage(self):
        return FusedShell(shape_in=self.half_fuselage, tool=self.fuselage, color=MyColors.light_grey)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Fuselage()
    display(obj)

