#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.core import *

# Other Modules
from directories import *

__all__ = ["ClassOne", "ClassTwo"]

# Input Validation Functions:


# def check_string(string):
#     """Perform ``Build()`` and check if ``builder`` is done building without
#     errors. Return ``builder`` if no errors occurred.
#
#     :type builder: OCC.BRepBuilderAPI.BRepBuilderAPI_MakeShape
#     :rtype: OCC.BRepBuilderAPI.BRepBuilderAPI_MakeShape
#     :raises Exception: if something went wrong during the construction using
#         ``builder``.
#     """
#     if string is not 'payload' or 'mtow':
#         raise Exception("Please enter a valid string")
#     else:
#         return string

# class Positive(ValidateBase):
#     """A validation class that checks if the supplied ``value`` is positive, i.e. :math:`value > 0`.
#     Note the zero is not included in the range."""
#
#     __slots__ = ["fn", "msg"]
#
#     def __init__(self, incl_zero=False, **kwargs):
#         super(Positive, self).__init__(**kwargs)
#         if incl_zero:
#             self.fn = lambda value: is_number(value) and value >= 0
#             self.msg = "<value >= 0>"
#         else:
#             self.fn = lambda value: is_number(value) and value > 0
#             self.msg = "<value > 0>"
#
#     def call(self, value, obj, slot):
#         return self.fn(value)
#
#     def __repr__(self):
#         return self.msg


class ClassOne(Base):
    """A simple Class-I weight estimation with values :attr:`mtow`, :attr:`payload`. This class allows for two
    use-cases answers either the question how heavy will the UAV need to be to carry a certain payload or how much
    payload can a UAV with a certain maximum take-off weight carry? This is accomplished by specifying with
    :type:`string` input what the target weight, or in other words, the known weight parameter, into the field
    :attr:`weight_target`. The field :attr:`target_value` is then the corresponding value for this target weight
    which needs to be a :type:`float` in kilograms.

    :param weight_target: A Test

        Usage:

        >>> from design import ClassOne
        >>> weight = ClassOne('payload',0.25)  # keywords: ClassOne (weight_target='payload', target_value=0.25)
        >>> weight.payload
        0.25
        >>> weight.mtow
        1.788395

        Alternative Usage:

        >>> from design import ClassOne
        >>> weight = ClassOne ('mtow',1.788395) # keywords: ClassOne (weight_target='mtow', target_value=1.788395)
        >>> weight.mtow
        1.788395
        >>> weight.payload
        0.2499994685
    """

    __initargs__ = ["weight_target", "target_value"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'weight.png')

    # TODO Figure out validator functions here to check string
    weight_target = Input('payload')
    target_value = Input(0.25)

    @Attribute
    def mtow(self):
        if self.weight_target == 'payload':
            mtow = 4.7551 * self.target_value + 0.59962
            #  Estimation of MTOW from payload mass from DSE Midterm Report.
            #  It is valid for UAVs with payload masses between 0 and 50 kg.
            return mtow
        elif self.weight_target == 'mtow':
            return self.target_value
        else:
            return self.errormsg

    @Attribute
    def payload(self):
        if self.weight_target == 'mtow':
            m_pl_derived = 0.2103 * self.target_value - 0.1261
            #  Estimation of m_pl from MTOW with reveresed Eq.
            return m_pl_derived
        elif self.weight_target == 'payload':
            return self.target_value
        else:
            return self.errormsg

    @Attribute(private=True)  # An error message for when an incorrect value of weight_target is entered
    def errormsg(self):
        error_str = "%s is not a valid weight_target. Valid inputs: 'payload', 'mtow'" % self.weight_target
        raise NameError(error_str)


class ClassTwo(Base):

    PlaceHolder = Input(None)


if __name__ == '__main__':
    from parapy.gui import display

    obj = ClassOne()
    display(obj)
