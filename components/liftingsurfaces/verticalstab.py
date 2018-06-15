#  This script will estimate the required VT size and planform from statistical data.
#  In the future, this will become more detailed!

#  Required Modules
from parapy.core import *
from parapy.geom import *
from math import *
from primitives import LiftingSurface
from definitions import *
from user import MyColors

#  TODO ADD VALIDATOR FOR AIRFOIL TYPE & CHOICE, OFFSET. ALSO IN LIFTING SURF AND HORIZONTAL STAB!!!!!!!

__author__ = ["Nelson Johnson"]
__all__ = ["VerticalStabilizer"]


class VerticalStabilizer(ExternalBody, LiftingSurface):
    """ This class will size the VT according to statistical VT volume coefficients and generate it using the
    LiftingSurface primitive. Also, the bounding box is made for the section of the VTP within the fuselage, which is
    used to size the fuselage frames.

    :returns: ParaPy Geometry of the VT

    :param wing_planform_area: This is the wing planfrom area in [m^2]
    :type wing_planform_area: float

    :param wing_mac_length: This is the MAC length of the wing in SI meters
    :type wing_mac_length: float

    :param wing_semi_span: This is the semispan of the wing in SI meters
    :type wing_semi_span: float

    :param lvc: This is non-dimensionalized vertical tail arm for the conventional plane.
    :type lvc: float

    :param lvc_canard: This is non-dimensionalized vertical tail arm for the canard plane. Note for the canard the \
    VTP is is much closer to the main wing!
    :type lvc_canard: float

    :param configuration: This is a switch to determine the configuration.
    :type configuration: float

    :param aspect_ratio: This is the assumed Aspect Ratio of the VT Surface.
    :type aspect_ratio: float

    :param is_half: This overwrites the is_half parameter from the class LiftingSurface stating that the entire \
    surface area is covering one VT.
    :type is_half: bool

    :param taper: This is the required Taper Ratio of the VT Surface.
    :type taper: float

    :param twist: This is the required Twist Angle of the Tip Airfoil w.r.t the Root Airfoil in degrees.
    :type twist: float

    :param offset: This is the offset in the flow direction of the tip W.R.T. the root Leading Edge.
    :type offset: float or NoneType

    :param fuse_width_factor: This is the assumed factor of the semispan which the fuselage extends over the VT semispan
    :type fuse_width_factor: float

    :param airfoil_type: This is the name of the folder within the 'airfoils' folder. There are three options \
    'cambered', 'reflexed' and 'symmetric'.
    :type airfoil_type: str

    :param airfoil_choice: This is the filename of the requested airfoil.
    :type airfoil_choice: str

    :param ply_number: Changes the number of ply's of carbon fiber pre-preg.
    :type ply_number: int
    """

    #: Below is the required TOTAL wing area of the main wings.
    wing_planform_area = Input(0.8, validator=val.Positive())

    #: Below is the MAC length of the wing.
    wing_mac_length = Input(0.43, validator=val.Positive())

    #: Below is the semispan of the wing.
    wing_semi_span = Input(1.9, validator=val.Positive())

    #: Below is non-dimensionalized vertical tail arm for the conventional plane.
    lvc = Input(3.0, validator=val.Instance(float))

    #: Below is non-dimensionalized vertical tail arm for the canard plane. Note for the canard the VTP is is much
    # closer to the main wing!
    lvc_canard = Input(0.5, validator=val.Instance(float))

    #: Below is a switch to determine the configuration.
    configuration = Input('conventional', validator=val.OneOf(['canard', 'conventional']))

    #: Below is the assumed VT aspect ratio.
    aspect_ratio = Input(1.4, validator=val.Positive())

    #: This overwrites the is_half parameter from the class `LiftingSurface`.
    is_half = Input(True, validator=val.Instance(bool))

    #: Below is the assumed VT taper ratio.
    taper = Input(0.35, validator=val.Range(0.1, 1.0))

    #:  This is the wing twist for the VT.
    twist = Input(0.0, validator=val.Range(-5.0, 5.0))

    #: Below is the chosen trailing edge offset.
    offset = Input(None)

    #: Below is the assumed factor relating the part of the VT covered by fuse to semispan.
    fuse_width_factor = Input(0.1, validator=val.Range(0.001, 0.5))

    #:  This is the airfoil type for the VT. This must contain the correct folder name to the airfoils.
    airfoil_type = Input('symmetric', validator=val.OneOf(['cambered', 'reflexed', 'symmetric']))

    #:  This is the airfoil filename for the VT. This must contain the correct filename name of the airfoil.
    airfoil_choice = Input('NACA0012')

    #: Changes the number of ply's of carbon fiber http://www.ijera.com/papers/Vol4_issue5/Version%202/J45025355.pdf
    ply_number = Input(3, validator=val.Instance(int))


# Attributes below------------------------------------------------------------------------------------------------------
    @Attribute
    def component_type(self):
        """ This attribute names the component 'vt' for horizontal stabilizer.

        :return: Name of VT
        :rtype: str
        """
        return 'vt'

    @Attribute
    def center_of_gravity(self):
        """ This finds the COG for the VT.

        :return: ParaPy Point
        :rtype: Point
        """
        pos = self.solid.cog
        return pos

    @Attribute
    def v_v(self):
        """ This attribute estimates the VTP volume coefficient from statistical agricultural conventional aircraft
        data.

        :return: Estimated VT volume coefficient
        :rtype: float
        """
        v_vset = [i * 2.0 for i in [0.054, 0.036, 0.011, 0.022, 0.034, 0.024, 0.022, 0.033, 0.035, 0.035, 0.032]]
        v_v_avg = sum(v_vset)/len(v_vset)
        return v_v_avg

    @Attribute
    def v_v_canard(self):
        """ This attribute calculates the tail volume coefficient for a canard. This is done by rewriting the equation
        for a conventional VT volume coefficient for S_v/S, equating it to the same equation of the canard. The canard
        tail volume is thus a reduced tail volume coefficient (with the canard having a smaller tail arm).

        :return: Estimated Canard VT volume coefficient
        :rtype: float
        """
        v_v_canard = (-self.lvc_canard/self.lvc)*self.v_v
        return v_v_canard

    @Attribute
    def planform_area(self):
        """ This attribute calculates the total tail surface area based on the estimated VT volume coefficient.

        :return: VT planform area
        :rtype: float
        """
        if self.configuration is 'conventional':
            s_v_req = (self.v_v * self.wing_planform_area * self.wing_semi_span * 2) / self.lvc
        else:
            s_v_req = (self.v_v_canard * self.wing_planform_area * self.wing_semi_span * 2) / self.lvc_canard
        return s_v_req

    @Attribute(private=True)
    def vtwing_cut_loc(self):
        """ This calculates the spanwise distance of the cut, inside of which, the VTP is inside the fuselage.

        :return: VTP length within the fuselage
        :rtype: float
        """
        return self.span * self.fuse_width_factor

    @Attribute(private=True)
    def vtright_cut_plane(self):
        """ This makes a plane at the VTP span location where the fuselage is to end.

        :return: VTP cut Plane ParaPy Geometry
        :rtype: Plane
        """
        return Plane(reference=translate(self.position, 'z', self.vtwing_cut_loc),
                     normal=Vector(0, 0, 1))

    @Attribute(private=True)
    def get_vtfuse_bounds(self):
        """ This attribute is obtaining (the dimensions of) a bounded box at a fuselage width factor of the semispan
        which will be used to size the fuselage frames. These frames drive the shape of the fuselage.

        :return: VTP fuselage section bounding box
        :rtype: bbox
        """
        inner_part = PartitionedSolid(solid_in=self.solid,
                                      tool=self.vtright_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        #  mirrored_part = MirroredShape(shape_in=inner_part, reference_point=self.ht.final_wing.position,
        #                              vector1=Vector(1, 0, 0),vector2=Vector(0, 0, 1))
        root = self.solid.wires[1]

        first_iter = Fused(inner_part, root)
        #  Fusion of the two wing cross sections.
        #  second_iter = Fused(first_iter, mirrored_part)

        bounds = first_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

    @Part
    def solid(self):
        """ This rotates the entire VT solid LiftingSurface instantiation by 90 deg.

        :return: ParaPy rotated lofted solid wing geometry.
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.no_dihedral_solid,
                            rotation_point=self.no_dihedral_solid.position,
                            vector=Vector(1, 0, 0),
                            angle=radians(90),
                            mesh_deflection=self.mesh_deflection)

    @Part
    def internal_shape(self):
        """ This is creating the bounded box at a fuselage width factor of the semispan which will be used to size the
        fuselage frames. These frames drive the shape of the fuselage.

        :return: VTP fuselage section bounding box
        :rtype: Box
        """
        return Box(width=self.get_vtfuse_bounds.width,
                   height=self.get_vtfuse_bounds.height,
                   length=self.get_vtfuse_bounds.length,
                   position=Position(self.get_vtfuse_bounds.center),
                   centered=True,
                   color=MyColors.cool_blue,
                   transparency=0.5,
                   hidden=True)

    @Part
    def external_shape(self):
        """ This defines the external shape for the ExternalBody class in definitions.

        :return: VTP External Geometry
        :rtype: ScaledShape
        """
        return ScaledShape(shape_in=self.solid, reference_point=self.position, factor=1, hidden=True)


if __name__ == '__main__':
    from parapy.gui import display

    obj = VerticalStabilizer()
    display(obj)
