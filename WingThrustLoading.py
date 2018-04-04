#This class will perform the Class I weight estimation for the fixed wing electric drone
#based on the input MTOW.
#There are assumed values for: C_lmax, Stall speed, propellor efficiency,
#zero-lift drag coefficient, Aspect Ratio and Oswald Efficiency Factor.
#Also, the climb rate and climb gradient must be assumed.
#All Values are in SI Units unless stated.


from parapy.core import *
from parapy.geom import *
from math import *
import matplotlib.pyplot as plt
from Aircraft import Aircraft

class WingPowerLoading(GeomBase):
                                #  The inputs are Below:
    m_pl = Input(2.0)           #  This is the value of payload mass from the users excel input file
    requested_MTOW = Input(60)  #  Alternatively, the value of the user requested MTOW in the input file

    C_Lmax = Input([1.0, 1.25, 1.5])  # These are 3 assumed values for C_Lmax
    AR = Input([6, 9, 12])  # These are the 3 assumed Aspect Ratios

    n_p = Input(0.7)  # Assumption for the propellor efficiency.
    e_factor = Input(0.8)  # Assumed Oswald Efficiency Factor.


    rho = 1.225                 #  STD ISA sea level density
    rho_cr = 0.9091             #  ISA 3km Density for climb rate power loading equation.
                                #  Below are the assumed stall speeds for the Stall Speed Wing Loading Eq.
    V_s_hand = 8.0              #  This is the assumed throwing speed of a hand launched UAV
    V_s_nonhand = 20.0          #  This is the assumed launch speed at the end of a catapult or runway.

    C_D0 = 0.02                 #  Assumed Value of Zero-Lift Drag Coefficient.
    RC = 1.524                  #  Assumption for Required Climb Rate, Same as Sparta UAV 1.1.2.
    G = 0.507                   #  Assumed Climb Gradient to clear 10m object 17m away.


    WS_range = [float(i) for i in range(1, 401)]
    #  Above is a dummy list of wing loadings for iterating in the Power Loading Equations.





#  This first Block is an estmiation of MTOW if user supplies m_pl also, this estimates m_pl
#  if user supplies MTOW with the same equation.
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


#  In this next block, the equations for the required Wing Loading must be coded.
    @Attribute
    def ws_hand(self):
        #  Below are 3 required wing loadings with various cl max for a hand-launched stall speed.
        ws_hand_1 = 0.5 * self.rho * self.C_Lmax[0] * self.V_s_hand ** 2
        ws_hand_2 = 0.5 * self.rho * self.C_Lmax[1] * self.V_s_hand ** 2
        ws_hand_3 = 0.5 * self.rho * self.C_Lmax[2] * self.V_s_hand ** 2
        return [ws_hand_1,ws_hand_2,ws_hand_3]

    @Attribute
    def ws_nonhand(self):
        #  Below are 3 required wing loadings with various cl max for a non-hand-launched stall speed.
        ws_nonhand_1 = 0.5 * self.rho * self.C_Lmax[0] * self.V_s_nonhand ** 2
        ws_nonhand_2 = 0.5 * self.rho * self.C_Lmax[1] * self.V_s_nonhand ** 2
        ws_nonhand_3 = 0.5 * self.rho * self.C_Lmax[2] * self.V_s_nonhand ** 2
        return [ws_nonhand_1,ws_nonhand_2,ws_nonhand_3]






#  In the following block, the equations for the required power loading are coded.

    @Attribute
    def climblift(self):
        C_Lcg = [self.C_Lmax[0] - 0.2, self.C_Lmax[1] - 0.2, self.C_Lmax[2] - 0.2]
        #  Above we subtract 0.2 from climb gradient C_l to keep away from stall during climb out
        return C_Lcg

    @Attribute
    def climbdrag(self):    #  For loop to generate C_D for Climb Gradient Equation.
        C_Dcg = []
        for i in range(0, len(self.climblift)):
            C_Dcg1 = self.C_D0 + self.climblift[i] ** 2 / (pi * self.AR[i] * self.e_factor)
            C_Dcg.append(C_Dcg1)
        C_Dcg = [C_Dcg[0], C_Dcg[1], C_Dcg[2]]
        return C_Dcg



    @Attribute
    def WP_rate(self):
        ## Calculate Required Power for Climb Rate Requirement at 3000 m for various AR.
        WpCr_1 = []  # Empty List for appending W/P Data for AR[0]
        for i in range(0, len(self.WS_range)):
            WpCri_1 = self.n_p / (self.RC + sqrt(self.WS_range[i] * (2.0 / self.rho_cr) * (sqrt(self.C_D0) / (1.81 * ((self.AR[0] * e) ** (3.0 / 2.0))))))
            WpCr_1.append(WpCri_1)  # Above is calculation of W/P for Rate of Climb at 3km alt.
        WpCr_2 = []  # Empty List for appending W/P Data for AR[1].
        for i in range(0, len(self.WS_range)):
            WpCri_2 = self.n_p / (self.RC + sqrt(self.WS_range[i] * (2.0 / self.rho_cr) * (sqrt(self.C_D0) / (1.81 * ((self.AR[1] * e) ** (3.0 / 2.0))))))
            WpCr_2.append(WpCri_2)  # Above is calculation of W/P for Rate of Climb at 3km alt.
        WpCr_3 = []  # Empty List for appending W/P Data for AR[2].
        for i in range(0, len(self.WS_range)):
            WpCri_3 = self.n_p / (self.RC + sqrt(self.WS_range[i] * (2.0 / self.rho_cr) * (sqrt(self.C_D0) / (1.81 * ((self.AR[2] * e) ** (3.0 / 2.0))))))
            WpCr_3.append(WpCri_3)  # Above is calculation of W/P for Rate of Climb at 3km alt.
        return [WpCr_1,WpCr_2,WpCr_3]

    @Attribute
    def WP_gradient(self):
        ## Calculate Required Power for Climb Gradient Requirement 10m high object 10m away.
        WpCg_1 = []
        for i in range(0, len(self.WS_range)):
            WpCgi_1 = self.n_p / (sqrt(self.WS_range[i] * (2.0 / self.rho) * (1 / self.climblift[0])) * (self.G + (self.climbdrag[0] / self.climblift[0])))
            WpCg_1.append(WpCgi_1)
        WpCg_2 = []
        for i in range(0, len(self.WS_range)):
            WpCgi_2 = self.n_p / (sqrt(self.WS_range[i] * (2.0 / self.rho) * (1 / self.climblift[1])) * (self.G + (self.climbdrag[1] / self.climblift[1])))
            WpCg_2.append(WpCgi_2)
        WpCg_3 = []
        for i in range(0, len(self.WS_range)):
            WpCgi_3 = self.n_p / (sqrt(self.WS_range[i] * (2.0 / self.rho) * (1 / self.climblift[2])) * (self.G + (self.climbdrag[2] / self.climblift[2])))
            WpCg_3.append(WpCgi_3)
        return [WpCg_1, WpCg_2, WpCg_3]



    @Attribute
    def wingpowerloading(self):
        plt.axvline(x=self.ws_hand[0], label='C_Lmax_h = 1', color='c', linestyle='-.')
        plt.axvline(x=self.ws_hand[1], label='C_Lmax_h = 1.25', color='m', linestyle='-.')
        plt.axvline(x=self.ws_hand[2], label='C_Lmax_h = 1.5', color='y', linestyle='-.')

        plt.axvline(x=self.ws_nonhand[0], label='C_Lmax_nh = 1', color='c')
        plt.axvline(x=self.ws_nonhand[1], label='C_Lmax_nh = 1.25', color='m')
        plt.axvline(x=self.ws_nonhand[2], label='C_Lmax_nh = 1.5', color='y')

        plt.plot(self.WS_range, self.WP_rate[0], 'b', label='RC, AR = 6')
        plt.plot(self.WS_range, self.WP_rate[1], 'g', label='RC, AR = 9')
        plt.plot(self.WS_range, self.WP_rate[2], 'r', label='RC, AR = 12')

        plt.plot(self.WS_range, self.WP_gradient[0], 'b-.', label='Gradient, C_Lmax = 1')
        plt.plot(self.WS_range, self.WP_gradient[1], 'g-.', label='Gradient, C_Lmax = 1.25')
        plt.plot(self.WS_range, self.WP_gradient[2], 'r-.', label='Gradient, C_Lmax = 1.5')

        plt.ylabel('W/P [N*W^-1]')
        plt.xlabel('W/S [N*m^-2]')
        plt.legend()
        plt.title('Wing and Power Loading (RC = 1 m/s)')
        plt.show()
        return "Plot generated and closed"


  #  @Attribute
  #  def design_point(self):
  #      hand_launch_choice = Aircraft.handlaunch
  #      return hand_launch_choice




if __name__ == '__main__':
    from parapy.gui import display

    obj = WingPowerLoading()
    display(obj)
