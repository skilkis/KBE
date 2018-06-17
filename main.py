#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Explanation of Main File Here


@author: Şan Kılkış & Nelson Johnson
@version: 1.0
"""

#  TODO DELIVERABLE:   WRITE   OUTPUT    EXCEL    FILE   !!!!!!!!!!!!!!!!!!!!!!

#  TODO !!!!!! IF AR (for example) CHANGED IN Main Wing INSTANTIATION, SCISSOR PLOT IS NOT UPDATED WITH CORRESP. VALUE!
#  TODO .... we must update the values in params, and change them ONLY there in the GUI!!!!!!!!!!!!!!!!

#  TODO MAKE final_cg NON LAZY OR USER SEES WRONG TAIL!!!!!!!!!!!!!!!!!! (Add listener to input cg)
#  TODO Make sure vt weight is correct in final weight for changes in the GUI ......


# TODO Add instance validator for each class input (check out performance.py for example)
# TODO Make a nice visual CG representation of both c.g. before and after run

#  TODO every class should have print statement saying that it has been instantiated into the console

# TODO delete all example and irrelevant documents & data files in KBE folder and rename folder with original name.

# TODO move everything except for main.py into a \bin folder to clean up directory

# TODO Add UML in doc

# TODO bug found in eletronics, number of engines messes up the Fuse Operation


# TODO Check that all plots are actually output, and consider trigerring all plots with an attribute

# TODO internal shape of electronics module is wrong


# TODO add validator Class IntersectedShapes on Fuselage


# TODO Change fuselage fit-width to actual dimension to be able to be a certain fraction of camera size

# TODO AIRFOIL BROWSER STOPPED WORKING!!!!

from design import *
from parapy.core import *
from parapy.geom import *
from parapy.exchange import STEPWriter
from components import *
from directories import *
from definitions import *
from math import sin, radians
from collections import Iterable
import copy
import xlwt
import matplotlib.pyplot as plt


# TODO (TBD) Visualize performance in the GUI through the addition of bar-charts utilizing ParaPy Boxes

class UAV(DesignInput):
    """  This class will generate UAV aircraft. It inherits from 'DesignInput.py' so that the input requirements are
    all in the top level of the tree. """

    __icon__ = os.path.join(DIRS['ICON_DIR'], 'plane.png')

    #: Switch case that handles build location of the single motor
    motor_integration = Input('pusher', validator=val.OneOf(['pusher', 'puller']))

    @Input
    def cg(self):
        """ Computes an initial-guess for the Center of Gravity Location at Run-Time utilizing 'weight_and_balance'

        :return: Initial Estimate C.G. location (x, y, z) in SI meter [m]
        :rtype: Point """
        return self.weight_and_balance()['CG']

    @Attribute
    def final_cg(self):
        """ This attribute utilizes a loop to find a converged final Center of Gravity that is stable, this step is
        necessary since at run-time the tail is not yet made and the scissor plot only calculates stability for a
        tail-less aircraft! """
        old_cg = self.cg
        print 'Run-Time CG = %1.4f \n' % old_cg.x
        new_cg = self.weight_and_balance()['CG']
        loop = 0
        xcg_cache = []
        while abs(old_cg.x - new_cg.x) > 0.0005 and loop < 20:
            loop += 1
            print 'Current Iteration: ' + str(loop)

            new_uav_object = copy.copy(self)  # Large Performance improvement from making a copy of the current object!
            old_cg = new_uav_object.cg
            print 'Old CG = %1.6f' % old_cg.x

            new_cg = new_uav_object.weight_and_balance()['CG']
            print 'New CG = %1.6f' % new_cg.x

            # Adding rounded c.g.x values to cache and cross-referencing to see if convergence behavior is oscillating
            if round(old_cg.x, 4) and round(new_cg.x, 4) in xcg_cache:
                new_cg = Point((new_cg.x + old_cg.x)/2.0, new_cg.y, new_cg.z)
            setattr(self, 'cg', new_cg)
            xcg_cache = xcg_cache + [round(old_cg.x, 4)] + [round(new_cg.x, 4)]

        fig = plt.figure('Convergence Behavior')
        plt.style.use('ggplot')
        plt.plot(xcg_cache)
        plt.title('Congergence History of the Center of Gravity')
        plt.xlabel(r'Iterations [-]')
        plt.ylabel(r'Longitudinal Center of Gravity Location [m]')
        plt.show()
        fig.savefig(fname=os.path.join(DIRS['USER_DIR'], 'plots', '%s.pdf' % fig.get_label()), format='pdf')

        return 'Converged after %d Iterations, Figure Plotted and Saved!' % loop

    @Attribute
    def write_step(self):
        """ This attribute utilizes a function :method:`part_fetcher` to loop through all children in the main file,
        and collect the :attr:`external_shape` from these children. These are then fed to the :class:`STEPWriter` which
        creates the .stp file in the user directory under KBE/user/model.

        :return:
        """

        def part_fetcher(external_shape, label):
            """ Collects all entities with 'TopoDS_Shapes' from the input external_shape and returns them in a list

            :param external_shape: The current external shape in the loop
            :param label: The label currently assigned to the child, this is used to name the part in the .stp file
            :return: List of properly labeled ParaPy default shapes that have the 'TopoDS_Shapes' attribute.
            """
            part_bin = []
            counter = 0
            if isinstance(external_shape, Iterable):
                for body in external_shape:
                    counter += 1
                    if hasattr(body, 'TopoDS_Shape'):
                        duplicate = copy.copy(body)
                        setattr(duplicate, 'label', '%s_%d' % (label, counter))
                        part_bin = part_bin + [duplicate]
                    else:
                        print '%s is not suitable for export, please verify geometry' % label
            else:  # Condition to preserve compatibility with older class definitions
                duplicate = copy.copy(external_shape)
                setattr(duplicate, 'label', label)
                part_bin = part_bin + [duplicate]

            return part_bin

        # Creating dummy lists to store all external_bodies
        output = []

        # Looping through all children
        children = self.get_children()
        for _child in children:
            if hasattr(_child, 'external_shape'):
                output = output + part_fetcher(_child.external_shape, label=_child.label)

        writer = STEPWriter(nodes=output, schema='AP214DIS',
                            filename=os.path.join(DIRS['USER_DIR'], 'model', '%s.stp' % self.label))
        writer.write()
        return writer

    @Attribute
    def weights(self):
        return self.weight_and_balance()['WEIGHTS']

    @Attribute
    def parasite_drag(self):
        """ Utilizes Raymer's Equivalent skin-friction drag method to compute Zero-Lift Drag. The utilized value used
        for the skin_friction_coef is taken from subsonic, light propeller aircraft

        http://www.fzt.haw-hamburg.de/pers/Scholz/HOOU/AircraftDesign_13_Drag.pdf

        :return: Zero-Lift Drag Coefficient
        :rtype: Float
        """

        skin_friction_coef = 0.0055
        area_dict = self.sum_area()
        reference_area = area_dict['REFERENCE']
        wetted_area = area_dict['WETTED']['total']
        if wetted_area and reference_area is not 0:
            parasite_drag = skin_friction_coef * (wetted_area / reference_area)
        else:
            parasite_drag = None
        return parasite_drag

    @Attribute
    def areas(self):
        return self.sum_area()

    @Attribute
    def write_excel(self):

        ignore_list = ['children', 'mesh_deflection', 'browse_airfoils', '_local_bbox_bounds', '_bbox_bounds', 'hidden']
        hdr_font = xlwt.Font()
        hdr_font.name = 'Times New Roman'
        hdr_font.bold = True

        hdr_style = xlwt.XFStyle()
        hdr_style.font = hdr_font

        wb = xlwt.Workbook()
        ws0 = wb.add_sheet('Weight & Balance')

        headers = ['Parameter', 'Value', 'Units']
        for i in range(0, len(headers)):
            ws0.write(1, i+1, headers[i], hdr_style)

        row = 3  # Filling in data for the weights w/ skip
        ws0.write(row, 1, 'Weights', hdr_style)
        for key, value in self.weights.items():
            row = row + 1
            ws0.write(row, 1, key)
            ws0.write(row, 2, value)
            ws0.write(row, 3, '[kg]')

        row = row + 2  # Skipping two rows to have a row seperating Weights and C.G
        ws0.write(row, 1, 'C.G. Location (X, Y, Z)', hdr_style)
        ws0.write(row, 2, '(%1.2f, %1.2f, %1.2f)' % (self.cg.x, self.cg.y, self.cg.z))
        ws0.write(row, 3, '[m]')

        row = row + 2
        ws0.write(row, 1, 'Areas', hdr_style)
        for key, value in self.areas['WETTED'].items():
            row = row + 1
            ws0.write(row, 1, key)
            ws0.write(row, 2, value)
            ws0.write(row, 3, '[m^2]')

        row = 1
        ws0.write(row, 5, 'Wing', hdr_style)
        ws0.write(row, 6, self.wing.airfoil_choice)
        for key in self.wing._slots:
            if key not in ignore_list and key.find('plot') == -1 and key.find('avl') == -1:
                value = getattr(self.wing, key)
                if isinstance(value, float) or isinstance(value, int) and not isinstance(value, basestring):
                    row = row + 1
                    ws0.write(row, 5, key)
                    ws0.write(row, 6, value)

        row = 1
        ws0.write(row, 8, 'Stability', hdr_style)
        for key in self.stability._slots:
            if key not in ignore_list and key.find('plot') == -1 and key.find('avl') == -1:
                value = getattr(self.stability, key)
                if isinstance(value, float) or isinstance(value, int):
                    row = row + 1
                    ws0.write(row, 8, key)
                    ws0.write(row, 9, value)

        row = 1
        ws0.write(row, 11, 'Stabilizer', hdr_style)
        for key in self.stabilizer._slots:
            if key not in ignore_list and key.find('plot') == -1 and key.find('avl') == -1:
                value = getattr(self.stabilizer, key)
                if isinstance(value, float) or isinstance(value, int):
                    row = row + 1
                    ws0.write(row, 11, key)
                    ws0.write(row, 12, value)

        wb.save(os.path.join(DIRS['USER_DIR'], 'results', 'output.xls'))
        return 'Excel File Written'

    # Geometry Constraints
    @Attribute(private=True)
    def pad_distance(self):
        return self.fuselage.pad_factor * self.wing.root_chord

    @Part
    def params(self):
        #  Here we instantiate the parameter generator, passing down the inputs from the User input file.
        return ParameterGenerator(pass_down=['performance_goal',
                                             'goal_value',
                                             'weight_target',
                                             'target_value',
                                             'payload_type',
                                             'configuration',
                                             'handlaunch',
                                             'portable'],
                                  label='Design Parameters')

    @Part
    def wing(self):
        return Wing(wing_loading=self.params.wing_loading,
                    weight_mtow=self.params.weight_mtow,
                    stall_speed=self.params.stall_speed,
                    rho=self.params.rho,
                    aspect_ratio=self.params.aspect_ratio,
                    label='Main Wing')

    @Part
    def stability(self):
        return ScissorPlot(x_cg=self.cg.x,
                           x_ac=self.wing.aerodynamic_center.x,
                           x_lemac=self.wing.lemac.x,
                           mac=self.wing.mac_length,
                           AR=self.params.aspect_ratio,
                           e=self.params.wingpowerloading.e_factor,
                           e_h=self.params.wingpowerloading.e_factor,
                           Cl_w=self.wing.lift_coef_control,
                           C_mac=self.wing.moment_coef_control,
                           Cla_w=self.wing.lift_coef_vs_alpha,
                           delta_xcg=0.1,  # Decreasing for a slightly smaller tail
                           configuration=self.configuration,
                           label='Stability Parameters')

    @Part
    def center_of_gravity(self):
        return VisualCG(vis_cog=self.cg)

    @Part
    def stabilizer(self):
        """ Instantiates a Compound Stabilizer by assuming that the location is simply a translation along the x-axis
        with a value equivalent to the assumed tail-arm multiplied by the MAC of the main wing. Please note this value
        neglects the dimension of the tail aerodynamic center as a simplification. Thus the tail arm is slightly larger
        than calculated due to the additional contribution to the tail arm that the tail aerodynamic center makes """
        return CompoundStabilizer(position=translate(self.wing.position,
                                                     'x', self.stability.lhc * self.wing.mac_length
                                                     + self.wing.aerodynamic_center.x,
                                                     'z', self.stabilizer.stabilizer_h.semi_span *
                                                     sin(radians(self.wing.dihedral))),
                                  required_planform_area=self.wing.planform_area * self.stability.shs_req,
                                  wing_planform_area=self.wing.planform_area,
                                  wing_mac_length=self.wing.mac_length,
                                  wing_semi_span=self.wing.semi_span,
                                  lhc=self.stability.lhc,
                                  configuration=self.configuration,
                                  aspect_ratio=self.stability.AR_h,
                                  taper=0.35,
                                  twist=0.0,
                                  label='Tail')

    @Part
    def booms(self):
        return Boom(wing_in=self.wing,
                    tail_in=self.stabilizer, label='Tail Booms')

    @Part
    def camera(self):
        return EOIR(target_weight=self.params.weight_payload,
                    position=translate(self.battery.position, 'x', -1 * (self.camera.box_length + self.pad_distance)))

    @Part
    def fuselage(self):
        return Fuselage(compartment_type=['nose', 'container', 'container', 'container', 'motor'] if
                        self.motor_integration is 'pusher' else
                        ['motor', 'container', 'container', 'container', 'tail'],
                        sizing_parts=[None, [self.camera,self.electronics], self.battery, self.wing, self.motor] if
                        self.motor_integration is 'pusher' else
                        [self.motor, [self.camera, self.electronics], self.battery, self.wing, None],
                        label='Fuselage')

    # TODO fix motor placement to be better looking
    @Part
    def motor(self):
        return Motor(target_power=self.params.motor_power,
                     integration=self.motor_integration,
                     position=translate(self.wing.position,
                                        'x', 1.2 * self.wing.root_chord,
                                        'z', self.wing.internal_shape.bbox.center.z)
                     if self.motor_integration is 'pusher' else
                     translate(self.camera.position,
                               'x', -1 * (self.pad_distance + self.motor.length),
                               'z', self.wing.internal_shape.bbox.center.z))

    @Part
    def battery(self):
        return Battery(position=translate(self.wing.position, 'x', (self.battery.length + self.pad_distance) * -1),
                       sizing_target='capacity',
                       sizing_value=self.params.wingpowerloading.battery_capacity,
                       max_width=self.camera.box_width,
                       max_height=self.camera.box_height)

    @Part
    def propeller(self):
        return Propeller(motor=self.motor, design_speed=self.params.design_speed)

    @Part
    def electronics(self):
        return Electronics(position=translate(self.camera.position,
                                              'x', self.camera.box_length / 2.0 - self.electronics.box_length*0.5,
                                              'z', self.camera.box_height),
                           motor_in=self.motor)

    @Part
    def performance(self):
        return Performance(motor_in=self.motor,
                           propeller_in=self.propeller,
                           battery_in=self.battery,
                           wing_in=self.wing,
                           weight_mtow=self.weights['mtow'],
                           parasitic_drag=self.parasite_drag,
                           oswald_factor=self.params.wingpowerloading.e_factor, label='Performance')

    def weight_and_balance(self):
        """ Retrieves all relevant parameters from children with `weight` and `center_of_gravity` attributes and then
        calculates the center of gravity w.r.t the origin Point(0, 0, 0)

        :return: A dictionary of component weights as well as the center of gravity fieldnames = 'WEIGHTS', 'CG'
        :rtype: dict
        """

        children = self.get_children()

        # Creating dummy lists to store all weights and respective c.g. locations
        weight = []
        cg = []

        # Defining the structure of the weight_dictionary
        weight_dict = {'WEIGHTS': {'wing': 0.0,
                                   'fuselage': 0.0,
                                   'vt': 0.0,
                                   'ht': 0.0,
                                   'ct': 0.0,
                                   'boom': 0.0,
                                   'payload': 0.0,
                                   'prop': 0.0,
                                   'battery': 0.0,
                                   'electronics': 0.0,
                                   'misc': 0.0},
                       'CG': Point(0, 0, 0)}

        for _child in children:
            if hasattr(_child, 'weight') and hasattr(_child, 'center_of_gravity'):
                weight.append(_child.getslot('weight'))
                cg.append(_child.getslot('center_of_gravity'))

                if _child.getslot('component_type') == 'wing':
                    weight_dict['WEIGHTS']['wing'] = weight_dict['WEIGHTS']['wing'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'fuselage':
                    weight_dict['WEIGHTS']['fuselage'] = weight_dict['WEIGHTS']['fuselage'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'vt':
                    weight_dict['WEIGHTS']['vt'] = weight_dict['WEIGHTS']['vt'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'ht':
                    weight_dict['WEIGHTS']['ht'] = weight_dict['WEIGHTS']['ht'] + (_child.getslot('weight'))

                # Special Case for Compound Tail
                elif _child.getslot('component_type') == 'ct':
                    weight_dict['WEIGHTS']['ct'] = weight_dict['WEIGHTS']['ct'] + (_child.getslot('weight'))
                    weight_dict['WEIGHTS']['ht'] = weight_dict['WEIGHTS']['ht'] + \
                                                   (_child.stabilizer_h.getslot('weight'))
                    weight_dict['WEIGHTS']['vt'] = weight_dict['WEIGHTS']['vt'] + \
                                                   2 * (_child.stabilizer_vright.getslot('weight'))

                elif _child.getslot('component_type') == 'boom':
                    weight_dict['WEIGHTS']['boom'] = weight_dict['WEIGHTS']['boom'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'payload':
                    weight_dict['WEIGHTS']['payload'] = weight_dict['WEIGHTS']['payload'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'prop':
                    weight_dict['WEIGHTS']['prop'] = weight_dict['WEIGHTS']['prop'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'battery':
                    weight_dict['WEIGHTS']['battery'] = weight_dict['WEIGHTS']['battery'] + (_child.getslot('weight'))

                elif _child.getslot('component_type') == 'electronics':
                    weight_dict['WEIGHTS']['electronics'] = weight_dict['WEIGHTS']['electronics'] + \
                                                            (_child.getslot('weight'))

                else:
                    weight_dict['WEIGHTS']['misc'] = weight_dict['WEIGHTS']['misc'] + _child.getslot('weight')
                    print Warning("%s does not have an Attribute 'component_type'"
                                  "it was thus added to the 'misc' category in the weight_dictionary" % _child)

        total_weight = sum(weight)
        weight_dict['WEIGHTS']['mtow'] = total_weight

        # CG calculation through a weighted average utilizing list comprehension
        if len(weight) and len(cg) is not 0:
            cg_x = sum([weight[i] * cg[i].x for i in range(0, len(weight))]) / total_weight
            cg_y = sum([weight[i] * cg[i].y for i in range(0, len(weight))]) / total_weight
            cg_z = sum([weight[i] * cg[i].z for i in range(0, len(weight))]) / total_weight

            weight_dict['CG'] = Point(cg_x, cg_y, cg_z)
        return weight_dict

    def sum_area(self):
        """ Retrieves all wetted surface areas of instantiated children that have the attributes `wetted_area` and
        `planform_area` which are defined by the class `ExternalBody`. This class

        :return: A dictionary of wetted surface and reference area with the fieldnames: 'WETTED' and 'REFERENCE'
        """
        children = self.get_children()

        areas = []
        area_dict = {'WETTED': {'wing': 0,
                                'fuselage': 0,
                                'vt': 0,
                                'ht': 0,
                                'ct': 0,
                                'boom': 0,
                                'misc': 0,
                                'total': 0},
                     'REFERENCE': 0}

        for _child in children:
            if hasattr(_child, 'wetted_area') and hasattr(_child, 'planform_area'):
                areas.append(_child.wetted_area)

                if _child.getslot('surface_type') == 'wing':
                    area_dict['WETTED']['wing'] = area_dict['WETTED']['wing'] + _child.wetted_area
                    area_dict['REFERENCE'] = area_dict['REFERENCE'] + _child.planform_area

                elif _child.getslot('surface_type') == 'fuselage':
                    area_dict['WETTED']['fuselage'] = area_dict['WETTED']['fuselage'] + _child.wetted_area

                elif _child.getslot('surface_type') == 'vt':
                    area_dict['WETTED']['vt'] = area_dict['WETTED']['vt'] + _child.wetted_area

                elif _child.getslot('surface_type') == 'ht':
                    area_dict['WETTED']['ht'] = area_dict['WETTED']['ht'] + _child.wetted_area

                # Special Case for Compound Tail
                elif _child.getslot('component_type') == 'ct':
                    area_dict['WETTED']['ct'] = area_dict['WETTED']['ct'] + _child.wetted_area
                    area_dict['WETTED']['ht'] = area_dict['WETTED']['ht'] + _child.stabilizer_h.wetted_area
                    area_dict['WETTED']['vt'] = area_dict['WETTED']['vt'] + _child.stabilizer_vright.wetted_area * 2.0

                elif _child.getslot('surface_type') == 'boom':
                    area_dict['WETTED']['boom'] = area_dict['WETTED']['boom'] + _child.wetted_area

                else:
                    area_dict['WETTED']['misc'] = area_dict['WETTED']['misc'] + _child.wetted_area
                    print Warning("%s does not have an Attribute 'surface_type' "
                                  "it was thus added to the 'misc' category in the area_dictionary" % _child)
        area_dict['WETTED']['total'] = sum(areas)

        return area_dict


if __name__ == '__main__':
    from parapy.gui import display

    obj = UAV(label='myUAV')
    display(obj)
