#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2017 ParaPy Holding B.V.
#
# This file is subject to the terms and conditions defined in
# the license agreement that you have received with this source code
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR
# PURPOSE.

"""Defines globals for ParaPy project."""

import os
import sys

__all__ = ["Directories", "os", "sys"]


def get_dir(subdir_name=None):
    """Return top-level directory of parapy source code.

    :rtype: str
    """

    # TODO Fix the directory addition operation to have a forward slash
    encoding = sys.getfilesystemencoding()
    root = os.path.dirname(unicode(__file__, encoding))
    if subdir_name is None:
        return root
    else:
        if isinstance(subdir_name, str):
            subdir = os.path.join(root, subdir_name)
            if os.path.isdir(subdir):
                return os.path.join(root, subdir_name)
            else:
                raise NameError('Specified directory %s' % subdir)
        else:
            raise TypeError('Please specify a sub-directory as :type: str')


class Directories(object):
    pass

#
# def icon_dir():


#: This will be the directory on your computer where this file resides,
#: but in case of executable building, it will be the parapy directory in the
#: same folder as where the .exe resides.
# PKG_DIR = root_dir()
# ICON_DIR = os.path.join(PKG_DIR, 'icons')
# FOIL_DIR = os.path.join(PKG_DIR, 'airfoils')
#
# DIR_LIST = [PKG_DIR,
#             ICON_DIR,
#             FOIL_DIR]
# #: support e-mail address
# SUPPORT_EMAIL = "sankilkis@msn.com"

if __name__ == '__main__':
    obj = Directories()
    print get_dir(2.0)
