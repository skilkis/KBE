#  This script will generate a lifting surface for the KBE Drone app.
#  The three types of Wing Types that can be generated are Straight / Tapered / Swept and Elliptical wings.
#  In the future, we would like to add functionalities for multi-component wings

from parapy.core import *
from parapy.geom import *
from math import *


class LiftingSurface(GeomBase):
    #  Required inputs for each instantiation: Wing Area, Aspect Ratio, Taper Ratio, Sweep Angle airfoil type and choice
    #  or Wing Area, Aspect Ratio, airfoil type and choice and Elliptical shape

    S_req = Input(0.8)
    #  Above is the Required Wing Area from Wing Loading Diagram.
    taper = Input(0.5)
    #  Above is the Requested Taper Ratio.
    sweep = Input(20.0)
    #  Above is the Required Sweep Angle.
    elliptical = Input(False)
    #  Above Elliptical wing or not.
    airfoil_type = Input('cambered')  #MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SD7062')  #MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'





    @Attribute
    def symm_data(self):  #  Pull Symmetric 0012 Airfoil Data and store as symm_data
        with open('airfoils/symmetric/NACA0012.dat', 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x), float(y)))
        return pts

    @Attribute
    def camb_data(self):
        #  Pull Cambered SD7062 Airfoil Data and store as camb_data
        with open('airfoils/cambered/SD7062.dat', 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x), float(y)))
        return pts

    @Attribute
    def reflex_data(self):
        #  Pull reflexed Airfoil Data and store as reflex_data
        with open('airfoils/reflexed/E182.dat', 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x), float(y)))
        return pts

    @Part
    def symm_airfoil(self):
        #  Create Symmetric Airfoil
        return FittedCurve(points = self.symm_data)

    @Part
    def camb_airfoil(self):
        #  Create Cambered Airfoil
        return FittedCurve(points = self.camb_data)
    @Part
    def refl_airfoil(self):
        #  Create refleced Airfoil
        return FittedCurve(points = self.reflex_data)


    @Attribute
    def data(self):  #  Pull Symmetric 0012 Airfoil Data and store as symm_data
        with open('airfoils/%s/%s.dat' % (self.airfoil_type, self.airfoil_choice), 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x), float(y)))
        return pts



if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface(label="LiftingSurface")
    display(obj)