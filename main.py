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
        return Wing(MTOW=self.mtow, WS_pt=self.wing_loading, position=translate(XOY, 'x', self.cg.x))

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
        return self.weight_and_balance()['WEIGHTS']['MTOW']

    # @Attribute

    @Attribute
    def payload(self):
        return self.params.weightestimator.payload

    @Attribute
    def battery_capacity(self):
        return self.sizing_value

    @Part
    def battery(self):
        return Battery(position=translate(XOY, 'x', -0.1))

    # @Part
    # def battery_test(self):
    #     return Battery(position=Position(self.cg))

    @Part
    def camera(self):
        return EOIR(target_weight=self.payload, position=translate(XOY, 'x', -0.3))

    @Attribute
    def cg(self):
        return self.weight_and_balance()['CG']

    def weight_and_balance(self):
        """ Retrieves all relevant parameters from children with `weight` and `center_of_gravity` attributes and then
        calculates the center of gravity w.r.t the origin Point(0, 0, 0)

        :return: A dictionary of component weights as well as the center of gravity fieldnames = `WEIGHTS`, `CG`
        :rtype: dict
        """

        children = self.get_children()
        weight = []
        cg = []
        weight_dict = {'WEIGHTS': {},
                       'CG': Point(0, 0, 0)}
        for _child in children:
            if hasattr(_child, 'weight') and hasattr(_child, 'center_of_gravity'):
                weight_dict['WEIGHTS'][_child.label] = _child.getslot('weight')
                weight.append(_child.getslot('weight'))
                cg.append(_child.getslot('center_of_gravity'))

        total_weight = sum(weight)
        weight_dict['WEIGHTS']['MTOW'] = total_weight

        # CG calculation through a weighted average utilizing list comprehension
        cg_x = sum([weight[i] * cg[i].x for i in range(0, len(weight))]) / total_weight
        cg_y = sum([weight[i] * cg[i].y for i in range(0, len(weight))]) / total_weight
        cg_z = sum([weight[i] * cg[i].z for i in range(0, len(weight))]) / total_weight

        weight_dict['CG'] = Point(cg_x, cg_y, cg_z)

        return weight_dict


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
