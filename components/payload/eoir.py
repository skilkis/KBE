#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" eoir.py is a file which automatically generates an EO/IR Imaging system on parametric input of battery weight,
 """

# Required ParaPy Modules
from parapy.core import *
from parapy.geom import *


# A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
show_primitives = False


class EOIR(GeomBase):

    weight = Input(0.25)

    test_box = 0.1
    test_gimbal = 0.10

    @Attribute
    def box_width(self):
        return self.test_box

    @Attribute
    def box_length(self):
        return self.test_box

    @Attribute
    def box_height(self):
        return self.test_box

    @Attribute
    def gimbal_height(self):
        return self.test_gimbal * 1.1

    @Attribute
    def gimbal_radius(self):
        return self.test_gimbal

    # Output Solids:

    @Attribute
    def mycolors(self):
        colors = {'light_grey': (128, 128, 128),
                  'deep_red': (128, 0, 0),
                  'dark_grey': (17, 17, 17)}
        return colors

    @Part
    def electronics(self):
        return TransformedShape(shape_in=self.support_box_import,
                                from_position=XOY,
                                to_position=translate(rotate90(XOY, 'z_'), 'x_', self.box_length / 2.0),
                                color=self.mycolors['deep_red'])


    @Part
    def gimbal(self):
        return TranslatedShape(shape_in=self.gimbal_import,
                               displacement=Vector(self.box_length / 2.0, 0, -self.gimbal_height),
                               color=self.mycolors['light_grey'])

    @Part
    def camera_body(self):
        return TranslatedShape(shape_in=self.camera_body_import,
                               displacement=Vector(self.box_length / 2.0, 0, -self.gimbal_height),
                               color = self.mycolors['light_grey'])

    # Input Primitives:

    @Part(in_tree=show_primitives)
    def support_box_import(self):  # The un-transformed box which creates the electronics part
        return Box(self.box_width, self.box_length, self.box_height, hidden=True)

    @Part(in_tree=show_primitives)
    def support_cylinder(self):  # The main cylinder used to create the gimbal
        return Cylinder(self.gimbal_radius, self.gimbal_height)

    @Part(in_tree=show_primitives)
    def cover_cylinder(self):  # A small cylinder used to fill the gap created by the cutout-tool
        return Cylinder(self.gimbal_radius, self.gimbal_height/2.0, position=translate(XOY, 'z', child.height))

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
                               tool=self.gimbal_sphere)

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





