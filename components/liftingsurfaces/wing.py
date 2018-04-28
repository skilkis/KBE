#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Import ParaPy math, numpy and matplotlib Modules.
from parapy.core import *
from parapy.geom import *
from math import *
import numpy as np
import matplotlib.pyplot as plt
import json

from primitives import LiftingSurface
from directories import *
from definitions import *
from user import MyColors
#  Import AVL wrapper written by Reno El Mendorp. https://github.com/renoelmendorp/AVLWrapper
from avl import Geometry, Surface, Section, Point, Spacing, Session, Case, FileAirfoil

__author__ = "Nelson Johnson"
__all__ = ["Wing"]


# class Wing(GeomBase, WingPowerLoading, ClassOne):  # TODO experiment if this works, multiple inheritance
class Wing(Component):
    """ This class will create the wing geometry based on the required:
    Wing Area (class I output), Aspect Ratio (class I input), taper ratio (assumed),
    dihedral angle (assumed), wing twist angle (assumed) and airfoil selection.
    It also can perform an avl analysis on the wing to obtain the linear value of C_L vs alpha.
    """

#  This block of code contains the inputs. ########---------------------------------------------------------------------
    #: Below is the required wing loading from the class I weight estimation.
    #: :type: float
    WS_pt = Input(100.0, validator=val.Positive())

    #: Below is the required MTOW from the class I weight estimation.
    #: :type: float
    mtow = Input(25.0, validator=val.Positive())

    @Input
    def mtow(self):
        #  When wing is instantiated in main without a supplied mtow, this attribute pulls the value from the ancestor.
        return 25 if self.is_root else self.get_ancestor_value('mtow')

    #: Below is the corresponding aspect ratio from the wing and power loading.
    #: :type: int
    AR = Input(12, validator=val.Positive())

    #: Below is the corresponding stall speed from the wing and power loading.
    #: :type: float
    V_s = Input(15.0, validator=val.Positive())

    #: Below is the chosen taper ratio.
    #: :type: float
    taper = Input(0.3, validator=val.Positive())

    #: Below is the chosen dihedral angle.
    #: :type: float
    dihedral = Input(5.0, validator=val.Range(-20.0, 20.0))

    #: Below is the chosen twist angle.
    #: :type: float
    twist = Input(-2.0, validator=val.Range(-10, 10.0))

    #: Below is the folder for the selected airfoil.
    #: :type: str
    airfoil_type = Input('cambered', validator=val.OneOf(['cambered', 'reflexed', 'symmetric']))

    #: Below is the file name (without extention) of the selected airfoil.
    #: :type: str
    airfoil_choice = Input('SA7036')

    #: Below is the chosen trailing edge offset.
    #: :type: NoneType or float
    offset = Input(None)

    #: Below is the ISA STD sea level density.
    #: :type: float
    rho = Input(1.225)

    #: Below is the radius for a sphere showing the COG.
    #: :type: float
    cog_radius = Input(0.05)    #  This is the radius of the sphere representing the COG.
    #  TODO Fix CH10 bug?

    #: Below is the assumed factor of the semispan in which the fuselage extends over the wing.
    #: :type: float
    fuse_width_factor = Input(0.05)      #  This is an assumed factor relating the part of the wing covered by fuse to semispan
    # Wf_wing = Input(0.2)                #  This is the mass fraction of the wing. TODO CALULATE THIS PROPERLY/ADD TO MAIN/CLASS I
    hide_bbox = Input(True)
    mesh_deflection = Input(0.0001)  # Default value is an optimum point between a good quality render and performance

    # TODO Add a wing weight estimator based on density

    @Attribute
    def component_type(self):
        return 'wing'

    @Attribute
    def weight(self):
        return 0.2*self.mtow

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity w.r.t the origin
        :return: Location Tuple in SI meter
        :rtype: Point
        """
        y = 0
        pos = Point(self.wing.final_wing.cog.x, y, self.wing.final_wing.cog.z)
        return pos

    @Attribute
    def S_req(self):
        # This calculation of the required TOTAL wing area from the design point.
        return ((self.mtow * 9.81) / self.WS_pt) # TODO wing loading is in N/m^2 thus we have to have a global variable for g

    @Attribute
    def C_L_cont(self):
        #  This is the Required C_L from the lift equation at 1.2*V_s @ MTOW for the controllability curve of scissor plot.
        clreq = 2 * 9.81 * self.mtow / (self.rho * ((1.2 * self.V_s) ** 2) * self.S_req)
        return clreq

    @Part
    def wing(self):
        """ Instantiates a primitive LiftingSurface with the inputs given on the right-hand side of the wing """
        return LiftingSurface(S=self.S_req * 0.5,  # Area is halved because lifting surface generates one wing
                              AR=self.AR,
                              taper=self.taper,
                              dihedral=self.dihedral,
                              phi=self.twist,
                              airfoil_type=self.airfoil_type,
                              airfoil_choice=self.airfoil_choice,
                              offset=self.offset,
                              color=MyColors.skin_color, pass_down="mesh_deflection")

    @Part
    def left_wing(self):
        return MirroredShape(shape_in=self.wing.final_wing,
                             reference_point=self.wing.position,
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1),
                             color=MyColors.skin_color)

    @Attribute(private=True)
    def wing_cut_loc(self):
        #  This calculates the spanwise distance of the cut, inside of which, the wing is inside the fuselage.
        return self.wing.semispan * self.fuse_width_factor

    @Part(private=True)
    def right_cut_plane(self):
        #  This makes a plane at the right wing span location where the fuselage is to end.
        return Plane(reference=translate(self.wing.position, 'y', self.wing_cut_loc),
                     normal=Vector(0, 1, 0),
                     hidden=True)

    @Attribute(private=True)
    def get_wingfuse_bounds(self):
        #  This attribute is obtaining (the dimensions of) a bounded box at a fuselaage width factor of the semispan
        #  which will be used to size the fuselage frames. These frames drive the shape of the fuselage.
        inner_part = PartitionedSolid(solid_in = self.wing.final_wing,
                                      tool = self.right_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        mirrored_part = MirroredShape(shape_in=inner_part, reference_point=self.wing.final_wing.position, vector1=Vector(1, 0, 0), vector2=Vector(0, 0, 1))
        root = self.wing.root_airfoil
        #  Above mirrors the cross section about the aircraft symmetry plane.
        first_iter = Fused(inner_part, root)
        #  Fusion of the three wing corss sections (thrid = root) done in 2 parts to avoid parapy errors.
        second_iter = Fused(first_iter, mirrored_part)

        bounds = second_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

    @Part
    def internal_shape(self):
        return Box(width=self.get_wingfuse_bounds.width,
                   height=self.get_wingfuse_bounds.height,
                   length=self.get_wingfuse_bounds.length,
                   position=Position(self.get_wingfuse_bounds.center),
                   centered=True,
                   color=MyColors.cool_blue,
                   transparency=0.5,
                   hidden=self.hide_bbox)

    # --- AVL Geometry & Analysis: ------------------------------------------------------------------------------------
    @Attribute
    def root_section(self):
        return Section(leading_edge_point=Point(0, 0, 0),
                       chord=self.wing.root_chord,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', self.airfoil_type,
                                                                '%s.dat' % self.airfoil_choice))))

    @Attribute
    def tip_section(self):
        #  Here we define the tip AVL section with proper location.
        return Section(leading_edge_point=Point(self.wing.semispan * tan(radians(self.wing.le_sweep)),
                                                self.wing.semispan,
                                                self.wing.semispan * tan(radians(self.dihedral))),
                       chord=self.wing.root_chord * self.taper,
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
                        reference_chord=self.wing.mac_length,
                        reference_span=self.wing.semispan * 2.0,
                        reference_point=Point(0.0, 0.0, 0.0),
                        surfaces=[self.wing_surface])

    @Attribute
    def alpha_cases(self):
        alphas = np.linspace(0.0, 10.0, 25)
        alpha_case = []
        for i in range(0, len(alphas)):
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
        error = [abs(cll[i] - self.C_L_cont) for i in range(0, len(cll))]
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
        with open(os.path.join(DIRS['USER_DIR'], 'results', 'avl_wing_out.json'), 'w') as f:
            f.write(json.dumps(results))
        return 'Done'
#  TODO add get_dir to directory here above, such that the output file goes to the user folder.


if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
