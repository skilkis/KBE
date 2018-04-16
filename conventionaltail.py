#  This script will generate a scissor plot to size the horizontal tail (HT).
#  The required inputs are: the center of gravity and aerodynamic center position of the current aircraft,
#  the tail arm to chord length ratio, the the HT aspect ratio, the tail to main wing speed ratio...


from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np
import matplotlib.pyplot as plt


class ConventionalTail(GeomBase):

    #  Sh/S inputs
    x_cg = Input(0.2)   #  NEED THIIS INPUT FROM CG SCRIPT FOR CURRENT AIRCRAFT!!!!!!!!!!!!!!!!!!!!!!!!!!
    x_ac = Input(0.1)   #  NEED THIS INPUT FROM LIFTING SURFACE SCRIPT! FOR COMPLETE WING OF CURRENT AIRCR!!!!!!!
    AR = Input(9.0)     #  NEED THIS INPUT FROM CLASS II FOR CURRENT AIRCRAFT!!!!!!!!1
    e = Input(0.8)      #  NEED THIS INPUT FROM CLASS I FOR CURRENT A/C!!!!!!!!!
    CD0 = Input(0.02)   #  NEED THIS FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#  FOR CONTROLABILITY CURVE, WE NEED TO FIND CL_A-H AT THE MINIMUM STALL SPEED-> MUST FIND CL_MAX FOR DIFFERENT WINGS!!!


    SM = Input(0.05)    #  This is the input Safety Margin
    AR_h = Input(5.0)   #  This is the assumed HT Aspect ratio.
    e_h = Input(0.8)    #  This is the assumed span Efficieny Factor of the Tail.
    lhc = Input(3.0)    #  This is the assumed tail arm to chord length ratio.

    VhV_conv = 0.85     #  This is the speed ratio for a conventional tail aircraft.
    Vhv_canard = 1.0    #  This is the speed ratio for a canard aircraft.


    a_0 = 2*pi          # This is the assumed airfoil lift slope.

    C_L_ah = Input(0.9) #  This is the maximum lift coeficcent of the wing (actually the wing and fuse, or A-h)
#  THIS IS WHAT MUST BE ESTIMATED WITH AVL????????? WE CAN CACLULATE EVERYTHING ELSE BY OTHER MEANS
    C_mac = Input(-0.1) #  THIS MUST BE ASCOCCIATED TO THE AIRFOILS!!!
    @Attribute
    def Cla_w(self):
        #  This estimates the lift slope of a low sweep, and speed 3D wing.
        Cla_w = self.a_0/(1+(self.a_0 / (pi * self.AR * self.e) ))
        return Cla_w

    @Attribute
    def Cla_h(self):
        #  This estimates the lift slope of a low sweep, and speed 3D HT.
        Cla_h = self.a_0/(1+(self.a_0 / (pi * self.AR_h * self.e_h) ))
        return Cla_h

    @Attribute
    def downwash_a(self):
        #  This estimates the wings change in down wash with angle of attack.
        deda = 4/(self.AR + 2)
        return deda

    @Attribute
    def cl_w(self):
        #  This is the cruise lift coefficient for maximum endurance.
        cl_w = sqrt(3*self.CD0*pi*self.AR*self.e)
        return cl_w

    def cl_h(self):
        #  This returns the maximum lift coefficent of the tail
        return -0.35*(self.AR_h**(1.0/3.0))

    @Attribute
    def xcg_range(self):
        values = np.linspace(0,10,100)
        return values


    @Attribute
    def shs_stability(self):
        #  This calculates the required Sh/S for stability
        shs_stab = []
        for i in range(0,len(self.xcg_range)):
            shs =  self.xcg_range[i]/((self.Cla_h/self.Cla_w)*(1-self.downwash_a)*(self.lhc)*((self.VhV_conv)**2)) - (self.x_ac -self.SM )/ ((self.Cla_h/self.Cla_w)*(1-self.downwash_a)*(self.lhc)*((self.VhV_conv)**2))
            shs_stab.append(shs)
        return shs_stab

    #  FOR CONTROLABILITY CURVE, WE NEED TO FIND CL_A-H AT THE MINIMUM STALL SPEED-> MUST FIND CL_MAX FOR DIFFERENT WINGS!!!


    @Attribute
    def shs_control(self):
        #  This calculates the required Sh/S for controllability.
        shs_c = []
        for i in range(0, len(self.xcg_range)):
            shs_cc = self.xcg_range[i]/((self.cl_h/self.C_L_ah)*(self.lhc)*((self.VhV_conv)**2)) + ((self.C_mac/self.C_L_ah) - self.x_ac) / ((self.cl_h/self.C_L_ah) *(self.lhc) * ((self.VhV_conv) ** 2))
            shs_c.append(shs_cc)
        return shs_c
#  above doesnt work





    @Attribute
    def scissorplot(self):
        plt.plot(self.xcg_range,self.shs_stability)
        plt.plot(self.xcg_range,self.shs_control)
        plt.ylabel('Sh/S')
        plt.xlabel('Xcg/c')
        plt.legend()
        plt.title('Scissor Plot')
        plt.show()
        return 'Plot Made, See ParaPy'






if __name__ == '__main__':
    from parapy.gui import display

    obj = ConventionalTail()
    display(obj)
