#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parapy.geom import *  # \
from parapy.core import *  # / Required ParaPy Modules

# Required Class Definitions
from definitions import Component
from components.motor import *


__author__ = "Şan Kılkış"


class Propeller(Component):

    motor = Input(Motor())

    @Part
    def hub(self):
        return Box(1, 1, 1)