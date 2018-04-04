
# TODO Update Header
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

    #: Boolean operator to determine if the user requires the UAV to be hand launched
    #: This parameter changes the stall-speed used for the Wing Loading
    #: :type: Boolean
    handlaunch = Input(True)

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


    @Attribute
    def wingloading(self):
        # TODO REMEMBER TO ADD ATTRIBUTE HEADER COMMENT HERE
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

        #Picks the first aspect ratio and proceeds since the climb-gradient requirement is not influenced heavily by AR
        wp_cg = []
        for i in range(len(self.C_Lmax)):
            wp_cg.append([self.n_p / (sqrt(num * (2.0 / self.rho) * (1 / self.climbcoefs['lift'][i])) *
                                      self.G + (self.climbcoefs['drag'][0][i] / self.climbcoefs['lift'][i]))
                          for num in self.WS_range])

        return {'climb_rate': wp_cr,
                'climb_gradient': wp_cg}

    @Attribute
    # TODO Make this a pretty graph with pretty colloooorrss please
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

        wp_cg_colors = ['m', 'b', 'r']
        for i in range(len(self.C_Lmax)):
            plt.plot(self.WS_range,
                     self.powerloading['climb_gradient'][i],
                     label='CG, C_Lmax = %.2f' % self.C_Lmax[i],
                     color=wp_cg_colors[i])

        plt.scatter(self.designpoint['wing_loading'],
                    self.designpoint['power_loading'],
                    label="design Point",
                    marker='^',
                    s=50)

        plt.ylabel('W/P [N*W^-1]')
        plt.xlabel('W/S [N*m^-2]')
        plt.legend()
        plt.title('Wing and Power Loading (Handlaunch = %s)' % self.handlaunch)
        plt.ion()
        plt.show()
        return "Plot generated and closed"

    @Attribute
    def designpoint(self):
        #TODO This header for design point
        """ An attribute which adds a safety factor to the lift coefficient in order to not stall out
        during climb-out. Modifying the lift coefficient changes drag coefficients as well due to induced drag
        the latter part of this code computes the new drag coefficients.

        :return: Dictionary containing design_point variables ('lift_coefficient') and drag coefficients ('climb_drag')
        """

        #: This value is based on the typical maximum lift that an airfoil generated by a clean airfoil
        #: :type: float
        C_L_realistic = 1.2

        #: Evaluation of the distance between C_L_realistic and user-inputed values for C_L
        #: :type: float array
        error = [abs(num - C_L_realistic) for num in self.C_Lmax]

        #: idx1 is the index corresponding to the minimum value within the array 'error'
        #: in other words idx1 is the index corresponding to the closest user-input value to C_L_realistic
        #: :type: integer
        idx1 = error.index(min(error))

        #: WS is the chosen Wing Loading based on idx1
        #: :type: float
        WS=self.wingloading['values'][idx1]

        #: Evaluation of the distance (error) between the chosen wing-loading and all values in WS_range
        # :type: float array
        error = [abs(num - WS) for num in self.WS_range]

        #: idx2 is the index corresponding to the closest value in WS_range to the chosen design wing-loading
        #: :type: integer
        idx2 = error.index(min(error))

        #TODO Add knowledge base assumption for best aspect ratio
        optimal_ARs=[7, 10]
        if self.handlaunch:
            optimal_AR = optimal_ARs[0]
        else:
            optimal_AR = optimal_ARs[1]

        #: Evaluation of the distance(error) between user-input aspect ratio and the optimal aspect ratio
        error = [abs(num - optimal_AR) for num in self.AR]

        #: idx3 corresponds to the index of the closest value within self.AR to the optimal_AR defined by the rule above
        #: :type: integer
        idx3 = error.index(min(error))

        WP_choices = [self.powerloading['climb_rate'][idx3][idx2],
                      self.powerloading['climb_gradient'][idx1][idx2]]
        if self.handlaunch:
            WP = WP_choices[1]
        else:
            WP = WP_choices[0]

        return{'lift_coefficient': self.C_Lmax[idx1],
               'aspect_ratio': self.AR[idx3],
               'wing_loading': WS,
               'power_loading': WP}

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
        return {'lift': C_Lcg,
                'drag': C_Dcg}

    @Attribute
    def WS_range(self):
        WS_limit = max(self.wingloading['values'])
        values = [float(i) for i in range(1, int(ceil(WS_limit / 100.0)) * 100)]
        return values
    #  Above is a dummy list of wing loadings for iterating in the Power Loading Equations.


if __name__ == '__main__':
    from parapy.gui import display

    obj = WingPowerLoading()
    display(obj)
