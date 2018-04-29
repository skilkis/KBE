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
__all__ = ["DesignInput"]

# These variables determine the default filename/sheetname(s)
filename = "userinput.xlsx"
sheetname = "export_ready_inputs"


# Function which returns all valid payloads in the directory /components/payload
def valid_payloads():
    """ Returns all valid payloads in the payloads directory

    :return: All valid entries for the field `payload_type`
    """
    payloads = os.listdir(os.path.join(DIRS['COMPONENTS_DIR'], 'payload'))
    return [str(i.split('.')[0]) for i in payloads if i.endswith('.py') and i != '__init__.py']


class DesignInput(Base):
    """ designinput.py aims to instantiate all primitive classes of a parametric UAV based on user-input of configuration type
        Other user-inputs cover global aircraft attributes and allow changes either through the use of the ParaPy GUI or
        through the use of the userinput.xlsx file.
    """

    __initargs__ = ["performance_goal",
                    "goal_value",
                    "weight_target",
                    "target_value",
                    "payload_type",
                    "configuration",
                    "handlaunch",
                    "portable"]

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'parameters.png') # TODO Change icon

    # TODO add validator functions here
    performance_goal = Input('endurance', validator=val.OneOf(['endurance', 'range']))
    goal_value = Input(1.0, validator=val.Positive())
    weight_target = Input('payload', validator=val.OneOf(['payload', 'mtow']))
    target_value = Input(0.25, validator=val.Positive())
    payload_type = Input('eoir', validator=val.OneOf(valid_payloads()))  #
    configuration = Input('conventional', validator=val.OneOf(['conventional', 'canard', 'flyingwing']))
    handlaunch = Input(True)
    portable = Input(True)
    user_input_file = Input([filename, sheetname])

    @Attribute
    def get_userinput(self):
        """ An attribute, that when evaluated, reads the input excel file present in the working directory and updates
        input values of the Aircraft class

        :return: Set of updated values which over-write the default ones in the ParameterGenerator class
        """

        # Load Excel file specified by filename and open Excel sheet specified by sheetname
        # NOTE FILE-CHECKING IS NOT NECESSARY DUE TO FILE-CHECKING IMPLEMENTATION IN get_dir
        excel_path = get_dir(os.path.join(DIRS['USER_DIR'], self.user_input_file[0]))
        wb = xlrd.open_workbook(excel_path)
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

        return 'Inputs have been overwritten from the supplied Excel File'



    # @Part
    # def wingpowerloading(self):
    #     return WingPowerLoading(pass_down="handlaunch", label="Wing & Thrust Loading")
    #
    # @Part
    # def weightestimator(self):
    #     return ClassOne(pass_down="weight_target, target_value", label="Weight Estimation")

    # @Attribute
    # def parameter_dict(self):
    #     dict = {'INPUTS': {},
    #             'OUTPUTS': {}}
    #
    #     dict['INPUTS']['performance_goal'] = self.performance_goal
    #     dict['INPUTS']['goal_value'] = self.performance_goal
    #     dict['INPUTS']['weight_target'] = self.performance_goal
    #     dict['INPUTS']['target_value'] = self.performance_goal
    #     dict['INPUTS']['payload_type'] = self.performance_goal
    #     dict['INPUTS']['payload_type'] = self.performance_goal
    #     dict['INPUTS']['payload_type'] = self.performance_goal
    #     return dict


if __name__ == '__main__':
    from parapy.gui import display

    obj = DesignInput(label="Design Parameters")
    display(obj)
