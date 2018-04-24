#  This script will generate the horizontal stabilizer using lifting surface with the required Sh
#  from the 'scissorplot.py' script.

from parapy.core import *
from parapy.geom import *
from liftingsurface import LiftingSurface
from scissorplot import ScissorPlot

class HorizontalStabilizer(GeomBase):

    S_req = Input(0.8)      #  This is the required total wing area from the Class I estimations. TODO CONNECT TO MAIN/ WINGPWR LOADING
    AR_h = Input(5.0)       #  This is the HT aspect ratio. TODO CONNECT TO MAIN/LS
    taper_h = Input(0.5)    #  This is the assumed HT Taper Ratio. TODO CONNECT TO MAIN/LS
    dihedral_h = Input(0.0) #  This is the dihedral angle of the HT. TODO CONNECT TO MAIN/LS
    phi_h = Input(0.0)      #  This is the wing twist for the HT. TODO CONNECT TO MAIN/LS
    airfoil_type_h = Input('symmetric')     #  TODO CONNECT TO MAIN/LS
    airfoil_choice_h = Input('NACA0012')    #  TODO CONNECT TO MAIN/LS
    offset_h = Input(None)                  #  TODO CONNECT TO MAIN/LS
    #  TODO CONNECT THESE INPUTS TO MAIN/WINGPOWER LOADING AND MTOW!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    @Attribute
    def scissor(self):
        #  Instantiation of scissor plot to obtain required tail to wing area ratio.
        #  TODO CONNECT THIS TO MAIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return ScissorPlot()

    @Attribute
    def shsreq(self):
        # This obtains the required tail to wing area ratio.
        print 'Required Sh/S is ', self.scissor.shs_req
        return self.scissor.shs_req

    @Attribute
    def sh(self):
        #  This calculates the required HT wing area from the scissor plots.
        return self.shsreq*self.S_req


    @Part
    def ht(self):
        #  This is an instantiation of the lifting surface for ONE HT.
        #  Remember, LiftingSurface takes as input the wing area for ONE WING!!
        return LiftingSurface(S = self.sh*0.5,
                              AR = self.AR_h,
                              taper = self.taper_h,
                              dihedral = self.dihedral_h,
                              phi = self.phi_h,
                              airfoil_type = self.airfoil_type_h,
                              airfoil_choice = self.airfoil_choice_h,
                              offset = self.offset_h)

    @Part
    def ht_mirror(self):
        return MirroredShape(shape_in = self.ht.final_wing,
                             reference_point = self.ht.position,
                             vector1 = Vector(1,0,0),
                             vector2 = Vector(0,0,1))



if __name__ == '__main__':
    from parapy.gui import display

    obj = HorizontalStabilizer()
    display(obj)
