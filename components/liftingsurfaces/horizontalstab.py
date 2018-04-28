#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.core import *
from parapy.geom import *
from primitives import LiftingSurface
from scissorplot import ScissorPlot
from definitions import *

# TODO CONNECT WEIGHT TO MAIN!!!!!!!!!!


class HorizontalStabilizer(ExternalBody):
    """  This script will generate the horizontal stabilizer using the lifting surface primitive with the required Sh
    from the 'scissorplot.py' script.
    """

    #: Below is the required tail surface area from the scissor plot.
    #: :type: float
    S_req = Input(0.8, validator=val.Positive())

    #: Below is the required tail aspect ratio.
    #: :type: float
    AR_h = Input(5.0, validator=val.Positive())

    #: Below is the required tail taper ratio.
    #: :type: float
    taper_h = Input(0.5, validator=val.Positive())

    #: Below is the tail dihedral angle.
    #: :type: float
    dihedral_h = Input(0.0)

    #: Below is the tail wing twist angle.
    #: :type: float
    phi_h = Input(-0.0)

    #: Below is the tail airfoil type. The input must correspond to an existing folder.
    #: :type: str
    airfoil_type_h = Input('symmetric', validator=val.OneOf(['cambered', 'reflexed', 'symmetric']))

    #: Below is the tail airfoil DAT file. The input must correspond to an existing filename.
    #: :type: str
    airfoil_choice_h = Input('NACA0012')

    #: Below is the chosen trailing edge offset.
    #: :type: NoneType or float
    offset_h = Input(None)

    #: Below is the assumed factor relating the part of the HT covered by fuse to semispan
    #: :type: float
    htfuse_width_factor = Input(0.025)

    #: Below is the MTOW from the Class I weight Estimation.
    #: :type: float
    weight_mtow = Input(25.0)

#  Attributes ########--------------------------------------------------------------------------------------------------
    @Attribute
    def component_type(self):
        """ This attribute names the component 'ht' for horizontal stabilizer.
        :return: str
        :rtype: str
        """
        return 'ht'

    @Attribute
    def weight(self):
        """ This attribute was the old method to calculate weight, assuming the HT is 10% MTOW.
        :return: float
        :rtype: float
        """
        return 0.1*self.weight_mtow

    @Attribute
    def center_of_gravity(self):
        """ This shows the COG which was found from one wing and translated to origin. This is because because the fused
        shape does not exhibit a C.G.
        :return: ParaPy Point
        :rtype: Point
        """
        y = 0
        pos = Point(self.ht.final_wing.cog.x, y, self.ht.final_wing.cog.z)
        return pos

    @Attribute
    def planform_area(self):
        """  This is an attribute giving the planform area.
        :return: HT wing area
        :rtype: float
        """
        return self.S_req

    @Attribute(private=True)
    def htwing_cut_loc(self):
        """  This calculates the spanwise distance of the cut plane, inside of which, the wing is inside the fuselage.
         :return: Spanwise distance to cut wing.
         :rtype: float
         """
        return self.ht.semispan*self.htfuse_width_factor

    @Attribute(private=True)
    def htright_cut_plane(self):
        """  This makes a plane at the right wing span location where the fuselage is to end..
         :return: ParaPy Plane to cut wing
         :rtype: Plane
         """
        return Plane(reference= translate(self.ht.position,
                                          'y', self.htwing_cut_loc),
                     normal=Vector(0, 1, 0),
                     hidden=True)

    @Attribute(private=True)
    def get_htfuse_bounds(self):
        """  This attribute is obtaining (the dimensions of) a bounded box at a fuselage width factor of the semispan
         which will be used to size the fuselage frames. These frames drive the shape of the fuselage.
         :return: ParaPy Bounding Box
         :rtype: bbox
         """
        inner_part = PartitionedSolid(solid_in = self.ht.final_wing,
                                      tool=self.htright_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        mirrored_part = MirroredShape(shape_in=inner_part,
                                      reference_point=self.ht.final_wing.position,
                                      vector1=Vector(1, 0, 0),
                                      vector2=Vector(0, 0, 1))
        #  Above mirrors the cross section about the aircraft symmetry plane.
        root = self.ht.root_airfoil
        first_iter = Fused(inner_part, root)
        #  Fusion of the three wing cross sections is done in 2 steps to avoid ParaPy errors.
        second_iter = Fused(first_iter, mirrored_part)

        bounds = second_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

#  Parts #####----------------------------------------------------------------------------------------------------------
    @Part
    def ht(self):
        """  This is an instantiation of the lifting surface for ONE HT. Remember, LiftingSurface takes as input the
        wing area for ONE WING!
        :return: HT right wing half
        :rtype: RotatedShape
        """
        return LiftingSurface(S=self.S_req*0.5,
                              AR=self.AR_h,
                              taper=self.taper_h,
                              dihedral=self.dihedral_h,
                              phi=self.phi_h,
                              airfoil_type=self.airfoil_type_h,
                              airfoil_choice=self.airfoil_choice_h,
                              offset=self.offset_h)

    @Part
    def ht_mirror(self):
        """  This is a mirrored shape of the right HT.
        :return: HT left wing half
        :rtype: MirroredShape
        """
        return MirroredShape(shape_in=self.ht.final_wing,
                             reference_point=self.ht.position,
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1))


    @Part
    def internal_shape(self):
        """ This part creates the bounding box for the part of the HT within the fuselage.
        :return: ParaPy Box
        :rtype: Box
        """
        return Box(width=self.get_htfuse_bounds.width,
                   height=self.get_htfuse_bounds.height,
                   length=self.get_htfuse_bounds.length,
                   position=Position(self.get_htfuse_bounds.center),
                   centered=True)

    @Part
    def external_shape(self):
        """ This part is the external shape of the HT.
        :return: Fused Shape
        :rtype: Fused
        """
        return Fused(self.ht.final_wing, self.ht_mirror)


if __name__ == '__main__':
    from parapy.gui import display

    obj = HorizontalStabilizer()
    display(obj)
