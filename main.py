from design import *
from parapy.core import *
from parapy.geom import *
from directories import *
from components import *
from primitives import *


class UAV(Base):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')

    sizing_target = Input('weight')
    sizing_value = Input(1.25)

    @Part
    def params(self):
        return ParameterGenerator(initialize_estimations=True, label="Design Parameters")

    @Attribute
    def configuration(self):
        return self.params.configuration

    @Attribute
    def mtow(self):
        return self.params.weightestimator.mtow

    @Part
    def fuselage(self):
        return Box(1, 1, 1)

    @Attribute
    def battery_capacity(self):
        return self.sizing_value

    @Part
    def battery(self):
        return Battery(pass_down="sizing_target", sizing_value=self.sizing_value)

    @Part
    def test(self):
        return FFrame(width=self.my_method_test['width'],
                      height=self.my_method_test['height'],
                      position=self.my_method_test['position'])

    # @Part
    # def test2(self):
    #     return FusedSolid(shape_in=self.battery, tool=self.camera)

    @Attribute
    def frame_test(self):
        frame1 = self.frame_parameters(self.battery)
        frame2 = self.frame_parameters(self.camera)

    @Part
    def camera(self):
        return EOIR()

    @staticmethod
    def frame_parameters(sizing_part):
        corners = sizing_part.internal_shape.bbox.corners
        point0 = min(corners)
        point1 = max(corners)

        width = abs(point1.y-point0.y)
        height = abs(point1.z-point0.z)
        length = abs(point1.x-point0.x)

        fill_factor = 0.01*length

        x = point0.x - fill_factor
        y = (width / 2.0) + point0.y
        z = (height/2.0) + point0.z

        parameter_dictionary = {'width': width,
                                'height': height,
                                'length': length,
                                'position': Position(Point(x, y, z))}

        return parameter_dictionary



if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
