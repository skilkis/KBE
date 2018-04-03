#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Aircraft.py aims to instantiate all primitive classes of a parametric UAV based on user-input of configuration type
    Other user-inputs cover global aircraft attributes and allow changes either through the use of the ParaPy GUI or
    through the use of the userinput.xlsx file.
"""

# Required ParaPy Modules
# from parapy.geom import *
# from parapy.core import *

# Useful package for checking working directory as well as the files inside this directory
import os

# Necessary package for importing Excel Files
import xlrd


# class Aircraft(Base):
#
#     endurance = Input(2.0)
#
#     @Attribute
#     def get_userinput(self):
#         """
#         An attribute, that when evaluated, reads the input excel file present in the working directory and updates input values
#         of the Aircraft class
#
#         :return: Array of updated values which over-write the default ones in the Aircraft class
#         """
#
#         # Assign spreadsheet filename to `file`
#         filename = 'userinput.xlsx'
#
#         # Load Excel file specified by filename
#         ex = pd.ExcelFile(filename)
#
#         # Load a sheet into a DataFrame by name: userinputs
#         userinputs = ex.parse('export_ready_inputs')
#
#         self.endurance = 0.5
#
#         print(userinputs.range)
#
#         return self.endurance
#
#
# if __name__ == '__main__':
#     from parapy.gui import display
#
#     obj = Aircraft(label="myAircraft")
#     display(obj)



# d = {}
# wb = xlrd.open_workbook('userinput.xlsx')
# sh = wb.sheet_by_name('export_ready_inputs')
# for i in range(138):
#     cell_value_class = sh.cell(i,2).value
#     cell_value_id = sh.cell(i,0).value
#     d[cell_value_class] = cell_value_id

wb = xlrd.open_workbook('userinput.xlsx')
ws = wb.sheet_by_name('export_ready_inputs')

a_range = [i[1] for i in ws._cell_values if i[0] == 'range'],
a_endurance = [i[1] for i in ws._cell_values if i[0] == 'endurance'],
pl_weight = [i[1] for i in ws._cell_values if i[0] == 'payload'],
pl_type = [i[1] for i in ws._cell_values if i[0] == 'payload_size'],
a_mtow = [i[1] for i in ws._cell_values if i[0] == 'mtow'],
a_configuration = [i[1] for i in ws._cell_values if i[0] == 'configuration'],
a_handlaunch = [i[1] for i in ws._cell_values if i[0] == 'handlaunch'],
a_portable = [i[1] for i in ws._cell_values if i[0] == 'portable']

userinputs=[range, endurance, weight_payload, weight_mtow, size_payload, configuration, handlaunch, portable]



# for col in range(ws.ncols):
#     column_names.append(str(ws.cell_value(0, col)))
# transform the workbook to a list of dictionaries
# data = []
# [item for item in column_names if ]
# for row in range(1, ws.nrows):
#     current_row = {}
#     for col in range(ws.ncols):
#         current_row[column_names[col]] = ws.cell_value(row, col)
#     data.append(current_row)
# print data

# x = {}
# x['name']=0.2


