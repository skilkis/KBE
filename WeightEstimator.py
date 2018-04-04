#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *


class ClassOne(Base):
    """
    """

    weight_target = Input('payload')
    target_value = Input(0.25)

    @Attribute
    def mtow(self):
        if self.weight_target == 'payload':
            mtow = 4.7551 * self.target_value + 0.59962
            #  Estimation of MTOW from payload mass from DSE Midterm Report.
            #  It is valid for UAVs with payload masses between 0 and 50 kg.
            return mtow
        else:
            return self.target_value

    @Attribute
    def payload(self):
        if self.weight_target == 'mtow':
            m_pl_derived = 0.2103 * self.target_value -0.1261
            #  Estimation of m_pl from MTOW with reveresed Eq.
            return m_pl_derived
        else:
            return self.target_value

class ClassTwo(Base):

    PlaceHolder = Input(None)


if __name__ == '__main__':
    from parapy.gui import display

    obj = ClassOne()
    obj2 = ClassTwo()
    display(obj, obj2)
