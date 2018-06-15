#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO Fix comments here
# TODO create csv 2 dict syntax document

""" my_csv2dict.py is a file containing the function read_csv which allows the user to quickly call a directory within
the project folder, also for convenience the packages os and sys are imported when directories.py is imported with
the * specifier. Finally the dictionary DIRS contains common directories so as to avoid multiple calls to get_dir.
Finally since the entries in DIRS are outputs of get_dir the inherent directory checking is also present. Thus an
invalid directory will raise errors"""

from directories import *
import io

__all__ = ["read_csv"]


def read_csv(product_name=str, directory=DIRS['EOIR_DATA_DIR']):
    """
    :param product_name:
    :param directory:
    :return:
    :rtype: dict
    """
    filename = ('%s.csv' % product_name)
    path = get_dir(os.path.join(directory, filename))
    with io.open(path, mode='r', encoding='utf-8-sig') as f:
        spec_dict = {}
        filtered = (line.replace("\n", '') for line in f)  # Removes \n from the created as a byproduct of encoding
        for line in filtered:
            field, value = line.split(',')
            if has_number(value) and value.find('"') == -1:
                if value.find('x') != -1:
                    if value.find('.') != -1:
                        value = [float(i) for i in value.split('x')]
                    else:
                        value = [int(i) for i in value.split('x')]
                else:
                    value = float(value)
            else:
                value = value.replace('"', '')
                if value.find('/') != -1:
                    value = [str(i) for i in value.split('/')]
                elif (value.lower()).find('true') != -1:
                    value = True
                elif (value.lower()).find('false') != -1:
                    value = False
                else:
                    value = str(value)
            spec_dict['%s' % str(field)] = value
        f.close()
        return spec_dict


def has_number(any_string):
    """ Returns True/False depending on if the input string contains any numerical characters (i.e 0, 1, 2, 3...9)

    :param any_string: A user-input, any valid string is accepted
    :type any_string: str

    :rtype: bool

    >>> has_number('I do not contain any numbers')
    False
    >>> has_number('Oh look what we have here: 2')
    True
    """
    return any(char.isdigit() for char in any_string)
