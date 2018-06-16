#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Useful package for checking working directory as well as the files inside this directory

# Required ParaPy Modules
from parapy.core import *

# Importing Necessary Classes
from wingpowerloading import WingPowerLoading
from weightestimator import *
from directories import *
from designinput import valid_payloads
from components import EOIR

__author__ = ["Şan Kılkış", "Nelson Johnson"]
__all__ = ["ParameterGenerator"]

#  TODO comments, documentation complete

# Function which returns all valid payloads in the directory /components/payload


class ParameterGenerator(Base):
    """ This class contains all the global design variables.

    :param performance_goal: The goal for which the UAV should be optimized (i.e. 'endurance or 'range')
    :type performance_goal: str
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'parameters.png')

    performance_goal = Input('endurance', validator=val.OneOf(['endurance', 'range']))
    goal_value = Input(1.0, validator=val.Positive())
    weight_target = Input('payload', validator=val.OneOf(['payload', 'mtow']))
    # target_value = Input(0.25, validator=val.Positive())
    target_value = Input(0.25)
    payload_type = Input('eoir', validator=val.OneOf(valid_payloads()))  #
    configuration = Input('conventional', validator=val.OneOf(['conventional', 'canard', 'flyingwing']))
    handlaunch = Input(True, validator=val.Instance(bool))
    portable = Input(True, validator=val.Instance(bool))

    @target_value.on_slot_change
    def payload_checker(self):
        if self.weight_target is 'payload':
            actual_weight = EOIR(target_weight=self.target_value).weight
            # setattr(self, 'target_value', actual_weight)
            # TODO Add custom dialog here
            print actual_weight

    # TODO add icons and labels for weight_estimator as well as wingpowerloading
    @Part
    def weightestimator(self):
        # Here we instantiate the class I weight estimation using the inputs.
        return ClassOne(weight_target=self.weight_target,
                        target_value=self.target_value if self.weight_target is 'payload' else self.target_value)

    @Part
    def wingpowerloading(self):
        # inputs = mtow, rang/endurance and value, pl target weight
        return WingPowerLoading(mtow=self.weight_mtow,
                                mission=self.performance_goal,
                                range=self.goal_value,
                                endurance=self.goal_value,
                                pl_target_weight=self.weight_payload,
                                handlaunch=self.handlaunch)


    # TODO make sure that the right payload mass is used for the weight estimation
#  Below are the attributes which are all the required vaiables for use in other scripts.
    @Attribute
    def weight_mtow(self):
        #  Here we obtain the MTOW of the UAV, from the Class I estimation in SI kilogram [kg]
        return self.weightestimator.weight_mtow

    @Attribute
    def weight_payload(self):
        #  Here we obtain the payload mass of the UAV, from the Class I estimation.
        return self.weightestimator.weight_payload

    @Attribute
    def wing_planform_area(self):
        #  Here we calculate the required wing loading from the mtow and design point.
        return self.weight_mtow/self.wing_loading

    @Attribute
    def aspect_ratio(self):
        #  Here we pull the UAV's aspect ratio from the design point.
        return self.wingpowerloading.designpoint['aspect_ratio']

    @Attribute
    def lift_coef_max(self):
        #  Here we pull the UAV's maximum lift coefficient from the design point.
        return self.wingpowerloading.designpoint['lift_coefficient']

    @Attribute
    def stall_speed(self):
        return self.wingpowerloading.stall_speed

    @Attribute
    def design_speed(self):
        return self.wingpowerloading.cruise_parameters['v_opt']

    @Attribute
    def power_loading(self):
        #  Here we pull the UAV's power loading from the design point.
        return self.wingpowerloading.designpoint['power_loading']

    @Attribute
    def wing_loading(self):
        #  Here we pull the UAV's wing loading from the design point.
        return self.wingpowerloading.designpoint['wing_loading']

    @Attribute
    def motor_power(self):
        return ((9.81 / self.power_loading) * self.weight_mtow) / self.wingpowerloading.eta_prop

    @Attribute
    def rho(self):
        return self.wingpowerloading.rho


if __name__ == '__main__':
    from parapy.gui import display

    obj = ParameterGenerator(label='test')
    display(obj)
