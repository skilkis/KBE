#this is a script to test the AVL run on ONE MAIN WING

from parapy.core import *
from parapy.geom import *
import parapy.lib.avl as avl

from liftingsurface import LiftingSurface

class AVLtest(GeomBase):

    S_req = Input(0.7)
    taper = Input(0.6)
    airf_type = Input('Cambered')
    airf_choice = Input('SD7062')
    @Part
    def my_wing1(self):
        return LiftingSurface(S_req = self.S_req,
                              AR = 10,
                              taper = self.taper,
                              dihedral = 0,
                              airfoil_type = self.airf_type,
                              airfoil_choice = self.airf_choice)

    @Part
    def left_wing(self):
        return TransformedShape(shape_in=self.my_wing1.wing_surf,
                                from_position=XOY,
                                to_position=translate(rotate90(XOY, 'x')))
    @Part
    def my_wing(self):
        return MirroredShape(shape_in=self.left_wing,
                             reference_point=self.left_wing.position,
                             vector1=self.left_wing.position.Vx,
                             vector2=self.left_wing.position.Vy)


    @Part
    def section_root(self):
        #  This creates an avl section for the wing root. Of the wing solid, the second edge is the trailing edge!
        return avl.AirfoilCurveSection(curve_in = self.my_wing.edges[0])
    @Part
    def section_tip(self):
        #  This creates an avl seciton for the wing tip.
        return avl.AirfoilCurveSection(curve_in=self.my_wing.edges[2])

    @Part
    def main_surface(self):
        #  This creates an AVL wing Surface
        return avl.Surface(name="Main Wing",
                           sections=[self.section_root, self.section_tip],
                           n_chord=10,
                           c_spacing=2.0,
                           n_span=20,
                           s_spacing=0.0,
                           y_duplicate=0.0)

    @Part
    def geometry(self):
        return avl.Geometry(name="MyGeometry",
                            surfaces=[self.main_surface],
                            mach_number=0.0,
                            velocity=15.0,
                            ref_area=(self.S_req),
                            ref_chord=(self.my_wing1.root_chord + (self.my_wing1.root_chord*self.taper)) * 0.5,
                            ref_span=self.my_wing1.semispan * 2,
                            ref_pt= Point(0, 0, 0))

    @Part
    def runcaseee(self):
        return avl.RunCase(filename = 'avlcases/alpha0.dat')

    @Part
    def interface(self):
        return avl.Interface(filename="Wingg",
                             directory="output",
                             geometry=self.geometry,
                             outputs=["ft", "fn", "fe", "fs"],
                             close_when_done=True,
                             if_exists="overwrite"
                             )




if __name__ == '__main__':
    from parapy.gui import display

    obj = AVLtest()
    display(obj)
