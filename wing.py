#!C:\Python27
#  This class will create the wing geometry based on the required:
#  Wing Area (class I output), Aspect Ratio (class I in/output), taper ratio (assumed),
#  dihedral angle (assumed/given), wing twist angle (assumed/given) and airfoil.


from parapy.core import *
from parapy.geom import *
from math import *
from liftingsurface import LiftingSurface
from avl import Geometry, Surface, Section, Point, Spacing, Session, Case, Parameter, DataAirfoil
import json

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
        # This calculation of the required TOTAL wing area from the design point.
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

    # control surface definition of a flap (to be used in the wing)





    # TODO

    @Attribute
    def airfoil_data_conversion(self):
        data = [[i.x, i.y] for i in self.wing_test.airfoil_data]
        return data





    @Attribute
    def root_section(self):
        return Section(leading_edge_point=Point(0, 0, 0),
                       chord=self.wing_test.root_chord,
                       airfoil=DataAirfoil(x_data = self.airfoil_data_conversion[0], z_data=self.airfoil_data_conversion[1]))

    @Attribute
    def tip_section(self):
        return Section(leading_edge_point=Point(self.wing_test.semispan*tan(self.wing_test.LE_sweep),
                                                self.wing_test.semispan*tan(self.dihedral),
                                                self.wing_test.semispan),
                       chord=self.wing_test.root_chord*self.taper,
                       angle = radians(self.twist),
                       airfoil=DataAirfoil(x_data = self.airfoil_data_conversion[0], z_data=self.airfoil_data_conversion[1]))
    @Attribute
    def wing_surface(self):
        return Surface(name="Wing",
                       n_chordwise=8,
                       chord_spacing=Spacing.cosine,
                       n_spanwise=12,
                       span_spacing=Spacing.cosine,
                       y_duplicate=0.0,
                       sections=[self.root_section, self.tip_section])

    @Attribute
    def wing_geom(self):
        return Geometry(name="Test wing",
                        reference_area=self.S_req,
                        reference_chord= self.wing_test.mac,
                        reference_span=self.wing_test.semispan*2.0,
                        reference_point=Point(0.21, 0, 0.15),
                        surfaces=[self.wing_surface])
    @Attribute
    def cruise_case(self):
        return Case(name='Cruise', alpha=4.0)  # Case defined by one angle-of-attack
    @Attribute
    def avl_session(self):
        return Session(geometry=self.wing_geom, cases=[self.cruise_case])

    @Attribute
    def show_avlgeom(self):
        self.avl_session.show_geometry()
        return 'Done'

    @Attribute
    def write_results(self):
        results = self.avl_session.get_results()
        with open('out.json', 'w') as f:
            f.write(json.dumps(results))
        return 'Done'







if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
