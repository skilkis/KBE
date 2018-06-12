
#  Required Modules
from parapy.core import *
from parapy.geom import *

from components.liftingsurfaces import VerticalStabilizer, HorizontalStabilizer
from math import radians
from user import MyColors
from definitions import ExternalBody

__author__ = ["Nelson Johnson"]
__all__ = ["CompoundStabilizer"]

# TODO Define proper ExternalBody attributes

class CompoundStabilizer(ExternalBody):
    """ This class will size the VT according to statistical VT volume coefficients and generate it using the
    LiftingSurface primitive. Also, the bounding box is made for the section of the VTP within the fuselage, which is
    used to size the fuselage frames.
    :returns: ParaPy Geometry of the VT
    """

    planform_area = Input(0.8, settable=False)

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
    configuration = Input('conventional', validator=val.OneOf(['canard', 'conventional']), settable=False)

    #: Below is the plane mtow
    #: :type: float
    weight_mtow = Input(25.0, settable=False)  # TODO REMOVE THIS!! THIS IS USED FOR THE OLD WEIGHT ESTIMATION!!!!!!!!!

    #: Below is the assumed VT aspect ratio.
    #: :type: float
    aspect_ratio = Input(1.4, settable=False)

    #: Below is the assumed VT taper ratio.
    #: :type: float
    taper = Input(0.35, settable=False)

    #:  This is the wing twist for the VT.
    #: :type: float
    twist = Input(0.0, settable=False)

    #
    color = Input(MyColors.skin_color)

    @Attribute
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

    @Part
    def stabilizer_h(self):
        return HorizontalStabilizer(position=self.position,
                                    planform_area=self.planform_area)

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

#  ---------------------------------------------------------------------------------------------------------------------

    @Attribute
    def tail_shaft_circle(self):
        _profile = Circle(position=self.stabilizer_vright.position, radius=(self.critical_thickness / 2.0) * 1.5)
        _extrude = ExtrudedSolid(island=_profile, distance=self.stabilizer_h.root_chord)
        return _profile, _extrude

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

    @Attribute
    def boom_plane(self):
        """ Defines the XZ-plane that is coincident with the boom connector """
        return Plane(reference=self.tail_shaft_circle[0].center,
                     normal=Vector(0, 1, 0),
                     binormal=Vector(0, 0, 1))


if __name__ == '__main__':
    from parapy.gui import display

    obj = CompoundStabilizer(label='compoundVstab')
    display(obj)
