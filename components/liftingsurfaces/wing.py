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
class Wing(ExternalBody, LiftingSurface):
    """ This class will create the wing geometry based on the required:
    Wing Area (class I output), Aspect Ratio (class I input), taper ratio (assumed),
    dihedral angle (assumed), wing twist angle (assumed) and airfoil selection.
    It also can perform an avl analysis on the wing to obtain the linear value of C_L vs alpha.
    """

#  This block of code contains the inputs. ########---------------------------------------------------------------------
    #: Below is the required wing loading from the class I weight estimation.
    #: :type: float
    wing_loading = Input(100.0, validator=val.Positive())

    #: Below is the required MTOW from the class I weight estimation.
    #: :type: float
    weight_mtow = Input(25.0, validator=val.Positive())
    
    #: The stall speed of the wing
    #: :type: float
    stall_speed = Input(8.0)

    #: Below is the ISA STD sea level density.
    #: :type: float
    rho = Input(1.225)

    #: Below is the assumed factor of the semi_span which the fuselage extends over the wing.
    #: :type: float
    fuse_width_factor = Input(0.07)

    #: Below is the a switch to hide/show the bbox of the wing section within the fuselage.
    #: :type: boolean
    hide_bbox = Input(True)

    #: Overwrites input from LiftingSurface to hide the Mean Aerodynamic Chord part
    hide_mac = Input(True)

    #: Below is the chosen mesh deflection. It's is an optimum point between a good quality render and performance
    #: :type: float
    mesh_deflection = Input(0.0001)

    #: Changes the color of the wing skin to the one defined in MyColors
    #: :type: tuple
    color = Input(MyColors.skin_color)

#  This block of Attributes calculates the planform parameters. ########------------------------------------------------
    @Attribute
    def component_type(self):
        """ This attribute names the component 'wing'.
        :return: str
        :rtype: str
        """
        return 'wing'

    @Attribute
    def weight(self):
        #  TODO connect this with main!!!!!!!!!!
        return 0.2*self.weight_mtow

    @Attribute
    def center_of_gravity(self):
        """ Location of the center of gravity w.r.t the origin (root airfoil leading edge).
        :return: Location Tuple in SI meter
        :rtype: Point
        """
        y = 0
        pos = Point(self.solid.cog.x, y, self.solid.cog.z)
        return pos

    @Attribute
    def s_req(self):
        """ This attribute contains the calculation of the required TOTAL wing area from the design point.
        :return: float
        :rtype: float
        """
        return (self.weight_mtow * 9.81) / self.wing_loading
        # TODO wing loading is in N/m^2 thus we have to have a global variable for g

    @Attribute
    def planform_area(self):
        """ Instantiating the required variable name for the class `ExternalBody`"""
        return self.s_req

    @Attribute
    def lift_coef_control(self):
        """ This is the Required C_L from the lift equation at 1.2*stall_speed @ MTOW for the controllability curve of the
         scissor plot.
         :return: float
         :rtype: float
         """
        clreq = 2 * 9.81 * self.weight_mtow / (self.rho * ((1.2 * self.stall_speed) ** 2) * self.s_req)
        return clreq

    @Part
    def left_wing(self):
        """" This part mirrors the right wing across the X-Z plane to make the left wing.
         :return: ParaPy Geometry
         :rtype: MirroredShape
         """
        return MirroredShape(shape_in=self.solid,
                             reference_point=self.solid.position,
                             vector1=Vector(1, 0, 0),
                             vector2=Vector(0, 0, 1))

    @Attribute(private=True)
    def wing_cut_loc(self):
        """" This calculates the spanwise distance of the cut, inside of which, the wing is inside the fuselage.
         :return: Spanwise distance from root chord to cut location
         :rtype: float
         """
        return self.semi_span * self.fuse_width_factor

    @Part(private=True)
    def right_cut_plane(self):
        """" This makes a plane at the right wing spanwise location where the fuselage is to end.
         :return: Plane at spanwise distance from root chord to cut location.
         :rtype: Plane
         """
        return Plane(reference=translate(self.position, 'y', self.wing_cut_loc),
                     normal=Vector(0, 1, 0),
                     hidden=True)

    @Attribute(private=True)
    def get_wingfuse_bounds(self):
        """" This attribute is obtaining (the dimensions of) a bounded box at a fuselage width factor of the semispan
         which will be used to size the local fuselage frames which drive the shape of the fuselage.
         :return: HT center section bounding box
         :rtype: bbox
         """
        inner_part = PartitionedSolid(solid_in=self.solid,
                                      tool=self.right_cut_plane).solids[0].faces[1].wires[0]
        #  Above obtains a cross section of the wing, at the specified fuselage width factor.

        mirrored_part = MirroredShape(shape_in=inner_part,
                                      reference_point=self.solid.position,
                                      vector1=Vector(1, 0, 0),
                                      vector2=Vector(0, 0, 1))
        #  Above mirrors the cross section about the aircraft symmetry plane.
        root = self.root_airfoil
        first_iter = Fused(inner_part, root)
        #  Fusion of the three wing cross sections done in 2 Fused operations to avoid ParaPy errors.
        second_iter = Fused(first_iter, mirrored_part)

        bounds = second_iter.bbox
        #  Above gets the bounds of the wing fuselage bounding box for return.
        return bounds

    @Part
    def internal_shape(self):
        """"  This part creates the bounding box for the part of the wing within the fuselage.
         :return: HT center section bounding box
         :rtype: Box
         """
        return Box(width=self.get_wingfuse_bounds.width,
                   height=self.get_wingfuse_bounds.height,
                   length=self.get_wingfuse_bounds.length,
                   position=Position(self.get_wingfuse_bounds.center),
                   centered=True,
                   color=MyColors.cool_blue,
                   transparency=0.5,
                   hidden=self.hide_bbox)

    @Part
    def external_shape(self):
        return Fused(self.solid, self.left_wing, hidden=True)


# --- AVL Geometry & Analysis: -----------------------------------------------------------------------------------------
#  In this block, the AVL analysis is setup, run and C_Lalpha is extracted.
    @Attribute(private=True)
    def root_section(self):
        """"  This defines the root section with the chosen airfoil.
         :return: AVL Section
         :rtype: Section
         """
        return Section(leading_edge_point=Point(0, 0, 0),
                       chord=self.root_chord,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', self.airfoil_type,
                                                                '%s.dat' % self.airfoil_choice))))

    @Attribute(private=True)
    def tip_section(self):
        """"  Here we define the tip AVL section with proper location and airfoil.
         :return: AVL Section
         :rtype: Section
         """
        return Section(leading_edge_point=Point(self.semi_span * tan(radians(self.le_sweep)),
                                                self.semi_span,
                                                self.semi_span * tan(radians(self.dihedral))),
                       chord=self.root_chord * self.taper,
                       angle=0.0,
                       airfoil=FileAirfoil(get_dir(os.path.join('airfoils', self.airfoil_type,
                                                                '%s.dat' % self.airfoil_choice))))

    @Attribute(private=True)
    def wing_surface(self):
        """" Here we define the wing surface using a symmetry plane at y=0. Here the number of vortecies and their
         chordwise and spanwise spacing is also set.
         :return: AVL Surface
         :rtype: Surface
         """
        return Surface(name="Wing",
                       n_chordwise=12,
                       chord_spacing=Spacing.cosine,
                       n_spanwise=16,
                       span_spacing=Spacing.neg_sine,
                       y_duplicate=0.0,
                       sections=[self.root_section, self.tip_section])

    @Attribute(private=True)
    def wing_geom(self):
        """"  Here we define the AVL geometry.
         :return: AVL Geometry
         :rtype: Geometry
         """
        return Geometry(name="Test wing",
                        reference_area=self.s_req,
                        reference_chord=self.mac_length,
                        reference_span=self.semi_span * 2.0,
                        reference_point=Point(0.0, 0.0, 0.0),
                        surfaces=[self.wing_surface])

    @Attribute(private=True)
    def alpha_cases(self):
        """"  Here we define the run cases for AVL. We are running input cases alpha from 0 to 10 with 25 data points, at
         the speed required for the controllability curve (1.2*v_s).
         :return: AVL List of RunCases
         :rtype: Case
         """
        alphas = np.linspace(0.0, 10.0, 25)
        alpha_case = []
        for i in range(0, len(alphas)):
            alpha_case.append(Case(name='alpha%s' % i, alpha=alphas[i], velocity=1.2*self.stall_speed))
        return alpha_case

    @Attribute(private=True)
    def avl_session(self):
        """"  Here we define the AVL session with the cases above.
         :return: AVL Session
         :rtype: Session
         """
        return Session(geometry=self.wing_geom, cases=self.alpha_cases)

    @Attribute
    def show_avlgeom(self):
        """"  Here we show the AVL geometry. NOTE: THERE IS A BUG HERE, IF DOUBLE CLICKED IN GUI, IT SHOWS BUT CAUSES
         PYTHON TO FREEZE. THE CODE MUST BE STOPPED AND RESTARTED IF THE GEOMETRY IS SHOWN. TODO FIX THIS IF POSSIBLE
         :return: AVL Geometry
         :rtype: AVL PltLib Viewer
         """
        self.avl_session.show_geometry()
        return 'Done'

    @Attribute
    def avl_results(self):
        """"  Here, the results are extracted and stored in the memory of ParaPy.
         :return:
         :rtype:
         """
        return self.avl_session.get_results()

    @Attribute(private=True)
    def avl_lift_grabber(self):
        # TODO Compare CL_max with assumed as well as plot with LLT
        """  Here, the cl vs alpha plot is created and the constant C_L vs alpha value is found.
        :return: Plot and float
        :rtype: dict
        """
        cl_alpha_array = (sorted([[self.avl_results[alpha]['Totals']['Alpha'],
                                   self.avl_results[alpha]['Totals']['CLtot']]
                                  for alpha in self.avl_results], key=lambda f: float(f[0])))
        #  Above we extract the c_l and angle of attack values.
        alpha_deg = [i[0] for i in cl_alpha_array]
        alpha_rad = [radians(i[0]) for i in cl_alpha_array]
        #  Conversion to radians.
        cl = [i[1] for i in cl_alpha_array]

        return {'lift_coefs': cl, 'alpha_degrees': alpha_deg, 'alpha_radians': alpha_rad}

    @Attribute
    def lift_coef_vs_alpha(self):
        """

        :return: Lift Coefficient Gradient [1/rad]
        """
        cl = self.avl_lift_grabber['lift_coefs']
        alpha_rad = self.avl_lift_grabber['alpha_radians']
        cl_alpha = np.mean([(cl[i+1] - cl[i]) / (alpha_rad[i+1] - alpha_rad[i]) for i in range(0, len(alpha_rad) - 1)])
        return cl_alpha

    @Attribute
    def plot_liftgradient(self):
        # Plotting
        plt.style.use('ggplot')
        plt.figure('LiftCoefficientGradient')
        plt.plot(self.avl_lift_grabber['alpha_degrees'], self.avl_lift_grabber['lift_coefs'], marker='o')
        plt.title('Lift Coefficient Gradient')
        plt.xlabel('Angle of Attack [deg]')
        plt.ylabel('Lift Coefficient [-]')
        plt.show()
        return 'Plot Made, See PyCharm'

    @Attribute
    def lift_coef_control_index(self):
        """"  This attribute returns the index of the AVL data corresponding to the case when C_L is closest to the
         required lift_coef_control required by the lift equation for the controllability curve.
         :return: index
         :rtype: int
         """
        cll_array = (sorted([[self.avl_results[alpha]['Totals']['Alpha'], self.avl_results[alpha]['Totals']['CLtot']]
                             for alpha in self.avl_results], key=lambda f: float(f[1])))
        cll = [i[1] for i in cll_array]
        error = [abs(cll[i] - self.lift_coef_control) for i in range(0, len(cll))]
        cl_cont_index = error.index(min(error))
        return cl_cont_index

    @Attribute
    def controllability_c_m(self):
        """"  This attribute gets the pitching moment of the wing about its aerodynamic center from avl corresponding to
         lift_coef_cont derived above.
         :return: C_mac
         :rtype: float
         """
        case_name = self.avl_results['alpha%s' % self.lift_coef_control_index]['Totals']['Cmtot']
        return case_name

    @Attribute
    def write_results(self):
        """"  Here the results are written into a .json file
         :return: AVL data file
         :rtype: .json file
         """
        results = self.avl_session.get_results()
        with open(os.path.join(DIRS['USER_DIR'], 'results', 'avl_wing_out.json'), 'w') as f:
            f.write(json.dumps(results))
        return 'Done'


if __name__ == '__main__':
    from parapy.gui import display

    obj = Wing()
    display(obj)
