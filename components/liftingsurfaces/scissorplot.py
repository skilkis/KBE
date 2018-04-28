#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Required Modules
from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np
import matplotlib.pyplot as plt
from directories import *

__author__ = "Nelson Johnson"
__all__ = ["ScissorPlot"]


class ScissorPlot(GeomBase):
    """  This script will generate a scissor plot to size the horizontal tail (HT). The required inputs are: the
    aerodynamic center position of the current aircraft, the tail arm, the the HT aspect ratio, HT span efficiency,
    the tail to main wing speed ratio, the wing pitching moment abo the aerodynamic center, thw wing lift slope,
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

    #: Below is the tail arm for a conventional tail aircraft.
    #: :type: float
    lhc = Input(3.0)

    #: Below is the tail arm for a canard aircraft.
    #: :type: float
    lhc_canard = Input(-3.0)

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
    configuration = Input('canard', validator=val.OneOf(['canard', 'conventional']))

    @Attribute
    def x_cg_vs_mac(self):
        #  This returns the non dimensional distance between the COG and the wing AC.
        print self.x_cg - self.x_ac / self.mac
        return (self.x_cg - self.x_ac) / self.mac

    @Attribute
    def cla_h(self):
        #  This estimates the lift slope of a low sweep, low speed 3D HT.
        cla_h = self.a_0/(1+(self.a_0 / (pi * self.AR_h * self.e_h)))
        return cla_h

    @Attribute
    def downwash_a(self):
        #  This estimates the wings change in down wash with angle of attack.
        deda = 4/(self.AR + 2)
        return deda

    @Attribute
    def cl_h(self):
        #  This returns the maximum lift coefficient of the tail for the controllability case.
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
        #  This reduces the wing lift slope for the canard case. It is reducing the C_lalpha from AVL.
        return self.Cla_w*(1 - ((2 * self.cla_h * self.shs_req) / (pi * self.AR * self.k_factor)))

    @Attribute
    def xcg_range(self):
        #  This is a dummy list of x_cg used for plotting Sh/S.
        values = np.linspace(-5, 5, 20)
        return values

    @Attribute
    def shs_stability(self):
        #  This calculates the required Sh/S for the stability requirement.
        shs_stab = []
        for i in range(0, len(self.xcg_range)):
            if self.configuration is 'conventional':
                shs_conv = (self.xcg_range[i] / ((self.cla_h / self.Cla_w) * (1 - self.downwash_a) * self.lhc *
                                                 (self.VhV_conv ** 2))) - \
                           ((self.x_ac - self.SM) / ((self.cla_h / self.Cla_w) * (1 - self.downwash_a) * self.lhc *
                                                     (self.VhV_conv ** 2)))
                shs_stab.append(shs_conv)
            else:
                shs_canard = (self.xcg_range[i] / ((self.cla_h / self.cla_w_canard) * self.lhc_canard *
                                                   self.VhV_canard ** 2)) - \
                             ((self.x_ac - self.SM) / ((self.cla_h / self.cla_w_canard) * self.lhc_canard *
                                                       (self.VhV_canard ** 2)))
                shs_stab.append(shs_canard)

        return shs_stab

    @Attribute
    def shs_control(self):
        #  This calculates the required Sh/S for the controllability requirement.
        shs_c = []
        for i in range(0, len(self.xcg_range)):
            if self.configuration is 'conventional':
                shs_conv = (self.xcg_range[i] / ((self.cl_h / self.Cl_w) * self.lhc * self.VhV_conv ** 2)) + \
                           (((self.C_mac/self.Cl_w) - self.x_ac) / ((self.cl_h / self.Cl_w) * self.lhc *
                                                                    (self.VhV_conv ** 2)))
                shs_c.append(shs_conv)
            else:
                shs_canard = (self.xcg_range[i] / ((self.cl_h / self.Cl_w) * self.lhc_canard * self.VhV_canard ** 2))\
                             + (((self.C_mac / self.Cl_w) - self.x_ac) / ((self.cl_h / self.Cl_w) * self.lhc_canard *
                                                                          (self.VhV_canard ** 2)))
                shs_c.append(shs_canard)

        return shs_c

    @Attribute
    def shs_req(self):
        #  This attribute will calculate the required Sh/S based on the required cg shift.
        #  TODO add error if there's a negative Sh/S output. Solution is to increase Cl_h or tail arm or reduce Cl_w
        if self.configuration is 'conventional':
            shs_req = (self.delta_xcg + self.SM - (self.C_mac / self.Cl_w)) / \
                      ((((self.cla_h / self.Cla_w) * (1 - self.downwash_a)) - (self.cl_h / self.Cl_w)) *
                       (self.VhV_conv ** 2) * self.lhc)
        else:
            shs_req = (self.delta_xcg + self.SM - (self.C_mac / self.Cl_w)) / \
                      (((self.cla_h / self.Cla_w) - (self.cl_h / self.Cl_w)) * (self.VhV_canard ** 2) *
                       self.lhc_canard)
        # print 'Required Sh/S = ', shs_req
        return shs_req

    @Attribute
    def scissorplot(self):
        fig = plt.figure('ScissorPlot')
        plt.style.use('ggplot')
        plt.title('Scissor Plot')
        plt.plot(self.xcg_range, self.shs_stability, 'b', label='Stability')
        plt.plot(self.xcg_range, self.shs_control, 'g', label='Controllablility')
        plt.axhline(y=self.shs_req, color='r', linestyle='-.', label='Required Sh/S')
        plt.scatter(x=self.x_cg_vs_mac, y=1, label='CG Location')
#        plt.axvline(x=self.x_ac-self.SM, color='r', linestyle='-.')
        plt.ylabel(r'$\frac{S_{h}}{S}$')
        plt.xlabel(r'$\frac{Xcg-Xac}{c}$')
        plt.axis([-2, 2, 0, 2])
        plt.legend(loc=0)
#        plt.ion()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        plt.show()
        return 'Plot Made, See PyCharm'


if __name__ == '__main__':
    from parapy.gui import display

    obj = ScissorPlot()
    display(obj)
