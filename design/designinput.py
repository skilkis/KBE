#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Useful package for checking working directory as well as the files inside this directory

# Required ParaPy Modules
from parapy.core import *

# Necessary package for importing Excel Files
import xlrd

# Importing Necessary Classes
from directories import *
import webbrowser
import os
from definitions import error_window

__author__ = ["Şan Kılkış"]
__all__ = ["DesignInput", "valid_payloads"]

# These variables determine the default filename/sheetname(s)
filename = "userinput.xlsx"
sheetname = "export_ready_inputs"


# Function which returns all valid payloads in the directory /components/payload
def valid_payloads():
    """ Returns all valid payloads in the payloads directory for the field `payload_type`

    :rtype: list
    """
    payloads = os.listdir(os.path.join(DIRS['COMPONENTS_DIR'], 'payload'))
    return [str(i.split('.')[0]) for i in payloads if i.endswith('.py') and i != '__init__.py']


class DesignInput(Base):
    """ designinput.py aims to instantiate all primitive classes of a parametric UAV based on user-input of
    configuration type. Other user-inputs cover global aircraft attributes and allow changes either through the use of
    the ParaPy GUI or through the use of the userinput.xlsx file.

    :param performance_goal: The goal for which the UAV should be optimized (i.e. 'endurance or 'range')
    :type performance_goal: str

    :param goal_value: The value pertaining to the endurance goal in SI hour [h] or range in SI kilometer [km]
    :type goal_value: float

    :param weight_target: The target weight for which the Class I estimation should be run (i.e. 'payload' or 'mtow')
    :type weight_target: str

    :param target_value: The value pertaining to the target weight in SI kilogram [kg]
    :type target_value: float

    :param payload_type: Sets the payload type that will be instantiated in the UAV (currently only 'EOIR')
    :type payload_type: str

    :param configuration: Sets the base configuration for the UAV (currently only 'conventional' is supported)
    :type configuration: str

    :param handlaunch: Sets the design point of the UAV to be hand-launchable
    :type handlaunch: bool

    """

    __initargs__ = ["performance_goal",
                    "goal_value",
                    "weight_target",
                    "target_value",
                    "payload_type",
                    "configuration",
                    "handlaunch",
                    "portable"]

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'parameters.png')

    #: The goal for which the UAV should be optimized (i.e. 'endurance or 'range')
    performance_goal = Input('endurance', validator=val.OneOf(['endurance', 'range']))

    #: The value pertaining to the endurance goal in SI hour [h] or range in SI kilometer [km]
    goal_value = Input(2.0, validator=val.Positive())

    #: The target weight for which the Class I estimation should be run (i.e. 'payload' or 'mtow')
    weight_target = Input('payload', validator=val.OneOf(['payload', 'mtow']))

    #: The value pertaining to the target weight in SI kilogram [kg]
    target_value = Input(0.25, validator=val.Positive())

    #: Sets the payload type that will be instantiated in the UAV (currently only 'EOIR')
    payload_type = Input('eoir', validator=val.OneOf(valid_payloads()))  #

    #: Sets the base configuration for the UAV (currently only 'conventional' is supported)
    configuration = Input('conventional', validator=val.OneOf(['conventional']))

    #: Sets the design point of the UAV to be hand-launchable
    handlaunch = Input(True, validator=val.IsInstance(bool))

    @target_value.on_slot_change
    def weight_checker(self):
        """ Validates the user-input weight to make sure it is within the bounds of the project and the region with
        the highest confidence interval for Class I """
        if self.weight_target is 'payload':
            if self.target_value > 5.0:
                error_window('The provided payload target exceeds the scope of this project (only light UAVs < 20 '
                             '[kg] represent the design space')
        else:
            if self.target_value < 1.0 or self.target_value > 20.0:
                error_window('The provided MTOW exceeds the scope of this project (only light UAVs < 20 [kg] '
                             'represent the design space')
        return None

    @Attribute
    def get_userinput(self):
        """ An attribute, that when evaluated, reads the input excel file present in the working directory and updates
        input values of the Aircraft class

        :return: Set of updated values which over-write the default values defined in the ParaPy Input classes above
        """

        # Load Excel file specified by filename and open Excel sheet specified by sheetname
        # NOTE FILE-CHECKING IS NOT NECESSARY DUE TO FILE-CHECKING IMPLEMENTATION IN get_dir
        excel_path = get_dir(os.path.join(DIRS['USER_DIR'], filename))
        wb = xlrd.open_workbook(excel_path)
        ws = wb.sheet_by_name(sheetname)

        # Extracts relevant inputs from user excel-file in which the variable order does not matter
        # if correct variable names are not present no inputs will be replaced in the GUI

        self.set_slot_value('performance_goal',[str(i[1]) for i in ws._cell_values if i[0] == 'performance_goal'][0])
        self.set_slot_value('goal_value', [i[1] for i in ws._cell_values if i[0] == 'goal_value'][0])
        self.set_slot_value('target_value', [i[1] for i in ws._cell_values if i[0] == 'target_value'][0])
        self.set_slot_value('weight_target', [str(i[1]) for i in ws._cell_values if i[0] == 'weight_target'][0])
        self.set_slot_value('payload_type', [str(i[1]) for i in ws._cell_values if i[0] == 'payload_type'][0])
        self.set_slot_value('configuration', [str(i[1]) for i in ws._cell_values if i[0] == 'configuration'][0])
        self.set_slot_value('handlaunch', [True if str(i[1]) == 'True' else False for i in ws._cell_values
                                     if i[0] == 'handlaunch'][0])

        self.reset_slot('configuration')  # Necessary step to fire dependent evaluation

        return 'Inputs have been overwritten from the supplied Excel File'

    @Attribute
    def open_documentation(self):
        """ Allows the user to open the documentation from within the GUI for reference or help.

        :return: KBE App Documentation
        """
        webbrowser.open('file://' + os.path.join(DIRS['DOC_DIR'], 'index.html'))
        return 'Documentation Opened'


if __name__ == '__main__':
    from parapy.gui import display

    obj = DesignInput(label="Design Parameters")
    display(obj)
