#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.core import *

# Other Modules
from directories import *

__author__ = "Nelson Johnson"
__all__ = ["ClassOne", "ClassTwo"]


class ClassOne(Base):
    """A simple Class-I weight estimation with values :attr:`mtow`, :attr:`payload`. This class sets the global weight
    of the aircraft in stone. A higher payload or maximum take-off weight from the one defined here will be flagged
    to the user. The following two use cases are possible which answer either one of two customer questions:
    [1] How heavy will the UAV need to be to carry a certain payload or [2] How much payload can a UAV with a certain
    maximum take-off weight carry? This is accomplished by specifying with :type:`string` input what the target weight,
    or in other words, the know weight parameter, into the field :attr:`weight_target`. The field :attr:`target_value`
    is then the corresponding value for this target weight which needs to be a :type:`float` in SI kilogram.

    :param weight_target: Defines if the input `target_value` is a payload weight or maximum take-off weight
    :type weight_target: str
    :param target_value: The weight value assigned to the respective type in `weight_target`
    :type target_value: float

    :returns: Weight values for maximum take-off weight ('weight_mtow') and payload weight ('weight_payload')
    :rtype: float

    |
    |   [1] Payload Weight to Required Maximum Take-Off Weight:
    >>> from design import ClassOne
    >>> weight = ClassOne('payload',0.25)  # keywords: ClassOne (weight_target='payload', target_value=0.25)
    >>> weight.weight_payload
    0.25
    >>> weight.weight_mtow
    1.788395

    |
    |   [2] Maximum Take-Off Weight to Allowable Payload Weight:
    >>> from design import ClassOne
    >>> weight = ClassOne ('mtow',1.788395) # keywords: ClassOne (weight_target='mtow', target_value=1.788395)
    >>> weight.weight_mtow
    1.788395
    >>> weight.weight_payload
    0.2499994685
    """

    __initargs__ = ["weight_target", "target_value"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'weight.png')

    # TODO Figure out validator functions here to check string
    weight_target = Input('payload', validator=val.OneOf(["payload", "mtow"]))
    target_value = Input(0.25, validator=val.Positive())

    @Attribute
    def weight_mtow(self):
        if self.weight_target == 'payload':
            mtow = 4.7551 * self.target_value + 0.59962
            #  Estimation of MTOW from payload mass from DSE Midterm Report.
            #  It is valid for UAVs with payload masses between 0 and 50 kg.
            return mtow
        elif self.weight_target == 'mtow':
            return self.target_value

    @Attribute
    def weight_payload(self):
        if self.weight_target == 'mtow':
            m_pl_derived = 0.2103 * self.target_value - 0.1261
            #  Estimation of m_pl from MTOW with reversed Eq.
            return m_pl_derived
        elif self.weight_target == 'payload':
            return self.target_value


class ClassTwo(Base):
    """A simple Class-II component weight estimation with values :attr:`mtow`,.....
    The propulsion, battery, electronics and payload masses are already calculated, the remaining weight from MTOW
    is split between the wings and the fuselage.
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'piechart.png')

    #: Below is the MTOW of the UAV.
    #: :type: float
    weight_mtow = Input(2.0)

    #: Below is the payload mass of the UAV.
    #: :type: float
    weight_payload = Input(0.1)

    #: Below is the motor mass of the UAV.
    #: :type: float
    weight_prop = Input(0.1)

    #: Below is the battery mass of the UAV.
    #: :type: float
    weight_batt = Input(0.2)

    #: Below is the electronics mass of the UAV.
    #: :type: float
    weight_electronics = Input(0.1)

    #: Below is the horizontal stabilizer area of the UAV.
    #: :type: float
    S_h = Input(0.1)

    #: Below is the total wing area of the UAV.
    #: :type: float
    S = Input(0.4)

    #: Below is the vertical stabilizer area of the UAV.
    #: :type: float
    S_v = Input(0.1)

    #: Below is the wetted fuselage area of the UAV.
    #: :type: float
    S_f = Input(0.1)

    @Attribute
    def weight_structural(self):
        #  This returns the remainder of the MTOW after the engine, battery and payload masses subtracted.
        #  This is assumed to be evenly split between the fuselage and wing weights.
        return self.weight_mtow - self.weight_prop - self.weight_batt - self.weight_payload - self.weight_electronics

    @Attribute
    def structural_weight_per_area(self):
        ratio = self.weight_structural / (self.S + self.S_v + self.S_h + self.S_f)
        return ratio

    @Attribute
    def weight_fuselage(self):
        #  This is the assumed fuselage weight. It is assumed to be 60% of the remaining MTOW.
        return self.weight_structural + self.weight_structural

    @Attribute
    def weight_wings(self):
        #  The wing weight is found by multiplying its area with the weight to area factor.
        return self.structural_weight_per_area*self.S

    @Attribute
    def weight_ht(self):
        #  The HT weight is found by multiplying its area with the weight to area factor.
        return self.structural_weight_per_area*self.S_h

    @Attribute
    def weight_vt(self):
        #  The VT weight is found by multiplying its area with the weight to area factor.
        return self.structural_weight_per_area*self.S_v


if __name__ == '__main__':
    from parapy.gui import display

    obj = ClassTwo()
    display(obj)
