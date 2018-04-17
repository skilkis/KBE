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

    @Attribute
    def payload(self):
        return self.params.weightestimator.payload

    @Attribute
    def battery_capacity(self):
        return self.sizing_value

    @Part
    def battery(self):
        return Battery(pass_down="sizing_target", max_width=self.camera.box_width * 2.0,
                       max_height=self.camera.box_height * 2.0,
                       sizing_value=self.sizing_value, position=Position(Point(-0.01, 0, 0)))

    @Part
    def frame_builder(self):
        return FFrame(quantify=len(self.frame_test), width=self.frame_test[child.index]['width'],
                      height=self.frame_test[child.index]['height'],
                      position=self.frame_test[child.index]['position'])

    @Attribute
    def frame_grabber(self):
        frames = [i.frame for i in self.frame_builder]
        return frames

    @Part
    def test2(self):
        return LoftedSurface(profiles=self.frame_grabber)

    @Attribute
    def position_camera(self):
        camera_pos = self.camera.position
        camera_length = self.camera.box_length
        self.camera.position = Point(camera_pos.x - camera_length, 0, 0)
        return self.camera.position

    @Attribute
    def frame_test(self):
        frame1 = self.frame_parameters(self.camera.internal_shape.bbox)
        frame2 = self.frame_parameters(self.battery.internal_shape.bbox)
        return [frame1, frame2]

    @Attribute
    def camera_selection(self):
        selected_camera = EOIR(target_weight=self.payload)
        camera_name = selected_camera.camera_selector
        camera_length = selected_camera.box_length
        return [camera_name, camera_length]

    @Part
    def nose_cone(self):
        return FCone(support_frame=self.frame_builder[0], fuselage_length=0.7, slenderness_ratio=1.0)

    @Part
    def camera(self):
        return EOIR(camera_name=self.camera_selection[0], position=Position(Point(-self.camera_selection[1], 0, 0)))

    @staticmethod
    def frame_parameters(sizing_part):

        corners = sizing_part.corners
        point0 = min(corners)
        point1 = max(corners)

        width = abs(point1.y-point0.y)
        height = abs(point1.z-point0.z)
        length = abs(point1.x-point0.x)

        fill_factor = 0.01*length

        x = point0.x - fill_factor
        y = (width / 2.0) + point0.y
        z = point0.z

        parameter_dictionary = {'width': width,
                                'height': height,
                                'length': length,
                                'position': Position(Point(x, y, z))}
        return parameter_dictionary

    @staticmethod
    def bbox_joiner(sizing_components):
        shape_out = None
        if len(sizing_components) > 1:
            shape_in = sizing_components[0].internal_shape
            for i in range(0, len(sizing_components) - 1):
                new_part = Fused(shape_in=shape_in, tool=sizing_components[i+1].internal_shape)
                shape_in = new_part
            shape_out = shape_in
        elif len(sizing_components) <= 1:
            shape_out = sizing_components.internal_shape
        return shape_out.bbox


    @Attribute
    def test_merge(self):
        return self.bbox_joiner()

    @Attribute
    def type_test(self):
        return type(self.camera)


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
