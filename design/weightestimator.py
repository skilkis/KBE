#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.core import *

# Other Modules
from directories import *

__all__ = ["ClassOne", "ClassTwo"]


class ClassOne(Base):
    """A simple Class-I weight estimation with values :attr:`mtow`, :attr:`payload`. This class allows for two
    use-cases. These use cases answer either one of two customer questions: how heavy will the UAV need to be to
    carry a certain payload or how much payload can a UAV with a certain maximum take-off weight carry?
    This is accomplished by specifying with :type:`string` input what the target weight, or in other words, the known
    weight parameter, into the field :attr:`weight_target`. The field :attr:`target_value` is then the corresponding
    value for this target weight which needs to be a :type:`float` in kilograms.

    :param weight_target: Defines if the input `target_value` is a payload weight or maximum take-off weight
    :type weight_target: str
    :param target_value: The weight value assigned to the respective type in `weight_target`
    :type target_value: float

    :returns: Weight values for maximum take-off weight ('weight_mtow') and payload weight ('weight_payload')
    :rtype: float

    |
    |   Usage:
    >>> from design import ClassOne
    >>> weight = ClassOne('payload',0.25)  # keywords: ClassOne (weight_target='payload', target_value=0.25)
    >>> weight.weight_payload
    0.25
    >>> weight.weight_mtow
    1.788395

    |
    |   Alternative Usage:
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
            #  Estimation of m_pl from MTOW with reveresed Eq.
            return m_pl_derived
        elif self.weight_target == 'payload':
            return self.target_value


class ClassTwo(Base):
    """A simple Class-II component weight estimation with values :attr:`mtow`,.....
    The propusion, battery, avionics masses and payload masses already calculated, the remaining wieght from MTOW
    is split between the wings and the fuselage.
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'piechart.png')

    weight_mtow = Input(2.0)
    weight_payload = Input(0.1)        #  This is the payload mass.
    weight_prop = Input(0.1)           #  This is the propulsion system (engine) mass.
    weight_batt = Input(0.2)           #  This is the battery mass.
    weight_avionics = Input(0.1)       #  This is the assumed avionics mass.


    S_h = Input(0.1)
    S = Input(0.4)
    S_v = Input(0.1)

    @Attribute
    def weight_structural(self):
        #  This returns the remainder of the MTOW after the engine, battery and payload masses subtracted.
        #  This is assumed to be evenly split between the fuselage and wing weights.
        return self.weight_mtow - self.weight_prop - self.weight_batt - self.weight_payload - self.weight_avionics

    @Attribute
    def weight_lifting_surfaces(self):
        #  This is the assumed weight of all wings. It is assumed to be 60% of the remaining MTOW.
        return 0.7*self.weight_structural

    @Attribute
    def fuse_weight(self):
        #  This is the assumed fuselage weight. It is assumed to be 60% of the remaining MTOW.
        return 0.3*self.weight_structural

    @Attribute
    def wings_weight_per_area(self):
        #  This gives a factor to split the wings weight over the HT, VT and wing based on their area.
        return self.weight_lifting_surfaces/(self.S+self.S_h+self.S_v)

    @Attribute
    def weight_wings(self):
        #  The wing weight is assumed to be half of the total wings weight.
        return self.wings_weight_per_area*self.S

    @Attribute
    def weight_ht(self):
        return self.wings_weight_per_area*self.S_h

    @Attribute
    def weight_vt(self):
        return self.wings_weight_per_area*self.S_v


if __name__ == '__main__':
    from parapy.gui import display

    obj = ClassTwo()
    display(obj)