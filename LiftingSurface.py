#  This script will generate a lifting surface for the KBE Drone app.
#  The three types of Wing Types that can be generated are Straight / Tapered / Swept and Elliptical wings.
#  In the future, we would like to add functionalities for multi-component wings

from parapy.core import *
from parapy.geom import *
from math import *


class LiftingSurface(GeomBase):

    #  Required inputs for each instantiation: Wing Area, Taper Ratio, Sweep Angle or Wing area and Elliptical shape

    S_req = Input(0.1)  #  This is the Required Wing Area from Wing Loading Diagram.
    taper = Input(0.5)  #  This is the Requested Taper Ratio.
    sweep = Input(20.0)  #  This is the Required Sweep Angle.
    elliptical = Input(False)  #  Requested Elliptical wing or not.



