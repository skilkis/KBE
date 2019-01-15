#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

__all__ = ["MyColors", "rgb"]

#  TODO explanation/ docuemtation???


def rgb(color):
    """ Converts a RGB value from 0-255 to a value from 0-1 """
    r = color[0] / 255.0
    g = color[1] / 255.0
    b = color[2] / 255.0
    return r, g, b


class MyColors(object):

    # Color Definitions

    light_grey = (128, 128, 128)
    deep_red = (128, 0, 0)
    deep_green = (0, 128, 0)
    dark_grey = (69, 69, 69)
    gold = (204, 155, 31)
    chill_white = (247, 247, 247)
    cool_blue = (128, 255, 255)
    deep_purple = (126, 59, 126)

    # <<<<<<< EDIT HERE >>>>>>>
    battery = deep_purple
    skin_color = light_grey



