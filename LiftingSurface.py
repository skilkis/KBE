#  This script will generate a lifting surface for the KBE Drone app.
#  The three types of Wing Types that can be generated are Straight / Tapered / Swept and Elliptical wings.
#  In the future, we would like to add functionalities for multi-component wings

from parapy.core import *
from parapy.geom import *
from math import *


class LiftingSurface(GeomBase):

    #  Required inputs for each instantiation: Wing Area, Aspect Ratio, Taper Ratio, Sweep Angle or...
    #  Wing Area, Aspect Ratio and Elliptical shape

    S_req = Input(0.8)  #  This is the Required Wing Area from Wing Loading Diagram.
    taper = Input(0.5)  #  This is the Requested Taper Ratio.
    sweep = Input(20.0)  #  This is the Required Sweep Angle.
    elliptical = Input(False)  #  Requested Elliptical wing or not.

    #  Cambered Symmetric and reflexed airfoil database is in folder 'Airfoils'


    @Attribute
    def data(self):
        with open('Airfoils/Symmetric/NACA0008.dat', 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x), float(y)))
        return pts


    @Part
    def airfoil(self):
        return FittedCurve(points = self.data)


if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface(label="LiftingSurface")
    display(obj)