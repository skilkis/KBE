# -*- coding: utf-8 -*-

from parapy.core import *
from components import Motor, Propeller, Wing, Battery
import matplotlib.pyplot as plt
import numpy as np
from math import pi, sqrt
from directories import *
from scipy.interpolate import interp1d

__author__ = ["San Kilkis"]
__all__ = ["Performance"]

# TODO Comment code, it is in documentation


class Performance(Base):
    """ This class calculates the end performance of the UAV created in the KBE GUI. This verifies that the UAV will
    fulfill the mission requirements.

    :param wing_in: The Wing input instantiation.
    :type wing_in: str
    """

    __initargs__ = ["parasitic_drag"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'performance.png')

    motor_in = Input(Motor(), validator=val.Instance(Motor))
    propeller_in = Input(Propeller(), validator=val.Instance(Propeller))
    battery_in = Input(Battery(), validator=val.Instance(Battery))
    wing_in = Input(Wing(), validator=val.Instance(Wing))
    weight_mtow = Input(5.0, validator=val.Instance(float))
    parasitic_drag = Input(0.02, validator=val.Instance(float))
    oswald_factor = Input(0.85, validator=val.Instance(float))
    stall_buffer = Input(1.5, validator=val.Range(1.0, 1.5))

    @Attribute
    def stall_speed(self):
        """ Computes the new stall speed caused by change in MTOW in Class II (bottoms-up) as compared to the initial \
        estimate from Class I

        :return: Stall Speed in SI meter per second [m/s]
        :rtype: float
        """
        return sqrt((2 * 9.81 * self.weight_mtow) /
                    (self.wing_in.rho * self.wing_in.lift_coef_max * self.wing_in.planform_area))

    @Attribute
    def power_available(self):
        """ Grabs the available shaft power of the engine from the provided motor. Index 0 refers to continuous power \
        and Index 1 refers to the burst power of the engine

        :rtype: list
        """
        return self.motor_in.power[0], self.motor_in.power[1]

    @Attribute
    def propeller_eta_curve(self):
        """ Fetches the propeller efficiency curve as a function of airspeed from the provided propeller

        :rtype: interpld
        """
        return self.propeller_in.propeller_selector[2]

    @Attribute
    def eta_curve_bounds(self):
        """ Defines the bounds of the propeller curve to not address values that are not covered by the propeller data \
        index 0 refers to the minimum velocity and index 1 refers to the maximum velocity

        :rtype: list
        """
        return self.propeller_in.propeller_selector[3]

    @Attribute
    def prop_speed_range(self):
        """ Defines the True Airspeed (TAS) range used for the analysis through use of the minimum and maximum values \
        available in propeller data so as to not force data extrapolation.

        :return: Range of True Airspeeds (TAS) in SI meter per second [m/s]
        :rtype: numpy array
        """
        return np.linspace(self.eta_curve_bounds[0], self.eta_curve_bounds[1], 100)

    @Attribute
    def speed_range(self):
        return np.linspace(0.1, self.eta_curve_bounds[1], 100)

    @Attribute
    def dynamic_pressures(self):
        return 0.5 * self.wing_in.rho * (self.speed_range ** 2)

    @Attribute
    def lift_coefficients(self):
        return (self.weight_mtow * 9.81) / (self.dynamic_pressures * self.wing_in.planform_area)

    @Attribute
    def drag_coefficients(self):
        return self.parasitic_drag + (self.lift_coefficients / (pi * self.wing_in.aspect_ratio * self.oswald_factor))

    @Attribute
    def parasite_power(self):
        return self.parasitic_drag \
               * self.dynamic_pressures * self.wing_in.planform_area * self.speed_range

    @Attribute
    def induced_power(self):
        return ((self.lift_coefficients ** 2) / (pi * self.wing_in.aspect_ratio * self.oswald_factor)) \
               * (self.dynamic_pressures * self.wing_in.planform_area * self.speed_range)

    @Attribute
    def power_required(self):
        return self.parasite_power + self.induced_power

    @Attribute
    def endurance_velocity(self):
        """ Computes the optimum endurance velocity utilizing the maximum positive difference between the power \
        available and required curves. If this value is too close to the stall speed (which is determined by the input \
        'stall_buffer', then the non-optimum but safe value is returned instead.

        :return: Optimum endurance velocity in SI meter per second [m/s]
        :rtype: float
        """
        diff = [self.power_available_cont[i] - self.power_required[i] for i in range(0, len(self.speed_range))]
        idx_e = diff.index(max(diff))
        safe_speed = self.stall_buffer * self.stall_speed
        calc_speed = self.speed_range[idx_e]
        if calc_speed >= safe_speed:
            safe = True
        else:
            safe = False
            print 'Computed optimum endurance velocity of %1.2f [m/s] is too close to the stall speed! Instead a value'\
                  ' safety factor has been added to the stall speed and returned' % calc_speed
        return calc_speed if safe else safe_speed

    @Attribute
    def cruise_velocity(self):
        """ Computes the optimum cruise velocity utilizing the maximum tangent between velocity axis and the power \
        required curves. If this value is too close to the stall speed (which is determined by the input \
        'stall_buffer', then the non-optimum but safe value is returned instead.

        :return: Optimum cruise velocity in SI meter per second [m/s]
        :rtype: float
        """
        diff = []
        for i in range(0, len(self.speed_range) - 1):
            tangent = self.power_required[i + 1] / self.speed_range[i+1]
            local_tangent = (self.power_required[i + 1] - self.power_required[i]) / \
                            (self.speed_range[i + 1] - self.speed_range[i])
            diff = diff + [(abs(tangent - local_tangent))]
        idx_c = diff.index(min(diff))
        safe_speed = self.stall_buffer * self.stall_speed
        calc_speed = self.speed_range[idx_c]
        if calc_speed >= safe_speed:
            safe = True
        else:
            safe = False
            print 'Computed optimum cruise velocity of %1.2f [m/s] is too close to the stall speed! Instead a value' \
                  ' safety factor has been added to the stall speed and returned' % calc_speed
        return calc_speed if safe else safe_speed

    @Attribute
    def power_spline(self):
        """ Creates a linear-spline of the power required curve to be able to call any velocity value.

        :rtype: interp1d
        """
        return interp1d(self.speed_range, self.power_required, fill_value='extrapolate')

    @Attribute
    def endurance(self):
        velocity = self.endurance_velocity
        prop_eta = self.propeller_eta_curve(velocity)
        hours = (self.battery_in.total_energy * self.motor_in.efficiency * prop_eta) / (self.power_spline(velocity))
        return hours

    @Attribute
    def range(self):
        velocity = self.cruise_velocity
        prop_eta = self.propeller_eta_curve(velocity)
        hours = (self.battery_in.total_energy * self.motor_in.efficiency * prop_eta) / (self.power_spline(velocity))
        range_km = 3.6 * hours * velocity
        return range_km

    @Attribute
    def eta_values(self):
        return [self.propeller_eta_curve(float(i)) for i in self.prop_speed_range]

    @Attribute
    def power_available_cont(self):
        return [self.power_available[0] * i for i in self.eta_values]

    @Attribute
    def power_available_burst(self):
        return [self.power_available[1] * i for i in self.eta_values]

    @Attribute
    def plot_airspeed_vs_power(self):
        fig = plt.figure('PowerDiagram')
        plt.style.use('ggplot')
        plt.title('Power Available and Required as a Function of True Airspeed')

        # TODO add vertical lines for max speed, endurance speed, and cruise speed
        plt.plot(self.prop_speed_range, self.power_available_cont, label='Continuous Power')
        plt.plot(self.prop_speed_range, self.power_available_burst, label='Burst Power')
        plt.plot(self.speed_range, self.parasite_power, label='Parasitic')
        plt.plot(self.speed_range, self.induced_power, label='Induced')
        plt.plot(self.speed_range, self.power_required, label='Required')
        plt.axvline(self.stall_speed)

        plt.xlabel(r'$V_{\mathrm{TAS}}$ [m/s]')
        plt.ylabel(r'Power [W]')
        plt.axis([0, self.speed_range[-1], 0, self.motor_in.power[1]])
        plt.legend(loc='best')
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        return 'Figure Plotted and Saved'

    @Attribute
    def plot_lift_to_drag(self):
        fig = plt.figure('LiftvsDrag')
        plt.style.use('ggplot')
        plt.title('Lift to Drag Ratio as a Function of True Airspeed')

        plt.plot(self.speed_range, self.lift_coefficients / self.drag_coefficients)

        plt.xlabel(r'$V_{\mathrm{TAS}}$ [m/s]')
        plt.ylabel(r'Lift to Drag Ratio [-]')
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        return 'Figure Plotted and Saved'
    #
    # # TODO Create L/D Plot, and Performance Squares
    # Transparent rectangular prisms w/ Text on their sides, test enumerate function to deal w/ non array and be able to
    # make any number of stacked bars next to each other in the GUI


if __name__ == '__main__':
    from parapy.gui import display

    obj = Performance(label='Performance Analysis')
    display(obj)