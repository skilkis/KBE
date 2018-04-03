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
    m_pl = Input(2.0)   #This is the value of payload mass from the users excel input file
    requested_MTOW = Input(60) #This is the value of the user requested MTOW in the input file

    C_Lmax = Input(np.linspace(1,1.5,3)) #These are 3 assumed values for C_Lmax
    rho = 1.225 #Sea Level Density

    V_s_hand = 8.0 #This is the assumed throwing speed of a hand launched UAV
    V_s_nonhand = 20.0 #This is the assumed launch speed at the end of a catapult or runway.




## This first Block is an estmiation of MTOW if user supplies m_pl
# or estimates m_pl if user supplies MTOW with same equation
    @Attribute
    def MTOW(self):
        MTOW = 4.7551*self.m_pl+0.59962 #Estmiation of MTOW from Payload mass from DSE Midterm Report
        #Above is valid for electric UAVs with payload masses between 0 and 60 kg.
        return MTOW

    @Attribute
    def m_pl_derived(self):
        m_pl_derived = 0.2103*self.requested_MTOW-0.1261 #Estmiation of m_pl from MTOW from DSE Midterm Report
        return m_pl_derived




## In this next block, the equations for the Wing and Thrust Loading must be cooded.
    @Attribute
    def WsStall_hand(self):
        WsStall_hand = 0.5 * self.rho * self.C_Lmax * self.V_s_hand ** 2
        #This Equation calculates the requires wing loading for a hand-launched stall speed.
        return WsStall_hand

    @Attribute
    def WsStall_nonhand(self):
        WsStall_nonhand = 0.5 * self.rho * self.C_Lmax * self.V_s_nonhand ** 2
        # This Equation calculates the requires wing loading for a non-hand-launched stall speed.
        return WsStall_nonhand








if __name__ == '__main__':
    from parapy.gui import display

    obj = WingPowerLoading()
    display(obj)
