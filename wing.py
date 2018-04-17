#!C:\Python27
#  This class will create the wing geometry based on the required:
#  Wing Area (class I output), Aspect Ratio (class I in/output), taper ratio (assumed),
#  dihedral angle (assumed/given), wing twist angle (assumed/given) and airfoil.


from parapy.core import *
from parapy.geom import *
from math import *
from liftingsurface import LiftingSurface
from avlwrapper import Geometry, Surface, Section, Point, Spacing, Session, Case, Parameter, NacaAirfoil


#from design.wingpowerloading import designpoint['wing_loading']
#from design.weightestimator import mtow



class Wing(GeomBase):
    WS_pt = Input(50.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    MTOW = Input(25.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    AR = Input(9.0)  # MUST GET THIS FROM CLASS i!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    taper = Input(0.6)
    #  Above is the User Requested Taper Ratio.
    dihedral = Input(5.0)
    #  Above is the User Required Dihedral Angle.
    twist = Input(5.0)
    #  Above is the twist of the tip section with respect to the root section.
    airfoil_type = Input('cambered')  # MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SD7062')  # MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'
    offset = Input(None)

    #  TODO Fix CH10 bug?



    @Attribute
    def S_req(self):
        # This calculation of the required wing area from the design point.
        return (self.MTOW/self.WS_pt)

    @Part
    #  This generates the wing. The area is halved because lifting surface generates one wing of that surface area.
    def wing_test(self):
        return LiftingSurface(S = self.S_req*0.5,
                              AR = self.AR,
                              taper = self.taper,
                              dihedral = self.dihedral,
                              phi = self.twist,
                              airfoil_type = self.airfoil_type,
                              airfoil_choice = self.airfoil_choice,
                              offset = self.offset)
    @Part
    def root_section(self):
        return Section(leading_edge_point = Point(0, 0, 0),
                           chord=1.0,
                           airfoil=NacaAirfoil(naca='2414'))


  #  @Part
  #  def wing_surface(self):
  #      wing_surface = Surface(name="AVLWing",
  #                             n_chordwise=8,
  #                             chord_spacing=Spacing.cosine,
  #                             n_spanwise=12,
  #                             span_spacing=Spacing.cosine,
  #                             y_duplicate=0.0,
  #                             sections=[self.wing_test.final_wing.faces[1], self.wing_test.final_wing.faces[2]])
  #      return wing_surface




if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
