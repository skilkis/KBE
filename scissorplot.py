#  This script will generate a scissor plot to size the horizontal tail (HT).
#  The required inputs are: the center of gravity and aerodynamic center position of the current aircraft,
#  the tail arm to chord length ratio, the the HT aspect ratio, the tail to main wing speed ratio...


from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np
import matplotlib.pyplot as plt


class ScissorPlot(GeomBase):

    #  Sh/S inputs
    x_cg = Input(0.0)   #  NEED THIIS INPUT FROM CG SCRIPT FOR CURRENT AIRCRAFT!!!!!!!!!!!!!!!!!!!!!!!!!!
    x_ac = Input(0.1)   #  NEED THIS INPUT FROM LIFTING SURFACE SCRIPT! FOR COMPLETE WING OF CURRENT AIRCR!!!!!!!

    AR = Input(12.0)     #  NEED THIS INPUT FROM CLASS II FOR CURRENT AIRCRAFT!!!!!!!!1
    e = Input(0.8)      #  NEED THIS INPUT FROM CLASS I FOR CURRENT A/C!!!!!!!!!
    CD0 = Input(0.02)   #  NEED THIS FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    k_factor = Input(1) #  This is the k factor to correct the canard main wing C_Lalpha due to canard downwash.
    SM = Input(0.05)    #  This is the input Safety Margin
    AR_h = Input(5.0)   #  This is the assumed HT Aspect ratio.
    e_h = Input(0.8)    #  This is the assumed span Efficieny Factor of the Tail.
    lhc = Input(3.0)    #  This is the assumed tail arm to chord length ratio.
    lhc_canard = Input(-3.0)
    VhV_conv = 0.85     #  This is the speed ratio for a conventional tail aircraft.
    VhV_canard = 1.0    #  This is the speed ratio for a canard aircraft.


    #  a_0 = 2*pi          # This is the assumed (thin) airfoil lift slope.



    Cl_w = Input(0.5)       #  This is the maximum lift coeficcent of the wing at 1.2*V_s IMPORT FROM WING.
                            #  There is a correction for the main wing if canard is chosen.
    C_mac = Input(-0.32)    #  This is the C_m of the wing from AVL IMPORT FROM WING
    Cla_w = Input(5.14)      #  This is the lift curve slope of the wing from AVL. IMPORT FROM WING
    delta_xcg = Input(0.3)  #  This is the change in the cg location due to dropping a payload. IMPORT FROM CG EST
    Cla_h = Input(4.9)      # This is the lift curve slope of the tail. IMPORT FROM TAIL WING INSTANTIATION
#  TODO In main code, get cla_h from AVL using wing primitive.
    configuration = Input('Conventional', validator=val.OneOf(['Canard', 'Conventional']))

   # @Attribute
   # def Cla_w(self):
   # #  This was the old method to estimate lift curve slope.
   #     #  This estimates the lift slope of a low sweep, and speed 3D wing. THIS IS FOUND WITH AVL IN WING!!!!!!!!!
   #     Cla_w = self.a_0/(1+(self.a_0 / (pi * self.AR * self.e) ))
   #     return Cla_w

   # @Attribute
   # def Cla_h(self):
   #     #  This estimates the lift slope of a low sweep, and speed 3D HT.
   #     Cla_h = self.a_0/(1+(self.a_0 / (pi * self.AR_h * self.e_h) ))
   #     return Cla_h

   # @Attribute
   # def x_np(self):
   #     return x_cg+

    @Attribute
    def downwash_a(self):
        #  This estimates the wings change in down wash with angle of attack.
        deda = 4/(self.AR + 2)
        return deda

    @Attribute
    def Cl_h(self):
        #  This returns the maximum lift coefficient of the tail
        if self.configuration is 'Conventional':
            Cl_h = -0.35*(self.AR_h**(1.0/3.0))
        else:
            Cl_h = 1
            # = 0.35 * (self.AR_h ** (1.0 / 3.0))
            #  Canard assumed to be full moving with Cl max = 1 in slow speed case.
            #  This assumption allows the scissor plot to return the correct value.
        return Cl_h

    @Attribute
    def Cla_w_canard(self):
        return self.Cla_w*(1-((2*self.Cla_h*self.shs_req)/(pi*self.AR*self.k_factor)))

    @Attribute
    def xcg_range(self):
        #  This is a dummy list for plotting Sh/S.
        values = np.linspace(-5,5,20)
        return values

    @Attribute
    def shs_stability(self):
        #  This calculates the required Sh/S for stability requirement.
        shs_stab = []
        for i in range(0,len(self.xcg_range)):
            if self.configuration is 'Conventional':
                shs_conv =  (self.xcg_range[i]/((self.Cla_h/self.Cla_w)*(1-self.downwash_a)*(self.lhc)*((self.VhV_conv)**2))) - ((self.x_ac -self.SM )/ ((self.Cla_h/self.Cla_w)*(1-self.downwash_a)*(self.lhc)*((self.VhV_conv)**2)))
                shs_stab.append(shs_conv)
            else:
                shs_canard = (self.xcg_range[i] / ((self.Cla_h / self.Cla_w_canard) * (self.lhc_canard) * ((self.VhV_canard) ** 2))) - ((self.x_ac - self.SM) / ((self.Cla_h / self.Cla_w_canard) * (self.lhc_canard) * ((self.VhV_canard) ** 2)))
                shs_stab.append(shs_canard)
        return shs_stab

    @Attribute
    def shs_control(self):
        #  This calculates the required Sh/S for controllability.
        shs_c = []
        for i in range(0, len(self.xcg_range)):
            if self.configuration is 'Conventional':
                shs_conv = (self.xcg_range[i]/((self.Cl_h/self.Cl_w)*(self.lhc)*((self.VhV_conv)**2))) + (((self.C_mac/self.Cl_w) - self.x_ac) / ((self.Cl_h/self.Cl_w) *(self.lhc) * ((self.VhV_conv) ** 2)))
                shs_c.append(shs_conv)
            else:
                shs_canard = (self.xcg_range[i] / ((self.Cl_h / self.Cl_w) * (self.lhc_canard) * ((self.VhV_canard) ** 2))) + (((self.C_mac / self.Cl_w) - self.x_ac) / ((self.Cl_h / self.Cl_w) * (self.lhc_canard) * ((self.VhV_canard) ** 2)))
                shs_c.append(shs_canard)


        return shs_c
#  TODO add error if there's a negative Sh/S output. Solution is to increase Cl_h or tail arm or reduce Cl_w

    @Attribute
    def shs_req(self):
        #  This attribute will calculate the required Sh/S based on the change in the cg due to flying with/without payload.
        if self.configuration is 'Conventional':
            shs_req = (self.delta_xcg + self.SM - (self.C_mac / self.Cl_w)) / ((((self.Cla_h/self.Cla_w)*(1-self.downwash_a))-(self.Cl_h/self.Cl_w))*(self.VhV_conv**2)*self.lhc)
        else:
            shs_req = (self.delta_xcg + self.SM - (self.C_mac / self.Cl_w)) / ((((self.Cla_h / self.Cla_w)) - (self.Cl_h / self.Cl_w)) * (self.VhV_canard ** 2) * self.lhc_canard)
        print 'Required Sh/S = ', shs_req
        return shs_req


    @Attribute
    def scissorplot(self):
        plt.plot(self.xcg_range,self.shs_stability,'b',label='Stability')
        plt.plot(self.xcg_range,self.shs_control, 'g',label='Controllablility')
        plt.axhline(y=self.shs_req, color='r', linestyle='-.',label='Required Sh/S')
        #plt.axvline(x=self.x_ac-self.SM, color='r', linestyle='-.')
        plt.ylabel('Sh/S')
        plt.xlabel('Xcg/c')
        plt.legend(loc = 0)
        plt.title('Scissor Plot')
        axes = plt.gca()
        axes.set_ylim([-max(self.shs_stability), max(self.shs_stability)])
        axes.set_xlim([min(self.xcg_range), max(self.xcg_range)])
        plt.show()
        return 'Plot Made, See ParaPy'



if __name__ == '__main__':
    from parapy.gui import display

    obj = ScissorPlot()
    display(obj)
