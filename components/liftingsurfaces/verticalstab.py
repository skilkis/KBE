#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.core import *
from parapy.geom import *
from math import *
from primitives import LiftingSurface
from definitions import *

__author__ = ["Nelson Johnson"]
__all__ = ["VerticalStabilizer"]


class VerticalStabilizer(ExternalBody):
    """ This class will size and construct the VT according to statistical VT volume coefficients.
    :returns: ParaPy Geometry of the VT
    """

    S_req = Input(0.8)      # This is the required total wing area from the Class I estimations. TODO CONNECT TO MAIN/ WINGPWR LOADING
    MAC = Input(0.43)       #  This is the MAC of the wing. TODO CONNECT TO MAIN/LIFTING SURFACE
    semispan = Input(1.9)   # This is the wing semispan TODO connect to main
    MTOW = Input(25.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    lvc = Input(3.0)        #  This is the VT tail arm with respect to the CG. TODO CONNECT THIS WITH MAIN/GEOMETRY
    lvc_canard = Input(-0.5)

    #: Below is a switch to determine the configuration.
    #: :type: str
    configuration = Input('conventional', validator=val.OneOf(['canard', 'conventional']))

    #: Below is the assumed VT aspect ratio.
    #: :type: float
    AR_v = Input(1.4)

    #: Below is the assumed VT taper ratio.
    #: :type: float
    taper_v = Input(0.35)

    #: Below is the required VT dihedral angle.
    #: :type: float
    dihedral_v = Input(0.0)

    #:  This is the wing twist for the VT.
    #: :type: float
    phi_v = Input(0.0)

    #:  This is the airfoil type for the VT. This must contain the correct folder name to the airfoils.
    #: :type: str
    airfoil_type_v = Input('symmetric')

    #:  This is the airfoil filename for the VT. This must contain the correct filename name of the airfoil.
    #: :type: str
    airfoil_choice_v = Input('NACA0012')

    #: Below is the chosen trailing edge offset.
    #: :type: NoneType or float
    offset_v = Input(None)

    #: Below is the assumed factor relating the part of the VT covered by fuse to semispan
    #: :type: float
    vtfuse_width_factor = Input(0.1)


# Attributes below------------------------------------------------------------------------------------------------------
    @Attribute
    def component_type(self):
        """ This attribute names the component 'vt' for horizontal stabilizer.
        :return: str
        :rtype: str
        """
        return 'vt'

    @Attribute
    def weight(self):
        """ This attribute was the old method to calculate weight, assuming the VT is 10% MTOW.
        :return: float
        :rtype: float
        """
        return 0.1 * self.MTOW

    @Attribute
    def center_of_gravity(self):
        """ This shows the COG which was found from one wing and translated to origin. This is because because the fused
        shape does not exhibit a C.G.
        :return: ParaPy Point
        :rtype: Point
        """
        pos = self.vt.cog
        return pos

    @Attribute
    def v_v(self):
        """ This attribute estimates the VTP volume coefficient from statistical agricultural conventional aircraft
        data.
        :return: Estimated VT volume coefficient
        :rtype: float
        """
        v_vset = [0.054, 0.036, 0.011, 0.022, 0.034, 0.024, 0.022, 0.033, 0.035, 0.035, 0.032]
        v_v_avg = sum(v_vset)/len(v_vset)
        return v_v_avg

    @Attribute
    def v_v_canard(self):
        """ This attribute calculates the tail volume coefficient for a canard. This is done by rewriting the equation
        for a conventional VT volume coefficient for S_v/S, equating it to the same equation of the canard. The canard
        tail volume is thus a reduced tail volume coefficient (with the canard having a smaller tail arm).
        :return: Canard VT volume coefficient
        :rtype: float
        """
        v_v_canard = (self.lvc_canard/self.lvc)*self.v_v
        return v_v_canard

    @Attribute
    def planform_area(self):
        """ This attribute calculates the total tail surface area based on the estimated VT volume coefficient.
        :return: VT planform area
        :rtype: float
        """
        if self.configuration is 'conventional':
            s_v_req = (self.v_v * self.S_req * self.semispan * 2) / self.lvc
        else:
            s_v_req = (self.v_v_canard * self.S_req * self.semispan * 2) / self.lvc_canard
        return s_v_req

    @Attribute(private=True)
    def vtwing_cut_loc(self):
        """ This calculates the spanwise distance of the cut, inside of which, the VTP is inside the fuselage.
        :return: VTP length within the fuselage
        :rtype: float
        """
        return self.vt_horiz.semispan * self.vtfuse_width_factor

    @Attribute(private=True)
    def vtright_cut_plane(self):
        """ This makes a plane at the VTP span location where the fuselage is to end.
        :return: VTP cut Plane ParaPy Geometry
        :rtype: Plane
        """
        return Plane(reference=translate(self.vt.position, 'y', self.vtwing_cut_loc),
                     normal=Vector(0, 0, 1))

    @Attribute(private=True)
    def get_vtfuse_bounds(self):
        """ This attribute is obtaining (the dimensions of) a bounded box at a fuselaage width factor of the semispan
        which will be used to size the fuselage frames. These frames drive the shape of the fuselage.
        :return: VTP fuselage section bounding box
        :rtype: bbox
        """
        inner_part = PartitionedSolid(solid_in=self.vt,
                                      tool=self.vtright_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        #  mirrored_part = MirroredShape(shape_in=inner_part, reference_point=self.ht.final_wing.position,
        #                              vector1=Vector(1, 0, 0),vector2=Vector(0, 0, 1))
        root = self.vt.wires[1]

        first_iter = Fused(inner_part, root)
        #  Fusion of the two wing cross sections.
        #  second_iter = Fused(first_iter, mirrored_part)

        bounds = first_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

    @Part
    def vt_horiz(self):
        """ This is an instantiation of the lifting surface for ONE HT. Remember, LiftingSurface takes as input the
        wing area for ONE WING!!
        :return: VTP surfaces ParaPy Geometry
        :rtype: RotatedShape
        """
        return LiftingSurface(S=self.planform_area,
                              AR=self.AR_v,
                              taper=self.taper_v,
                              dihedral=self.dihedral_v,
                              phi=self.phi_v,
                              airfoil_type=self.airfoil_type_v,
                              airfoil_choice=self.airfoil_choice_v,
                              offset=self.offset_v,
                              hidden=True)

    @Part
    def vt(self):
        """ This rotates the VTP over a right angle to the correct orientation WRT the aircraft reference system.
        :return: VTP surfaces ParaPy Geometry
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.vt_horiz.final_wing,
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90))

    @Part
    def internal_shape(self):
        """ This is creating the bounded box at a fuselaage width factor of the semispan which will be used to size the
        fuselage frames. These frames drive the shape of the fuselage.
        :return: VTP fuselage section bounding box
        :rtype: Box
        """
        return Box(width=self.get_vtfuse_bounds.width,
                   height=self.get_vtfuse_bounds.height,
                   length=self.get_vtfuse_bounds.length,
                   position=Position(self.get_vtfuse_bounds.center),
                   centered=True)

    @Part
    def external_shape(self):
        """ This rotates the VT over a right angle to the correct orientation WRT the aircraft reference system.
        :return: VTP ParaPy Geometry
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.vt_horiz.final_wing,
                            rotation_point=Point(0, 0, 0),
                            vector=Vector(1, 0, 0),
                            angle=radians(90))


if __name__ == '__main__':
    from parapy.gui import display

    obj = VerticalStabilizer()
    display(obj)
