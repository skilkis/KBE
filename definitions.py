#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from directories import *


__author__ = "Şan Kılkış"
__all__ = ["Component", "ExternalBody", "VisualCG"]


class VisualCG(GeomBase):

    # TODO add header here and create a nice looking visual CG

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'battery.png')
    __initargs__ = ["vis_cog"]
    # TODO Find a proper icon here
    vis_cog = Input()
    scale = Input(0.01)

    @Part
    def visual_cg_location(self):
        return Sphere(radius=self.scale,
                      position=translate(self.position,
                                         'x', self.vis_cog.x,
                                         'y', self.vis_cog.y,
                                         'z', self.vis_cog.z),
                      color='yellow', hidden=self.hidden)


class Component(GeomBase):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'gear.png')

    position = Input(Position(Point(0, 0, 0)))  # Locks Orientation to that defined inside the component
    inside_fuselage = Input(True)  # Defaults to treating the component as a `sizing_part` used in fuselage construction
    hide_labels = Input(True)
    hide_cg = Input(True)

    # TODO Make a method that automatically finds the proper faces on the YOZ axis

    @Attribute
    def component_type(self):
        """ An identifier to be able to lump masses together.

        |
        Possible entries:

        |   'wing'
        |   'fuselage'
        |   'vt'
        |   'ht'
        |   'ct'
        |   'boom'
        |   'payload'
        |   'prop'
        |   'battery'
        |   'electronics'
        """

        return None

    @Attribute
    def weight(self):
        """ Total mass of the component

        :return: Mass in SI kilogram
        :rtype: float
        """
        return 0

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity w.r.t the origin

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        return Point(0, 0, 0)

    @Attribute(private=True)
    def text_label_position(self):
        """ Sets the default position of the text_label to be on the front-left corner of the internal_shape
        :rtype: Point
        """
        return self.internal_shape.bbox.corners[0]

    @Part
    def internal_shape(self):
        """ The geometry of the component that will be placed inside a structure, (i.e in a wing or fuselage)

        :rtype: parapy.geom
        """
        return Box(1, 1, 1, transparency=0.8)

    @Part
    def text_label(self):
        """ Automatically creates a text label that inherits whatever object is labelled as. This can be hidden
        through use of the Input parameter `hide_labels`

        :rtype: TextLabel
        """
        return TextLabel(text="     %s" % self.label,
                         position=self.text_label_position, hidden=self.hide_labels)

    @Part
    def cog_sphere(self):
        return VisualCG(self.center_of_gravity, hidden=self.hide_cg)


class ExternalBody(Component):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'air.png')

    material_choice = Input('cfrp', validator=val.OneOf(['cfrp']))
    ply_number = Input(1, validator=val.Positive())

    @Attribute
    def weight(self):
        return self.material_volume * self.material_density

    @Attribute
    def material_volume(self):
        ply_thickness = 0.234 * 10e-3
        return self.wetted_area * ply_thickness * float(self.ply_number)

    @Attribute
    def material_density(self):
        return 1524.8 if self.material_choice is 'cfrp' else 0

    @Attribute
    def surface_type(self):
        """ An identifier to be able to lump areas together.

        |
        Possible entries:

        |   'wing'
        |   'fuselage'
        |   'vt'
        |   'ht'
        |   'ct'
        |   'boom'
        |
        """

        return self.component_type

    @Attribute
    def wetted_area(self):
        """ Returns the total wetted area of the external_part to be able to perform drag and weight estimations

        :return: Total wetted area of the external_part in SI sq. meter
        :rtype: float
        """
        area = 0
        if hasattr(self.external_shape, 'shells'):
            for i in self.external_shape.shells:
                area = area + i.area
        else:
            raise Exception('%s has no solids/shells to find wetted_area from, please create a fused operation '
                            'to resolve' % self.external_shape)
        return area

    @Attribute
    def planform_area(self):
        """ The projected area of an `external_shape` when looking at the XY plane in the nadir direction ('z_')

        :return: Projected Area on the XY plane in SI sq. meter
        :rtype: float
        """
        return 0

    @Part
    def external_shape(self):
        """  The final shape of a ExternalSurface class which is to be exported THIS PART MUST BE OVERWRITTEN!!! """
        return Box(0.5, 0.5, 0.5, transparency=0.8, centered=True, position=self.position)

        # TODO Not make this a fused part, be abld to extract area w/o fused operation


if __name__ == '__main__':
    from parapy.gui import display

    obj = Component()
    display(obj)

