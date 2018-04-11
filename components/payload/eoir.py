#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" eoir.py is a file which automatically generates an EO/IR Imaging system on parametric input of battery weight,
 """

# TODO Comment the whole code
# TODO add attributes necessary for fuselage class

# Required ParaPy Modules
from parapy.core import *
from parapy.geom import *

# Necessary Modules for Data Processing
from directories import *
from os import listdir
import io

__all__ = ["EOIR", "show_primitives"]

# A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
show_primitives = False


class EOIR(GeomBase):

    target_weight = Input(0.2)
    camera_name = Input(None)

    test_box = 0.1
    test_gimbal = 0.10

    @Attribute
    def specs(self):
        if self.camera_name is None:
            selected_camera_specs = [num[1] for num in self.camera_database if num[0] == self.camera_selector]
            return selected_camera_specs[0]
        else:
            return self.read_csv(self.camera_name)

    @Attribute
    def specs_test(self):
        if self.camera_name is None:
            camera_index = [name.index(self.camera_selector) for name in self.camera_database]
            return self.camera_database[camera_index][1]
        else:
            return self.read_csv(self.camera_name)

    @Attribute
    def camera_database(self):
        database_path = DIRS['EOIR_DATA_DIR']
        camera_names = [str(i.split('.')[0]) for i in listdir(database_path) if i.endswith('csv')]
        cameras = [[name, self.read_csv(name)] for name in camera_names]
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
    def weight(self):
        return self.specs['weight']

    @Attribute
    def box_width(self):
        return self.specs['box_dimensions'][0] / 1000.0

    @Attribute
    def box_length(self):
        return self.specs['box_dimensions'][1] / 1000.0

    @Attribute
    def box_height(self):
        return self.specs['box_dimensions'][2] / 1000.0

    @Attribute
    def gimbal_radius(self):
        diameter = self.specs['gimbal_dimensions'][0]  # Diameter is specified in mm
        return diameter / (2 * 1000.0)

    @Attribute
    def gimbal_height(self):  # Total height of the gimbal arm (neglecting gimbal_radius)
        min_height = self.gimbal_radius * 1.1
        read_height = self.specs['gimbal_dimensions'][1] / 1000.0
        if read_height <= min_height:
            return min_height
        else:
            return read_height

    @Attribute
    def exposed_height(self):
        return (self.specs['gimbal_dimensions'][2] / 1000.0) - self.gimbal_radius

    # TODO consider moving read_csv in-case other files require the same class
    def read_csv(self, camera_name):
        filename = ('%s.csv' % camera_name)
        directory = get_dir(os.path.join(DIRS['EOIR_DATA_DIR'], filename))
        with io.open(directory, mode='r', encoding='utf-8-sig') as f:
            spec_dict = {}
            filtered = (line.replace("\n", '') for line in f)  # Removes \n from the created as a byproduct of encoding
            for line in filtered:
                field, value = line.split(',')
                if self.has_number(value):
                    if value.find('x') != -1:
                        if value.find('.') != -1:
                            value = [float(i) for i in value.split('x')]
                        else:
                            value = [int(i) for i in value.split('x')]
                    else:
                        value = float(value)
                else:
                    if value.find('/') != -1:
                        value = [str(i) for i in value.split('/')]
                    elif (value.lower()).find('true') != -1:
                        value = True
                    elif (value.lower()).find('false') != -1:
                        value = False
                    else:
                        value = str(value)
                spec_dict['%s' % str(field)] = value
            f.close()
            return spec_dict

    @staticmethod
    def has_number(any_string):
        """ Returns True/False depending on if the input string contains any numerical characters (i.e 0, 1, 2, 3...9)
        :param any_string: A user-input, any valid string is accepted
        :type any_string: str
        :rtype: bool

        >>> has_number('I do not contain any numbers')
        False
        >>> has_number('Oh look what we have here: 2')
        True
        """
        return any(char.isdigit() for char in any_string)

    # --- Output Solids: ----------------------------------------------------------------------------------------------

    @Attribute
    def mycolors(self):
        colors = {'light_grey': (128, 128, 128),
                  'deep_red': (128, 0, 0),
                  'dark_grey': (17, 17, 17)}
        return colors

    @Part
    def internals(self):
        return TransformedShape(shape_in=self.support_box_import,
                                from_position=XOY,
                                to_position=translate(rotate90(XOY, 'z_'), 'x_', self.box_width / 2.0),
                                color=self.mycolors['deep_red'],
                                transparency=0.2)


    @Part
    def gimbal(self):
        return TranslatedShape(shape_in=self.gimbal_import,
                               displacement=Vector(self.box_length / 2.0, 0, -self.exposed_height),
                               color=self.mycolors['light_grey'])

    # TODO Investigate of making this a compound improves performance
    @Part
    def camera_body(self):
        return TranslatedShape(shape_in=self.camera_body_import,
                               displacement=Vector(self.box_length / 2.0, 0, -self.exposed_height),
                               color=self.mycolors['light_grey'])

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=show_primitives)
    def support_box_import(self):  # The un-transformed box which creates the internals
        return Box(self.box_width, self.box_length, self.box_height, hidden=True)

    @Part(in_tree=show_primitives)
    def support_cylinder(self):  # The main cylinder used to create the gimbal
        return Cylinder(self.gimbal_radius, self.gimbal_height)

    @Part(in_tree=show_primitives)
    def cover_cylinder(self):  # A small cylinder used to fill the gap created by the cutout-tool
        return Cylinder(self.gimbal_radius, (child.radius / 2.0) + (self.gimbal_height - child.radius),
                        position=translate(XOY, 'z', child.radius / 2.0))

    @Part(in_tree=show_primitives)
    def gimbal_sphere(self):  # The main sphere used to create the camera body
        return Sphere(self.gimbal_radius)

    @Part(in_tree=show_primitives)
    def gimbal_outer_solid(self):  # A fused solid that is used to create the outer shape of the gimbal
        return FusedSolid(shape_in=self.gimbal_sphere, tool=self.support_cylinder)

    @Part(in_tree=show_primitives)
    def gimbal_main_support(self):  # The cutout_tool is used to empty out a space for the camera body
        return SubtractedSolid(shape_in=self.gimbal_outer_solid,
                               tool=self.cutout_tool)

    @Part(in_tree=show_primitives)
    def gimbal_cover(self):  # The top part of the gimbal_sphere is removed from 'cover_cylinder' to fill the gap
        return SubtractedSolid(shape_in=self.cover_cylinder,
                               tool=self.gimbal_sphere, make_compound=True)

    @Part(in_tree=show_primitives)
    def gimbal_import(self):  # The final gimbal part before translation
        return FusedSolid(shape_in=self.gimbal_main_support, tool=self.gimbal_cover)

    @Part(in_tree=show_primitives)
    def camera_body_import(self):  # The final camera part before translation
        return CommonSolid(shape_in=self.gimbal_sphere, tool=self.cutout_tool)

    @Part(in_tree=show_primitives)
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





