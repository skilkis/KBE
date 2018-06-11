
#  Required Modules
from parapy.core import *
from parapy.geom import *

from components.liftingsurfaces import VerticalStabilizer, HorizontalStabilizer

__author__ = ["Nelson Johnson"]
__all__ = ["CompoundStabilizer"]


class CompoundStabilizer(GeomBase):
    """ This class will size the VT according to statistical VT volume coefficients and generate it using the
    LiftingSurface primitive. Also, the bounding box is made for the section of the VTP within the fuselage, which is
    used to size the fuselage frames.
    :returns: ParaPy Geometry of the VT
    """

    planform_area = Input(0.8)

    #: Below is the required TOTAL wing area of the main wings.
    #: :type: float
    wing_planform_area = Input(0.8)

    #: Below is the MAC length of the wing
    #: :type: float
    wing_mac_length = Input(0.43)

    #: Below is the semispan of the wing
    #: :type: float
    wing_semi_span = Input(1.9)

    #: Below is the non-dimensionalized horizontal tail arm
    #: :type: float
    lhc = Input(3.0)

    #: Below is non-dimensionalized vertical tail arm for the conventional plane.
    #: :type: float
    lvc = Input(3.0)

    #: Below is non-dimensionalized vertical tail arm for the canard plane. Note for the canard the VTP is is much
    # closer to the main wing!
    #: :type: float
    lvc_canard = Input(0.5)

    #: Below is a switch to determine the configuration.
    #: :type: str
    configuration = Input('conventional', validator=val.OneOf(['canard', 'conventional']))

    #: Below is the plane mtow
    #: :type: float
    weight_mtow = Input(25.0)  # TODO REMOVE THIS!! THIS IS USED FOR THE OLD WEIGHT ESTIMATION!!!!!!!!!!!

    #: Below is the assumed VT aspect ratio.
    #: :type: float
    aspect_ratio = Input(1.4)

    #: Below is the assumed VT taper ratio.
    #: :type: float
    taper = Input(0.35)

    #:  This is the wing twist for the VT.
    #: :type: float
    twist = Input(0.0)


    @Part
    def stabilizer_h(self):
        #  TODO Fix attribute Samispan
        return HorizontalStabilizer(position=self.position,
                                    planform_area=self.planform_area)

    @Part
    def stabilizer_vright(self):
    #  TODO connect lvc to config and figure out how to calc v_v_canard
    #  TODO Relation for AR_v, taper -> STATISTICS
    #  TODO integrate lvc into stability module
        return VerticalStabilizer(position=translate(self.position, 'y', self.stabilizer_h.semi_span),
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
        return VerticalStabilizer(position=translate(self.position, 'y', -1*self.stabilizer_h.semi_span),
                                  wing_planform_area=self.wing_planform_area,
                                  wing_mac_length=self.wing_mac_length,
                                  wing_semi_span=self.wing_semi_span,
                                  lvc=self.lhc,
                                  lvc_canard=0.5,
                                  configuration=self.configuration,
                                  aspect_ratio=1.4,
                                  taper=0.35,
                                  twist=0.0)


if __name__ == '__main__':
    from parapy.gui import display

    obj = CompoundStabilizer(label='compoundVstab')
    display(obj)
