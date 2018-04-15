from math import *

from parapy.core import *
from parapy.geom import *

from parapy.geom import FilledSurface, FittedCurve, LineSegment, Point
pts1 = [Point(0, 0, 0), Point(1, 0, 1), Point(2, 0, 0)]
crv1 = FittedCurve(points=pts1)
pts2 = [Point(0, 1, 0), Point(1, 1, 1), Point(2, 1, 0)]
crv2 = FittedCurve(points=pts2)
rail1 = LineSegment(start=crv1.start, end=crv2.start)
rail2 = LineSegment(start=crv1.end, end=crv2.end)
obj = FilledSurface(curves=[rail1, rail2, crv1, crv2])

if __name__ == '__main__':
    from parapy.gui import display

    display(obj)
