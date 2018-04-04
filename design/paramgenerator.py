#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Required ParaPy Modules

# Useful package for checking working directory as well as the files inside this directory

# Necessary package for importing Excel Files
import xlrd

from parapy.core import*

# Importing Necessary Classes
from design.wingpowerloading import WingPowerLoading
from design.weightestimator import *

# These variables determine the default filename/sheetname(s)
filename = 'userinput.xlsx'
sheetname = 'export_ready_inputs'


class ParameterGenerator(Base):
    """ paramgenerator.py aims to instantiate all primitive classes of a parametric UAV based on user-input of configuration type
        Other user-inputs cover global aircraft attributes and allow changes either through the use of the ParaPy GUI or
        through the use of the userinput.xlsx file.
    """

    user_input_file = Input([filename, sheetname])
    performance_goal = Input('endurance')
    goal_value = Input(1.0)
    weight_target = Input('payload')
    target_value = Input(0.25)
    payload_type = Input('eoir')
    configuration = Input('conventional')
    handlaunch = Input(True)
    portable = Input(True)


    @Attribute
    def get_userinput(self):
        """ An attribute, that when evaluated, reads the input excel file present in the working directory and updates
        input values of the Aircraft class

        :return: Array of updated values which over-write the default ones in the Aircraft class
        """

        # Load Excel file specified by filename and open Excel sheet specified by sheetname
        wb = xlrd.open_workbook(self.user_input_file[0])
        ws = wb.sheet_by_name(self.user_input_file[1])

        # Extracts relevant inputs from user excel-file in which the variable order does not matter
        # if correct variable names are not present no inputs will be replaced in the GUI

        self.performance_goal = [str(i[1]) for i in ws._cell_values if i[0] == 'performance_goal'][0]
        self.goal_value = [i[1] for i in ws._cell_values if i[0] == 'goal_value'][0]
        self.weight_target = [str(i[1]) for i in ws._cell_values if i[0] == 'weight_target'][0]
        self.target_value = [i[1] for i in ws._cell_values if i[0] == 'target_value'][0]
        self.payload_type = [str(i[1]) for i in ws._cell_values if i[0] == 'payload_type'][0]
        self.configuration = [str(i[1]) for i in ws._cell_values if i[0] == 'configuration'][0]
        self.handlaunch = [True if str(i[1]) == 'True' else False for i in ws._cell_values if i[0] == 'handlaunch'][0]
        self.portable = [True if str(i[1]) == 'True' else False for i in ws._cell_values if i[0] == 'portable'][0]

        return (self.performance_goal, self.goal_value, self.weight_target, self.target_value, self.payload_type,
                self.configuration, self.handlaunch, self.portable)

    @Part
    def wingpowerloading(self):
        return WingPowerLoading(pass_down="handlaunch", label="Wing & Thrust Loading")

    @Part
    def weightestimator(self):
        return ClassOne(pass_down="weight_target, target_value", label="Weight Estimation")

if __name__ == '__main__':
    from parapy.gui import display

    obj = ParameterGenerator(label="design Parameters")
    display(obj)
