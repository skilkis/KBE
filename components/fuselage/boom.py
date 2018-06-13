#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from definitions import *
from components.liftingsurfaces import CompoundStabilizer, Wing
from math import radians

__author__ = ["Şan Kılkış", "Nelson Johnson"]
__all__ = ["Boom"]


class Boom(ExternalBody):

    wing_in = Input(Wing())
    tail_in = Input(CompoundStabilizer())
    diameter_factor = Input(0.75, validator=val.Between(0.5, 1.0))

    @Attribute
    def component_type(self):
        return 'boom'

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

    @Attribute(private=True)
    def booms_import(self):
        _unrotated = ExtrudedSolid(island=self.boom_tail_curve, distance=self.boom_length)
        _left_boom = MirroredShape(shape_in=_unrotated, reference_point=Point(0, 0, 0), vector1=Vector(1, 0, 0),
                                   vector2=Vector(0, 0, 1))
        _dual_booms = Fused(_unrotated, _left_boom)
        return _dual_booms

    @Part
    def tail_boom(self):
        return RotatedShape(shape_in=self.booms_import,
                            rotation_point=self.tail_end_point,
                            vector=Vector(0, -1, 0),
                            angle=radians(90))

    @Part
    def external_shape(self):
        """ This part is the external shape of the boom.
        :return: Fused Shape
        :rtype: Fused
        """
        return ScaledShape(shape_in=self.tail_boom, reference_point=self.tail_boom.position, factor=1, hidden=True,
                           label=self.label)

    @Attribute(private=True)
    def internal_shape(self):
        """ This overwrites the Part defined in the class `Component` an internal_shape w/ a Dummy Value"""
        return None


if __name__ == '__main__':
    from parapy.gui import display

    obj = Boom(label='Tail Boom')
    display(obj)
