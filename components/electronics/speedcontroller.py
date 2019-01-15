#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Required Modules
from parapy.core import *
from parapy.geom import *
from definitions import *
from directories import *
import matplotlib.pyplot as plt
from scipy import stats


__author__ = ["Nelson Johnson"]
__all__ = ["SpeedController"]


class SpeedController(Component):
    """ This class will create the electronic speed controllers for the UAV. This is done based on the number of
    engines (each requires its own ESC), and the engine choice (determines amp rating). This will return a number of
    ESCs stacked vertically, and the COG displayed at the end is the combined COG of all ESCs. The ESC is sized (mass
    and volume) my linear regression of reference ESC's found on HobbyKing.

    :return: ParaPy Geometry of the ESC(s)

    :param amp_recc: This is the recommended ESC amperage from the chosen motor(s). In the case of multiple motors.
    :type amp_recc: float

    :param num_engines: This is the number of engines.
    :type num_engines: int
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'electricity.png')

    #:  This is the recommended ESC amperage from the chosen motor(s). In the case of multiple motors, this is the total
    #:  amperage.
    amp_recc = Input(40.0, validator=val.Positive())

    #:  This is the number of engines.
    num_engines = Input(1, validator=val.Positive())

    @Attribute
    def amp_range(self):
        """ This attribute contains the amp rating for ESCs found on hobbyking covering our spectrum of motor options
        in our motor database that will be used for regression.

        :return: List of ECC amperage's in SI Amps
        :rtype: list
        """
        return [6.0, 20.0, 30.0, 40.0, 60.0, 100.0, 120.0]

    @Attribute
    def weight_range(self):
        """ This attribute contains the corresponding weights of the ESCs found on hobbyking

        :return: List of ECS Weights in SI kg
        :rtype: list
        """
        return [0.006, 0.017, 0.021, 0.036, 0.063, 0.081, 0.164]

    @Attribute
    def volume_range(self):
        """ This attribute contains the corresponding volumes of the ESCs found on hobbyking

        :return: List of ECS Volumes in SI m^3
        :rtype: list
        """
        return [1728*10**-9, 7560*10**-9, 7560*10**-9, 15444*10**-9, 19200*10**-9, 22400*10**-9, 43428*10**-9]

    #:  Below are the constant Navio 2 Flight computer dimensions
    #:  The ESC is assumed have the same cross sectional dims (when looking perpendicular to x-y plane) as the flight
    #:  controller and will change in height based on the required amperage (which changes the ESC volume).
    #:  For box function: Width is x direction, length is y direction, height is z direction.
    @Attribute
    def l_navio(self):
        """ The 65mm length of the Flight Computer is the longest dimension and is to be oriented parallel with the x
         axis. Dimensions are at https://emlid.com/navio/

        :return: ParaPy Flight Controller Length
        :rtype: float
        """
        return 0.065

    @Attribute
    def w_navio(self):
        """ The 55mm width is to be oriented parallel with the y axis.

        :return: ParaPy Flight Controller Width
        :rtype: float
        """
        return 0.055

    @Attribute
    def h_navio(self):
        """ The flight controller height is to be oriented parallel with the y axis. This height was assumed from their
        figure.

        :return: ParaPy Flight Controller height
        :rtype: float
        """
        return 0.017

    @Attribute
    def component_type(self):
        """ This attribute names the component 'speedcontroller' for speedcontroller.

        :return: String with speedcontroller's component name
        :rtype: str
        """
        return 'speedcontroller'

    @Attribute
    def esc_weight_plot(self):
        """ This attribute creates a plot of the ESC weight vs. continuous amperage. It is saved in the path
        'user/plots'.

        :return: Plot of ESC weight vs. Amperage
        :rtype: Plot
        """
        fig = plt.figure('ESC_Weight_vs_Amperage')
        plt.style.use('ggplot')
        plt.title('ESC Weight vs. Continuous Amperage')
        plt.plot(self.amp_range, self.weight_range, 'b', label='ESC Weight')
        plt.ylabel('Weight')
        plt.xlabel('Amperage')
        plt.legend(loc=0)
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        return 'Plot Made, See PyCharm'

    @Attribute
    def esc_size_plot(self):
        """ This attribute creates a plot of the ESC volume vs. continuous amperage. It is save in the path 'user/plots'

        :return: Plot of ESC volume vs. continuous amperage
        :rtype: Plot
        """
        fig = plt.figure('ESC_Volume_vs_Amperage')
        plt.style.use('ggplot')
        plt.title('ESC Volume vs. Continuous Amperage')
        plt.plot(self.amp_range, self.volume_range, 'b', label='ESC Volume')
        plt.ylabel(r'Volume [$\mathrm{m}^3$]')
        plt.xlabel(r'Amperage [$\mathrm{A}$]')
        plt.legend(loc=0)
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        return 'Plot Made, See PyCharm'

    @Attribute
    def esc_weight(self):
        """ This attribute estimates the esc weight from the linear regression of the found ESC amperage's and
        corresponding weights. If there are more than one motor, multiple ESCs are used and the complete weight is
        calculated here

        :return: Total ESC weight
        :rtype: float
        """
        gradientt, interceptt, r_valuee, p_valuee, std_errr = stats.linregress(self.amp_range, self.weight_range)
        #  print "Weight Regression Gradient and intercept", gradientt, interceptt
        #  print "Weight Regression R-squared", r_valuee ** 2
        if self.num_engines == 1:
            esc_weight = self.amp_recc * gradientt + interceptt
        else:
            amp_per_engine = self.amp_recc / self.num_engines #  This is why the input is total Amperage
            esc_weight = (amp_per_engine * gradientt + interceptt)*self.num_engines

        if esc_weight < 0:
            esc_weight = self.weight_range[0]*self.num_engines
            #  This returns the minimum found ESC weight if a low required amperage is input and the linear regression
            #  returns a negative weight.
        return esc_weight

    @Attribute
    def esc_size(self):
        """ This attribute estimates the esc size from the linear regression of the found ESC amperage's and
        corresponding volumes. If there are more than one engine, there will be more than one ESC.

        :return: Total ESC weight
        :rtype: float
        """
        gradient, intercept, r_value, p_value, std_err = stats.linregress(self.amp_range, self.volume_range)
        #  print "Volume Regression Gradient and intercept", gradient, intercept
        #  print "Volume Regression R-squared", r_value ** 2
        if self.num_engines == 1:
            esc_size = self.amp_recc * gradient + intercept
        else:
            amp_per_engine = self.amp_recc / self.num_engines
            esc_size = amp_per_engine * gradient + intercept

        if esc_size < 0:
            #  This returns the minimum found ESC volume if a low required amperage is input and the linear regression
            #  returns a negative volume.
            esc_size = self.volume_range[0]
        return esc_size

    @Attribute
    def esc_dims(self):
        """ This attribute creates the speed controller dimensions, with the same cross-section as the flight computer.
        Their height can change, according to the required size.

        :return: ESC Dimensions
        :rtype: List
        """
        esc_width = self.l_navio
        esc_length = self.w_navio
        esc_height = self.esc_size/(esc_width*esc_length)
        return [esc_width, esc_length, esc_height]

    @Attribute
    def first_esc_pos(self):
        """   This is the first position of the bottom ESC, which is to be placed on top of the flight computer

        :return: First ESC Position
        :rtype: Position
        """
        return Position(Point(self.position.x, self.position.y -self.w_navio*0.5, self.position.z+self.h_navio))

    @Part
    def speed_controllers(self):
        """   This creates the speed controller(s). If there are multiple, they are positioned relative to one another.

         :return: ESC Geometries
         :rtype: Box
         """
        return Box(quantify=self.num_engines,
                   width=self.esc_dims[0], length=self.esc_dims[1], height=self.esc_dims[2],
                   position=translate(self.first_esc_pos if child.index == 0 else child.previous.position,
                                      'z',
                                      0 if child.index == 0 else self.esc_dims[2]),
                   transparency=0.5)

    @Attribute
    def center_of_gravity(self):
        """ This attribute finds the center of gravities of the separate ESCs, then finds the combined C.G.

          :return: ParaPy Point
          :rtype: Point
          """
        cogs = [self.speed_controllers[i].cog for i in range(0, self.num_engines)]
        avg_z = sum([i.z for i in cogs])/self.num_engines
        return Point(cogs[0].x, cogs[0].y, avg_z)

    @Attribute
    def esc_joiner(self):
        """ This joins the ESC's together through a series of Fuse operations to be able to present a
        single `internal_shape` required for the fuselage frame sizing.

        :return: ParaPy Fused Boxes
        :rtype: Fused
        """
        parts_in = self.speed_controllers
        if self.num_engines > 1:
            shape_in = parts_in[0]
            for i in range(0, self.num_engines - 1):
                new_part = Fused(shape_in=shape_in, tool=parts_in[i+1])
                shape_in = new_part
            shape_out = shape_in
        else:
            shape_out = parts_in[0]
        return shape_out

    @Part
    def internal_shape(self):
        """ This is creating a box for the fuselage frames. This is used to get around ParaPy errors.

        :return: Speed Controller(s) bounded box
        :rtype: ScaledShape
        """
        return ScaledShape(shape_in=self.esc_joiner, reference_point=self.center_of_gravity, factor=1, transparency=0.7,
                           hidden=True)

    @Attribute
    def weight(self):
        """ The mass of the speed controller(s)

        :return: Speed Controller(s) Mass
        :rtype: float
        """
        return self.esc_weight

    @Attribute
    def label(self):
        """ This labels the speed controller 'Speed Controller'

        :return: Navio2 Mass
        :rtype: float
        """
        return 'Speed Controller'


if __name__ == '__main__':
    from parapy.gui import display
    obj = SpeedController()
    display(obj)
