#  This code will do make a very simple estimation of the required electronic speed controllers (ESC)
#  mass and dimensions, based on the motor's ESC reccomendation in Amps.

from parapy.core import *
from parapy.geom import *
from definitions import *
from directories import *
import matplotlib.pyplot as plt
from scipy import stats
__author__ = ["Nelson Johnson"]
__all__ = ["SpeedController"]


class SpeedController(Component):

    #  The required inputs for this class are below.
    amp_recc = 40      #  This is the reccomended ESC amperage from the chosen motor.

    num_engines = 2  # This is the number of engines


    amp_range =      [6,      20,    30,     40,    60,   100,   120]
    #  Above are amp rating for ESCs found on hobbyking, covering our spectrum of motor options in the database.
    weight_range =  [0.006, 0.017, 0.021, 0.036, 0.063, 0.081, 0.164]
    #  Above are the corresponding weights of the ESC's found on hobbyking
    volume_range =  [1728*10**-9,  7560*10**-9,   7560*10**-9, 15444*10**-9, 19200*10**-9, 22400*10**-9, 43428*10**-9]
    #  Above are the corresponding volume of the ESC's in cubic m.

    #  Below are the Navio 2 Flight computer dimensions
    #  The ESC is assumed have the same cross secitonal dims (when looking perpendicular to x-y plane) as the flight controller,
    #  and will change in height based on the required amperage (which changes the ESC size).
    l_navio = 0.065     #  65mm Length
    w_navio = 0.025     #  55mm Width
    h_navio = 0.017     #  17mm height assumed.
    #  For box function: Width is x direction, length is y direction, height is z direction.

    @Attribute
    def component_type(self):
        return 'electronics'


    @Attribute
    def esc_weight_plot(self):
        fig = plt.figure('ESC_Weight_vs_Amperage')
        plt.style.use('ggplot')
        plt.title('ESC Weight vs. Continuous Amperage')
        plt.plot(self.amp_range, self.weight_range, 'b', label='ESC Weight')
        plt.ylabel('Weight')
        plt.xlabel('Amperage')
        plt.legend(loc=0)
        #plt.ion()
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        return 'Plot Made, See PyCharm'

    @Attribute
    def esc_size_plot(self):
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
        #  This attr estimates the esc weight from the linear regression of the found ESC amperages and corresponding weights.
        #  If there are more than one motor, multiple ESCs are used and the complete weight is calculated here
        gradientt, interceptt, r_valuee, p_valuee, std_errr = stats.linregress(self.amp_range, self.weight_range)
        print "Weight Regression Gradient and intercept", gradientt, interceptt
        print "Weight Regression R-squared", r_valuee ** 2
        if self.num_engines == 1:
            esc_weight = self.amp_recc * gradientt + interceptt
        else:
            amp_per_engine = self.amp_recc / self.num_engines
            esc_weight = (amp_per_engine * gradientt + interceptt)*self.num_engines

        if esc_weight <0:
            #  This returns the minimum found ESC weight if a low required amperage is input and the linear regression returns a negative weight.
            esc_weight = self.weight_range[0]*self.num_engines

        return esc_weight


    @Attribute
    def esc_size(self):
        #  This attr estimates the esc weight from the linear regression of the found ESC amperages and corresponding weights.
        #  If there are more than one engine, there will be more than one ESC.
        gradient, intercept, r_value, p_value, std_err = stats.linregress(self.amp_range, self.volume_range)
        print "Volume Regression Gradient and intercept", gradient, intercept
        print "Volume Regression R-squared", r_value ** 2
        if self.num_engines == 1:
            esc_size = self.amp_recc * gradient + intercept
        else:
            amp_per_engine = self.amp_recc / self.num_engines
            esc_size = amp_per_engine * gradient + intercept

        if esc_size < 0:
            #  This returns the minimum found ESC weight if a low required amperage is input and the linear regression returns a negative weight.
            esc_size = self.volume_range[0]

        return esc_size

    #  Now we must change the estimated volume into a rectangular prism.

    @Attribute
    def esc_dims(self):
        esc_width = self.l_navio        # The BOX functions width is in the x dir.
        esc_length = self.w_navio       #  The BOX functions length is in the y dir.
        esc_height = self.esc_size/(esc_width*esc_length)
        return [esc_width, esc_length, esc_height]

    @Attribute
    def first_esc_pos(self):
        #  This is the first position of the bottom ESC, which is to be placed on top of the flight computer
        return Position(Point(0,-self.w_navio*0.5,self.h_navio))

    @Part
    def speed_controllers(self):
        return Box(quantify=self.num_engines,
                   width=self.esc_dims[0], length=self.esc_dims[1], height=self.esc_dims[2],
                   position=translate(self.first_esc_pos if child.index == 0 else child.previous.position,
                                      'z',
                                      0 if child.index == 0 else self.esc_dims[2]),
                   transparency = 0.5)

    @Attribute
    def center_of_gravity(self):
        #  This finds the center of gravities of the seperate ESCs, then finds the combined C.G.
        cogs = [self.speed_controllers[i].cog for i in range(0,self.num_engines)]
        avg_z = sum([i.z for i in cogs])/self.num_engines

        print avg_z
        return Point(cogs[0].x, cogs[0].y, avg_z)

    @Attribute
    def esc_joiner(self):
        """ Joines the quantified ESC's together through a series of Fuse operations to be able to present a
        single `internal_shape` which is required per definition of the Class Component

        :return:
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
        return ScaledShape(shape_in=self.esc_joiner, reference_point=self.center_of_gravity, factor=1, transparency=0.7)

    @Attribute
    def weight(self):
        #  The weight of the navio2 flight computer is 23 grams.
        return self.esc_weight


if __name__ == '__main__':
    from parapy.gui import display
    obj = SpeedController()
    display(obj)