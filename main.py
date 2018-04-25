# from components import Battery
from design import *
from parapy.core import *
from parapy.geom import *
from wing import *
from components import *


# TODO Make sure that excel read and things are top level program features (not buried within the tree)

class UAV(Base):

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')

    sizing_target = Input('weight')
    sizing_value = Input(1.25)

    @Attribute
    def wing_loading(self):
        return self.params.wingpowerloading.designpoint['wing_loading']

    @Part
    def params(self):
        return ParameterGenerator(initialize_estimations=True, label="Design Parameters")

    @Part
    def wing(self):
        return Wing(MTOW=self.mtow, WS_pt=self.wing_loading)

    @Part
    def fuselage(self):
        return Fuselage(compartment_type=['motor', 'container', 'container', 'container', 'tail'],
                        sizing_parts=[self.motor, self.camera, self.battery, self.wing, None])

    @Part
    def motor(self):
        return Motor(integration='puller', position=translate(XOY, 'x', -0.2))

    @Part
    def propeller(self):
        return Propeller(motor=self.motor)



    @Attribute
    def configuration(self):
        return self.params.configuration

    @Attribute
    def mtow(self):
        return self.params.weightestimator.mtow

    @Attribute
    def payload(self):
        return self.params.weightestimator.payload

    @Attribute
    def battery_capacity(self):
        return self.sizing_value

    @Part
    def battery(self):
        return Battery(position=translate(XOY, 'x', -0.1))


    @Part
    def camera(self):
        return EOIR(target_weight=self.payload, position=translate(XOY, 'x', -0.3))

    @Attribute
    def weight_and_balance(self):
        children = self.get_children()
        weight = []
        cg = []
        for _child in children:
            if hasattr(_child, 'weight') and hasattr(_child, 'center_of_gravity'):
                weight.append(_child.getslot('weight'))
                cg.append(_child.getslot('center_of_gravity'))
            print weight

        total_weight = sum(weight)
        cg_x = sum([weight[i] * cg[i].x for i in range(0, len(weight))]) / total_weight
        cg_y = sum([weight[i] * cg[i].y for i in range(0, len(weight))]) / total_weight
        cg_z = sum([weight[i] * cg[i].z for i in range(0, len(weight))]) / total_weight

        return total_weight, Point(cg_x, cg_y, cg_z)


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
