#!C:\Python27
#  This class will create the wing geometry based on the required:
#  Wing Area (class I output), Aspect Ratio (class I in/output), taper ratio (assumed),
#  dihedral angle (assumed/given), wing twist angle (assumed/given) and airfoil.


from parapy.core import *
from parapy.geom import *
from math import *
from liftingsurface import LiftingSurface
from avl import Geometry, Surface, Section, Point, Spacing, Session, Case, DataAirfoil, NacaAirfoil, FileAirfoil
import json
from directories import *
import numpy as np

#from design.wingpowerloading import designpoint['wing_loading']
#from design.weightestimator import mtow



class Wing(GeomBase):
    WS_pt = Input(50.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    MTOW = Input(25.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    AR = Input(12.0)  # MUST GET THIS FROM CLASS i!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    V_s = Input(15.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  Above is the required stall speed from the class I estimation.

    taper = Input(0.3)
    #  Above is the User Requested Taper Ratio.
    dihedral = Input(5.0)
    #  Above is the User Required Dihedral Angle.
    twist = Input(2.0)
    #  Above is the twist of the tip section with respect to the root section.
    airfoil_type = Input('cambered')  # MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SA7036')  # MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'
    offset = Input(None)

    rho = Input(1.225)
    #  Above is the density used to calculate the C_L for controlability curve

    #  TODO Fix CH10 bug?



    @Attribute
    def S_req(self):
        # This calculation of the required TOTAL wing area from the design point.
        return (self.MTOW/self.WS_pt)


    @Attribute
    def C_L_cont(self):
        #  This is the Required C_L from the lift equation at 1.2*V_s @ MTOW for the controllability curve of scissor plot.
        clreq = 2*self.MTOW/(self.rho*((1.2*self.V_s)**2)*self.S_req)
        return clreq


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







    @Attribute
    def airfoil_data_conversion(self):
        data = [[i.x, i.z] for i in self.wing_test.airfoil_data]
        x = [i[0] for i in data]
        z = [j[1] for j in data]
        return x, z

    @Attribute
    def root_section(self):
        return Section(leading_edge_point=Point(0, 0, 0),
                       chord=self.wing_test.root_chord,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', self.airfoil_type,'%s.dat' %self.airfoil_choice))))

    @Attribute
    def tip_section(self):
        #  Here we define the tip AVL section with proper location.
        return Section(leading_edge_point=Point(self.wing_test.semispan*tan(radians(self.wing_test.LE_sweep)),
                                                self.wing_test.semispan,
                                                self.wing_test.semispan*tan(radians(self.dihedral))),
                       chord=self.wing_test.root_chord*self.taper,
                       angle = 0.0,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', 'cambered', '%s.dat' % self.airfoil_choice))))

    @Attribute
    def wing_surface(self):
        return Surface(name="Wing",
                       n_chordwise=12,
                       chord_spacing=Spacing.cosine,
                       n_spanwise=16,
                       span_spacing=Spacing.neg_sine,
                       y_duplicate=0.0,
                       sections=[self.root_section, self.tip_section])

    @Attribute
    def wing_geom(self):
        return Geometry(name="Test wing",
                        reference_area=self.S_req,
                        reference_chord= self.wing_test.mac,
                        reference_span=self.wing_test.semispan*2.0,
                        reference_point=Point(0.0, 0.0, 0.0),
                        surfaces=[self.wing_surface])

    @Attribute
    def cruise_case(self):
        return Case(name='Cruise', alpha = 2.75, velocity = 1.2*self.V_s)  # Case defined by one angle-of-attack

    @Attribute
    def alpha_cases(self):
        alphas = np.linspace(0.0,5.0,20)
        alpha_case = []
        for i in range(0,len(alphas)):
            alpha_case.append(Case(name='alpha%s' % i, alpha = alphas[i], velocity = 1.2*self.V_s))
        return alpha_case

    @Attribute
    def avl_session(self):
        return Session(geometry=self.wing_geom, cases=self.alpha_cases)

    @Attribute
    def show_avlgeom(self):
        self.avl_session.show_geometry()
        return 'Done'

    @Attribute
    def results(self):
        return self.avl_session.get_results()

    @Attribute
    def cl_vs_alpha(self):
        my_array=[]
        my_array = sorted([[self.results[alpha]['Totals']['Alpha'], self.results[alpha]['Totals']['CLtot']]
                          for alpha in self.results], key=lambda f: float(f[0]))
        return my_array

  #  @Attribute
  #  #  Now we must get the data corresponding to C_L_cont derived above.
  #  def cl_controllability(self):
  #
  #      return



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
