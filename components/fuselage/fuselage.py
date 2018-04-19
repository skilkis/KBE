#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

# Required Modules
from user import *
from primitives import *
from components import *


__all__ = ["Fuselage"]


class Fuselage(GeomBase):

    # @Part
    # def box1(self):
    #     return Box(position=YOZ, width=1, length=0.5, height=2, centered=True)
    #
    # @Part
    # def box2(self):
    #     return Box(position=translate(YOZ, z=2.2), width=1.5, length=0.5, height=2, centered=True)
    #
    # @Part
    # def motor(self):
    #     return Cylinder(position=translate(YOZ, z=4), radius=0.2, height=0.4)

    compartment_type = Input(['nose', 'container', 'container', 'motor'])
    # sizing_parts = ([None,
    #                 Box(position=YOZ, width=1, length=0.5, height=2, centered=True),
    #                 Box(position=translate(YOZ, z=2.2), width=1.5, length=0.5, height=2, centered=True),
    #                 Cylinder(position=translate(YOZ, z=2.5), radius=0.1, height=0.2)])


    sizing_parts = Input([None,
                          EOIR(position=translate(YOZ, 'z', -0.2)),
                          [Battery(position=Position(Point(0, 0, 0))),
                          EOIR(position=translate(XOY, 'z', 0.5))], Motor()])

    @Attribute
    def frame_builder(self):

        if len(self.compartment_type) == len(self.sizing_parts):

            frames = []
            still_to_build = []
            for i in range(0, len(self.compartment_type)):

                if i == 0 and self.compartment_type[i] == 'nose':
                    still_to_build.append(['nose', i])

                if self.compartment_type[i] == 'container':
                    bbox = self.bbox_extractor(self.sizing_parts[i])
                    frames.append(self.bbox_to_frame(bbox))

                elif self.compartment_type[i] == 'motor':
                    frames.append([MFrame(motor_radius=self.sizing_parts[i].radius,
                                          position=self.sizing_parts[i].position), None])
        else:
            raise IndexError('The supplied ')

        return frames

    @Attribute
    def frame_grabber(self):
        return [i[0].frame for i in self.frame_builder]

    @Part
    def fuselage_left(self):
        return LoftedSurface(profiles=self.frame_grabber)





    @staticmethod
    def bbox_to_frame(bbox):

        corners = bbox.corners
        point0 = min(corners)
        point1 = max(corners)

        width = abs(point1.y-point0.y)
        height = abs(point1.z-point0.z)
        length = abs(point1.x-point0.x)

        # fill_factor = 0.01*length

        x = point0.x
        y = (width / 2.0) + point0.y
        z = point0.z
        position = Position(Point(x, y, z))

        frame = FFrame(width, height, position)
        param_dict = {'width': width,
                      'height': height,
                      'length': length,
                      'position': position}

        return [frame, param_dict]

    @staticmethod
    def bbox_extractor(sizing_components):
        shape_out = None
        if type(sizing_components) == list:
            if len(sizing_components) > 1:
                shape_in = sizing_components[0].internal_shape
                for i in range(0, len(sizing_components) - 1):
                    new_part = Fused(shape_in=shape_in, tool=sizing_components[i+1].internal_shape)
                    shape_in = new_part
                shape_out = shape_in
            elif len(sizing_components) <= 1:
                shape_out = sizing_components.internal_shape
        else:
            shape_out = sizing_components.internal_shape
        return shape_out.bbox





    # widths = Input([0.4, 0.8, 0.8, 0.5])
    # heights = Input([0.2, 0.4, 0.4, 0.3])
    # boom_length = Input(4.0)
    # x_locs = Input([0, 1, 2, 3])
    # z_locs = Input([0, 0, 0, 0])

    # @Attribute
    # def frame_grabber(self):
    #     frames = [i.frame for i in self.frame_builder]
    #     # frames.append(self.motor.frame)
    #     return frames
    #
    # @Attribute
    # def current_pos(self):
    #     self.position = translate(self.position, 'x', 10)
    #     return self.position
    #
    # @Attribute
    # def weird_pos(self):
    #     return self.frame_grabber[-1].position.x / 2.0  # What the hell is going on here? this number comes out doubled
    #
    # @Part
    # def frame_builder(self):
    #     return FFrame(quantify=len(self.widths), width=self.widths[child.index],
    #                   height=self.heights[child.index],
    #                   position=translate(self.position, 'x', self.x_locs[child.index], 'z', self.z_locs[child.index]))
    # #
    # # @Part
    # # def motor(self):
    # #     return MFrame(motor_radius=0.1, position=translate(self.position, 'x', 4, 'z', 0.1))
    # #
    #
    # @Part
    # def right(self):
    #     return LoftedSurface(profiles=self.frame_grabber)
    #
    # #
    # # @Part
    # # def surface2(self):
    # #     return LoftedSurface(profiles=[self.frame_grabber[0], self.nosecone.tip_point])
    # #
    # # @Part
    # # def boom(self):
    # #     return FFrame(width=0.1, height=0.1,
    # #                   position=translate(self.position,
    # #                                      'x', (self.frame_grabber[-1].frame.position.x / 2.0) + self.boom_length,
    # #                                      'z', self.frame_grabber[-1].frame.position.z))
    # #
    # # @Part
    # # def nosecone(self):
    # #     return FCone(support_frame=self.frame_builder[0], color=MyColors.light_grey)
    #
    # # @Part
    # # def tailcone(self):
    # #     return FCone(support_frame=self.boom, direction='x_')
    #
    # # @Part
    # # def tailcone_2(self):
    # #     return FCone(support_frame=self.motor, direction='x_')
    #
    # # @Part
    # # def nose_reference(self):
    # #     return Point(-0.5, 0, 0)
    # #
    # # @Attribute
    # # def nose_top_guide(self):
    # #     start_frame = self.frame_builder[0]
    # #     points = start_frame.spline_points
    # #     return FittedCurve(points=[points[0], self.nose_reference, points[2]])
    # #
    # # @Attribute
    # # def nose_side_guide(self):
    # #     start_frame = self.frame_builder[0]
    # #     points = start_frame.spline_points
    # #     return FittedCurve(points=[points[1], self.nose_reference, points[3]])
    # #
    # # @Attribute
    # # def nose_frame(self):
    # #     start_frame = self.frame_builder[0]
    # #     points = start_frame.spline_points
    # #     return SplitCurve(curve_in=start_frame.frame, tool=points[1])
    # #
    # # @Part
    # # def nose_top_guide_split(self):
    # #     return SplitCurve(curve_in=self.nose_top_guide, tool=self.nose_reference)
    # #
    # # @Part
    # # def nose_side_guide_split(self):
    # #     return SplitCurve(curve_in=self.nose_side_guide, tool=self.nose_reference)
    # #
    # # @Part
    # # def filled_test(self):
    # #     return FilledSurface(curves=[self.nose_frame.edges[1], self.nose_top_guide_split.edges[1],
    # #                                  self.nose_side_guide_split.edges[0]])
    #
    # # @Part
    # # def fuselage(self):
    # #     return MirroredShape(shape_in=self.half_fuselage, reference_point=YOZ,
    # #                            vector1=Vector(1, 0, 0),
    # #                            vector2=Vector(0, 0, 1),
    # #                            color=MyColors.light_grey)
    # #
    # # @Part
    # # def end_fuselage(self):
    # #     return FusedShell(shape_in=self.half_fuselage, tool=self.fuselage, color=MyColors.light_grey)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Fuselage()
    display(obj)

