
#  Required Modules
from parapy.core import *
from parapy.geom import *

from components.liftingsurfaces import VerticalStabilizer, HorizontalStabilizer
from math import radians
from user import MyColors
from definitions import ExternalBody

__author__ = ["Nelson Johnson"]
__all__ = ["CompoundStabilizer"]

#  TODO fix error when hide_label changed to false and it is displayed from tree.


class CompoundStabilizer(ExternalBody):
    """ This class will size the VT according to statistical VT volume coefficients and generate it using the
    LiftingSurface primitive. Also, the bounding box is made for the section of the VTP within the fuselage, which is
    used to size the fuselage frames.
    :returns: ParaPy Geometry of the VT
    """

    #: Below is the required horizontal tail area of the main wings from the stability analysis.
    #: :type: float
    required_planform_area = Input(0.8, settable=False)

    #: Below is the required TOTAL wing area of the main wings.
    #: :type: float
    wing_planform_area = Input(0.8, settable=False)

    #: Below is the MAC length of the wing
    #: :type: float
    wing_mac_length = Input(0.43, settable=False)

    #: Below is the semispan of the wing
    #: :type: float
    wing_semi_span = Input(1.9, settable=False)

    #: Below is the non-dimensionalized horizontal tail arm
    #: :type: float
    lhc = Input(3.0, settable=False)

    #: Below is a switch to determine the configuration.
    #: :type: str
    configuration = Input('conventional', validator=val.OneOf(['conventional']), settable=False)

    #: Below is the assumed VT aspect ratio.
    #: :type: float
    aspect_ratio = Input(1.4, settable=False)

    #: Below is the assumed VT taper ratio.
    #: :type: float
    taper = Input(0.35, settable=False)

    #:  This is the wing twist for the VT.
    #: :type: float
    twist = Input(0.0, settable=False)

    #: This value is used to set the default color of the wing-part
    #: :type: tuple
    color = Input(MyColors.skin_color)

    @Attribute
    def component_type(self):
        """ An identifier to classify the part as a Compound Tail """
        return 'ct'

    # TODO Make sure that the horizontal tail does not allow dihedral angle!!!

    @Attribute
    def weight(self):
        """ Total mass of the component

        :return: Mass in SI kilogram
        :rtype: float
        """
        return self.stabilizer_h.weight + self.stabilizer_vright.weight + self.stabilizer_vleft.weight

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity w.r.t the origin

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        return self.position

    @Attribute
    def boom_plane(self):
        """ Defines the XZ-plane that is coincident with the boom connector """
        return Plane(reference=self.tail_shaft_circle[0].center,
                     normal=Vector(0, 1, 0),
                     binormal=Vector(0, 0, 1))

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
        """ This attribute finds the larger airfoil thickness of the horiz. or vert. stabilizer to then be able to
        construct the tail-boom shaft.

        :return: The larger airfoil thickness of the horiz. or vert. stabilizer
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
        _profile = Circle(position=self.stabilizer_vright.position, radius=(self.critical_thickness / 2.0) * 1.5)
        _extrude = ExtrudedSolid(island=_profile, distance=self.stabilizer_h.root_chord)
        return _profile, _extrude

    @Part
    def stabilizer_h(self):
        return HorizontalStabilizer(position=self.position,
                                    planform_area=self.required_planform_area)

    @Part
    def stabilizer_vright(self):
    #  TODO connect lvc to config and figure out how to calc v_v_canard
    #  TODO Relation for AR_v, taper -> STATISTICS
    #  TODO integrate lvc into stability module
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
    #  TODO connect lvc to config and figure out how to calc v_v_canard
    #  TODO Relation for AR_v, taper -> STATISTICS
    #  TODO integrate lvc into stability module
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

    @Part
    def connector_right(self):
        return RotatedShape(shape_in=self.tail_shaft_circle[1],
                            rotation_point=self.tail_shaft_circle[0].center,
                            vector=Vector(0, 1, 0),
                            angle=radians(90))

    @Part
    def connector_left(self):
        return MirroredShape(shape_in=self.connector_right,
                             reference_point=self.position,
                             vector1=Vector(1, 0, 0), vector2=Vector(0, 0, 1))

    @Part
    def external_shape(self):
        """ The final shape of a ExternalSurface class which is to be exported """
        return ScaledShape(shape_in=self.tail_joiner, reference_point=Point(0, 0, 0), factor=1, hidden=True)

    @Attribute(private=True)
    def internal_shape(self):
        """ This overwrites the Part defined in the class `Component` an internal_shape w/ a Dummy Value"""
        return None


if __name__ == '__main__':
    from parapy.gui import display

    obj = CompoundStabilizer(label='Compound Tail')
    display(obj)
