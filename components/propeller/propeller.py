#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# Required Class Definitions
from definitions import Component
from components.motor import *
from math import radians
from user import MyColors
from directories import *


__author__ = "Şan Kılkış"
__all__ = ["Propeller"]

# Useful links for knoweldge base:
# https://www.apcprop.com/technical-information/file-downloads/
# https://www.southampton.ac.uk/~jps7/Aircraft%20Design%20Resources/Sydney%20aerodynamics%20for%20students/propeller/prop1.html


class Propeller(Component):
    """ Always spins in motor direction

    """

    # TODO make sure the propeller code is structured nicely
    # Change label to chosen propeller

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    motor = Input(Motor(integration='puller'))
    position = Input(Position(Point(0, 0, 0)))

    @Input
    def position(self):
        """ Automatically snaps the propeller to the specified motor from the input `motor`. If a user-input is provided
        the propeller will become detached. In this case please invalidate this slot """
        return self.motor.position


    @Attribute
    def propeller_diameter(self):
        return 0.5

    @Attribute
    def allowed_prop_range(self):
        props = self.motor.specs['prop_recommendation']
        return

    # --- Geometry Visualization: -------------------------------------------------------------------------------------

    @Attribute
    def propeller_geometry(self):
        """ Defines the geometry parameters necessary to instantiate a propeller with the Attribute `airfoil_builder`
        NOTE: Propeller geometry is only for visualization purposes. Constructing a proper propeller would
        take too much time and would be out of the scope of our project.

        :return: A dictionary containing geometry parameters ['spanwise_loc', 'chord_dist', 'twist_dist']
        :rtype: dict
        """

        # Span-wise Location
        radius = self.propeller_diameter / 2.0
        unit_z_locs = [0.0, 0.1, 0.2, 0.3, 0.7, 0.8, 0.9, 1.0]
        z_locs = [i * radius for i in unit_z_locs]

        # Chord Distribution
        root_chord = self.motor.diameter * 0.5  # Scaled off of the motor to avoid too large of a chord
        unit_chord_lengths = [1.0, 1.5, 2.5, 2.3, 1.5, 1.3, 1.0, 0.1]  # Scaled w.r.t the root_chord
        chords = [i * root_chord for i in unit_chord_lengths]

        # Twist Distribution
        twists = [0, 0, 7, 6, 5, 4, 3, 2]

        return {'spanwise_loc': z_locs, 'chord_dist': chords, 'twist_dist': twists}

    @Attribute
    def airfoil_builder(self):
        airfoils = []
        geom = self.propeller_geometry
        for i in range(0, len(geom['spanwise_loc'])):
            scaled = ScaledCurve(curve_in=self.airfoil_unit_curve,
                                 reference_point=XOY,
                                 factor=geom['chord_dist'][i])
            rotated = RotatedCurve(curve_in=scaled,
                                   rotation_point=XOY,
                                   vector=XOY.Vz,
                                   angle=radians(geom['twist_dist'][i]))
            translated = TranslatedCurve(curve_in=rotated,
                                         displacement=Vector(0,
                                                             0,
                                                             geom['spanwise_loc'][i]))
            airfoils.append(translated)
        return airfoils

    @Attribute(private=True)
    def propeller_builder(self):
        prop_top = LoftedSolid(profiles=self.airfoil_builder)
        prop_bottom = MirroredShape(shape_in=prop_top, reference_point=XOY, vector1=XOY.x_, vector2=XOY.y)
        propeller = Compound(built_from=[prop_top, prop_bottom])
        return propeller

    @Attribute
    def text_label_position(self):
        """ Redefines the default text_label_position to be at the tip of the propeller blade """
        tip_airfoil_pos = self.propeller.bbox.corners[1]
        return tip_airfoil_pos

    # --- Output Shapes: ----------------------------------------------------------------------------------------------

    @Part
    def propeller(self):
        return TranslatedShape(shape_in=self.propeller_builder,
                               displacement=Vector(self.position.x + self.build_direction * (self.fairing_length * 0.1),
                                                   self.position.y,
                                                   self.position.z),
                               color=MyColors.dark_grey,
                               mesh_deflection=10 ** -4)  # An optimum value between a good quality render & performance

    @Part
    def propeller_fairing(self):
        return TranslatedShape(shape_in=self.propeller_fairing_thrust_aligned,
                               displacement=Vector(self.position.x,
                                                   self.position.y,
                                                   self.position.z),
                               color=MyColors.chill_white)

    @Part
    def internal_shape(self):
        """ The propeller does not have an internal part, thus a place holder part is created with zero area """
        return Circle(radius=0, hidden=True)

    # --- Primitives & Private Attributes: ----------------------------------------------------------------------------

    @Attribute(private=True)
    def airfoil_data(self):
        """ Imports airfoil data, this code borrowed from LiftingSurface

        :return: List of airfoil points on the YX plane
        """
        #  This reads and scans User chosen Airfoil Data from the database and stores it as airfoil_data.
        _type = 'cambered'
        _name = 'SD7062.dat'  # This is only for visualization, in the future this attribute can be modified
        filepath = get_dir(os.path.join(DIRS['AIRFOIL_DIR'], _type, _name))
        with open(filepath, 'r') as f:
            pts = []
            for i in f:
                x, y = i.split(' ', 1)
                # Orients the airfoil properly since the motor is assumed to always spins in shaft extrude direction
                pts.append(Point(self.build_direction * float(y), self.build_direction * (float(x) - 0.5), 0))
        return pts

    @Attribute(private=True)
    def airfoil_unit_curve(self):
        """ Returns a `FittedCurve` through the points in `airfoil_data` with a chord-length of 1 SI meter """
        return FittedCurve(self.airfoil_data)

    @Attribute(private=True)
    def scaled_airfoil(self):
        """ Scales the `FittedCurve` defined by `airfoil_unit_curve` to be the same width as the motor diameter.
        This eliminates the risk of the propeller chord being larger than the fairing diameter """
        return ScaledCurve(curve_in=self.airfoil_unit_curve, reference_point=XOY, factor=self.motor.diameter)

    @Attribute(private=True)
    def build_direction(self):
        """ A switch case that determines which cirection the propeller assembly is facing (value 1 is for the positive
        `x` direction, value -1 is for 'x_' direction

        :rtype: int
        """
        return 1 if self.motor.integration is 'pusher' else -1

    @Attribute
    def fairing_length(self):
        # TODO add this into the knowledge base
        """ This fairing length provides a realistic proportion w.r.t the motor diameter. This ratio was determined
         through use of Adobe Photoshop along with reference images """
        return self.motor.diameter * 1.5

    @Attribute(private=True)
    def fairing_curve(self):
        """ The curve utilized to create the fairing. It would have been easier to revolve at one go around the x-axis
        but ParaPy does not allow this, thus that is why the curve is defined on the YZ plane """
        points = [Point(0, - (self.motor.diameter / 2.0), XOY.z),
                  Point(0, 0, self.fairing_length)]
        crv = InterpolatedCurve(points=points, tangents=[XOY.Vz, None])
        return crv

    @Attribute(private=True)
    def propeller_fairing_import(self):
        return Revolution(self.fairing_curve)

    @Attribute(private=True)
    def propeller_fairing_thrust_aligned(self):
        return RotatedShape(shape_in=self.propeller_fairing_import,
                            rotation_point=XOY,
                            vector=XOY.Vy, angle=radians(self.build_direction * 90))




if __name__ == '__main__':
    from parapy.gui import display

    obj = Propeller()
    display(obj)

