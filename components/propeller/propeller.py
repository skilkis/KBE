#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# Required Class Definitions
from definitions import Component
from components.motor import *

# Other Modules
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

    Propeller Nomenclature
    APC propellers are (by default) assumed to be of a standard type (sport) unless modified for specific
    characteristics or purpose. Sport propellers are intended for use with internal combustion engines.

    |
    |   `Types`:
    |   E   = Electric
    |   F   = Folding Blade (electric only)
    |   MR  = Multi-Rotor (electric only)
    |   SF  = Slow Fly (electric only)
    |   R   = Reversible ESC (electric only)
    |
    |   `Modifiers`:
    |   B4  = Bundle (2CW and 2 CCW propellers)
    |   W   = Wide (Chord)
    |   N   = Narrow (Chord)
    |   NN  = Very Narrow
    |   PN  = Pattern
    |   P   = Pusher (and reverse rotation for electrics)
    |   C   = Carbon
    |   ( ) = Reserved for Special Notes
    """

    # TODO (TBD) Make user selection of a propeller possible in the future
    # TODO (TBD) Import propeller weight from data-files (currently it is negligible and neglected)

    __initargs__ = ["motor", "design_speed"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'propeller.png')

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool # TODO rename this parameter

    motor = Input(Motor(integration='puller'), val=val.InstanceList("Motor"))
    design_speed = Input(15, validator=val.Range(0, 50))
    # position = Input(Position(Point(0, 0, 0)))
    database_path = DIRS['PROPELLER_DATA_DIR']

    @Input
    def position(self):
        """ Automatically snaps the propeller to the specified motor from the input `motor`. If a user-input is provided
        the propeller will become detached. In this case please invalidate this slot """
        return self.motor.position

    @Attribute
    def propeller_diameter(self):
        """ Fetches the string value of the selected propeller from `propeller_selector` and cross-references it
        with the 'Filename" field of each entry in the attribute `allowed_props` to obtain the proper diameter. This is
        done to not have to parse the propeller name multiple times.

        :return: Diameter of the propeller blades in SI meter
        :rtype: float
        """
        diameter_in = [i['Diameter'] for i in self.allowed_props if i['Filename'] == self.propeller_selector[0]][0]
        diameter = diameter_in * 0.0254
        return diameter

    @Attribute
    def component_type(self):
        return 'payload'

    @Attribute
    def weight(self):
        """ No reliable source of information could be obtained for propeller weight, thus it is neglected """
        return 0

    @Attribute
    def center_of_gravity(self):
        return self.propeller.bbox.center

    @Attribute
    def efficiency(self):
        """ Fetches the efficiency of the selected propeller at the `design_speed` """
        return self.propeller_selector[1]

    @Attribute
    def propeller_recommendation(self):
        """ Grabs the `prop_recommendation` field from the dictionary `motor.specs` for easy reference in the GUI

        :rtype: str
        """
        return self.motor.specs['prop_recommendation']

    @Attribute(private=True)
    def allowed_props(self):
        """ An attribute which parses the string array provided by the attribute `propeller_recommendation` and uses
        this information to create a list containing all propellers that fit this recommendation. Typically, the string
        list provided by `propeller_recommendation` specifies a minimum and maximum value of diameter. However, there
        are some cases where the motor only provides a single value. The selection algorithm can cope with both of these
        cases. Furthermore, to preserve lazy-evaluation as much as possible and increase performance, only the header of
        each propeller data file is read to verify if the propeller is compliant in diameter and type.

        :return: List of allowed propeller dictionaries with their corresponding `Name`, `Filename`, and `Diameter`
        :rtype: List
        """

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

        return allowed_props

    @Attribute
    def propeller_database(self):
        """ Gathers all relevant data for the propellers listed in the attribute `allowed_props` and builds a dict to
        neatly store the data.

        :return: Dictionary containing the arrays `RPM`, `ETA`, `V` for each propeller in the attribute `allowed_props`
        :rtype: Dict
        """
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
        """ The main selection algorithm which iterates through all propellers in the attribute `propeller_database`.
        For each propeller the algorithm logs the maximum propulsive efficiency at each RPM as well as the true-airspeed
        (TAS) of this local maxima. A linear-spline is fitted through the data and the efficiency at the input
        `design_speed` is evaluated. These values are appended to the private list `_design_etas` and the propeller with
        the maximum efficiency at the `design_speed` is selected from this list at the end of the iteration. If no data
        can be obtained at the `design_speed` a ValueError is raised warning the user.

        :returns: Filename of the selected prop [0], propeller efficiency at the user-input `design_speed` [1],
                  Fitted linear spline of efficiency vs true airspeed [2]
        :rtype: list
        """
        _prop_names = []
        _design_etas = []
        _eta_splines = []
        _spline_bounds = []

        _data_found = False  # Switch case to determine if data-points exist for the chosen design point
        for name in self.propeller_database:
            _prop_names.append(name)
            max_eta = self.propeller_database[name]['max_etas']  # Grabs dict of RPM, ETA, V for the current propeller
            velocities = max_eta['V']  # Velocity entries in the `max_eta` dict
            etas = max_eta['ETA']

            # Interpolates the data with a linear spline and appends to _eta_splines
            eta_vs_velocity = interp1d(velocities, etas, kind='slinear', fill_value=[0])
            _eta_splines.append(eta_vs_velocity)
            _spline_bounds.append([min(velocities), max(velocities)])

            # Returns the efficiency if data-points exist for `self.design_speed`
            if min(velocities) <= self.design_speed <= max(velocities):
                _design_etas.append(float(eta_vs_velocity(self.design_speed)))
                _data_found = True
            else:
                _design_etas.append(0)

        if _data_found:
            idx_selected = _design_etas.index(max(_design_etas))
            selected_prop = _prop_names[idx_selected]
            selected_eta = _design_etas[idx_selected]
            selected_curve = _eta_splines[idx_selected]
            curve_bounds = _spline_bounds[idx_selected]
        else:
            raise ValueError('No propeller data could be found for the design speed of %0.2f' % self.design_speed)

        return selected_prop, selected_eta, selected_curve, curve_bounds

    @Attribute
    def efficiency_plotter(self):
        """ Plots all efficiencies of the gathered propeller data as a function of true airspeed for the user to be able
        to visualize how the efficiency changes. This allows for more logical choices when it comes to changing the
        design if necessary.

        :return: Plot of Propeller Efficiency as a function of True Airspeed
        :rtype: str
        """
        fig = plt.figure('PropellerEfficiency')
        plt.style.use('ggplot')
        plt.title('Propeller Efficiency as a Function of True Airspeed')

        for i in self.propeller_database:
            max_eta = self.propeller_database[i]['max_etas']
            plt.plot(max_eta['V'],  # x_data
                     max_eta['ETA'],  # y_data
                     label='%s' % i.split('.')[0])  # legend label

        plt.axvline(self.design_speed,
                    dashes=[6, 2],
                    color='k',
                    alpha=0.1)

        plt.axhline(self.propeller_selector[1], dashes=[6, 2], color='k', alpha=0.1)

        plt.plot(self.design_speed, self.propeller_selector[1],
                 marker='o',
                 markerfacecolor='white',
                 markeredgecolor='black', markeredgewidth=1,
                 linewidth=0,
                 label=r'Design Point : '
                       r'$\left(V_{\mathrm{TAS}}=%0.1f'
                       r',\eta_{\mathrm{prop}}=%0.2f\right)$' % (self.design_speed, self.propeller_selector[1]))

        plt.xlabel(r'$V_{\mathrm{TAS}}$ [m/s]')
        plt.ylabel(r'$\eta_{\mathrm{prop}}$ [-]')
        plt.legend(loc='lower right')
        plt.ion()
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')
        return "Plot generated and saved"

    @Attribute
    def label(self):
        return [i['Name'] for i in self.allowed_props if i['Filename'] == self.propeller_selector[0]][0]

    # --- Output Shapes: ----------------------------------------------------------------------------------------------

    @Part
    def propeller(self):
        """ The propeller geometry which is visible in the GUI. The attributes used to construct it are below """
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
        """ The propeller fairing which is visible in the GUI. The attributes used to construct it are below """
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
        root_chord = self.motor.diameter * 0.25  # Scaled off of the motor to avoid too large of a chord
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
        """ Instantiates the airfoils used to create the LoftedSolid in attribute `propeller_builder' """
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
        """ The un-translated version of the main part `propeller` constructed from a Compound between a LoftedSolid
        and its MirroredShape

        :return: A scale representation of the propeller geometry at the origin
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
        """ A switch case that determines which direction the propeller assembly is facing (value 1 is for the positive
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

