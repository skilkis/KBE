#  This script will estimate the required VT size and planform from statistical data.
#  In the future, this will become more detailed!

from parapy.core import *
from parapy.geom import *
from math import *
from old.liftingsurface import LiftingSurface
from definitions import *



class VerticalStabilizer(Component):


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
    vtfuse_width_factor = Input(0.1)  # This is an assumed factor relating the part of the HT covered by fuse to semispan
    WF_VT = Input(0.1)  # This is the weight fraction of the HT.
    MTOW = Input(25.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!


    @Attribute
    def weight(self):
        return self.WF_VT * self.MTOW

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
        #  This rotates the VT over a right angle to the correct orientation WRT the aircraft reference system.
        return RotatedShape(shape_in = self.vt_horiz.final_wing,
                            rotation_point=Point(0, 0, 0),
                            vector = Vector(1,0,0),
                            angle = radians(90))

    @Attribute
    def vtwing_cut_loc(self):
        #  This calculates the spanwise distance of the cut, inside of which, the wing is inside the fuselage.
        return self.vt_horiz.semispan*self.vtfuse_width_factor

    @Part
    def vtright_cut_plane(self):
        #  This makes a plane at the right wing span location where the fuselage is to end.
        return Plane(reference= translate(self.vt.position,
                                          'y', self.vtwing_cut_loc),
                     normal=Vector(0, 0, 1))

    @Attribute
    def get_vtfuse_bounds(self):
        #  This attribute is obtaining (the dimensions of) a bounded box at a fuselaage width factor of the semispan
        #  which will be used to size the fuselage frames. These frames drive the shape of the fuselage.
        inner_part = PartitionedSolid(solid_in = self.vt,
                                      tool = self.vtright_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        #mirrored_part = MirroredShape(shape_in=inner_part, reference_point=self.ht.final_wing.position,vector1=Vector(1, 0, 0),vector2=Vector(0, 0, 1))
        root = self.vt.wires[1]
        #  Above mirrors the cross section about the aircraft symmetry plane.
        first_iter = Fused(inner_part, root)
        #  Fusion of the three wing corss sections (thrid = root) done in 2 parts to avoid parapy errors.
        #second_iter = Fused(first_iter, mirrored_part)

        bounds = first_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

    @Part
    def internal_shape(self):
        return Box(width=self.get_vtfuse_bounds.width,
                   height=self.get_vtfuse_bounds.height,
                   length=self.get_vtfuse_bounds.length,
                   position=Position(self.get_vtfuse_bounds.center),
                   centered=True)




    @Attribute
    def center_of_gravity(self):
        #  This shows the COG.
        pos = self.vt.cog
        return pos

  #  @Part
  #  def cog_ct(self):
  #      return Sphere(radius=self.cog_radius,
  #                    position=self.vt.cog, color='red')





if __name__ == '__main__':
    from parapy.gui import display

    obj = VerticalStabilizer()
    display(obj)
