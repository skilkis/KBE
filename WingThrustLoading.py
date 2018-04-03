#This class will perform the Class I weight estimation for the fixed wing electric drone
#based on the input MTOW.
#There are assumed values for: C_lmax, Stall speed, propellor efficiency,
#zero-lift drag coefficient, Aspect Ratio and Oswald Efficiency Factor.
#Also, the climb rate and climb gradient must be assumed.
#All Values are in SI Units unless stated.


from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np


class WingPowerLoading(GeomBase):
                                #The inputs are Below:
    m_pl = Input(2.0)           #This is the value of payload mass from the users excel input file
    requested_MTOW = Input(60)  #Alternatively, the value of the user requested MTOW in the input file

    rho = 1.225                 #STD ISA sea level density
    rho_cr = 0.9091             #ISA 3km Density for climb rate power loading equation.
                                #Below are the assumed stall speeds for the Stall Speed Wing Loading Eq.
    V_s_hand = 8.0              #This is the assumed throwing speed of a hand launched UAV
    V_s_nonhand = 20.0          #This is the assumed launch speed at the end of a catapult or runway.

    C_Lmax = Input([1.0, 1.25, 1.5])  #These are 3 assumed values for C_Lmax






#  This first Block is an estmiation of MTOW if user supplies m_pl also, this estimates m_pl
#  if user supplies MTOW with same equation

    @Attribute
    def MTOW(self):
        MTOW = 4.7551*self.m_pl+0.59962
        #  Estimation of MTOW from payload mass from DSE Midterm Report.
        #  It is valid for UAVs with payload masses between 0 and 50 kg.
        return MTOW

    @Attribute
    def m_pl_derived(self):
        m_pl_derived = 0.2103*self.requested_MTOW-0.1261
        #  Estimation of m_pl from MTOW with reveresed Eq.
        return m_pl_derived


#  In this next block, the equations for the Wing Loading must be coded.
    @Attribute
    def ws_hand(self):
        ws_hand_1 = 0.5 * self.rho * self.C_Lmax[0] * self.V_s_hand ** 2
        ws_hand_2 = 0.5 * self.rho * self.C_Lmax[1] * self.V_s_hand ** 2
        ws_hand_3 = 0.5 * self.rho * self.C_Lmax[2] * self.V_s_hand ** 2
        #  Above are arrays of 3 required wing loadings with various cl max for a hand-launched stall speed.
        return [ws_hand_1,ws_hand_2,ws_hand_3]

    @Attribute
    def ws_nonhand(self):
        ws_nonhand_1 = 0.5 * self.rho * self.C_Lmax[0] * self.V_s_nonhand ** 2
        ws_nonhand_2 = 0.5 * self.rho * self.C_Lmax[1] * self.V_s_nonhand ** 2
        ws_nonhand_3 = 0.5 * self.rho * self.C_Lmax[2] * self.V_s_nonhand ** 2
        #  3 required wing loadings with various cl max for a non-hand-launched stall speed.
        return [ws_nonhand_1,ws_nonhand_2,ws_nonhand_3]




  #  @Attribute
  #  def plot_cl_alpha_curve(self):
  #      plt.plot(self.aoa, self.cl)
  #      plt.xlabel('alpha')
  #      plt.ylabel('Cl')
  #      plt.grid(b=True, which='both', color='0.65', linestyle='-')
  #      plt.title("Close it to refresh the ParaPy GUI")
  #      plt.show()
  #      return "Plot generated and closed"



if __name__ == '__main__':
    from parapy.gui import display

    obj = WingPowerLoading()
    display(obj)
