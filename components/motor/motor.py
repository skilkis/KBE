#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules
from parapy.geom import *
from parapy.core import *

from definitions import *

# Required Modules
from my_csv2dict import *
from directories import *
from os import listdir
from user import MyColors

__all__ = ["Motor"]


class Motor(Component):

    __initargs__ = ["target_power", "motor_name", "position"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'motor.png')

    # A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
    __show_primitives = False  # type: bool

    target_power = Input(100.0, validator=val.Positive())
    motor_name = Input('Not Specified')
    integration = Input('pusher', validator=val.OneOf(["pusher", "puller"]))
    position = Input(Position(Point(0, 0, 0)))
    database_path = Input(DIRS['MOTOR_DATA_DIR'])

    @Input
    def label(self):
        """Overwrites the inherited slot `label' with the chosen motor_name"""
        return self.specs['name']

    @Attribute
    def specs(self):
        if self.motor_name == 'Not Specified':
            selected_motor_specs = [num[1] for num in self.motor_database if num[0] == self.motor_selector][0]
            selected_motor_specs['name'] = self.motor_selector
        else:
            selected_motor_specs = read_csv(self.motor_name, DIRS['EOIR_DATA_DIR'])
            selected_motor_specs['name'] = self.motor_name
        return selected_motor_specs

    @Attribute
    def motor_database(self):
        database_path = DIRS['MOTOR_DATA_DIR']
        motor_names = [str(i.split('.')[0]) for i in listdir(database_path) if i.endswith('csv')]
        motors = [[name, read_csv(name, self.database_path)] for name in motor_names]
        return motors

    @Attribute
    def motor_selector(self):
        """ An attribute which selects a motor based on input of target power. A tolerance of 10% is added to this value
        in order to allow the algorithm to select a slightly under-powered motor and utilize it's burst power to meet
        the requirement. This can be set to zero in the code if desired with the variable `tolerance` below. Finally,
        a condition is added to select the lightest motor from the list of available motors.

        :return: Name of the selected motor
        :rtype: str
        """
        tolerance = 0.1
        motor_list = sorted([[name[0], name[1]['constant_power'], name[1]['weight']]
                             for name in self.motor_database],
                            key=lambda f: float(f[1]))
        allowed_motors = [[i[0], abs(i[1] - self.target_power), i[2]]
                          for i in motor_list if i[1] >= self.target_power * (1-tolerance)]
        if len(allowed_motors) == 0:
            raise ValueError('The target power of %.2f [W] is too large to find a suitable motor'
                             % self.target_power)
        else:
            error_list = [i[1] for i in allowed_motors]
            weight_list = [i[2] for i in allowed_motors]
            idx1 = error_list.index(min(error_list))  # Index of minimum error (provided power - desired)
            idx2 = weight_list.index(min(weight_list))  # Index of minimum weight
            if idx1 != idx2:  # Code to prefer minimum error over minimum weight
                selected_index = idx1
            else:
                selected_index = idx2
            selected_motor = allowed_motors[selected_index][0]
        return selected_motor

    @Attribute
    def weight(self):
        """ Total mass of the motor

        :return: Mass in SI kilogram
        :rtype: float
        """
        return self.specs['weight'] / 1000.0

    @Attribute
    def diameter(self):
        """ The outer diameter of the motor body

        :return: Diameter in SI meter
        :rtype: float
        """
        return self.specs['diameter'] / 1000.0

    @Attribute
    def length(self):
        """ The length of the motor body

        :rtype: Length in SI meter
        :rtype: float
        """
        return self.specs['length'] / 1000.0

    @Attribute
    def shaft_diameter(self):
        """ The outer diameter of the motor shaft

        :return: Diameter in SI meter
        :rtype: float
        """
        return self.specs['shaft_diameter'] / 1000.

    @Attribute
    def shaft_length(self):
        """ The protruding length of the motor shaft

        :return: Length in SI meter
        :rtype: float
        """
        return 0.3 * self.length

    @Attribute
    def power(self):
        """ Pulls the corresponding `field_names` `constant_power` and `burst_power` from the dictionary `specs`.
        This is done to minimize the amount of characters necessary to call these parameters. Index 0 of the list is
        `constant_power` and Index 1 is `burst_power`.

        :rtype: list
        """
        return [self.specs['constant_power'], self.specs['burst_power']]

    @Attribute
    def efficiency(self):
        """ Assumed motor efficiency is at the higher-end of typical values and equal to 90%

        http://www.radiocontrolinfo.com/brushless-motor-efficiency/ """
        return 0.9

    @Attribute
    def extrude_direction(self):
        """ Defines the extrude direction as a `vector` of the motor-body as well as the shaft. To access this dict
        use the `field_names`: `body` and `shaft` respectively.

        :rtype: dict
        """
        if self.integration == 'pusher':
            body = self.position.Vx_
            shaft = self.position.Vx
        else:
            body = self.position.Vx
            shaft = self.position.Vx_
        return {'body': body, 'shaft': shaft}

    @Attribute
    def chamfer_edges(self):
        """ Rejects the line edge which will only have 2 sample_points

        :return: Edge table of circular edges of the motor-body
        """
        edges = [i for i in self.motor_body_import.edges if len(i.sample_points) > 2]
        return edges[0], edges[1]

    # --- Output Parts: -----------------------------------------------------------------------------------------------

    @Part
    def internal_shape(self):
        """ Chamfers the edges of `motor_body_import` to better resemble the shape of RimFire engines """
        return ChamferedSolid(built_from=self.motor_body_import,
                              distance=self.shaft_diameter,
                              edge_table=self.chamfer_edges,  # Flagged as an error but works fine
                              color=MyColors.gold)

    @Part
    def shaft(self):
        """ Creates the motor shaft as an `ExtrudedSolid` in the direction specified in `extrude_direction` """
        return ExtrudedSolid(island=self.shaft_circle,
                             distance=self.shaft_length,
                             direction=self.extrude_direction['shaft'],
                             color=MyColors.dark_grey)

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=__show_primitives)
    def motor_circle(self):
        """ Creates the circle that is used to extrude and form the motor body """
        return Circle(position=translate(YOZ, 'x', self.position.y, 'y', self.position.z, 'z', self.position.x),
                      radius=self.diameter / 2.0)

    @Part(in_tree=__show_primitives)
    def shaft_circle(self):
        """ Creates the circle that is used to extrude and form the motor shaft """
        return Circle(position=translate(YOZ, 'x', self.position.y, 'y', self.position.z, 'z', self.position.x),
                      radius=self.shaft_diameter / 2.0)

    @Part(in_tree=__show_primitives)
    def motor_body_import(self):
        """ Creates the motor body as an `ExtrudedSolid` in the direction specified in `extrude_direction` """
        return ExtrudedSolid(island=self.motor_circle,
                             distance=self.length,
                             direction=self.extrude_direction['body'])


if __name__ == '__main__':
    from parapy.gui import display

    obj = Motor()
    display(obj)

