#!/usr/bin/env python
# -*- coding: utf-8 -*-


# TODO Comment the whole code, it is in documentation

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# Component Class Definition
from definitions import *

# Necessary Modules for Data Processing
from directories import *
from os import listdir
from my_csv2dict import *

# Custom Colors
from user import *

# GUI Browser
from Tkinter import *
import tkFileDialog

__all__ = ["EOIR"]
__author__ = "Şan Kılkış"

#: A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
__show_primitives = False  # type: bool

# TODO comments here


class EOIR(ExternalBody):
    """  This script will generate the parametric Electro-Optical Infra-Ied camera as a payload. There are 7 cameras
    which span the entire payload range of 1 to 20 kg.

    :returns: ParaPy Geometry of the Horizontal Tail Surface

    :param target_weight: This is the target payload weight.
    :type target_weight: float
    """

    __initargs__ = ["target_weight", "camera_name", "position"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'camera.png')

    #: A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    target_weight = Input(0.2, validator=val.Positive())
    camera_name = Input('Not Specified')

    @Input
    def browse_motors(self):
        """ Allows the user to easily choose amongst available cameras with a GUI File-Browser.

        :return: Sets the `cameras_name` to the value chosen in the GUI Browser
        """
        root = Tk()
        root.withdraw()
        path = tkFileDialog.askopenfilename(initialdir=DIRS['EOIR_DATA_DIR'], title="Select Camera",
                                            filetypes=(("Camera Data Files", "*.csv"), ("All Files", "*.*")))
        root.destroy()

        valid_dir = DIRS['EOIR_DATA_DIR'].replace('\\', '/')
        if path.find(valid_dir) is -1:
            error_window("Custom Cameras must be placed in the pre-allocated directory")
            return 'Camera selection failed, please invalidate and run-again'
        else:
            if len(path) > 0:
                setattr(self, 'camera_name', str(path.split('.')[-2].split('/')[-1]))  # Selects the motor_name
            return 'Camera has been successfully chosen, invalidate to run-again'

    @Input
    def label(self):
        """Overwrites the inherited slot `label` with the chosen camera_name

        :return: Name of Camera
        :rtype: str
        """
        return self.specs['name']

    @Attribute
    def specs(self):
        if self.camera_name == 'Not Specified':
            selected_camera_specs = [num[1] for num in self.camera_database if num[0] == self.camera_selector][0]
            selected_camera_specs['name'] = self.camera_selector
        else:
            selected_camera_specs = read_csv(self.camera_name, DIRS['EOIR_DATA_DIR'])
            selected_camera_specs['name'] = self.camera_name
        return selected_camera_specs

    @Attribute
    def camera_database(self):
        database_path = DIRS['EOIR_DATA_DIR']
        camera_names = [str(i.split('.')[0]) for i in listdir(database_path) if i.endswith('csv')]
        cameras = [[name, read_csv(name, DIRS['EOIR_DATA_DIR'])] for name in camera_names]
        return cameras

    @Attribute
    def camera_selector(self):
        camera_list = sorted([[name[0], name[1]['weight']] for name in self.camera_database], key=lambda f: float(f[1]))
        error = [abs(i[1] - self.target_weight) for i in camera_list if i[1] <= self.target_weight]
        if len(error) == 0:
            raise ValueError('The given payload weight of %.2f [kg] is too small to find a suitable EO/IR Sensor'
                             % self.target_weight)
        else:
            idx1 = error.index(min(error))
            selected_camera = camera_list[idx1][0]
        return selected_camera

    @Attribute
    def component_type(self):
        return 'payload'

    @Attribute
    def weight(self):
        return self.specs['weight']

    @Attribute(private=True)
    def box_width(self):
        return self.specs['box_dimensions'][0] / 1000.0

    @Attribute(private=True)
    def box_length(self):
        return self.specs['box_dimensions'][1] / 1000.0

    @Attribute(private=True)
    def box_height(self):
        return self.specs['box_dimensions'][2] / 1000.0

    @Attribute(private=True)
    def gimbal_radius(self):
        diameter = self.specs['gimbal_dimensions'][0]  # Diameter is specified in mm
        return diameter / (2 * 1000.0)

    @Attribute(private=True)
    def gimbal_height(self):  # Total height of the gimbal arm (neglecting gimbal_radius)
        min_height = self.gimbal_radius * 1.1
        read_height = self.specs['gimbal_dimensions'][1] / 1000.0
        if read_height <= min_height:
            return min_height
        else:
            return read_height

    @Attribute(private=True)
    def exposed_height(self):
        return (self.specs['gimbal_dimensions'][2] / 1000.0) - self.gimbal_radius

    @Attribute
    def center_of_gravity(self):
        """ The center of gravity of the EOIR sensor is assumed to be the center of the bottom face

        :return: EOIR Center of gravity
        :rtype: Point
        """
        return self.internal_shape.faces[4].cog

    @Attribute
    def text_label_position(self):
        """ Overwrites the default text_label position to put it closer to the gimbal

        :rtype: Point
        """
        return self.gimbal.edges[0].midpoint

    # --- Output Solids: ----------------------------------------------------------------------------------------------

    @Part
    def internal_shape(self):
        return TransformedShape(shape_in=self.support_box_import,
                                from_position=XOY,
                                to_position=translate(translate(rotate90(XOY, 'z_'), 'x_', self.box_width / 2.0),
                                                      'x', -self.position.y,
                                                      'y', self.position.x,
                                                      'z', self.position.z),
                                color=MyColors.deep_red,
                                transparency=0.23)

    @Part
    def gimbal(self):
        return TranslatedShape(shape_in=self.gimbal_import,
                               displacement=Vector(self.position.x + (self.box_length / 2.0),
                                                   self.position.y, self.position.z - self.exposed_height),
                               color=MyColors.light_grey)

    @Part
    def camera_body(self):
        return TranslatedShape(shape_in=self.camera_body_import,
                               displacement=Vector(self.position.x + (self.box_length / 2.0),
                                                   self.position.y, self.position.z - self.exposed_height),
                               color=MyColors.light_grey)

    @Part
    def external_shape(self):
        return Fused(self.gimbal, self.camera_body, hidden=True, label=self.label)

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=__show_primitives)
    def support_box_import(self):  # The un-transformed box which creates the internals
        return Box(self.box_width, self.box_length, self.box_height, position=XOY)

    @Part(in_tree=__show_primitives)
    def support_cylinder(self):  # The main cylinder used to create the gimbal
        return Cylinder(self.gimbal_radius, self.gimbal_height, position=XOY)

    @Part(in_tree=__show_primitives)
    def cover_cylinder(self):  # A small cylinder used to fill the gap created by the cutout-tool
        return Cylinder(self.gimbal_radius, (child.radius / 2.0) + (self.gimbal_height - child.radius),
                        position=translate(XOY, 'z', child.radius / 2.0))

    @Part(in_tree=__show_primitives)
    def gimbal_sphere(self):  # The main sphere used to create the camera body
        return Sphere(self.gimbal_radius, position=XOY)

    @Part(in_tree=__show_primitives)
    def gimbal_outer_solid(self):  # A fused solid that is used to create the outer shape of the gimbal
        return FusedSolid(shape_in=self.gimbal_sphere, tool=self.support_cylinder)

    @Part(in_tree=__show_primitives)
    def gimbal_main_support(self):  # The cutout_tool is used to empty out a space for the camera body
        return SubtractedSolid(shape_in=self.gimbal_outer_solid,
                               tool=self.cutout_tool)

    @Part(in_tree=__show_primitives)
    def gimbal_cover(self):  # The top part of the gimbal_sphere is removed from 'cover_cylinder' to fill the gap
        return SubtractedSolid(shape_in=self.cover_cylinder,
                               tool=self.gimbal_sphere, make_compound=True)

    @Part(in_tree=__show_primitives)
    def gimbal_import(self):  # The final gimbal part before translation
        return FusedSolid(shape_in=self.gimbal_main_support, tool=self.gimbal_cover)

    @Part(in_tree=__show_primitives)
    def camera_body_import(self):  # The final camera part before translation
        return CommonSolid(shape_in=self.gimbal_sphere, tool=self.cutout_tool)

    @Part(in_tree=__show_primitives)
    def cutout_tool(self):
        return Box(width=1.5 * self.gimbal_radius,
                   length=2.1 * self.gimbal_radius, # Added .1 safety factor to account for errors in subtraction
                   height=self.gimbal_radius*2.0,
                   position=rotate90(XOY, 'z'),
                   centered=True)


if __name__ == '__main__':
    from parapy.gui import display

    obj = EOIR()
    display(obj)

