#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Required Modules
from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from directories import *

__author__ = "Nelson Johnson"
__all__ = ["ScissorPlot"]


class ScissorPlot(Base):
    """  This script will generate a scissor plot to size the horizontal tail (HT). The required inputs are: the
    aerodynamic center position of the current aircraft, the tail arm, the HT aspect ratio, HT span efficiency,
    the tail to main wing speed ratio, the wing pitching moment about the aerodynamic center, the wing lift slope,
    the c_l for controllability (derived in wing), and the allowable shift in center of gravity.
    """

#  This block of code contains the inputs. ########---------------------------------------------------------------------
    #: Below is the current COG position
    #: :type: float
    x_cg = Input(0.3)

    #: Below is the current Aerodynamic Center position
    #: :type: float
    x_ac = Input(0.1)

    #: Below is the current leading edge of the MAC position
    #: :type: float
    x_lemac = Input(0.0)

    #: Below is the MAC length
    #: :type: float
    mac = Input(1.0)

    #: Below is the wing aspect ratio.
    #: :type: float
    AR = Input(12.0, validator=val.Positive())

    #: Below is the wing span efficiency factor
    #: :type: float
    e = Input(0.8, validator=val.Positive())

    #: Below is the assumed zero lift drag coefficient
    #: :type: float
    CD0 = Input(0.02, validator=val.Positive())

    #: Below is the k factor to correct the canard main wing C_Lalpha due to canard downwash.
    #: :type: float
    k_factor = Input(1.0, validator=val.Positive())

    #: Below is the assumed Safety Margin.
    #: :type: float
    SM = Input(0.05, validator=val.Positive())

    #: Below is the HT aspect ratio.
    #: :type: float
    AR_h = Input(5.0, validator=val.Positive())

    #: Below is the assumed HT span efficiency factor.
    #: :type: float
    e_h = Input(0.8, validator=val.Positive())

    #: Below is the speed ratio for a conventional tail aircraft.
    #: :type: float
    VhV_conv = sqrt(0.85)

    #: Below is the speed ratio for a canard aircraft.
    #: :type: float
    VhV_canard = 1.0

    #: Below is the lift slope for a thin airfoil.
    #: :type: float
    a_0 = 2*pi

    #: Below is the controllability lift coefficient of the wing at 1.2*V_s imported from wing.
    #: :type: float
    Cl_w = Input(0.5, validator=val.Positive())

    #: Below is the pitching moment about the aerodynamic center of the wing. This is calculated with AVL in 'wing.py'.
    #: :type: float
    C_mac = Input(-0.32)

    #: Below is the lift curve slope of the wing. This is calculated with AVL in 'wing.py'.
    #: :type: float
    Cla_w = Input(5.14, validator=val.Positive())

    #: Below is the assumed change in the cg location.
    #: :type: float
    delta_xcg = Input(0.3, validator=val.Positive())

    #: Below is a switch to determine the configuration.
    #: :type: str
    configuration = Input('conventional', validator=val.OneOf(['canard', 'conventional']))

    @Input
    def lhc(self):
        """ Derived input of the non-dimensionalized tail arm based on configuration choice

        :return: Non-dimensional tail arm
        :rtype: float
        """
        return -4.0 if self.configuration is 'canard' else 4.0

    @Attribute
    def x_cg_vs_mac(self):
        """ This attribute returns the non dimensional distance between the COG and the wing AC.
        :return: x_cg
        :rtype: float
        """
        return (self.x_cg - self.x_ac) / self.mac

    @Attribute
    def cla_h(self):
        """ This attribute estimates the lift slope of a low sweep, low speed 3D HT.
        :return: HT lift curve slope
        :rtype: float
        """
        cla_h = self.a_0/(1+(self.a_0 / (pi * self.AR_h * self.e_h)))
        return cla_h

    @Attribute
    def downwash_a(self):
        """ This attribute estimates the wings change in downwash with angle of attack.
        :return: Downwash gradient
        :rtype: float
        """
        deda = 4/(self.AR + 2)
        return deda

    @Attribute
    def cl_h(self):
        """ This attribute returns the lift coefficient of the tail for the controllability case. The
        canard is assumed to be all moving.
        :return: HT lift coefficient
        :rtype: float
        """
        if self.configuration is 'conventional':
            cl_h = -0.35*(self.AR_h**(1.0/3.0))
        else:
            cl_h = 1
            # = 0.35 * (self.AR_h ** (1.0 / 3.0))
            #  Canard assumed to be full moving with Cl max = 1 in slow speed case.
            #  This assumption allows the scissor plot lines to intersect and create a design space.
        return cl_h

    @Attribute
    def cla_w_canard(self):
        """ This attribute reduces the wing lift slope for the canard case. It is reducing the C_lalpha from AVL.
        :return: Canard wing lift slope
        :rtype: float
        """
        return self.Cla_w*(1 - ((2 * self.cla_h * self.shs_sm) / (pi * self.AR * self.k_factor)))

    @Attribute
    def xcg_range(self):
        """ This attribute is a dummy list of x_cg used for plotting Sh/S.
        :return: List of values of X_cg
        :rtype: list
        """
        values = np.linspace(-5, 5, 100)
        return values

    @Attribute
    def shs_stability(self):
        """ This attribute calculates the required Sh/S for the stability requirement.
        :return: Required Sh/S for stability
        :rtype: list
        """
        shs_stab = []
        for i in range(0, len(self.xcg_range)):
            if self.configuration is 'conventional':
                shs_conv = (self.xcg_range[i] / ((self.cla_h / self.Cla_w) * (1 - self.downwash_a) * self.lhc *
                                                 (self.VhV_conv ** 2))) - \
                           ((self.x_ac - self.SM) / ((self.cla_h / self.Cla_w) * (1 - self.downwash_a) * self.lhc *
                                                     (self.VhV_conv ** 2)))
                shs_stab.append(shs_conv)
            else:
                shs_canard = (self.xcg_range[i] / ((self.cla_h / self.cla_w_canard) * self.lhc *
                                                   self.VhV_canard ** 2)) - \
                             ((self.x_ac - self.SM) / ((self.cla_h / self.cla_w_canard) * self.lhc *
                                                       (self.VhV_canard ** 2)))
                shs_stab.append(shs_canard)

        return shs_stab

    @Attribute
    def shs_control(self):
        """ This attribute calculates the required Sh/S for the controllability requirement
        :return: Required Sh/S for controllability.
        :rtype: list
        """
        shs_c = []
        for i in range(0, len(self.xcg_range)):
            if self.configuration is 'conventional':
                shs_conv = (self.xcg_range[i] / ((self.cl_h / self.Cl_w) * self.lhc * self.VhV_conv ** 2)) + \
                           (((self.C_mac/self.Cl_w) - self.x_ac) / ((self.cl_h / self.Cl_w) * self.lhc *
                                                                    (self.VhV_conv ** 2)))
                shs_c.append(shs_conv)
            else:
                shs_canard = (self.xcg_range[i] / ((self.cl_h / self.Cl_w) * self.lhc * self.VhV_canard ** 2))\
                             + (((self.C_mac / self.Cl_w) - self.x_ac) / ((self.cl_h / self.Cl_w) * self.lhc *
                                                                          (self.VhV_canard ** 2)))
                shs_c.append(shs_canard)

        return shs_c

    @Attribute
    def shs_sm(self):
        #  TODO add error if there's a negative Sh/S output. Solution is to increase Cl_h or tail arm or reduce Cl_w
        """ This attribute will calculate the required Sh/S based on the required cg shift.
        :return: Required Sh/S.
        :rtype: float
        """
        if self.configuration is 'conventional':
            shs_req_sm = (self.delta_xcg + self.SM - (self.C_mac / self.Cl_w)) / \
                      ((((self.cla_h / self.Cla_w) * (1 - self.downwash_a)) - (self.cl_h / self.Cl_w)) *
                       (self.VhV_conv ** 2) * self.lhc)
        else:
            shs_req_sm = (self.delta_xcg + self.SM - (self.C_mac / self.Cl_w)) / \
                      (((self.cla_h / self.Cla_w) - (self.cl_h / self.Cl_w)) * (self.VhV_canard ** 2) *
                       self.lhc)

        return shs_req_sm

    @Attribute
    def shs_req(self):

        shs_req = self.shs_sm
        xcg_vs_shs_control = interp1d(self.shs_control, self.xcg_range, kind='linear', fill_value='extrapolate')
        xcg_vs_shs_stability = interp1d(self.shs_stability, self.xcg_range, kind='linear', fill_value='extrapolate')

        shs_range = np.linspace(0, max(self.shs_control), 100)
        stability_criteria = []
        for i in shs_range:
            if self.xcg_range[0] <= self.x_cg_vs_mac <= self.xcg_range[-1]:
                _stab_pnt = float(xcg_vs_shs_stability(i))
                _cont_pnt = float(xcg_vs_shs_control(i))
                if _cont_pnt <= self.x_cg_vs_mac <= _stab_pnt:
                    _current_margin = _stab_pnt - _cont_pnt
                    midpoint = _current_margin / 2.0 + _cont_pnt
                    error = abs(self.x_cg_vs_mac - midpoint)
                    stability_criteria.append([i, _cont_pnt, _stab_pnt, _current_margin, error])

        if len(stability_criteria) != 0:
            stability_criteria = sorted(stability_criteria, key=lambda x: x[3])
            shs_cg = stability_criteria[0][0]
            if shs_cg >= self.shs_sm:
                shs_req = shs_cg
        else:
            print Warning('The current aircraft design is not stable w/ reference tail arm ratios')

        return shs_req
        # shs_control = float(shs_control_vs_xcg(self.x_cg_vs_mac + 0.05))  # Adding a SF to allow forward shift
        # neutral_point = float(xcg_vs_shs_stability(shs_control))
        # stability_margin = neutral_point - self.x_cg_vs_mac
        # if stability_margin > 0:
        #     stable = True
        # else:
        #     raise Warning('The current design is unstable')
        # return stability_margin, shs_control
        # #

    @Attribute
    def plot_scissordiagram(self):
        """ This attribute will plot the scissor plot.
        :return: Scissor Plot.
        :rtype: Plot
        """
        fig = plt.figure('ScissorPlot')
        plt.style.use('ggplot')
        plt.title('Scissor Plot')
        plt.plot(self.xcg_range, self.shs_stability, 'b', label='Stability')
        plt.plot(self.xcg_range, self.shs_control, 'g', label='Controllablility')
        plt.axhline(y=self.shs_req, color='r', linestyle='-.', label='Required Sh/S')
        # plt.axhline(y=self.test[1])
        plt.scatter(x=self.x_cg_vs_mac, y=self.shs_req, label='CG Location')
        plt.ylabel(r'$\frac{S_{h}}{S}$')
        plt.xlabel(r'$\frac{X_{cg}-X_{ac}}{c}$')
        plt.axis([-2, 2, 0, 2])
        plt.legend(loc=0)
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        plt.show()
        return 'Plot Made, See PyCharm'


if __name__ == '__main__':
    from parapy.gui import display

    obj = ScissorPlot()
    display(obj)
