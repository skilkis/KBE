#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Propeller.py aims to parametrically create a propeller based on user input of diameter, as well as airfoil shape as
optional input
"""

from math import pi

from parapy.geom import *
from parapy.core import *


class Propeller(GeomBase):

    #: Propeller Diameter [cm]
    #: :type: float
    p_diameter = Input(14.0)


    @Attribute
    def pts(self):
        """ Extract airfoil coordinates from data file and create a list of
        points.

        :rtype: collections.Sequence[Point]
        """

        with open(self.airfoil, 'r') as datafile:
            points = []
            for line in datafile:
                x, y = line.split(' ', 1)
                points.append(
                    Point(float(x), float(y)))  # Convert the string to a number
                #  and make a Point of the coordiantes
        return points
