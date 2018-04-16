from parapy.core import *
from parapy.geom import *


class Test(GeomBase):

    nose_pos = Input(-0.5)

    @Attribute
    def points(self):
        return [Point(1, 0, 0), Point(0, 0, 0), Point(self.nose_pos, 0, 0), Point(0, 0.2, 0), Point(1, 0.4, 0)]

    @Attribute
    def tangents(self):
        return [Vector(1, 0, 0), None, None, Vector(0, 1, 0), None, None, Vector(1, 0, 0)]

    @Part
    def test_curve(self):
        return FittedCurve(points=self.points)


if __name__ == '__main__':
    from parapy.gui import display

    obj=Test()
    display(obj)
