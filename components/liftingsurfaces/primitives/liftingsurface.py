#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  This script will generate a lifting surface primitive for the KBE app.
  The surface type can be straight, tapered and swept swept wing.
  In the future, we would like to add functionality for elliptical wings.
"""

from parapy.core import *       # / Required ParaPy Module
from parapy.geom import *       # / Required ParaPy Module
from math import *              # / Python math operations.
from directories import *       # / Project Directory

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

#  This block of code contains the inputs. ########---------------------------------------------------------------------
    #: Below is the Required Wing Area for this SINGLE surface!
    #: :type: float
    S = Input(0.8)

    #: Below is the required Aspect Ratio of the Surface.
    #: :type: float
    AR = Input(9.0)

    #: Below is the Taper Ratio, which is chosen by the user.
    #: :type: float
    taper = Input(0.6)

    #: Below is the User chosen Dihedral Angle.
    #: :type: float
    dihedral = Input(5.0)

    #: Below is the twist of the tip section with respect to the root section. Positive phi is tip twisted up
    #: with respect to the root.
    #: :type: float
    phi = Input(-5.0)

    #: Below is the name of the folder within the 'airfoils' folder. There are three options: 'cambered', 'reflexed' and
    #: 'symmetric'.
    #: :type: str
    airfoil_type = Input('cambered')

    #: Below is the default airfoil. Please see the three folders to find the correct filename, if you wish to change
    #: the airfoil.
    #: :type: str
    airfoil_choice = Input('SD7062')

    #: Below is the offset in the flow direction of the tip W.R.T. the root Leading Edge. The default input (None)
    #: causes the TE to be unswept (offset = c_r-c_t), however, if the user inputs 0 in the GUI, then the leading
    #: edge becomes unswept. In this case, with taper ratio < 1, the TE becomes forward swept.
    #: :type: NoneType or float
    offset = Input(None)

    #: Boolean below allows the MAC curve to be shown on the wing when changed in the GUI to False.
    #: :type: bool
    hide_mac = Input(True)

    #: Boolean below allows the leading edge line to be shown (without dihedral).
    #: :type: bool
    hide_LE = Input(True)

    #: The default value is an optimum between a good quality render and performance
    #: :type: float
    mesh_deflection = Input(0.0001)

#  This block of Attributes calculates the planform parameters. ########------------------------------------------------
    @Attribute
    def semispan(self):
        """ This attribute calculates the required semi-span based on the wing area and Aspect Ratio. REMEMBER: The
        wing area input for this primitive is the wing area for ONE WING!

        :return: Wing Semispan
        :rtype: float
        """
        return sqrt(2*self.AR*self.S)*0.5

    @Attribute
    def root_chord(self):
        """ This attribute calculates the required root chord, with an assumed taper ratio.
        :return: Wing Root Chord
        :rtype: float
        """
        return 2*self.S/((1+self.taper)*self.semispan)

    """
    @Attribute
    def macc(self):
        #  This will calculate the mean aerodynamic chord of the swept and tapered wing.
        #  This was commented out as we are using ParaPy's IntersectedShapes class at the spanwise position
        #  to find this.
        macc = ((2 * self.root_chord)/3.0)*((1 + self.taper + (self.taper ** 2))/(1+self.taper))
        return macc
    """

    @Attribute
    def mac_span_calc(self):
        """ This will determine the spanwise location (y) of the Mean Aerodynamic Chord with respect to the root airfoil.
        :return: Wing Spanwise MAC position
        :rtype: float
        """
        return (self.semispan/3.0)*((1+(2*self.taper))/(1+self.taper))

    @Attribute
    def mac_x(self):
        """ This will determine the x relative position of the MAC WRT the wing root. Thus, it must be added to the
        position of the wing root.
        :return: Wing Flow direction MAC position
        :rtype: float
        """
        return self.mac_span_calc*tan(radians(self.le_sweep))

    @Attribute
    def mac_z(self):
        """ This will determine the z relative position of the MAC WRT the wing root. Thus, it must be added to the
        position of the wing root.
        :return: Wing z direction MAC position
        :rtype: float
        """
        return self.mac_span_calc*tan(radians(self.dihedral))

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

    @Attribute
    def le_sweep(self):
        """ This will calculate the leading edge sweep of the wing.
        :return: Wing LE sweep
        :rtype: float
        """
        le_sweep = degrees(atan((self.tip_airfoil.position.x-self.root_airfoil.position.x)/self.semispan))
        return le_sweep

    @Attribute(in_tree=True)
    def leading_edge(self):
        """ This makes a line indicating the leading edge (for a wing without dihedral).
        :return: Wing leading edge ParaPy Geometry
        :rtype: LineSegment
        """

        # Sorts the faces based on minimum distance of their Attribute `cog` relative to the position
        faces = sorted(self.final_wing.faces, key=lambda x: x.cog.distance(self.position))
        root_le = sorted(faces[0].edges[0].sample_points, key=lambda point: point.x)[0]
        tip_le = sorted(faces[-1].edges[0].sample_points, key=lambda point: point.x)[0]

        return LineSegment(start=root_le,
                           end=tip_le,
                           hidden=self.hide_LE,
                           color='yellow')

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


# This block of code builds the wing by importing, scaling positioning and lofting airfoils ##--------------------------
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

    @Part
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
                           factor=self.root_chord)

    @Part
    def scaled_tip(self):
        """  This scales the original airfoil to the required tip chord.
        :return: Tip Airfoil scaled curve ParaPy Geometry
        :rtype: ScaledCurve
        """
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.root_airfoil.position,
                           factor=(self.root_chord*self.taper),
                           hidden=True)

    @Part
    def tip_airfoil_notwist(self):
        """ This positions another tip airfoil with respect to the required semispan & requested/standard offset.
        It does not yet incorporate twist.
        :return: Tip Airfoil in position without twist ParaPy Geometry
        :rtype: TransformedCurve
        """
        return TransformedCurve(curve_in=self.scaled_tip,
                                from_position=self.scaled_tip.position,
                                to_position=translate(self.scaled_tip.position,
                                                        'y', self.semispan,
                                                        'x', self.tip_offset),
                                hidden=True)

    @Part
    def tip_airfoil(self):
        """ This rotates the tip airfoil over the wing twist angle input. The rotation is about the leading edge.
        :return: Tip Airfoil in position without twist ParaPy Geometry
        :rtype: TransformedCurve
        """
        return TransformedCurve(curve_in=self.tip_airfoil_notwist,
                                from_position=self.tip_airfoil_notwist.position,
                                to_position=rotate(self.tip_airfoil_notwist.position, 'y', radians(self.phi)),
                                hidden=True)

    @Part
    def wing_surf(self):
        """ This generates a solid wing half with the sign convention mentioned above.
        :return: ParaPy lofted solid wing geometry.
        :rtype: LoftedSolid
        """
        return LoftedSolid([self.root_airfoil, self.tip_airfoil],
                           hidden = True)

    @Part
    def final_wing(self):
        """ This rotates the entire solid wing half over the dihedral angle.
        :return: ParaPy rotated lofted solid wing geometry.
        :rtype: RotatedShape
        """
        return RotatedShape(shape_in=self.wing_surf,
                            rotation_point=self.wing_surf.position,
                            vector=Vector(1, 0, 0),
                            angle=radians(self.dihedral),
                            mesh_deflection=self.mesh_deflection)

    @Attribute(in_tree=True)
    def mac_airfoil(self):
        """ This finds the mean aerodynamic chord wing section by using a plane intersecting the rotated wing half.
        The location of this cut is found above. (Note: to see this on the wing, you must change hide_mac to True)
        :return: ParaPy MAC airfoil.
        :rtype: IntersectedShapes
        """
        cut_plane = Plane(reference=translate(self.final_wing.position, 'y', self.mac_span_calc),
                          normal=self.final_wing.orientation.Vy, hidden=True)

        mac = IntersectedShapes(shape_in=self.final_wing,
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


if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface()
    display(obj)
