#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

from directories import *
from collections import Iterable
from Tkinter import *
import tkMessageBox

__author__ = "Şan Kılkış"
__all__ = ["Component", "ExternalBody", "VisualCG", "error_window", "warn_window"]


def error_window(msg):
    """ Provides a simple easy way to bring up an error message, useful for reducing clutter around error-message calls
    within the code """
    root = Tk()
    root.withdraw()
    tkMessageBox.showerror("Warning", msg)
    root.destroy()


def warn_window(msg):
    """ Provides a simple easy way to bring up an warning message, useful for reducing clutter around error-message
    calls within the code """
    root = Tk()
    root.withdraw()
    tkMessageBox.showwarning("Warning", msg)
    root.destroy()


class VisualCG(GeomBase):
    """ VisualCG provides the user with a nice visualization of the C.G. location without relying in small and hard to
    see points

    :return: A sphere at the location of th specified center of gravity
    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'cg.png')
    __initargs__ = ["vis_cog"]

    vis_cog = Input(Point(0, 0, 0), validator=val.IsInstance(Point))
    scale = Input(0.01, validator=val.Positive())
    color = Input('yellow')

    @Part
    def visual_cg_location(self):
        """ The sphere which is visibile in the GUI

         :rtype: Sphere
         """
        return Sphere(radius=self.scale,
                      position=translate(XOY,
                                         'x', self.vis_cog.x,
                                         'y', self.vis_cog.y,
                                         'z', self.vis_cog.z),
                      color='yellow', hidden=self.hidden)


class Component(GeomBase):
    """ Defines the main class definition for the entire components module. This acts as a template to then allow better
    meshing between modded components or multiple collaborators. Thus, the use of such primitive classes makes it easy
    for the code to be expanded later, since any class which inherits from Component can be assigned a new method simply
    by changing it once in this class

    :param position: Position of the current component in SI meter [m]
    :type position: Position

    :param inside_fuselage: Although currently not implemented this would allow non-dimensioned fuselage creation where
    parts could simply be assigned without constraints and the fuselage would be able to create a shell around them
    :type: inside_fuselage: bool

    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'gear.png')

    position = Input(Position(Point(0, 0, 0)), validator=val.IsInstance(Position))  # Locks Orientation to that defined inside the component
    inside_fuselage = Input(True, validator=val.IsInstance(bool))  # Defaults to treating the component as a `sizing_part` used in fuselage construction
    hide_labels = Input(True, validator=val.IsInstance(bool))
    hide_cg = Input(True, validator=val.IsInstance(bool))

    @Attribute
    def component_type(self):
        """ An identifier to be able to lump masses together.
        Possible entries:
        'wing'
        'fuselage'
        'vt'
        'ht'
        'ct'
        'boom'
        'payload'
        'prop'
        'battery'
        'electronics'

        :return: Component Type
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
        return self.internal_shape.bbox.corners[0] if self.internal_shape is not None else Point(self.position.x,
                                                                                                 self.position.y,
                                                                                                 self.position.z)

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
    ply_number = Input(1, validator=val.IsInstance(int))

    @Attribute
    def weight(self):
        return self.material_volume * self.material_density

    @Attribute
    def material_volume(self):
        ply_thickness = 0.234 * 1e-3
        return self.wetted_area * ply_thickness * float(self.ply_number)

    @Attribute
    def material_density(self):
        return 1524.8 if self.material_choice is 'cfrp' else 0

    @Attribute
    def surface_type(self):
        """ An identifier to be able to lump areas together.
        Possible entries:
        'wing'
        'fuselage'
        'vt'
        'ht'
        'ct'
        'boom'

        :return: Component Type
        """

        return self.component_type

    @Attribute
    def wetted_area(self):
        """ Returns the total wetted area of the external_part to be able to perform drag and weight estimations
        accurate to 3 decimal places. This is accomplished by subtracting the total shell area from the area of the
        intersected faces to obtain a fairly accurate wetted area.

        :return: Total wetted area of the external_part in SI sq. meter [m^2]
        :rtype: float
        """
        if isinstance(self.external_shape, Iterable):
            total_area = 0
            common_areas = []
            for body in self.external_shape:
                if hasattr(body, 'shells'):
                    for _shell in body.shells:
                        total_area = total_area + _shell.area
                for second_body in self.external_shape:
                    if body is not second_body:
                        _common_faces = Common(shape_in=body, tool=second_body).faces
                        for _face in _common_faces:
                            _calc_area = round(_face.area, 4)
                            if _calc_area not in common_areas:
                                common_areas = common_areas + [_calc_area]

            area = total_area - sum(common_areas)

        else:  # Opted to keep this funcionality in-case of old Fused class defintion is still used somewhere
            area = 0.0
            if hasattr(self.external_shape, 'shells'):
                for i in self.external_shape.shells:
                    area = area + i.area
            else:
                raise Exception('%s has no solids/shells to find wetted_area from, please create a fused operation '
                                'to resolve' % self.external_shape)
        return area

    @Attribute
    def planform_area(self):
        """ The projected area of an `external_shape` when looking at the XY plane in the nadir direction (z)

        :return: Projected Area on the XY plane in SI sq. meter
        :rtype: float
        """
        return 0

    @Part
    def external_shape(self):
        """  The final shape of a ExternalSurface class which is to be exported THIS PART MUST BE OVERWRITTEN!!!

        :return: External Shape
        :rtype: Box
        """
        return Box(0.5, 0.5, 0.5, transparency=0.8, centered=True, position=self.position)


if __name__ == '__main__':
    from parapy.gui import display

    obj = Component()
    display(obj)

