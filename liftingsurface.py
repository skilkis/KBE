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

    cog_radius = Input(0.05)    #  This is the radius for the displayed cog.
    @Attribute
    def semispan(self):
        #  This attribute calculated the required semi-span based on the Class I area and Aspect Ratio
        return sqrt(self.AR*self.S*0.5)

    @Attribute
    def root_chord(self):
        #  This attribute calculates the required root chord, with an assumed taper ratio.
        return 2*self.S/((1+self.taper)*self.semispan)

    @Attribute (in_tree = True)
    #  This will return the Wings Center of Gravity calculated from the parapy solid.
    def cog_wing(self):
        return self.final_wing.cog

    @Attribute
    #  This will clculate the mean aerodynamic chord of the swept and tapered wing.
    def mac(self):
        mac = (2*self.root_chord*(1 + self.taper + self.taper ** 2))/(3*(1+self.taper))
        return mac
    @Attribute
    #  This will determine the x and y location of the mac
    def mac_y(self):
        return ((self.semispan*2)/6.0)*((1+2*self.taper)/(1+self.taper))
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
        return LineSegment(start= self.root_airfoil.position, end = self.tip_airfoil.position)
















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
                pts.append(Point(float(x), 0, float(y)))
        return pts

    @Part
    def airfoil(self):
        #  This creates an original Airfoil from the data from the chosen airfoil.
        return FittedCurve(points = self.airfoil_data,
                           hidden=True)


#  Below we build the wing  with the Leading Edge at (x,y,z) = (0,0,0), x is chordwise and y is up.
    @Part
    def root_airfoil(self):
        # This scales original airfoil to required root chord.
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.airfoil.position,
                           factor=self.root_chord)

    @Part
    def scaled_tip(self):
        #  This scales the original airfoil to the required tip chord.
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=self.airfoil.position,
                           factor=(self.root_chord*self.taper),
                           hidden=True)

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
                                                     'y',
                                                     -radians(self.phi)))


    @Part
    def wing_surf(self):
        # This generates a solid wing half with the sign convention mentioned above.
        return LoftedSolid([self.root_airfoil,self.tip_airfoil],
                           hidden=True)

    @Part
    def final_wing(self):
        #  This rotates the entire solid wing over a dihedral angle.
        return RotatedShape(shape_in = self.wing_surf,
                            rotation_point=Point(0, 0, 0),
                            vector = Vector(1,0,0),
                            angle = radians(self.dihedral))

    @Part
    def cog_wing(self):
        # This displays a red ball at the COG location of the SOLID wing.
        return Sphere(radius=self.cog_radius,
                      position=self.final_wing.cog, color='red')

    @Part
    def mac_notwist(self):
        #  This will make a visual MAC on the wing.
        return ScaledCurve(curve_in=self.airfoil,
                           reference_point=Point(self.mac_x,
                                                 self.mac_y,
                                                 self.mac_z),
                           factor=self.mac,
                           hidden = True)
    @Part
    def mac_dummy(self):
        #  This orients the mac over the wing twist angle input. The rotation is about the leading edge.
        return TransformedCurve(curve_in = self.mac_notwist,
                                from_position = self.mac_notwist.position,
                                to_position = rotate(self.mac_notwist.position,
                                                     'y',
                                                     -radians((self.phi/self.semispan)*self.mac_y)),
                                color = 'red')

if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface()
    display(obj)



