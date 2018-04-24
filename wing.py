#!C:\Python27
#  This class will create the wing geometry based on the required:
#  Wing Area (class I output), Aspect Ratio (class I in/output), taper ratio (assumed),
#  dihedral angle (assumed/given), wing twist angle (assumed/given) and airfoil.


from parapy.core import *
from parapy.geom import *
from math import *

from design.wingpowerloading import WingPowerLoading
from liftingsurface import LiftingSurface
from avl import Geometry, Surface, Section, Point, Spacing, Session, Case, DataAirfoil, NacaAirfoil, FileAirfoil
import json
from directories import *
import numpy as np
import matplotlib.pyplot as plt

from design import *
from definitions import *


# class Wing(GeomBase, WingPowerLoading, ClassOne):  # TODO experiment if this works, multiple inheritance
class Wing(Component):

    WS_pt = Input(100.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    MTOW = Input(25.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    AR = Input(12)  # MUST GET THIS FROM CLASS i!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    V_s = Input(15.0)  # MUST GET THIS INPUT FROM CLASS I!!!!!!!!!!!!!!!!!!!!!!!!!!
    #  Above is the required stall speed from the class I estimation.

    taper = Input(0.3, validator=val.Positive())
    #  Above is the User Requested Taper Ratio.
    dihedral = Input(5.0, validator=val.Range(-20.0, 20.0))
    #  Above is the User Required Dihedral Angle.
    twist = Input(2.0, validator=val.Range(-10, 10.0))
    #  Above is the twist of the tip section with respect to the root section.
    airfoil_type = Input('cambered', validator=val.OneOf(['cambered', 'reflexed', 'symmetric']))
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SA7036')
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'
    offset = Input(None)
#  TODO add validators for inputs
    rho = Input(1.225)
    #  Above is the density used to calculate the C_L for the controlability curve
    cog_radius = Input(0.05)    #  This is the radius of the sphere representing the COG.
    #  TODO Fix CH10 bug?
    fuse_width_factor = Input(0.2)      #  This is an assumed factor relating the part of the wing covered by fuse to semispan
    Wf_wing = Input(0.2)                #  This is the mass fraction of the wing. TODO CALULATE THIS PROPERLY/ADD TO MAIN/CLASS I


    @Attribute
    def weight(self):
        return self.Wf_wing*self.MTOW


    @Attribute
    def S_req(self):
        # This calculation of the required TOTAL wing area from the design point.
        return ((self.MTOW * 9.81)/self.WS_pt) # TODO wing loading is in N/m^2 thus we have to have a global variable for g


    @Attribute
    def C_L_cont(self):
        #  This is the Required C_L from the lift equation at 1.2*V_s @ MTOW for the controllability curve of scissor plot.
        clreq = 2*9.81*self.MTOW/(self.rho*((1.2*self.V_s)**2)*self.S_req)
        return clreq


    @Part
    #  This generates the wing. The area is halved because lifting surface generates one wing of that surface area.
    def wing_test(self):
        return LiftingSurface(S=self.S_req*0.5,
                              AR=self.AR,
                              taper=self.taper,
                              dihedral=self.dihedral,
                              phi=self.twist,
                              airfoil_type=self.airfoil_type,
                              airfoil_choice=self.airfoil_choice,
                              offset=self.offset)

    @Attribute
    def wing_cut_loc(self):
        #  This calculates the spanwise distance of the cut, inside of which, the wing is inside the fuselage.
        return self.wing_test.semispan*self.fuse_width_factor

    @Part
    def right_cut_plane(self):
        #  This makes a plane at the right wing span location where the fuselage is to end.
        return Plane(reference= translate(self.wing_test.position,
                                          'y', self.wing_cut_loc),
                     normal=Vector(0, 1, 0))

    @Attribute
    def inner_part(self):
        inner_part = PartitionedSolid(solid_in = self.wing_test.final_wing,
                                tool = self.right_cut_plane).solids[0].faces[1].wires[0]

        mirrored_part = MirroredShape(shape_in=inner_part, reference_point=inner_part.position,vector1=Vector(1, 0, 0),vector2=Vector(0, 0, 1))
        root = self.wing_test.root_airfoil

        first_iter = Fused(inner_part, root)
        second_iter = Fused(first_iter, mirrored_part)

        return second_iter

    @Part
    def internal_shape(self):
        return ScaledShape(shape_in=self.inner_part, reference_point=self.wing_test.position, factor=1)

    # @Part
    # def

  #  @Part
  #  def wingmirror(self):
  #      return MirroredShape(shape_in = self.wing_test.final_wing,
  #                           reference_point = self.wing_test.position,
  #                           vector1=Vector(1, 0, 0),
  #                           vector2 = Vector(0,0,1))
#
  #  @Part
  #  def wing(self):
  #      return Fused(shape_in = self.wingmirror,
  #                        tool = self.wing_test.final_wing,
  #                        mesh_deflection = 1*10**(-4))

  #  @Attribute
  #  def center_of_gravity(self):
  #      """ Location of the center of gravity w.r.t the origin
  #      :return: Location Tuple in SI meter
  #      :rtype: Point
  #      """
  #      return self.wing_test.cog




   # @Part
   # def left_cut_plane(self):
   #     #  This makes a plane at the left wing span location where the fuselage is to end.
   #     return Plane(reference=translate(self.wing.position,
   #                                      'y', -self.wing_cut_loc),
   #                  normal=Vector(0, 1, 0),
   #                  hidden = True)

   # @Part
   # def subtracted_wing(self):
   #     return Subtracted(shape_in = self.wing,
   #                       tool = [self.left_cut_plane, self.right_cut_plane],
   #                       hidden = True)

  #  @Attribute
  #  def internal_shape_right(self):
  #      return self.subtracted_wing.faces[2]
  #  @Attribute
  #  def internal_shape_left(self):
  #      return self.subtracted_wing.faces[0]
  #  @Part
  #  def internal_shape(self):
  #      return FusedShell(shape_in=self.internal_shape_right,
  #                        tool=self.internal_shape_left,
  #                        mesh_deflection=1 * 10 ** (-5))






    #  This next block prepares the AVL geometry and runcases. It runs and stores the data.
    @Attribute
    def root_section(self):
        return Section(leading_edge_point=Point(0, 0, 0),
                       chord=self.wing_test.root_chord,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', self.airfoil_type,
                                                                '%s.dat' % self.airfoil_choice))))

    @Attribute
    def tip_section(self):
        #  Here we define the tip AVL section with proper location.
        return Section(leading_edge_point=Point(self.wing_test.semispan*tan(radians(self.wing_test.LE_sweep)),
                                                self.wing_test.semispan,
                                                self.wing_test.semispan*tan(radians(self.dihedral))),
                       chord=self.wing_test.root_chord*self.taper,
                       angle=0.0,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', self.airfoil_type,
                                                                '%s.dat' % self.airfoil_choice))))

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

  #  @Attribute
  #  def cruise_case(self):
  #      return Case(name='Cruise', alpha=2.75, velocity=1.2*self.V_s)  # One Case defined by one angle-of-attack

    @Attribute
    def alpha_cases(self):
        alphas = np.linspace(0.0,10.0,25)
        alpha_case = []
        for i in range(0,len(alphas)):
            alpha_case.append(Case(name='alpha%s' % i, alpha=alphas[i], velocity=1.2*self.V_s))
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
        cl_alpha_array = (sorted([[self.results[alpha]['Totals']['Alpha'], self.results[alpha]['Totals']['CLtot']]
                            for alpha in self.results], key=lambda f: float(f[0])))

        alpha_deg = [i[0] for i in cl_alpha_array]
        alpha_rad = [radians(i[0]) for i in cl_alpha_array]
        cl = [i[1] for i in cl_alpha_array]

        # Plotting
        plt.style.use('ggplot')
        plt.figure('LiftCoefficientGradient')
        plt.plot(alpha_deg, cl, marker='o')
        plt.title('Lift Coefficient Gradient')
        plt.xlabel('Angle of Attack [deg]')
        plt.ylabel('Lift Coefficient [-]')
        plt.show()

        # Calculating the Gradient w/ a quick list comprehension (NOTE: THIS VALUE IS IN RADIANS)
        cl_alpha = np.mean([(cl[i+1] - cl[i]) / (alpha_rad[i+1] - alpha_rad[i]) for i in range(0, len(alpha_rad) - 1)])
        return cl_alpha

    @Attribute
    def C_L_cont_index(self):
        #  This attribute returns the index of the AVL data corresponding to the case when C_L is closest to the
        #  required C_L_cont required by the lift equation for the controllability curve.
        cll_array = (sorted([[self.results[alpha]['Totals']['Alpha'], self.results[alpha]['Totals']['CLtot']]
                            for alpha in self.results], key=lambda f: float(f[1])))
        cll = [i[1] for i in cll_array]
        error = [abs(cll[i] - self.C_L_cont) for i in range(0,len(cll))]
        cl_cont_index = error.index(min(error))
        return cl_cont_index

    @Attribute
    #  Now we must get the C_m from avl corresponding to C_L_cont derived above.
    def controllability_C_m(self):
        casename = self.results['alpha%s' % self.C_L_cont_index]['Totals']['Cmtot']
        return casename

    @Attribute
    def write_results(self):
        results = self.avl_session.get_results()
        with open('out.json', 'w') as f:
            f.write(json.dumps(results))
        return 'Done'
#  TODO add get_dir to directory here above, such that the output file goes to the user folder.


if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
