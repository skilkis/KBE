#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" directories.py is a file containing the function get_dir which allows the user to quickly call a directory within
the project folder, also for convenience the packages os and sys are imported when directories.py is imported with
the * specifier. Finally the dictionary DIRS contains common directories so as to avoid multiple calls to get_dir"""

import os
import sys

__all__ = ["get_dir", "DIRS", "os", "sys"]


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
    specified. If an exiting sub directory is specified as :type:`str` into the field :attr:`folder_name` then the
    return of get_dir will be absolute path to this sub directory.

    :type folder_name: str

    Usage:

    >>> get_dir() # This will return the absolute path to root directory
    C:/Python27/KBE

    Alternate Usage:

    >>> get_dir('icons') # This will return the absolute path to the subdirectory /icons
    C:/Python27/KBE/icons

    :rtype: str
    """

    # TODO Fix the directory addition operation to have a forward slash
    encoding = sys.getfilesystemencoding()

    if is_frozen():
        root = os.path.join(os.path.dirname(unicode(sys.executable, encoding)),
                            "KBE")
    else:
        root = os.path.dirname(unicode(__file__, encoding))

    if folder_name is None:
        return root
    else:
        if isinstance(folder_name, str):
            subdir = root + ('/%s' % folder_name)
            if os.path.isdir(subdir):
                return subdir
            else:
                raise NameError('Specified directory %s does not exist' % subdir)
        else:
                raise TypeError('%s is not :type: str')


DIRS = {'ICON_DIR': get_dir('icons')}

if __name__ == '__main__':
    print get_dir('icons')
