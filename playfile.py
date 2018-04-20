# import ConfigParser
#
# from directories import *
#
# avl_dir = get_dir(os.path.join('avl', 'avl.exe'))
#
#
#
# config = ConfigParser.RawConfigParser()
#
# # When adding sections or items, add them in the reverse order of
# # how you want them to be displayed in the actual file.
# # In addition, please note that using RawConfigParser's and the raw
# # mode of ConfigParser's respective set functions, you can assign
# # non-string values to keys internally, but will receive an error
# # when attempting to write to a file or when you get it in non-raw
# # mode. SafeConfigParser does not allow such assignments to take place.
# config.add_section('Section1')
# config.set('Section1', 'an_int', '15')
# config.set('Section1', 'a_bool', 'true')
# config.set('Section1', 'a_float', '3.1415')
# config.set('Section1', 'baz', 'fun')
# config.set('Section1', 'bar', 'Python')
# config.set('Section1', 'foo', '%(bar)s is %(baz)s!')
# config.set('Section1', 'path', avl_dir)
#
# # Writing our configuration file to 'example.cfg'
# with open('example.cfg', 'wb') as configfile:
#     config.write(configfile)

nose_length = 2.0
N_sections = 10
from math import sin, pi
import numpy as np

test = [nose_length*sin((i*pi)/(N_sections*2.0)) for i in range(0, N_sections-1)]

x = '"7.5x10"'

x=x.replace('"', '')

from parapy.core import *
from parapy.geom import Point

x = (float(0), float(1), float(1))
for i in x:
    i = i + 0.05


