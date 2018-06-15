#!/usr/bin/env python
# -*- coding: utf-8 -*-


from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# TODO All necessary comments and documentation

# Other Modules
from user import *
from definitions import *
from directories import *

__all__ = ["Battery", "show_primitives"]


# TODO remove error message since it is already handled by a validator
# TODO Add power requirement

# A parameter for debugging, turns the visibility of miscellaneous parts ON/OFF
show_primitives = False  # type: bool


class Battery(Component):
    """  Battery.py is a file which automatically generates a battery part depending on parametric input of battery
    weight, or battery capacity. Also maximum allowed width and height of the battery can parameterized to enable the
    typical use-case of setting the width and height to be equal to that of the payload module to obtain a coherent
    inner fuselage structure.

    :return: ParaPy Geometry of the Battery(s)

    :param sizing_target: Accepts either 'capacity' or 'weight' and sizes based on required capacity on the former
    :type sizing_target: basestring

    :param sizing_value: The sizing value corresponding to the current target
    :type sizing_value: float

    :param max_width: Sets the maximum allowed width of the battery in SI meter [m]
    :type max_width: float

    :param max_height: Sets the maximum allowed height of the battery in SI meter [m]
    :type max_height: float
    """

    __initargs__ = ["sizing_target", "sizing_value"]
    __icon__ = os.path.join(DIRS['ICON_DIR'], 'batteryIII.png')

    sizing_target = Input('capacity', validator=val.OneOf(["capacity", "weight"]))
    # TODO link this to custom validator function

    sizing_value = Input(500, validator=val.Positive())
    max_width = Input(0.15, validator=val.Positive())
    max_height = Input(0.1, validator=val.Positive())  # Suggested to use a wider-battery, max_height = max_width / 2 for fuselage aerodynamics
    # position = Input(Position(Point(0, 0, 0)))
    label = Input('LiPo Battery')

    @Attribute
    def component_type(self):
        """ This attribute names the component 'battery' for Battery.

        :return: str
        :rtype: str
        """
        return 'battery'

    @Attribute
    def weight(self):
        """ Total mass of the battery

        :return: Mass in SI kilogram
        :rtype: float
        """
        return self.total_energy / self.constants['energy_density']

    @Attribute
    def center_of_gravity(self):
        """ Location of the battery center of gravity w.r.t the origin

        :return: Location Tuple in SI meter
        :rtype: Point
        """
        return self.internal_shape.cog

    @Attribute
    def constants(self):
        """ This attribute contains the battery constants

        :return: Dictionary With Battery Constants
        :rtype: dict
        """
        mydict = {
            'energy_density': 158.0,            # Wh/kg http://www.hardingenergy.com/lithium/
            'energy_volume': 220.0 * (10**3),   # Wh/m^3 http://www.hardingenergy.com/lithium/
            'minimum_volume': 0.000015,         # m^3
            'power_density': 430                # 430 W/kg http://www.hardingenergy.com/lithium/
        }
        return mydict

    @Attribute
    def total_energy(self):
        """ This attribute calculates the required battery total energy.

        :return: Battery Energy
        :rtype: float
        """
        if self.sizing_target == 'weight':
            e_bat = self.sizing_value * self.constants['energy_density']
            # Code to put a minimum weight to not break the code with div by zero
            if self.sizing_value < self.minimum_weight:
                raise ZeroDivisionError('%s [kg] results in a battery size that is too small to manufacture,'
                                        ' please change it to at least %s [kg]' % (self.sizing_value,
                                                                                   self.minimum_weight))
            else:
                return e_bat
        elif self.sizing_target == 'capacity':
            # Code to put a minimum size of capacity to not break the code with div by zero
            e_bat = self.sizing_value
            if self.sizing_value < self.minimum_capacity:
                raise ZeroDivisionError('%s [Wh] results in a battery size that is too small to manufacture,'
                                        ' please change it to at least %s [Wh]' % (self.sizing_value,
                                                                                   self.minimum_capacity))
            else:
                return e_bat

    @Attribute
    def volume(self):
        """ This attribute calculates the Battery Volume.

        :return: Battery Volume
        :rtype: float
        """
        return self.total_energy / self.constants['energy_volume']

    @Attribute
    def width(self):
        return self.max_width

    @Attribute
    def length(self):
        length = self.volume / self.battery_profile.area
        return length

    @Attribute
    def height(self):
        return self.max_height

    @Attribute(private=True)
    def minimum_capacity(self):
        return self.constants['minimum_volume'] * self.constants['energy_volume']

    @Attribute(private=True)
    def minimum_weight(self):
        return self.minimum_capacity / self.constants['energy_density']

    @Attribute(private=True)
    def radius(self):
        """Defines the radius in a way that prevents the battery_profile from self-destructing.

        :rtype: float
        """
        min_dimension = min(self.width, self.height)
        return min_dimension / 2.0

    @Attribute(private=True)
    def type_errormsg(self):
        error_str = "%s is not a valid weight_target. Valid inputs: 'weight', 'capacity'" % self.sizing_target
        raise TypeError(error_str)

    # --- Output Solid: -----------------------------------------------------------------------------------------------

    @Part
    def internal_shape(self):
        return TranslatedShape(shape_in=self.battery_import, displacement=Vector(self.position.x,
                                                                                 self.position.y,
                                                                                 (self.height / 2.0) + self.position.z),
                               color=MyColors.battery,
                               transparency=0.7)

    # --- Primitives: -------------------------------------------------------------------------------------------------

    @Part(in_tree=show_primitives)
    def rectangle(self):
        return RectangularFace(width=self.max_width, length=self.max_height,
                               position=YOZ)

    @Part(in_tree=show_primitives)
    def battery_profile(self):
        return FilletedFace(built_from=self.rectangle, radius=self.radius)

    @Part(in_tree=show_primitives)
    def battery_import(self):
        return ExtrudedSolid(face_in=self.battery_profile, distance=self.length, direction='x')


if __name__ == '__main__':
    from parapy.gui import display

    obj = Battery()
    display(obj, background_image=False)
