#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" directories.py is a file containing the function get_dir which allows the user to quickly call a directory within
the project folder, also for convenience the packages os and sys are imported when directories.py is imported with
the * specifier. Finally the dictionary DIRS contains common directories so as to avoid multiple calls to get_dir.
Finally since the entries in DIRS are outputs of get_dir the inherent directory checking is also present. Thus an
invalid directory will raise errors"""

import os
import sys

__all__ = ["get_dir", "DIRS", "os", "sys"]

# TODO Re-organize this to be a class structure if needed

# TODO Maybe re-write to use os.getcwd()


def is_frozen():
    """Is the current application code *frozen?*, i.e. build by a tool like
    py2exe.

    :rtype: bool

    # Copyright (C) 2016-2017 ParaPy Holding B.V.
    #
    # This file is subject to the terms and conditions defined in
    # the license agreement that you have received with this source code
    #
    # THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
    # KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    # IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
    # PURPOSE.

    """

    return hasattr(sys, "frozen")


def get_dir(folder_name=None):
    """get_dir returns the top-level directory of the package as an absolute path if :attr:`folder_name` is not
    specified [1]. If an exiting sub directory is specified as :type:`str` into the field :attr:`folder_name` then the
    return of get_dir will be absolute path to this sub directory [2]. Usage with file names inside a directory is also
    possible, see example below [3]

        :param folder_name: The name of a folder, file, or relative path
        :type folder_name: basestring

        :return: The absolute path to the root directory or, if specified, to a sub directory within the root
        :rtype: unicode

        [1] Obtaining Root Directory:

        >>> get_dir() # This will return the absolute path to root directory
        C:/Python27/KBE

        [2] Obtaining a Sub-Directory:

        >>> get_dir('icons') # This will return the absolute path to the subdirectory /icons
        C:/Python27/KBE\icons

        [3] Obtaining File-Directory:

        >>> get_dir('user/userinput.xlsx') # This will return the absolute path to the file userinput.xlsx
        C:/Python27/KBE\user\userinput.xlsx
    """

    encoding = sys.getfilesystemencoding()  # A variable that returns encoding of the user's machine

    if is_frozen():  # Checks if the user is running through an .exe or from Python, Refer to is_frozen definition above
        root = os.path.join(os.path.dirname(unicode(sys.executable, encoding)),
                            "KBE")
    else:
        root = os.path.dirname(unicode(__file__, encoding))

    if folder_name is None:  # Checks if user has specified a value for field :attr:`folder_name`
        return root
    else:
        if isinstance(folder_name, str) or isinstance(folder_name, unicode):  # Check if folder_name has valid input
            subdir = os.path.join(root, folder_name)
            if os.path.isdir(subdir) or os.path.isfile(subdir):  # Check to see if folder_name is a valid path or file
                return subdir
            else:
            # TODO Properly distinguish between folder and file type, a folder named '2.0' will be treated as a file
                if subdir.find('.') != -1:  # Error handling to see if user was looking for a file or directory
                    raise NameError('Specified file %s does not exist' % subdir)
                else:
                    raise NameError('Specified directory %s does not exist' % subdir)
        else:
            raise TypeError('Please enter a valid string or unicode path into folder_name, %s is %s'
                            % (folder_name, type(folder_name)))


DIRS = {'ICON_DIR': get_dir('icons'),
        'AIRFOIL_DIR': get_dir('airfoils'),
        'USER_DIR': get_dir('user'),
        'EOIR_DATA_DIR': get_dir(os.path.join('components', 'payload', 'database', 'eoir')),
        'MOTOR_DATA_DIR': get_dir(os.path.join('components', 'motor', 'database')),
        'PROPELLER_DATA_DIR': get_dir(os.path.join('components', 'propeller', 'database'))}

if __name__ == '__main__':
    print get_dir('user')
