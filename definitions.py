#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from directories import *


__author__ = "Şan Kılkış"
__all__ = ["Component"]


class Component(GeomBase):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'gear.png')

    position = Input(Position(Point(0, 0, 0)))  # Locks Orientation to that defined inside the component
    hide_labels = Input(False)

    # TODO Make a method that automatically finds the proper faces on the YOZ axis

    @Attribute
    def weight(self):
        """ Total mass of the component

        :return: Mass in SI kilogram
        :rtype: float
        """
        return 1.0

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity w.r.t the origin

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        return Point(0, 0, 0)

    @Attribute
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
    def cog_shpere(self):
        return Sphere(radius = 0.05,
                      position = Position(self.center_of_gravity),
                      color = 'Red')

if __name__ == '__main__':
    from parapy.gui import display

    obj = Component()
    display(obj)

