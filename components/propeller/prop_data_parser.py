from directories import *

__author__ = ["Diego de Buysscher"]
__all__ = ["prop_data_parser"]


def prop_data_parser(database_path, filename):
    """ This data parser was written last year by my colleague Diego for a DSE project, written permission was obtained
    from him to use this code to interpret the datafiles from the APC prop website:

    https://www.apcprop.com/technical-information/performance-data/

    This code has been modified from its original form to work to preserve the lazy evaluation of ParaPy

    :return: A dictionary of all propeller performance parameters
    """

    prop_data = {}
    f = open(os.path.join(database_path, filename))
    lines = f.readlines()
    f.close()

    n_lines = 0
    specs_dict = {}
    new_entry = False
    registering = False
    for line in lines:
        line = line.replace(4*' ', '\t').replace('\t\t', '\t').replace('\r', '').replace('\n', '').replace(' ', '')
        split_line = line.split('\t')

        split_line = [x for x in split_line if x != '']

        if len(split_line) > 0:

            n_lines += 1
            if 'PROPRPM=' in split_line:
                if len(prop_data) > 0 or len(specs_dict) > 0:
                    prop_data.update({rpm_entry: specs_dict})
                    specs_dict = {}

                rpm_entry = split_line[1]
                new_entry = True
                registering = True
                n_lines = 0

            elif n_lines < 3 and new_entry:
                if n_lines == 1:
                    specs_entries = split_line

                elif n_lines == 2:
                    j = 0
                    for i in range(len(specs_entries)):
                        entry = specs_entries[i]
                        if entry not in ['Pe', 'Ct', 'Cp']:
                            unit = split_line[j]
                            j += 1

                        else:
                            unit = None
                        specs_dict.update({entry:[[], unit]})
                    new_entry = False

            elif registering:
                # print split_line
                for k in range(len(split_line)):
                    entry = specs_entries[k]
                    try:
                        value = float(split_line[k])
                    except ValueError:
                        value = split_line[k]
                    specs_dict[entry][0].append(value)

            else:
                # print split_line
                registering = False

    return prop_data


obj = prop_data_parser(DIRS['PROPELLER_DATA_DIR'], 'PER3_4x4E-3.txt')
