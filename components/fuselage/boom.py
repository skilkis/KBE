#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from definitions import *
from components.liftingsurfaces import CompoundStabilizer, Wing
from math import radians
from user import MyColors
from directories import *

__author__ = ["Şan Kılkış", "Nelson Johnson"]
__all__ = ["Boom"]

class Boom(ExternalBody):
    """ This class will create a dual boom connection between the Main wing's spar line and the front face of the
    connector described in 'CompoundStabilizer'.

    :returns: ParaPy Geometry of the Booms

    :param wing_in: This is the Wing instantiation to build the booms.
    :type wing_in: Wing

    :param tail_in: This is the CompoundStabilizer instantiation with connectors to build the booms.
    :type tail_in: CompoundStabilizer

    :param diameter_factor: This is a factor to scale the boom diameter to the connector diameter so they fit inside \
    one another.
    :type diameter_factor: float

    :param ply_number: This is the number of carbon fiber pre-preg plys which the hollow booms are to be made of.
    :type ply_number: int
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'booms.png')

    wing_in = Input(Wing(), validator=val.Instance(Wing))

    tail_in = Input(CompoundStabilizer(), validator=val.Instance(CompoundStabilizer))

    diameter_factor = Input(0.75, validator=val.Between(0.5, 1.0))

    #: Changes the number of ply's of carbon fiber http://www.ijera.com/papers/Vol4_issue5/Version%202/J45025355.pdf
    ply_number = Input(3, validator=val.Instance(int))

    color = Input(MyColors.dark_grey, validator=val.Instance(tuple))

    @Attribute
    def center_of_gravity(self):
        """ Retrives the Center of Gravity location of the combined booms in SI meter [m]

        :rtype: Point """
        half_cg = self.tail_boom.solids[0].cog

        return Point(half_cg.x, 0, half_cg.z)

    @Attribute
    def component_type(self):
        return 'boom'

    @Attribute
    def wing_end_point(self):
        """ Defines the termination point of the boom-extrude.

        :return: Point corresponding to intersection between the :attr:`boom_plane` defined in
        :class:`CompoundStabilizer` and the :attr:`front_spar_line` defined in :class:`Wing`
        tail
        :rtype: Fused
        """
        srf = self.tail_in.boom_plane
        line = self.wing_in.front_spar_line
        return srf.intersection_point(line)

    @Attribute
    def tail_end_point(self):
        """ Components the most forward position of the compound tail

        :return: Position of the front face that the boom will join to
        :rtype: Position
        """
        return self.tail_in.tail_shaft_circle[0].center

    @Attribute
    def boom_length(self):
        """ Computes the length of the boom

        :rtype: float
        """
        return abs(self.wing_end_point.vector_from(self.tail_end_point).x)

    @Attribute
    def boom_tail_curve(self):
        """ Instantiates the curve which is later used by :attr:`booms_import` in an extrude process

        :rtype: RotatedCurve
        """
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
        """ Responsible for instantiating and thus importing the boom shape into the class, this is accomplished first
         by an Extruded solid that is then mirrored and later fused

         :rtype: Fused
         """
        _unrotated = ExtrudedSolid(island=self.boom_tail_curve, distance=self.boom_length)
        _left_boom = MirroredShape(shape_in=_unrotated, reference_point=Point(0, 0, 0), vector1=Vector(1, 0, 0),
                                   vector2=Vector(0, 0, 1))
        _dual_booms = Fused(_unrotated, _left_boom)
        return _dual_booms

    @Part
    def tail_boom(self):
        """ The main geometry output of this class

        :return: A joined set of tail-booms
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.booms_import,
                            rotation_point=self.tail_end_point,
                            vector=Vector(0, -1, 0),
                            angle=radians(90))

    @Part
    def external_shape(self):
        """ This part is the external shape of the boom.

        :return: Presents the two booms for use in wetted area calculation as well as goemetry export
        :rtype: ScaledShape
        """
        return ScaledShape(shape_in=self.tail_boom, reference_point=self.tail_boom.position, factor=1, hidden=True,
                           label=self.label)

    @Attribute(private=True)
    def internal_shape(self):
        """ This overwrites the Part defined in the class `Component` an internal_shape w/ a Dummy Value

        :rtype: None
        """
        return None


if __name__ == '__main__':
    from parapy.gui import display

    obj = Boom(label='Tail Boom')
    display(obj)
