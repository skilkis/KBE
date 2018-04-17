from parapy.core import *
from parapy.geom import *


# class Test(GeomBase):
#
#     nose_pos = Input(-0.5)
#
#     @Attribute
#     def points(self):
#         return [Point(1, 0, 0), Point(0, 0, 0), Point(self.nose_pos, 0, 0), Point(0, 0.2, 0), Point(1, 0.4, 0)]
#
#     @Attribute
#     def tangents(self):
#         return [Vector(1, 0, 0), None, None, Vector(0, 1, 0), None, None, Vector(1, 0, 0)]
#
#     @Part
#     def test_curve(self):
#         return FittedCurve(points=self.points)
#
#
# if __name__ == '__main__':
#     from parapy.gui import display
#
#     obj=Test()
#     display(obj)

import ConfigParser

from directories import *

avl_dir = get_dir(os.path.join('avl', 'avl.exe'))



config = ConfigParser.RawConfigParser()

# When adding sections or items, add them in the reverse order of
# how you want them to be displayed in the actual file.
# In addition, please note that using RawConfigParser's and the raw
# mode of ConfigParser's respective set functions, you can assign
# non-string values to keys internally, but will receive an error
# when attempting to write to a file or when you get it in non-raw
# mode. SafeConfigParser does not allow such assignments to take place.
config.add_section('Section1')
config.set('Section1', 'an_int', '15')
config.set('Section1', 'a_bool', 'true')
config.set('Section1', 'a_float', '3.1415')
config.set('Section1', 'baz', 'fun')
config.set('Section1', 'bar', 'Python')
config.set('Section1', 'foo', '%(bar)s is %(baz)s!')
config.set('Section1', 'path', avl_dir)

# Writing our configuration file to 'example.cfg'
with open('example.cfg', 'wb') as configfile:
    config.write(configfile)

