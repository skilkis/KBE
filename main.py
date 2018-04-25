# from components import Battery
from design import *
from parapy.core import *
from parapy.geom import *
from directories import *
# from components import Battery, EOIR
from primitives import *
from wing import *
from components import *


# TODO Make sure that excel read and things are top level program features (not buried within the tree)

class UAV(Base):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')

    sizing_target = Input('weight')
    sizing_value = Input(1.25)
    show_labels = Input(True)

    @Part
    def params(self):
        return ParameterGenerator(initialize_estimations=True, label="Design Parameters")

    @Part
    def wing(self):
        return Wing(MTOW=self.mtow)

    @Part
    def fuselage(self):
        return Fuselage(compartment_type=['nose', 'container', 'container', 'container', 'motor'],
                        sizing_parts=[None, self.camera, self.battery, self.wing, self.motor])

    @Part
    def motor(self):
        return Motor(position=translate(XOY, 'x', 0.5))

    @Part
    def propeller(self):
        return Propeller(motor=self.motor)



    @Attribute
    def configuration(self):
        return self.params.configuration

    @Attribute
    def mtow(self):
        return self.params.weightestimator.mtow

    @Attribute
    def payload(self):
        return self.params.weightestimator.payload

    @Attribute
    def battery_capacity(self):
        return self.sizing_value

    @Part
    def battery(self):
        return Battery(position=translate(XOY, 'x', -0.1))


    # @Attribute
    # def position_camera(self):
    #     camera_pos = self.camera.position
    #     camera_length = self.camera.box_length
    #     self.camera.position = Point(camera_pos.x - camera_length, 0, 0)
    #     return self.camera.position

    @Attribute
    def camera_selection(self):
        selected_camera = EOIR(target_weight=self.payload)
        camera_name = selected_camera.camera_selector
        camera_length = selected_camera.box_length
        return [camera_name, camera_length]


    @Part
    def camera(self):
        return EOIR(camera_name=self.camera_selection[0], position=translate(XOY, 'x', -0.3))


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
