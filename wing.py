#  This class will create the wing geometry based on the required:
#  Wing Area (class I output), Aspect Ratio (class I in/output), taper ratio (assumed),
#  dihedral angle (assumed/given), wing twist angle (assumed/given) and airfoil.


from parapy.core import *
from parapy.geom import *
from math import *
from liftingsurface import LiftingSurface
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
    phi = Input(5.0)
    #  Above is the twist of the tip section with respect to the root section.
    airfoil_type = Input('cambered')  # MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SD7062')  # MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'
    offset = Input(None)


    @Attribute
    def S_req_half(self):
        # This calculation of the required wing area from the design point is HALVED to work consistently
        return self.MTOW/self.WS_pt

    @Part
    def wing_oop(self):
        return LiftingSurface(S_req = self.S_req,
                              AR = self.AR,
                              taper = self.taper,
                              dihedral = self.dihedral,
                              phi = self.phi,
                              airfoil_type = self.airfoil_type,
                              airfoil_choice = self.airfoil_choice,
                              offset = self.offset)



if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
