#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.core import *
from parapy.geom import *
from primitives import LiftingSurface
from scissorplot import ScissorPlot
from definitions import *
from user import MyColors

#  TODO ADD VALIDATOR FOR AIRFOIL TYPE & CHOICE, OFFSET. ALSO IN LIFTING SURF AND VERTICAL STAB!!!!!!!

__author__ = ["Nelson Johnson"]
__all__ = ["HorizontalStabilizer"]


class HorizontalStabilizer(ExternalBody, LiftingSurface):
    """  This script will generate the horizontal stabilizer using the lifting surface primitive with the required area
    from the 'scissorplot.py' script. Also, the bounding box is made for the section of the HTP within the fuselage,
    which is used to size the fuselage frames.

    :returns: ParaPy Geometry of the Horizontal Tail Surface

    :param planform_area: This is the Required Planfrom Area for the HT from the Scissor Plot in [m^2]
    :type planform_area: float

    :param aspect_ratio: This is the required Aspect Ratio of the HT Surface corresponding to the scissor plot value.
    :type aspect_ratio: float

    :param taper: This is the required Taper Ratio of the HT Surface.
    :type taper: float

    :param dihedral: This is the required Dihedral Angle of the HT Surface in degrees.
    :type dihedral: float

    :param twist: This is the required Twist Angle of the Tip Airfoil w.r.t the Root Airfoil in degrees.
    :type twist: float

    :param offset: This is the offset in the flow direction of the tip W.R.T. the root Leading Edge.
    :type offset: float or NoneType

    :param fuse_width_factor: This is the assumed factor of the semispan which the fuselage extends over the HT semispan
    :type fuse_width_factor: float

    :param color: Changes the color of the wing skin to the one defined in MyColors
    :type color: tuple

    :param airfoil_type: This is the name of the folder within the 'airfoils' folder. There are three options \
    'cambered', 'reflexed' and 'symmetric'.
    :type airfoil_type: str

    :param airfoil_choice: This is the filename of the requested airfoil.
    :type airfoil_choice: str

    :param ply_number: Changes the number of ply's of carbon fiber pre-preg.
    :type ply_number: int
    """

    #: Below is the required tail surface area from the scissor plot.
    planform_area = Input(0.8, validator=val.Positive())

    #: Below is the required HT aspect ratio.
    aspect_ratio = Input(5.0, validator=val.Positive())

    #: Below is the required HT taper ratio.
    taper = 1.0

    #: Below is the tail dihedral angle.
    dihedral = 0.0

    #: Below is the tail wing twist angle.
    twist = Input(0.0, validator=val.Range(-5.0, 5.0))

    #: Below is the chosen trailing edge offset.
    offset = Input(None)

    #: Below is the assumed factor relating the part of the HT covered by fuse to semispan
    fuse_width_factor = Input(0.025)

    #: Changes the color of the wing skin to the one defined in MyColors
    color = Input(MyColors.skin_color)

    #: Below is the tail airfoil type. The input must correspond to an existing folder.
    airfoil_type = Input('symmetric', validator=val.OneOf(['cambered', 'reflexed', 'symmetric']))

    #: Below is the tail airfoil DAT file. The input must correspond to an existing filename.
    airfoil_choice = Input('NACA0012')

    #: Changes the number of ply's of carbon fiber http://www.ijera.com/papers/Vol4_issue5/Version%202/J45025355.pdf
    ply_number = Input(4, validator=val.Instance(int))


#  Attributes ########--------------------------------------------------------------------------------------------------
    @Attribute
    def component_type(self):
        """ This attribute names the component 'ht' for horizontal stabilizer.

        :return: Name of HT
        :rtype: str
        """
        return 'ht'

    @Attribute
    def center_of_gravity(self):
        """ This shows the COG which was found from one wing and translated to origin. This is because because the fused
        shape does not exhibit a C.G.

        :return: ParaPy Point of HT CG
        :rtype: Point
        """
        pos = Point(self.solid.cog.x, self.position.y, self.solid.cog.z)
        return pos

    @Attribute
    def htwing_cut_loc(self):
        """ This calculates the spanwise distance of the cut, inside of which, the HT is inside the fuselage. This
        location is where the HT bbox to size the fuselage frame(s) ends in the spanwise direction. The height of this
        bbox is the maximum thickness of the wing at this cut location.

        :return: Spanwise distance from HT root chord to cut location
        :rtype: float
        """
        return self.semi_span*self.fuse_width_factor

    @Attribute
    def htright_cut_plane(self):
        """  This makes a plane at the right HT span location where the fuselage is to end.

         :return: ParaPy Plane to cut HT
         :rtype: Plane
         """
        return Plane(reference=translate(self.solid.position,
                                         'y', self.htwing_cut_loc),
                     normal=Vector(0, 1, 0),
                     hidden=True)

    @Attribute
    def get_htfuse_bounds(self):
        """  This attribute is obtaining (the dimensions of) a bounded box at a fuselage width factor of the semispan
         which will be used to size the fuselage frames. These frames drive the shape of the fuselage.

         :return: ParaPy Bounding Box
         :rtype: bbox
         """
        inner_part = PartitionedSolid(solid_in=self.solid,
                                      tool=self.htright_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        mirrored_part = MirroredShape(shape_in=inner_part,
                                      reference_point=self.solid.position,
                                      vector1=Vector(1, 0, 0),
                                      vector2=Vector(0, 0, 1))
        #  Above mirrors the cross section about the aircraft symmetry plane.
        root = sorted(self.solid.faces, key=lambda f: f.cog.y)[0].edges[0]
        first_iter = Fused(inner_part, root)
        #  Fusion of the three wing cross sections is done in 2 steps to avoid ParaPy errors.
        second_iter = Fused(first_iter, mirrored_part)

        bounds = second_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

#  Parts #####----------------------------------------------------------------------------------------------------------

    @Part
    def ht_mirror(self):
        """  This is a mirrored shape of the right HT.

        :return: HT left wing half
        :rtype: MirroredShape
        """
        return MirroredShape(shape_in=self.solid,
                             reference_point=self.solid.position,
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1))

    @Part
    def internal_shape(self):
        """ This part creates the bounding box for the part of the HT within the fuselage.

        :return: HT fuselage Sizing bbox
        :rtype: Box
        """
        return Box(width=self.get_htfuse_bounds.width,
                   height=self.get_htfuse_bounds.height,
                   length=self.get_htfuse_bounds.length,
                   position=Position(self.get_htfuse_bounds.center),
                   centered=True,
                   color=MyColors.cool_blue,
                   transparency=0.5,
                   hidden=True)

    @Part
    def external_shape(self):
        """ This part is the external shape of the HT.

        :return: Fused Shape of left and right HT surfaces
        :rtype: Fused
        """
        return Fused(self.solid, self.ht_mirror, hidden=True)


if __name__ == '__main__':
    from parapy.gui import display

    obj = HorizontalStabilizer()
    display(obj)
