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


class WingPowerLoading(Base):

    # INPUTS:
    #: Defines which weight the user is trying to design for, current options are 'payload', 'mtow'
    #: :type: string
    weight_target = Input('payload')

    #: Value attributed to the target weight defined above
    #: If weight_target = 'mtow' then target value is MTOW = target_value
    #: :type: float
    target_value = Input(0.25)

    #: Boolean operator to determine if the user requires the UAV to be hand launched
    #: This parameter changes the stall-speed used for the Wing Loading
    handlaunch = Input(True)

    #                             #  The inputs required for the Wing/Power Loading Diagrams are Below:
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
        if self.weight_target == 'payload':
            MTOW = 4.7551*self.target_value+0.59962
            #  Estimation of MTOW from payload mass from DSE Midterm Report.
            #  It is valid for UAVs with payload masses between 0 and 50 kg.
            return MTOW

    @Attribute
    def m_pl_derived(self):
        if self.weight_target == 'mtow':
            m_pl_derived = 0.2103*self.target_value-0.1261
            #  Estimation of m_pl from MTOW with reveresed Eq.
            return m_pl_derived


    @Attribute
    def wingloading(self):

# REMEMBER TO ADD ATTRIBUTE HEADER COMMENT HERE
        if self.handlaunch:
            V_s = self.V_s_hand
            ws_string = '_hand'
        else:
            V_s = self.V_s_nonhand
            ws_string = ''
        ws = []
        for i in range(len(self.C_Lmax)):
            ws.append(0.5 * self.rho * self.C_Lmax[i] * V_s ** 2)
        return {'values': ws, 'flag': ws_string}

#  In the following block, the equations for the required power loading are coded.


    @Attribute
    def climbcoefs(self):
        """ An attribute which adds a safety factor to the lift coefficient in order to not stall out
        during climb-out. Modifying the lift coefficient changes drag coefficients as well due to induced drag
        the latter part of this code computes the new drag coefficients.

        :return: Dictionary containing modified lift coefficients ('climb_lift') and drag coefficients ('climb_drag')
        """
        C_Lcg = [num - 0.2 for num in self.C_Lmax]
        # Above we subtract 0.2 from climb gradient C_l to keep away from stall during climb out
        C_Dcg = []
        for i in range(len(self.AR)):
            C_Dcg.append([(self.C_D0 + num ** 2 / (pi * self.AR[i] * self.e_factor)) for num in self.C_Lmax])
            # Due to how C_Dcg is defined the first array dim is aspect ratios, the second dim is lift coefficient
            # Thus accessing the 2nd aspect ratio and 1st lift coefficient would be C_dcg[1][0]
        return {'lift': C_Lcg, 'drag': C_Dcg}

    @Attribute
    def powerloading(self):
        """ Lazy-evaluation of Power Loading due to a Climb Rate Requirement at 3000m for various Aspect Ratios

        :return: Stacked-Array where first dimension corresponds to Aspect Ratio, and sub-dimension contains
        an array of floats in order of smallest Wing Loading to Largest. This range is set w/ parameter 'WS_range'
        """
        wp_cr = []
        for i in range(len(self.AR)):
            wp_cr.append([self.n_p / (self.RC + sqrt(
                num * (2.0 / self.rho_cr) * (sqrt(self.C_D0) / (1.81 *
                                                                ((self.AR[i] * e) ** (3.0 / 2.0))))))
                         for num in self.WS_range])
            # evaluating all values of WS_range w/ list comprehension

            ## Calculate Required Power for Climb Gradient Requirement 10m high object 10m away.

        #Picks the middle-aspect ratio and proceeds
        wp_cg = []
        for i in range(len(self.C_Lmax)):
            wp_cg.append([self.n_p / (sqrt(num * (2.0 / self.rho) * (1 / self.climbcoefs['lift'][i])) *
                                      self.G + (self.climbcoefs['drag'][1][i] / self.climbcoefs['lift'][i]))
                          for num in self.WS_range])

        return {'climb_rate': wp_cr, 'climb_gradient': wp_cg}

    @Attribute
    def loadingdiagram(self):


        ws_colors = ['c', 'm', 'y']
        for i in range(len(self.C_Lmax)):
            plt.axvline(x=self.wingloading['values'][i],
                        label='C_Lmax%s = %.2f' % (self.wingloading['flag'], self.C_Lmax[i]),
                        color=ws_colors[i])

        wp_cr_colors = ['b', 'r', 'g']
        for i in range(len(self.AR)):
            plt.plot(self.WS_range,
                     self.powerloading['climb_rate'][i],
                     label='CR, AR = %d' % self.AR[i],
                     color=wp_cr_colors[i])

        # wp_cg_colors = ['m', 'b', 'r']
        # for i in range(len(self.AR)):
        #     plt.plot(self.WS_range,
        #              self.powerloading['climb_gradient'][i],
        #              label='C_Lmax%s = %.2f' % (self.wingloading['flag'], self.C_Lmax[i]),
        #              color=wp_cg_colors[i])

        plt.ylabel('W/P [N*W^-1]')
        plt.xlabel('W/S [N*m^-2]')
        plt.legend()
        plt.title('Wing and Power Loading (RC = 1 m/s)')
        plt.show()
        return "Plot generated and closed"


if __name__ == '__main__':
    from parapy.gui import display

    obj = WingPowerLoading()
    display(obj)
