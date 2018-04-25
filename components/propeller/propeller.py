#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# Required Class Definitions
from definitions import Component
from components.motor import *
from math import radians, ceil, floor
from user import MyColors
from directories import *
from prop_data_parser import *
from os import listdir
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


__author__ = "Şan Kılkış"
__all__ = ["Propeller"]

# Useful links for knowledge base:
# https://www.apcprop.com/technical-information/file-downloads/
# https://www.southampton.ac.uk/~jps7/Aircraft%20Design%20Resources/Sydney%20aerodynamics%20for%20students/propeller/prop1.html


class Propeller(Component):
    """ Always spins in motor direction

    """

    # TODO make sure the propeller code is structured nicely
    # TODO Make user selection of a propeller possible
    # Change label to chosen propeller

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    motor = Input(Motor(integration='puller'))
    design_speed = Input(15, validator=val.Range(0, 50))
    position = Input(Position(Point(0, 0, 0)))
    database_path = DIRS['PROPELLER_DATA_DIR']

    @Input
    def position(self):
        """ Automatically snaps the propeller to the specified motor from the input `motor`. If a user-input is provided
        the propeller will become detached. In this case please invalidate this slot """
        return self.motor.position

    @Attribute
    def propeller_diameter(self):
        return 0.5

    @Attribute
    def propeller_recommendation(self):
        return self.motor.specs['prop_recommendation']

    @Attribute
    def allowed_props(self):

        # Parsing the str in `self.prop_recommendation` to obtain diameter range
        diameter_range = [float(i.split('x')[0]) for i in self.propeller_recommendation]

        # Parsing the str in `self.prop_recommendation` to obtain pitch and type
        pitch_entries = [i.split('x')[1] for i in self.propeller_recommendation]
        pitch_range = []
        type_range = []
        for entry in pitch_entries:
            _local_type = ''
            _local_pitch = ''
            for i in entry:
                if i.isdigit() or i == '.':
                    _local_pitch = _local_pitch + i
                else:
                    _local_type = _local_type + i

            type_range.append(_local_type)
            try:
                pitch_range.append(float(_local_pitch))
            except ValueError:
                raise Exception('Could not convert recommended propeller pitch to a float')

        # All propeller files in the database
        prop_files = [i for i in listdir(self.database_path) if i.endswith('.txt')]

        allowed_props = []
        for prop in prop_files:
            f = open(os.path.join(self.database_path, prop))
            name = f.readline().split()[0]
            f.close()

            # Parsing the Header for Diameter
            diameter = float(name.split('x')[0])
            diameter_ok = False
            if len(diameter_range) > 1:
                if min(diameter_range) <= diameter <= max(diameter_range):
                    diameter_ok = True
            elif len(diameter_range) == 1:
                if floor(diameter_range[0]) <= diameter <= ceil(diameter_range[0]):
                    diameter_ok = True
            else:
                raise IndexError('Selected Motor Spec File is Corrupted')

            # Parsing the Header for Modifiers
            type_ok = False
            if len(type_range) > 1:
                if name.find(type_range[0]) != -1 or name.find(type_range[1]) != -1:
                    type_ok = True
            elif len(type_range) == 1:
                if name.find(type_range[0]) != -1:
                    type_ok = True

            # Selecting only the propellers which have the proper diameter and type
            if diameter_ok and type_ok:
                allowed_props.append({'Name': name, 'Filename': prop, 'Diameter': diameter})

                # , prop_files, diameter_range, pitch_range, type_range

        return allowed_props

    @Attribute
    def propeller_database(self):
        selected_prop_files = [i['Filename'] for i in self.allowed_props]
        prop_dict = {}
        max_eta = {}
        for i in selected_prop_files:
            _name = str(i)
            prop_dict[_name] = prop_data_parser(DIRS['PROPELLER_DATA_DIR'], i)
            max_eta[_name] = {'RPM': [],
                              'ETA': [],
                              'V': []}

            for RPM in sorted(prop_dict[_name].iterkeys(), key=lambda x: float(x)):  # Sorts the RPM Dictionary in order
                idx = np.argmax((prop_dict[_name][RPM]['Pe'][0]))  # Index where maximum efficiency (eta) occurs per RPM
                max_eta[i]['RPM'].extend([float(RPM)])  # Returns current RPM
                max_eta[i]['ETA'].extend([prop_dict[_name][RPM]['Pe'][0][idx]])  # Returns max eta
                max_eta[i]['V'].extend([0.44704 * prop_dict[_name][RPM]['V'][0][idx]])  # Returns velocity at max eta

            prop_dict[_name]['max_etas'] = max_eta[_name]  # Appends the max eta_dict to current prop_dict entry

        return prop_dict

    @Attribute
    def propeller_selector(self):
        _prop_names = []
        _design_etas = []

        for name in self.propeller_database:
            _prop_names.append(name)
            max_eta = self.propeller_database[name]['max_etas']  # Grabs dict of RPM, ETA, V for the current propeller
            velocities = max_eta['V']  # Velocity entries in the `max_eta` dict
            etas = max_eta['ETA']
            eta_vs_velocity = interp1d(velocities, etas)

            _design_etas.append(float(eta_vs_velocity(self.design_speed)))
            # error = [abs(v - self.design_speed) for v in velocities]
            # idx = error.index(min(error))
            # _design_etas.append(max_eta['ETA'][idx])

        idx_selected = _design_etas.index(max(_design_etas))
        selected_prop = _prop_names[idx_selected]
        selected_eta = _design_etas[idx_selected]

        return selected_prop, selected_eta





    @Attribute
    def efficiency_plotter(self):

        fig = plt.figure('PropellerEfficiency')
        # ax = fig.add_subplot(111)
        plt.style.use('ggplot')
        plt.title('Propeller Efficiency as a Function of True Airspeed')
        ax = fig.gca()

        for i in self.propeller_database:
            max_eta = self.propeller_database[i]['max_etas']
            plt.plot(max_eta['V'], max_eta['ETA'], label='%s' % i.split('.')[0])

        plt.axvline(self.design_speed, dashes=[6, 2], color='k', alpha=0.1,
                    label='Design Speed = %0.2f [m/s]' % self.design_speed)

        plt.axhline(self.propeller_selector[1], dashes=[6, 2], color='k', alpha=0.1)

        plt.scatter(self.design_speed, self.propeller_selector[1], marker='o', markerfacecolor='white',
                    markeredgecolor='black')

        ax.text(self.design_speed, self.propeller_selector[1],
                r'$\eta_{\mathrm{prop}}=%0.2f$' % self.propeller_selector[1])

        plt.xlabel(r'$V_{\mathrm{TAS}}$ [m/s]')
        plt.ylabel(r'$\eta_{\mathrm{prop}}$ [-]')
        plt.legend(loc='lower right')
        plt.ion()
        plt.show()
        return "Plot generated and saved"




        # PROPSELECT = [
        #     'PER3_10x4',
        #     'PER3_10x7',
        #     'PER3_10x10E',
        # ]
        #
        # MAXETA = {}
        # for i in PROPSELECT:
        #     MAXETA[i] = {
        #         'RPM': [],
        #         'ETA': [],
        #         'V': [],
        #     }
        #     for RPM in sorted(PROP[i].iterkeys(), key=lambda x: float(x)):
        #         idx4 = np.argmax(PROP[i][RPM]['Pe'][0])
        #         MAXETA[i]['RPM'].extend([float(RPM)])
        #         MAXETA[i]['ETA'].extend([PROP[i][RPM]['Pe'][0][idx4]])
        #         MAXETA[i]['V'].extend([0.44704 * PROP[i][RPM]['V'][0][idx4]])
        return prop_dict
    # @Attribute
    # def propeller_database(self):
    #
    #     return build_database()

    # --- Output Shapes: ----------------------------------------------------------------------------------------------

    @Part
    def propeller(self):
        return TranslatedShape(shape_in=self.propeller_builder,
                               displacement=Vector(self.position.x + self.build_direction * (self.fairing_length * (0.1
                                                                                             if self.motor.integration
                                                                                             == 'puller' else 0.15)),
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

    # --- Propeller Geometry Creation: --------------------------------------------------------------------------------

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
                # Orients the airfoil properly since the motor is assumed to always spins in flight direction
                pts.append(Point(-float(y), -(float(x) - 0.5), 0))
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
        """

        :return:
        """
        # TODO Comment here
        prop_top = LoftedSolid(profiles=self.airfoil_builder)
        prop_bottom = MirroredShape(shape_in=prop_top, reference_point=XOY, vector1=XOY.x_, vector2=XOY.y)
        propeller = Compound(built_from=[prop_top, prop_bottom])
        return propeller

    @Attribute(private=True)
    def text_label_position(self):
        """ Redefines the default text_label_position to be at the tip of the propeller blade """
        tip_airfoil_pos = self.propeller.bbox.corners[1]
        return tip_airfoil_pos

    # --- Primitives & Private Attributes: ----------------------------------------------------------------------------

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

