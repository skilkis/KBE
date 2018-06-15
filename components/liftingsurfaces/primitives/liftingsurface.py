#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  This script will generate a lifting surface primitive for the KBE app.
  The surface type can be straight, tapered and swept.
  In the future, we would like to add functionality for elliptical wings.
"""

#  TODO ADD VALIDATOR FOR AIRFOIL TYPE & CHOICE, OFFSET. ALSO IN HORIZONTAL AND VERTICAL STAB!!!!!!!


from parapy.core import *           # / Required ParaPy Module
from parapy.geom import *           # / Required ParaPy Module
from math import *                  # / Python math operations.
from directories import *           # / Project Directory
# from collections import namedtuple  # / Allows creation of named tuples similar to Point
from Tkinter import *
import tkFileDialog
import tkMessageBox

__author__ = "Nelson Johnson"
__all__ = ["LiftingSurface"]


class LiftingSurface(GeomBase):
    """ The required inputs for each instantiation are Wing Area, Aspect Ratio, Taper Ratio, TE offset , dihedral angle,
    wing twist and airfoil DAT file. Possible airfoils are in the folder 'airfoils', then within another folder, either
    'cambered', 'reflexed', or 'symmetric'. Feel free to add new airfoils. Also note, this primitive is instantiated in
    'wing.py', where you can perform an AVL analysis. The sign convention is +x pointing with direction of chord,
    +y pointing toward right wingtip, +z up.

    """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'liftingsurface.png')

    # --- Inputs: -----------------------------------------------------------------------------------------------------

    #: Below is the Required Planfrom Area, if mirrored is true then this is the total wing area
    #: :type: float
    planform_area = Input(0.8, validator=val.Positive())

    #: Below is the required Aspect Ratio of the Surface.
    #: :type: float
    aspect_ratio = Input(9.0, validator=val.Range(1.0, 30.0))

    #: Below is the Taper Ratio, which is chosen by the user.
    #: :type: float
    taper = Input(0.3, validator=val.Range(0.1, 1.0))

    #: Below is the User chosen Dihedral Angle.
    #: :type: float
    dihedral = Input(5.0, validator=val.Range(-10.0, 10.0))

    #: Below is the twist of the tip section with respect to the root section. Positive twist is tip twisted up
    #: with respect to the root.
    #: :type: float
    twist = Input(-5.0, validator=val.Range(-5.0, 5.0))

    #: Below is the offset in the flow direction of the tip W.R.T. the root Leading Edge. The default input (None)
    #: causes the TE to be unswept (offset = c_r-c_t), however, if the user inputs 0 in the GUI, then the leading
    #: edge becomes unswept. In this case, with taper ratio < 1, the TE becomes forward swept.
    #: :type: NoneType or float
    offset = Input(None)

    @Input
    def browse_airfoils(self):
        """ Allows the user to easily choose amongst available airfoils with a GUI File-Browser

        :return: Sets the inputs `airfoil_type` and `airfoil_choice` above to the value chosen in the GUI Browser
        """
        root = Tk()
        root.update()
        path = tkFileDialog.askopenfilename(initialdir=DIRS['AIRFOIL_DIR'], title="Select Airfoil",
                                            filetypes=(("Airfoil Data Files", "*.dat"), ("All Files", "*.*")))
        root.destroy()

        valid_dir = DIRS['AIRFOIL_DIR'].replace('\\', '/')
        if path.find(valid_dir) is -1:
            root = Tk()
            root.update()
            tkMessageBox.showerror("Directory Error", "Custom airfoils must be placed in the pre-allocated directory")
            root.destroy()
            print 'Test Failed'
        else:
            if len(path) > 0:
                self.airfoil_choice = str(path.split('.')[-2].split('/')[-1])  # Selects the airfoil name
                self.airfoil_type = str(path.split('.')[-2].split('/')[-2])  # Selects the folder-name

        return self.airfoil_choice, self.airfoil_type

    #: Boolean below allows the MAC curve to be shown on the wing when changed in the GUI to False.
    #: :type: bool
    hide_mac = Input(True, validator=val.Instance(bool))

    #: Boolean below allows the leading edge line to be shown (without dihedral).
    #: :type: bool
    hide_leading_edge = Input(True, validator=val.Instance(bool))

    #: A switch case that determines if the `planform_area` is half of the total required area
    #: :type: bool
    is_half = Input(False, validator=val.Instance(bool))

    #: The default value is an optimum between a good quality render and performance
    #: :type: float
    mesh_deflection = Input(0.0001, validator=val.Range(0.00001, 0.001))

    #: Below is the name of the folder within the 'airfoils' folder. There are three options: 'cambered', 'reflexed' and
    #: 'symmetric'.
    #: :type: str
    airfoil_type = Input('cambered', validator=val.OneOf(['cambered', 'reflexed', 'symmetric']))

    #: Below is the default airfoil. Please see the three folders to find the correct filename, if you wish to change
    #: the airfoil.
    #: :type: str
    airfoil_choice = Input('SD7062')

#  This block of Attributes calculates the planform parameters. ########------------------------------------------------
    @Attribute
    def span(self):
        """ This attribute calculates the required wingspan based on the wing area and Aspect Ratio.
        :return: Wing Semispan
        :rtype: float
        """
        return sqrt(self.aspect_ratio * self.planform_area)

    @Attribute
    def semi_span(self):
        """ This attribute calculates the required semi-span based on the wing area and Aspect Ratio. REMEMBER: The
        wing area input for this primitive is the wing area for ONE WING!
        :return: Wing Semispan
        :rtype: float
        """
        if self.is_half:
            semi_span = self.span
        else:
            semi_span = self.span / 2.0
        return semi_span

    @Attribute
    def root_chord(self):
        """ This attribute calculates the required root chord, with an assumed taper ratio.
        :return: Wing Root Chord
        :rtype: float
        """
        return 2 * self.planform_area / ((1 + self.taper) * self.span)

    @Attribute
    def tip_chord(self):
        """ This attribute calculates the tip chord, with the assumed taper ratio and the root chord.
        :return: Wing Tip Chord
        :rtype: float
        """
        return self.root_chord * self.taper

    @Attribute
    def tip_offset(self):
        """  Below is the offset in the flow direction of the tip W.R.T. the root Leading Edge. The default input (None)
        causes the TE to be unswept (offset = c_r-c_t), however, if the user inputs 0 in the GUI, then the leading
        edge becomes unswept. In this case, with taper ratio < 1, the TE becomes forward swept.
        :return: Offset between tip and root leading edges
        :rtype: float
        """
        if self.offset is not None:
            tip_offset = self.offset
        else:
            tip_offset = self.root_chord-(self.root_chord*self.taper)
        return tip_offset

    @Attribute
    def le_sweep(self):
        """ This will calculate the leading edge sweep of the wing.
        :return: Wing LE sweep
        :rtype: float
        """
        le_sweep = degrees(atan((self.tip_airfoil.position.x-self.root_airfoil.position.x) / self.semi_span))
        return le_sweep

    @Attribute(in_tree=True)
    def leading_edge(self):
        """ This makes a line indicating the leading edge (for a wing without dihedral).
        :return: Wing leading edge ParaPy Geometry
        :rtype: LineSegment
        """

        # Sorts the faces based on minimum distance of their Attribute `cog` relative to the position
        faces = sorted(self.solid.faces, key=lambda x: x.cog.distance(self.position))
        root_le = sorted(faces[0].edges[0].sample_points, key=lambda point: point.x)[0]
        tip_le = sorted(faces[-1].edges[0].sample_points, key=lambda point: point.x)[0]

        return LineSegment(start=root_le,
                           end=tip_le,
                           hidden=self.hide_leading_edge,
                           color='yellow')

    # --- Wing Geometry Creation: -------------------------------------------------------------------------------------

    @Attribute
    def airfoil_data(self):
        """ This reads and scans the user chosen Airfoil DAT file from the database and stores it as airfoil_data.
        :return: Airfoil Data Points (Tuple List of Points)
        :rtype: List
        """
        filepath = get_dir(os.path.join('airfoils', self.airfoil_type, '%s.dat' % self.airfoil_choice))
        with open(filepath, 'r') as f:
            pts = []
            for i in f:
                x, y = i.split(' ', 1)
                pts.append(Point(float(x) + self.position.x, self.position.y, float(y)+self.position.z))
        return pts

    @Attribute(private=True)
    def airfoil(self):
        """ This creates an Airfoil from the DAT file.
        :return: Airfoil fitted curve ParaPy Geometry
        :rtype: FittedCurve
        """
        return FittedCurve(points=self.airfoil_data,
                           hidden=True)

    @Part
    def root_airfoil(self):
        """ This scales the original airfoil to required root chord.
        :return: Root Airfoil scaled curve ParaPy Geometry
        :rtype: ScaledCurve
        """
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.position,
                           factor=self.root_chord,
                           hidden=True)

    @Attribute(private=True)
    def scaled_tip(self):
        """  This scales the original airfoil to the required tip chord.
        :return: Tip Airfoil scaled curve ParaPy Geometry
        :rtype: ScaledCurve
        """
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.position,
                           factor=(self.root_chord*self.taper),
                           hidden=True)

    @Attribute(private=True)
    def tip_airfoil_notwist(self):
        """ This positions another tip airfoil with respect to the required semispan & requested/standard offset.
        It does not yet incorporate twist.
        :return: Tip Airfoil in position without twist ParaPy Geometry
        :rtype: TransformedCurve
        """
        return TransformedCurve(curve_in=self.scaled_tip,
                                from_position=self.position,
                                to_position=translate(self.position,
                                                      'y', self.semi_span,
                                                      'x', self.tip_offset))

    @Part
    def tip_airfoil(self):
        """ This rotates the tip airfoil over the wing twist angle input. The rotation is about the leading edge.
        :return: Tip Airfoil in position without twist ParaPy Geometry
        :rtype: TransformedCurve
        """
        return TransformedCurve(curve_in=self.tip_airfoil_notwist,
                                from_position=self.tip_airfoil_notwist.position,
                                to_position=rotate(self.tip_airfoil_notwist.position, 'y', radians(self.twist)),
                                hidden=True)

    @Attribute(private=True)
    def bottom_z_loc(self):
        """ This attribute computes the bottom surface of the root airfoil
        :return: Z-location of the root chord bottom surface
        :rtype: float
        """
        bottom_z = sorted(self.root_airfoil.bbox.corners, key=lambda point: point.z)[0].z
        return bottom_z

    @Attribute(private=True)
    def no_dihedral_solid(self):
        """ This generates a solid wing half with the sign convention mentioned above.
        :return: ParaPy lofted solid wing geometry.
        :rtype: LoftedSolid
        """
        return LoftedSolid([self.root_airfoil, self.tip_airfoil], position=self.position, hidden=True)

    @Part
    def dihedral_solid(self):
        """ This rotates the entire solid wing half over the dihedral angle.
        :return: ParaPy rotated lofted solid wing geometry.
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.no_dihedral_solid,
                            rotation_point=self.position,
                            vector=Vector(1, 0, 0),
                            angle=radians(self.dihedral),
                            mesh_deflection=self.mesh_deflection,
                            hidden=True)

    @Part
    def solid(self):
        """ This translates the entire solid wing half to make the bottom surface flush with the origin
        :return: ParaPy rotated lofted solid wing geometry.
        :rtype: RotatedShape
        """
        return TranslatedShape(shape_in=self.dihedral_solid,
                               displacement=Vector(0, 0, -1*(self.bottom_z_loc - self.position.z)))

    # --- Mean Aerodynamic Chord: -------------------------------------------------------------------------------------

    @Attribute(private=True)
    def mac_span_calc(self):
        """ This will determine the spanwise location (y) of the Mean Aerodynamic Chord with respect to the root airfoil.
        :return: Wing Spanwise MAC position
        :rtype: float
        """
        return (self.semi_span / 3.0) * ((1 + (2 * self.taper)) / (1 + self.taper))

    @Attribute(private=True)
    def mac_x(self):
        """ This will determine the x relative position of the MAC WRT the wing root. Thus, it must be added to the
        position of the wing root.
        :return: Wing Flow direction MAC position
        :rtype: float
        """
        return self.mac_span_calc * tan(radians(self.le_sweep))

    @Attribute(private=True)
    def mac_z(self):
        """ This will determine the z relative position of the MAC WRT the wing root. Thus, it must be added to the
        position of the wing root.
        :return: Wing z direction MAC position
        :rtype: float
        """
        return self.mac_span_calc * tan(radians(self.dihedral))

    @Attribute
    def lemac(self):
        """ Quickly calculates the Leading Edge Mean Aerodynamic Chord by sorting through all `sample_points` of the
        part `mac_airfoil` and selects the one with the minimum x (thus closest to the flight direction which is x_)

        :return: Location of the Leading Edge Mean Aerodynamic Chord in SI meter
        :rtype: Tuple
        """
        sample_points = self.mac_airfoil.edges[0].sample_points
        lemac = sorted(sample_points, key=lambda point: point.x)[0]
        return lemac

    @Attribute(in_tree=True)
    def mac_airfoil(self):
        """ This finds the mean aerodynamic chord wing section by using a plane intersecting the rotated wing half.
        The location of this cut is found above. (Note: to see this on the wing, you must change hide_mac to True)
        :return: ParaPy MAC airfoil.
        :rtype: IntersectedShapes
        """
        cut_plane = Plane(reference=translate(self.solid.position, 'y', self.mac_span_calc),
                          normal=self.solid.orientation.Vy, hidden=True)

        mac = IntersectedShapes(shape_in=self.solid,
                                tool=cut_plane,
                                hidden=self.hide_mac)
        return mac

    @Attribute
    def mac_length(self):
        """ This attribute finds the length of the MAC using the bbox of the intersected shape. This is used instead
        of the normal equation for the equation
        :return: MAC length
        :rtype: float
        """
        return self.mac_airfoil.edges[0].bbox.width

    @Attribute
    def aerodynamic_center(self):
        """ This attribute finds the aerodynamic center assuming it lies at 0.25*MAC.
        :return: Aerodynamic Center Position of wing component. ParaPy Point
        :rtype: Point
        """
        mac_bbox = self.mac_airfoil.edges[0].bbox
        le_mac = mac_bbox.corners[0]
        ac_loc_x = 0.25 * mac_bbox.width + le_mac.x
        ac_loc_y = mac_bbox.center.y
        ac_loc_z = mac_bbox.center.z
        return Point(ac_loc_x, ac_loc_y, ac_loc_z)

    # --- Front Spar Plane Creation: ----------------------------------------------------------------------------------

    @Attribute
    def front_spar_line(self):
        sorted_faces = sorted(self.solid.faces, key=lambda f: f.cog.y)
        root_spar_point = sorted_faces[0].cog
        tip_spar_point = sorted_faces[-1].cog
        # faces = sorted(self.solid.faces, key=lambda x: x.cog.distance(self.position))
        # root_le = sorted(faces[0].edges[0].sample_points, key=lambda point: point.x)[0]
        # tip_le = sorted(faces[-1].edges[0].sample_points, key=lambda point: point.x)[0]
        #
        # root_spar_point = Point(root_le.x + self.front_spar_frac * self.root_chord, root_le.y, root_le.z)
        # tip_spar_point = Point(tip_le.x + self.front_spar_frac * self.tip_chord, tip_le.y, tip_le.z)

        return LineSegment(start=root_spar_point,
                           end=tip_spar_point,
                           color='yellow')


if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface()
    display(obj)
