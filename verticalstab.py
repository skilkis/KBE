#  This script will estimate the required VT size and planform from statistical data.
#  In the future, this will become more detailed!

from parapy.core import *
from parapy.geom import *
from math import *
from liftingsurface import LiftingSurface




class VerticalStabilizer(GeomBase):


    S_req = Input(0.8)      # This is the required total wing area from the Class I estimations. TODO CONNECT TO MAIN/ WINGPWR LOADING
    MAC = Input(0.43)       #  This is the MAC of the wing. TODO CONNECT TO MAIN/LIFTING SURFACE
    lvc = Input(3.0)        #  This is the VT tail arm with respect to the CG. TODO CONNECT THIS WITH MAIN/GEOMETRY

# BELOW ARE ALL LIFTING SUFACE INPUTS TODO CONNECT TO MAIN

    AR_v = Input(1.4)       #  This is the VT aspect ratio. TODO CONNECT TO MAIN/LS
    taper_v = Input(0.35)    #  This is the assumed VT Taper Ratio. TODO CONNECT TO MAIN/LS
    dihedral_v = Input(0.0) #  This is the dihedral angle of the VT. TODO CONNECT TO MAIN/LS
    phi_v = Input(0.0)      #  This is the wing twist for the VT. TODO CONNECT TO MAIN/LS
    airfoil_type_v = Input('symmetric')     #  TODO CONNECT TO MAIN/LS
    airfoil_choice_v = Input('NACA0012')    #  TODO CONNECT TO MAIN/LS
    offset_v = Input(None)                  #  TODO CONNECT TO MAIN/LS
    #  TODO CONNECT THESE INPUTS TO MAIN/WINGPOWER LOADING AND MTOW!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    cog_radius = 0.01       #  This reduces the size of the COG sphere.
    semispan = Input(1.9)   # This is the wing semispan TODO connect to main
    @Attribute
    def V_v(self):
        #  This is a collection of VTP volume coefficients of agricultural aircraft.
        v_vset = [0.054, 0.036, 0.011, 0.022, 0.034, 0.024, 0.022, 0.033, 0.035, 0.035, 0.032]
        v_v_avg = sum(v_vset)/len(v_vset)
        print v_v_avg
        return v_v_avg

    @Attribute
    def S_v(self):
        return (self.V_v*self.S_req*self.semispan)/self.lvc



    @Part
    def vt_horiz(self):
        #  This is an instantiation of the lifting surface for ONE HT.
        #  Remember, LiftingSurface takes as input the wing area for ONE WING!!
        return LiftingSurface(S = self.S_v,
                              AR = self.AR_v,
                              taper = self.taper_v,
                              dihedral = self.dihedral_v,
                              phi = self.phi_v,
                              airfoil_type = self.airfoil_type_v,
                              airfoil_choice = self.airfoil_choice_v,
                              offset = self.offset_v,
                              cog_radius = self.cog_radius,
                              hidden = True)
    @Part
    def vt(self):
        return RotatedShape(shape_in = self.vt_horiz.final_wing,
                            rotation_point=Point(0, 0, 0),
                            vector = Vector(1,0,0),
                            angle = radians(90))

    @Part
    def cog_ct(self):
        return Sphere(radius=self.cog_radius,
                      position=self.vt.cog, color='red')

if __name__ == '__main__':
    from parapy.gui import display

    obj = VerticalStabilizer()
    display(obj)
