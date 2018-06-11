#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from definitions import *
from directories import *
from components.liftingsurfaces import CompoundStabilizer, Wing
from math import radians

__author__ = ["Şan Kılkış", "Nelson Johnson"]
__all__ = ["Boom"]


class Boom(ExternalBody):

    wing_in = Input(Wing())
    tail_in = Input(CompoundStabilizer())
    diameter_factor = Input(0.75, validator=val.Between(0.5, 1.0))

    @Attribute
    def wing_end_point(self):
        """ Defines the termination point of the boom-extrude """
        srf = self.tail_in.boom_plane
        line = self.wing_in.front_spar_line
        return srf.intersection_point(line)

    @Attribute
    def tail_end_point(self):
        return self.tail_in.tail_shaft_circle[0].center

    @Attribute
    def boom_length(self):
        return abs(self.wing_end_point.vector_from(self.tail_end_point).x)

    @Attribute
    def boom_tail_curve(self):
        sorted_faces = sorted(self.tail_in.connector_right.faces, key=lambda f: f.cog.x)
        scaled_curve = ScaledCurve(curve_in=sorted_faces[0].edges[0],
                                   reference_point=self.tail_end_point,
                                   factor=self.diameter_factor)
        rotated_curve = RotatedCurve(curve_in=scaled_curve,
                                     rotation_point=self.tail_end_point,
                                     vector=Vector(0, 1, 0),
                                     angle=radians(90))
        return rotated_curve

    @Attribute
    def boom_right(self):
        _unrotated = ExtrudedSolid(island=self.boom_tail_curve, distance=self.boom_length)
        left_boom = MirroredShape(shape_in=_unrotated, reference_point=Point(0, 0, 0), vector=Vector(1, 0, 0))
        dual_booms = Fused(_unrotated, left_boom)
        return RotatedShape(shape_in=dual_booms,
                            rotation_point=self.tail_end_point,
                            vector=Vector(0, -1, 0),
                            angle=radians(90))

if __name__ == '__main__':
    from parapy.gui import display

    obj = Boom(label='Tail Boom')
    display(obj)
