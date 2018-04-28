#  This script will generate the horizontal stabilizer using lifting surface with the required Sh
#  from the 'scissorplot.py' script.

from parapy.core import *
from parapy.geom import *
from primitives import LiftingSurface
from scissorplot import ScissorPlot
from definitions import *


class HorizontalStabilizer(Component):

    S_req = Input(0.8)      #  This is the required total wing area from the Class I estimations. TODO CONNECT TO MAIN/ WINGPWR LOADING
    AR_h = Input(5.0)       #  This is the HT aspect ratio. TODO CONNECT TO MAIN/LS
    taper_h = Input(0.5)    #  This is the assumed HT Taper Ratio. TODO CONNECT TO MAIN/LS
    dihedral_h = Input(0.0) #  This is the dihedral angle of the HT. TODO CONNECT TO MAIN/LS
    phi_h = Input(0.0)      #  This is the wing twist for the HT. TODO CONNECT TO MAIN/LS
    airfoil_type_h = Input('symmetric')     #  TODO CONNECT TO MAIN/LS
    airfoil_choice_h = Input('NACA0012')    #  TODO CONNECT TO MAIN/LS
    offset_h = Input(None)                  #  TODO CONNECT TO MAIN/LS
    #  TODO CONNECT THESE INPUTS TO MAIN/WINGPOWER LOADING AND MTOW!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    htfuse_width_factor = Input(0.025)  # This is an assumed factor relating the part of the HT covered by fuse to semispan
    WF_HT = Input(0.1)      #  This is the weight fraction of the HT.
    MTOW = Input(25.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!


    @Attribute
    def component_type(self):
        return 'ht'

    @Attribute
    def weight(self):
        return self.WF_HT*self.MTOW
    #
    # @Attribute
    # def scissor(self):
    #     #  Instantiation of scissor plot to obtain required tail to wing area ratio.
    #     #  TODO CONNECT THIS TO MAIN!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #     return ScissorPlot()
    #
    # @Attribute
    # def shsreq(self):
    #     # This obtains the required tail to wing area ratio.
    #     print 'Required Sh/S is ', self.scissor.shs_req
    #     return self.scissor.shs_req
    #
    # @Attribute
    # def sh(self):
    #     #  This calculates the required HT wing area from the scissor plots.
    #     return self.shsreq*self.S_req


    @Part
    def ht(self):
        #  This is an instantiation of the lifting surface for ONE HT.
        #  Remember, LiftingSurface takes as input the wing area for ONE WING!!
        return LiftingSurface(S = self.S_req*0.5,
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

    @Attribute
    def htwing_cut_loc(self):
        #  This calculates the spanwise distance of the cut, inside of which, the wing is inside the fuselage.
        return self.ht.semispan*self.htfuse_width_factor

    @Part
    def htright_cut_plane(self):
        #  This makes a plane at the right wing span location where the fuselage is to end.
        return Plane(reference= translate(self.ht.position,
                                          'y', self.htwing_cut_loc),
                     normal=Vector(0, 1, 0),
                     hidden = True)
    @Attribute
    def get_htfuse_bounds(self):
        #  This attribute is obtaining (the dimensions of) a bounded box at a fuselaage width factor of the semispan
        #  which will be used to size the fuselage frames. These frames drive the shape of the fuselage.
        inner_part = PartitionedSolid(solid_in = self.ht.final_wing,
                                      tool = self.htright_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        mirrored_part = MirroredShape(shape_in=inner_part, reference_point=self.ht.final_wing.position,vector1=Vector(1, 0, 0),vector2=Vector(0, 0, 1))
        root = self.ht.root_airfoil
        #  Above mirrors the cross section about the aircraft symmetry plane.
        first_iter = Fused(inner_part, root)
        #  Fusion of the three wing corss sections (thrid = root) done in 2 parts to avoid parapy errors.
        second_iter = Fused(first_iter, mirrored_part)

        bounds = second_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

    @Part
    def internal_shape(self):
        return Box(width=self.get_htfuse_bounds.width,
                   height=self.get_htfuse_bounds.height,
                   length=self.get_htfuse_bounds.length,
                   position=Position(self.get_htfuse_bounds.center),
                   centered=True)

    @Attribute
    def center_of_gravity(self):
        #  This shows the COG.
        #  It was found from one wing and translated to origin because the fused shape does not exhibit a C.G..
        y = 0
        pos = Point(self.ht.final_wing.cog.x, y, self.ht.final_wing.cog.z)
        return pos



if __name__ == '__main__':
    from parapy.gui import display

    obj = HorizontalStabilizer()
    display(obj)
