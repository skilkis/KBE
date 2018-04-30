#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Useful package for checking working directory as well as the files inside this directory

# Required ParaPy Modules
from parapy.core import *

# Necessary package for importing Excel Files
import xlrd

# Importing Necessary Classes
from wingpowerloading import WingPowerLoading
from weightestimator import *
from directories import *

__author__ = ["Şan Kılkış"]
__all__ = ["ParameterGenerator"]

# These variables determine the default filename/sheetname(s)
filename = "userinput.xlsx"
sheetname = "export_ready_inputs"


# Function which returns all valid payloads in the directory /components/payload

class ParameterGenerator(Base):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'parameters.png')

    @Part
    def wingpowerloading(self):
        return WingPowerLoading()

    @Part
    def weightestimator(self):
        return ClassOne()

    # TODO Make this the gathering point of all variables