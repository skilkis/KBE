#  This script will generate a lifting surface for the KBE Drone app.
#  The three types of Wing Types that can be generated are Straight / Tapered / Swept and Elliptical wings.
#  In the future, we would like to add functionalities for multi-component wings

from parapy.core import *
from parapy.geom import *
from math import *


class LiftingSurface(GeomBase):
    #  Required inputs for each instantiation: Wing Area, Aspect Ratio, Taper Ratio, Sweep Angle airfoil type and choice
    #  or Wing Area, Aspect Ratio, airfoil type and choice and Elliptical shape

    S_req = Input(0.8)
    #  Above is the Required TOTAL Wing Area for this SINGLE lifting surface.
    AR = Input(9.0)
    #  Above is the requested
    taper = Input(0.6)
    #  Above is the User Requested Taper Ratio.
    dihedral = Input(5.0)
    #  Above is the User Required Dihedral Angle.
    phi = Input(5.0)
    #  Above is the twist of the tip section with respect to the root section.
    airfoil_type = Input('cambered')  #MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above is the standard airfoil type.
    airfoil_choice = Input('SD7062')  #MAKE ERROR IF WRONG NAME INPUT!!!!!!!!!!!!!!
    #  Above the Standard airfoil. The Cambered Symmetric and reflexed airfoil database is in folder 'airfoils'
    offset = Input(None)
    #  The STANDARD OFFSET INPUT(none) causes the TE to be unswept (offset = c_r-c_t), however,
    #  if the user inputs 0 in the GUI, then the leading edge becomes unswept (with taper ratio < 1)

    @Attribute
    def semispan(self):
        #  This attribute calculated the required semi-span based on the Class I area and Aspect Ratio
        return sqrt(self.AR*self.S_req*0.5)

    @Attribute
    def root_chord(self):
        #  This attribute calculates the required root chord, with an assumed taper ratio.
        return 2*self.S_req/((1+self.taper)*self.semispan)

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
        with open('airfoils/%s/%s.dat' % (self.airfoil_type, self.airfoil_choice), 'r') as f:
            pts = []
            for i in f:
                x,y = i.split(' ',1)
                pts.append(Point(float(x), float(y)))
        return pts

    @Part
    def airfoil(self):
        #  This creates an original Airfoil from the data from the chosen airfoil.
        return FittedCurve(points = self.airfoil_data)


#  Below we build the wing  with the Leading Edge at (x,y,z) = (0,0,0), x is chordwise and y is up.
    @Part
    def root_airfoil(self):
        # This scales original airfoil to required root chord.
        return ScaledCurve(curve_in=self.airfoil, reference_point=self.airfoil.position, factor=self.root_chord)

    @Part
    def scaled_tip(self):
        #  This scales the original airfoil to the required tip chord.
        return ScaledCurve(curve_in=self.airfoil, reference_point=self.airfoil.position, factor=(self.root_chord*self.taper))

    @Part
    def tip_airfoil_notwist(self):
        #  This orients the tip airfoil with respect to the required semispan, requested/standard offset
        #  and the dihedral angle.
        return TransformedCurve(curve_in = self.scaled_tip,
                                from_position = self.scaled_tip.position,
                                to_position = translate(self.scaled_tip.position,
                                                        'z', self.semispan,
                                                        'x', self.tipp_offsett,
                                                        'y', self.semispan*tan(radians(self.dihedral))))
    @Part
    def tip_airfoil(self):
        #  This orients the tip airfoil over the wing twist angle input. The rotation is about the leading edge.
        return TransformedCurve(curve_in = self.tip_airfoil_notwist,
                                from_position = self.tip_airfoil_notwist.position,
                                to_position = rotate(self.tip_airfoil_notwist.position,
                                                     'z',
                                                     -radians(self.phi)))


    @Part
    def wing_surf(self):
        # This generates a solid wing half with the sign convention mentioned above.
        return LoftedSolid([self.root_airfoil,self.tip_airfoil])


if __name__ == '__main__':
    from parapy.gui import display

    obj = LiftingSurface()
    display(obj)



