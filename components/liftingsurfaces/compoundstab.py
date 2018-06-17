
#  Required Modules
from parapy.core import *
from parapy.geom import *

from components.liftingsurfaces import VerticalStabilizer, HorizontalStabilizer
from math import radians
from user import MyColors
from definitions import ExternalBody
from directories import *

__author__ = ["Nelson Johnson", "San Kilkis"]
__all__ = ["CompoundStabilizer"]

# TODO fix boom position and add spheres to booms


class CompoundStabilizer(ExternalBody):
    """ This class will instantiate the horizontal tail with the required area form the scissor plot. Also it will
    instantiate the vertical tails and position them relative to one another in a 'boom tail' conifguration.  It also
    places a connector at the VT and HT intersection for the fuselage booms.

    :returns: ParaPy Geometry of the VT

    :param required_planform_area: This is the required horizontal tail area of the main wings from the stability \
    analysis.
    :type required_planform_area: float

    :param wing_planform_area: This is the wing planfrom area in [m^2]
    :type wing_planform_area: float

    :param wing_mac_length: This is the MAC length of the wing in SI meters
    :type wing_mac_length: float

    :param wing_semi_span: This is the semispan of the wing in SI meters
    :type wing_semi_span: float

    :param lhc: This is non-dimensionalized horizontal tail arm for the conventional plane.
    :type lhc: float

    :param configuration: This is a switch to determine the configuration.
    :type configuration: str

    :param aspect_ratio: This is the assumed Aspect Ratio of the HT Surface. The VT surface is a fixed AR of 1.4
    :type aspect_ratio: float

    :param taper: This is the required Taper Ratio of the VT Surface.
    :type taper: float

    :param twist: This is the required Twist Angle of the Tip Airfoil w.r.t the Root Airfoil in degrees.
    :type twist: float

    :param color: Changes the color of the wing skin to the one defined in MyColors
    :type color: tuple
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'ctail.png')

    #: Below is the required horizontal tail area of the main wings from the stability analysis.
    required_planform_area = Input(0.8, settable=False)

    #: Below is the required TOTAL wing area of the main wings.
    wing_planform_area = Input(0.8, settable=False)

    #: Below is the MAC length of the wing
    wing_mac_length = Input(0.43, settable=False)

    #: Below is the semispan of the wing
    wing_semi_span = Input(1.9, settable=False)

    #: Below is the non-dimensionalized horizontal tail arm
    lhc = Input(3.0, settable=False)

    #: Below is a switch to determine the configuration.
    configuration = Input('conventional', validator=val.OneOf(['conventional']), settable=False)

    #: Below is the assumed HT aspect ratio.
    aspect_ratio = Input(5.0, settable=False)

    #: Below is the assumed VT taper ratio.
    taper = Input(0.35, settable=False)

    #:  This is the wing twist for the VT.
    twist = Input(0.0, settable=False)

    #: This value is used to set the default color of the wing-part
    color = Input(MyColors.skin_color)

    @Part
    def stabilizer_h(self):
        """ This is an instantiation of the :class:`HorizontalStabilizer` class with the required planform area from the
        scissor plot.

        :return: Horizontal Tail Object
        :rtype: Fused
        """
        return HorizontalStabilizer(position=self.position,
                                    planform_area=self.required_planform_area,
                                    aspect_ratio=self.aspect_ratio)

    @Part
    def stabilizer_vright(self):
        """ This is an instantiation of the :class:`VerticalStabilizer` class with the current aircraft dimensions for
        the right VT.

        :return: Right Vertical Tail Object
        :rtype: Fused
        """
        return VerticalStabilizer(position=translate(self.position,
                                                     'y', self.stabilizer_h.semi_span,
                                                     'z', sorted(self.stabilizer_h.solid.faces,
                                                                 key=lambda f: f.cog.y)[-1].cog.z - self.position.z),
                                  wing_planform_area=self.wing_planform_area,
                                  wing_mac_length=self.wing_mac_length,
                                  wing_semi_span=self.wing_semi_span,
                                  lvc=self.lhc,
                                  lvc_canard=0.5,
                                  configuration=self.configuration,
                                  aspect_ratio=1.4,
                                  taper=0.35,
                                  twist=0.0)

    @Part
    def stabilizer_vleft(self):
        """ This is an instantiation of the :class:`VerticalStabilizer` with the current aircraft dimensions for the \
        left VT.

        :return: Left Vertical Tail Object
        :rtype: VerticalStabilizer
        """
        return VerticalStabilizer(position=translate(self.position,
                                                     'y', -1 * self.stabilizer_h.semi_span,
                                                     'z', sorted(self.stabilizer_h.solid.faces,
                                                                 key=lambda f: f.cog.y)[-1].cog.z - self.position.z),
                                  wing_planform_area=self.wing_planform_area,
                                  wing_mac_length=self.wing_mac_length,
                                  wing_semi_span=self.wing_semi_span,
                                  lvc=self.lhc,
                                  lvc_canard=self.lhc,
                                  configuration=self.configuration,
                                  aspect_ratio=1.4,
                                  taper=0.35,
                                  twist=0.0)

    @Attribute
    def weight(self):
        """ Total mass of the compound tail.

        :return: Mass in SI kilogram
        :rtype: float
        """
        return self.stabilizer_h.weight + self.stabilizer_vright.weight + self.stabilizer_vleft.weight

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity of the compound stabilizer w.r.t the origin. This is calculated with
        weighted averages.

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        weights = [self.stabilizer_h.weight, self.stabilizer_vright.weight, self.stabilizer_vleft.weight]
        cgs = [self.stabilizer_h.center_of_gravity, self.stabilizer_vright.center_of_gravity,
               self.stabilizer_vleft.center_of_gravity]
        total_weight = sum(weights)
        cg_x = sum([weights[i] * cgs[i].x for i in range(0, len(weights))]) / total_weight
        cg_y = sum([weights[i] * cgs[i].y for i in range(0, len(weights))]) / total_weight
        cg_z = sum([weights[i] * cgs[i].z for i in range(0, len(weights))]) / total_weight

        return Point(cg_x, cg_y, cg_z)

    @Attribute(private=True)
    def tail_joiner(self):
        """ This joins the tails and connector shafts together through a series of Fuse operations to be able to
        present a single `external_shape` required for the .step file output.

        :return: ParaPy Fused Boxes
        :rtype: Fused
        """

        # Fusing Right Horizontal Tail:
        shape_in_r = Fused(shape_in=self.stabilizer_h.solid, tool=self.stabilizer_vright.solid)
        shape_out_r = Fused(shape_in=shape_in_r, tool=self.connector_right)

        # Fusing Left Horizontal Tail:
        shape_in_l = Fused(shape_in=self.stabilizer_h.ht_mirror, tool=self.stabilizer_vleft.solid)
        shape_out_l = Fused(shape_in=shape_in_l, tool=self.connector_left)

        shape_out = Fused(shape_in=shape_out_r, tool=shape_out_l)

        return shape_out

    @Attribute(private=True)
    def critical_thickness(self):
        """ This attribute finds the larger airfoil thickness of the HT or VT stabilizers to then be able to
        construct the tail-boom shaft with a radius equal to this larger thickness.

        :return: The larger airfoil thickness of the HT or VT
        :rtype: float
        """
        horizontal_tail_thickness = sorted(self.stabilizer_h.solid.faces, key=lambda f: f.cog.y)[-1].bbox.height
        vertical_tail_thickness = sorted(self.stabilizer_vright.solid.faces, key=lambda f: f.cog.z)[0].bbox.length
        if horizontal_tail_thickness >= vertical_tail_thickness:
            critical_thickness = horizontal_tail_thickness
        else:
            critical_thickness = vertical_tail_thickness
        return critical_thickness

    @Attribute(private=True)
    def tail_shaft_circle(self):
        """ This attribute makes a circle with thickness found from 'critical_thickness' attribute and extrudes it
        along the HT tip chord.

        :return: Boom Connector Cross-Section and Extrude
        """
        _profile = Circle(position=self.stabilizer_vright.position, radius=(self.critical_thickness / 2.0) * 1.5)
        _extrude = ExtrudedSolid(island=_profile, distance=self.stabilizer_h.root_chord)
        return _profile, _extrude

    @Attribute(private=True)
    def internal_shape(self):
        """ This is the internal shape of the compound stabilizer. It is None because the current app uses a boom tail\
        structure instead of a single fuselage, and thus there is no shape to present for the fuselage builder.

        :rtype: None
        """
        return None

    @Attribute(private=True)
    def ply_number(self):
        """ This overwrites the input defined by the :class:`ExternalBody` since the ply-number should only be \
        controlled from the respective stabilizers themselves.

        :rtype: None
        """
        return None

    @Attribute
    def boom_plane(self):
        """ Defines the XZ-plane that is coincident with the boom connector.

        :return: Boom XZ Plane
        :rtype: Plane
        """
        return Plane(reference=self.tail_shaft_circle[0].center,
                     normal=Vector(0, 1, 0),
                     binormal=Vector(0, 0, 1))

    @Part
    def connector_right(self):
        """ This rotates the extruded right boom shaft connector to point in the X direction.

        :return: Right Boom Connector
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.tail_shaft_circle[1],
                            rotation_point=self.tail_shaft_circle[0].center,
                            vector=Vector(0, 1, 0),
                            angle=radians(90))

    @Part
    def connector_left(self):
        """ This rotates the extruded left boom shaft connector to point in the X direction.

        :return: Left Boom Connector
        :rtype: MirroredShape
        """
        return MirroredShape(shape_in=self.connector_right,
                             reference_point=self.position,
                             vector1=Vector(1, 0, 0), vector2=Vector(0, 0, 1))

    @Attribute
    def component_type(self):
        """ This attribute names the component 'ct' for compound stabilizer.

        :return: Name of Compound Tail Configuration
        :rtype: str
        """
        return 'ct'

    @Part
    def external_shape(self):
        """ This defines the external shape for the ExternalBody class in definitions.

        :return: CompoundStabilizer External Geometry
        :rtype: ScaledShape
        """
        return ScaledShape(shape_in=self.tail_joiner, reference_point=Point(0, 0, 0), factor=1, hidden=True)


if __name__ == '__main__':
    from parapy.gui import display

    obj = CompoundStabilizer(label='Compound Tail')
    display(obj)
