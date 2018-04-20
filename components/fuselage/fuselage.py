#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from user import *
from primitives import *
from components import *
from definitions import *
from wing import Wing

__author__ = "Şan Kılkış"
__all__ = ["Fuselage"]

# TODO Add boom, add tail cone
# TODO add validator to make sure proper instance list is entered [validator=val.InstanceList(Component)]


class Fuselage(GeomBase):

    compartment_type = Input(['nose', 'container', 'container', 'container', 'motor'])
    sizing_parts = Input([None,
                          EOIR(position=translate(YOZ, 'z', -0.2)),
                          [Battery(position=Position(Point(0, 0, 0))), EOIR(position=translate(XOY, 'z', 0.02))],
                          EOIR(position=translate(YOZ, 'z', 0.5)),
                          Motor(position=translate(XOY, 'x', 1.0))])
    nose_loc = Input(Point(-0.3, 0, 0))
    minimize_frames = Input(False)
    ruled = Input(False)

    @Attribute
    def frame_builder(self):

        if len(self.compartment_type) == len(self.sizing_parts):

            frames = []
            still_to_build = []  # Special parts which require the fuselage to be completed before instantiation
            first_container = True  # Boolean to determine if current instance is first occurance of a container frame
            apex_reached = False  # Boolean that indicates if a maxima in  fuselage thickness has been reached
            apex_index = 0
            build_loc = 'start'  # Switch case to determine frame placement
            for i in range(0, len(self.compartment_type) - 1):
                _type = self.compartment_type[i]
                _next_type = self.compartment_type[i+1]
                print i  #debugging

                # Start Boundary Condition
                if i == 0:
                    if _type == 'nose':
                        still_to_build.append(['nose', i])
                    elif _type == 'boom':
                        raise Exception('A boom has been requested with no supports. Please try again with a boom'
                                        ' instance surrounded by at least 2 frame containers')

                # Container Logic
                if _type == 'container':
                    if first_container:
                        _bbox = self.bbox_extractor(self.sizing_parts[i])
                        frames.append(self.bbox_to_frame(_bbox, build_loc))
                        first_container = False
                    else:
                        if _next_type == 'container':
                            _bbox = self.bbox_extractor(self.sizing_parts[i])
                            _frame = self.bbox_to_frame(_bbox, build_loc)

                            _next_bbox = self.bbox_extractor(self.sizing_parts[i+1])
                            _next_frame = self.bbox_to_frame(_next_bbox, build_loc)

                            # True means that the next frame is larger than the current
                            _width_check = (True
                                            if _frame[1]['width'] < _next_frame[1]['width']
                                            else False)
                            _height_check = (True
                                             if _frame[1]['height'] < _next_frame[1]['height']
                                             else False)

                            if _width_check and _height_check is True:
                                frames.append(self.bbox_to_frame(_bbox, build_loc))
                            else:
                                if not apex_reached:
                                    frames.append(self.bbox_to_frame(_bbox, build_loc))
                                    build_loc = 'end'
                                    frames.append(self.bbox_to_frame(_bbox, build_loc))
                                    apex_reached = True
                                    apex_index = i - 1  # Making up for i = 1 being the first frame
                                    print "apex reached"
                                elif apex_reached:
                                    raise TypeError('Only a fuselage with one apex (location of maximum area) is '
                                                    'allowed. Please re-arrange internals so that maximum thickness'
                                                    ' occurs only once')
                        elif _next_type != 'container':
                            _bbox = self.bbox_extractor(self.sizing_parts[i])
                            if apex_reached:
                                frames.append(self.bbox_to_frame(_bbox, build_loc))
                            else:
                                frames.append(self.bbox_to_frame(_bbox, 'start'))
                                frames.append(self.bbox_to_frame(_bbox, 'end'))
                                apex_index = i - 1

                # Boom Logic
                # TODO (TBD) Currently not implemented, it doesn't do anything, but would be nice to have in the future
                elif _type == 'boom':
                    still_to_build.append(['boom', i])

                # End Boundary Condition
                if i + 2 == len(self.compartment_type):
                    if _next_type == 'motor':
                        frames.append([MFrame(motor_diameter=self.sizing_parts[i+1].diameter,
                                              position=self.sizing_parts[i+1].position), None])
                    elif _next_type == 'tail':
                        still_to_build.append(['tail', i])

            fuselage_complete = (True if len(still_to_build) is 0 else False)
        else:
            raise IndexError('The supplied inputs do not have the same dimension')

        # return [frames, still_to_build, apex_index]
        return {'built_frames': frames,
                'apex_index': apex_index,
                'still_to_build': still_to_build,
                'fuselage_complete': fuselage_complete}

    @Attribute
    def nose_cone_frame(self):
        return FFrame(0.01, 0.01, Position(self.nose_loc))

    @Attribute
    def frame_grabber(self):
        grabbed_frames = [i[0] for i in self.frame_builder['built_frames']]
        apex_index = self.frame_builder['apex_index']
        if self.minimize_frames:
            index_to_keep = [0, apex_index, apex_index+1, len(grabbed_frames) - 1]
            grabbed_frames = [grabbed_frames[i] for i in range(0, len(grabbed_frames))
                              if i in index_to_keep]
        return grabbed_frames

    @Attribute
    def curve_grabber(self):
        return [i.frame for i in self.frame_grabber]

    @Attribute
    def point_grabber(self):
        return [i.spline_points for i in self.frame_grabber]

    @Attribute
    def side_bc(self):
        # Point 0 = Bottom, Point 1 = Side, Point 2 = Top, Point 3 = Side Reflected
        # Make this into a block comment
        points = [i[1] for i in self.point_grabber]
        spline = FittedCurve(points)

        start_tangent = spline.tangent1
        x = start_tangent.x
        y = start_tangent.y
        z = start_tangent.z
        start_tangent = Vector(-x, -y, -z)  # Opposite direction required due to sign convention in FFrame

        end_tangent = spline.tangent2
        return [start_tangent, end_tangent, spline]

    @Attribute
    def top_bc(self):
        # Due to the sign convention edge 1 will always be the top curve
        spline = self.fuselage_left.edges[1]

        start_tangent = spline.tangent1

        end_tangent = spline.tangent2
        x = end_tangent.x
        y = 0  # Forced to zero to avoid minute floating point errors
        z = end_tangent.z
        end_tangent = Vector(-x, y, -z)  # Opposite direction required due to sign convention in FFrame
        return [start_tangent, end_tangent]

    # @Attribute
    # def selected_bcs(self):
    #     if

    @Attribute(in_tree=True)
    def fuselage_left(self):
        return LoftedShell(profiles=self.curve_grabber, check_compatibility=True, ruled=self.ruled)

    # @Part
    # def fuselage_left(self):
    #     return LoftedSurface(profiles=self.curve_grabber)

    @Attribute
    def length(self):
        return self.fuselage_left.bbox.width

    @Attribute
    def fuselage_nose(self):
        if not self.frame_builder['fuselage_complete']:
            nose_cone = (FCone(support_frame=self.frame_grabber[0], top_tangent=self.top_bc[0], side_tangent=self.side_bc[0],
                         direction='x_') if self.frame_builder['still_to_build'][0][0] is 'nose' else None)
            # tail_cone = (FCone(support_frame=self.frame_grabber[-1], top_tangent=self.top_bc[1], side_tangent=self.side_bc[1],
            #              direction='x') if self.frame_builder['still_to_build'][1][0] is 'tail' else None)
        return nose_cone

    # @Part
    # def nose_cone(self):
    #     return ScaledShape(shape_in=self.fuselage_nose[0].cone, reference_point=XOY, factor=1)


    @staticmethod
    def bbox_to_frame(bbox, placement='start'):

        corners = bbox.corners
        point0 = min(corners)
        point1 = max(corners)

        width = abs(point1.y-point0.y)
        height = abs(point1.z-point0.z)
        length = abs(point1.x-point0.x)

        # fill_factor = 0.01*length

        x = (point0.x if placement == 'start' else point0.x + length if placement == 'end' else 0)
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

