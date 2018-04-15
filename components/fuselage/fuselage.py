#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

# Required Modules
from primitives import *
from user import *


class Fuselage(GeomBase):

    widths = Input([0.5, 0.8, 0.8, 0.5, 0.1])
    heights = Input([0.2, 0.4, 0.4, 0.2, 0.1])
    boom_length = Input(4.0)
    x_locs = Input([0, 1, 2, 3, 4])
    z_locs = Input([0, 0, 0, 0, 0])

    @Attribute
    def frame_grabber(self):
        frames = [self.frame_builder[i].frame for i in range(0, self.frame_builder.number_of_items)]
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
    def surface(self):
        return LoftedSurface(profiles=self.frame_grabber)

    @Part
    def surface2(self):
        return LoftedSurface(profiles=[self.frame_grabber[-1], self.boom.frame])

    @Part
    def boom(self):
        return FFrame(width=0.1, height=0.1,
                      position=translate(self.position,
                                         'x', (self.frame_grabber[-1].frame.position.x / 2.0) + self.boom_length,
                                         'z', self.frame_grabber[-1].frame.position.z))

    @Part
    def half_fuselage(self):
        return FusedShell(shape_in=self.surface, tool=self.surface2)

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

