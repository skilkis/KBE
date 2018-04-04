#this is a script to test the AVL run on ONE MAIN WING

from parapy.core import *
from parapy.geom import *
import parapy.lib.avl as avl

from liftingsurface import wing_surf

class AVLtest(GeomBase):

    @Part
    def my_wing(self):
        return LiftingSurface()

  #  @Part
  #  def section_root(self):
  #      return avl.AirfoilCurveSection(curve_in = self.)

    @Part
    def section_main_root(self):
        return avl.AirfoilCurveSection(curve_in=self.right_wing.edges[0])

