#  This script will generate a lifting surface for the KBE Drone app.
#  The three types of Wing Types that can be generated are Straight / Tapered / Swept and Elliptical wings.
#  In the future, we would like to add functionalities for multi-component wings

from parapy.core import *
from parapy.geom import *
from math import *
from directories import *

class LiftingSurface(GeomBase):
    #  Required inputs for each instantiation: Wing Area, Aspect Ratio, Taper Ratio, Sweep Angle airfoil type and choice
    #  or Wing Area, Aspect Ratio, airfoil type and choice and Elliptical shape
    #  Below we build the wing  with the Leading Edge at (x,y,z) = (0,0,0), x is chordwise and y is up.

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'liftingsurface.png')

    S = Input(0.8)
    #  Above is the Required TOTAL Wing Area for this SINGLE lifting surface.
    AR = Input(9.0)
    #  Above is the requested
    taper = Input(0.6)
    #  Above is the User Requested Taper Ratio.
    dihedral = Input(5.0)
    #  Above is the User Required Dihedral Angle.
    phi = Input(1.0)
    #  Above is the twist of the tip section with respect to the root section.
    airfoil_type = Input('cambered')  #MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SD7062')  #MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'
    offset = Input(None)
    #  The STANDARD OFFSET INPUT(none) causes the TE to be unswept (offset = c_r-c_t), however,
    #  if the user inputs 0 in the GUI, then the leading edge becomes unswept (with taper ratio < 1)
    #position = XOY
    cog_radius = Input(0.05)    #  This is the radius for the displayed cog.
    hide_mac = Input(False)      #  This allows the MAC to be shown on the wing (without dihedral).
    hide_LE = Input(True)       #  This allows the leading edge line to be shown (without dihedral).
    transparency = Input(0.5)
    mesh_deflection = Input(0.0001)  # The default value is an optimum between a good quality render and performance

    @Attribute
    def semispan(self):
        #  This attribute calculated the required semi-span based on the Class I area and Aspect Ratio
        return sqrt(2*self.AR*self.S)*0.5

    @Attribute
    def root_chord(self):
        #  This attribute calculates the required root chord, with an assumed taper ratio.
        return 2*self.S/((1+self.taper)*self.semispan)

    # @Attribute
    # def mac(self):
    #     #  This will clculate the mean aerodynamic chord of the swept and tapered wing.
    #     mac = ((2 * self.root_chord)/3.0)*((1 + self.taper + (self.taper ** 2))/(1+self.taper))
    #     return mac

    @Attribute
    #  This will determine the x and y location of the mac
    def mac_span_calc(self):
        return ((self.semispan)/3.0)*((1+(2*self.taper))/(1+self.taper))

    @Attribute
    #  This will determine the x location of the MAC
    def mac_x(self):
        return (self.mac_y*tan(radians(self.LE_sweep)))

    @Attribute
    def mac_z(self):
        return (self.mac_y*tan(radians(self.dihedral)))

    @Attribute
    def LE_sweep(self):
        #  This will calculate the leading edge sweep of the wing. (before dihedral applied)
        le_sweep = degrees(atan(self.tip_airfoil.position.x/self.semispan))
        return le_sweep

    @Part
    def LE(self):
        #  This makes a line indicating the leading edge, which will be used to calculate the sweep.
        return LineSegment(start= self.root_airfoil.position, end = self.tip_airfoil.position,
                           hidden=self.hide_LE)














    @Attribute
    def tipp_offsett(self):
        #  This attribute determines the spanwise offset of the root and tip leading edges.
        #  The STANDARD OFFSET INPUT(none) causes the TE to be unswept (offset = c_r-c_t), however,
        #  if the user inputs 0 in the GUI, then the leading edge becomes unswept (with taper ratio < 1)
        if self.offset is not None:
            tip_offset = self.offset
        else:
            tip_offset = self.root_chord-(self.root_chord*self.taper)
        return tip_offset



    @Attribute
    def airfoil_data(self):
        #  This reads and scans User chosen Airfoil Data from the database and stores it as airfoil_data.
        filepath = get_dir(os.path.join('airfoils', self.airfoil_type,'%s.dat' %self.airfoil_choice))
        with open(filepath, 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x) + self.position.x, self.position.y, float(y)+self.position.z))
        return pts

    @Part
    def airfoil(self):
        #  This creates an original Airfoil from the data from the chosen airfoil.
        return FittedCurve(points = self.airfoil_data,
                           hidden = True)


#  Below we build the wing  with the Leading Edge at (x,y,z) = (0,0,0), x is chordwise and y is up.
    @Part
    def root_airfoil(self):
        # This scales original airfoil to required root chord.
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point= self.position,
                           factor=self.root_chord)

    @Part
    def scaled_tip(self):
        #  This scales the original airfoil to the required tip chord.
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.root_airfoil.position,
                           factor=(self.root_chord*self.taper),
                           hidden = True)

    @Part
    def tip_airfoil_notwist(self):
        #  This orients the tip airfoil with respect to the required semispan, requested/standard offset
        return TransformedCurve(curve_in = self.scaled_tip,
                                from_position = self.scaled_tip.position,
                                to_position = translate(self.scaled_tip.position,
                                                        'y', self.semispan,
                                                        'x', self.tipp_offsett),
                                hidden=True)


    @Part
    def tip_airfoil(self):
        #  This orients the tip airfoil over the wing twist angle input. The rotation is about the leading edge.
        return TransformedCurve(curve_in = self.tip_airfoil_notwist,
                                from_position = self.tip_airfoil_notwist.position,
                                to_position = rotate(self.tip_airfoil_notwist.position,
                                                     'y', -radians(self.phi)),
                                hidden = True)


    @Part
    def wing_surf(self):
        # This generates a solid wing half with the sign convention mentioned above.
        return LoftedSolid([self.root_airfoil,self.tip_airfoil],
                           hidden = True)

    @Part
    def final_wing(self):
        #  This rotates the entire solid wing over a dihedral angle.
        return RotatedShape(shape_in=self.wing_surf,
                            rotation_point=self.wing_surf.position,
                            vector=Vector(1,0,0),
                            angle=radians(self.dihedral),
                            transparency=self.transparency,
                            mesh_deflection=self.mesh_deflection)

    @Attribute (in_tree=True)
    def mac_airfoil(self):
        cut_plane = Plane(reference= translate(self.final_wing.position,'y', self.mac_span_calc),normal=Vector(0, 1, 0),hidden = True)
        mac = IntersectedShapes(shape_in = self.final_wing,
                                  tool = cut_plane)
        return mac
    @Attribute
    def mac_length(self):
        return self.mac_airfoil.edges[0].bbox.width

    @Attribute
    def aerodynamic_center(self):
        mac_bbox = self.mac.edges[0].bbox
        le_mac = mac_bbox.corners[0]
        ac_loc_x = 0.25 * mac_bbox.width + le_mac.x
        ac_loc_y = mac_bbox.center.y
        ac_loc_z = mac_bbox.center.z
        return Point(ac_loc_x, ac_loc_y, ac_loc_z)






if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface()
    display(obj)



