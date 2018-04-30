# -*- coding: utf-8 -*-

from parapy.core import *
from components import Motor, Propeller
import matplotlib.pyplot as plt
import numpy as np


class Performance(Base):

    motor_in = Input(Motor())
    propeller_in = Input(Propeller())
    weight_mtow = Input(5.0)

    @Attribute
    def power_available(self):
        return self.motor_in.power[0] * self.motor_in.efficiency

    @Attribute
    def propeller_eta_curve(self):
        return self.propeller_in.propeller_selector[2]

    @Attribute
    def eta_curve_bounds(self):
        return self.propeller_in.propeller_selector[3]

    @Attribute
    def plot_airspeed_vs_power(self):
        speed_range = np.linspace(self.eta_curve_bounds[0], self.eta_curve_bounds[1], 100)
        eta_values = [self.propeller_eta_curve(float(i)) for i in speed_range]
        power_available_values = [self.power_available * i for i in eta_values]

        fig = plt.figure('LoadingDiagram')
        plt.style.use('ggplot')
        plt.plot(speed_range, power_available_values)
        fig.show()
        return 'Figure Plotted and Saved'



    # @Attribute
    # def prop_eta_curve(self):
    #     self.propeller_in.

# # Constants:
# g = 9.807
# rho_SL = ISA.ISA_m(0)[0]
# rho_ceil = ISA.ISA_m(2000)[0]
#
# # Assumptions
# eta_elec = 0.6  # Electric Efficiency
# n_max = 3.8  # Maximum Load Factor
# n_min = -1.5  # Maximum Negative Load Factor
# CR = 1.524  # Climb Rate at Ceiling [m/s]
# CG = 8.3 / 100  # %Climb Gradient from CS23 for Low Speed Airplanes [%]
# P_BR = [325, 390]  # Total Propulsive Power [W] Constant Power of Rimfire .10
# MTOW = 4.46  # Maximum Take-Off Weight [kg]
# P_NP = 23.1  # Power-Draw of the Payload
#
# PROP = PDI.create_propeller_database()
#
# PROPSELECT = [
#     'PER3_10x4',
#     'PER3_10x7',
#     'PER3_10x10E',
# ]
#
# MAXETA = {}
# for i in PROPSELECT:
#     MAXETA[i] = {
#         'RPM': [],
#         'ETA': [],
#         'V': [],
#     }
#     for RPM in sorted(PROP[i].iterkeys(), key=lambda x: float(x)):
#         idx4 = np.argmax(PROP[i][RPM]['Pe'][0])
#         MAXETA[i]['RPM'].extend([float(RPM)])
#         MAXETA[i]['ETA'].extend([PROP[i][RPM]['Pe'][0][idx4]])
#         MAXETA[i]['V'].extend([0.44704 * PROP[i][RPM]['V'][0][idx4]])
#
# # Manual Input of Fuselage Drag and Surface Area
# UpdateFuselage = 0
# if UpdateFuselage:
#     ds.UpdateValue('CD0_fuse', 0.201, '[-]', 'values_preliminary')
#     ds.UpdateValue('S_fuse', 0.056594, '[m2]', 'values_preliminary')
#
# # Populating Initial UAV Dictionary with Values
# UAV = {}
#
# UAV['WEIGHTS'] = {
#     'MTOW': MTOW,  # Maximum Take-Off Weight [kg]
#     'BAT': ds.GetValue('FW_w_bat', 'values_concept')[0],  # Battery Weight [kg]
#     'WING': ds.GetValue('FW_w_wing', 'values_concept')[0],  # Maximum Take-Off Weight [kg]
#     'FUS': ds.GetValue('FW_w_fus', 'values_concept')[0]  # Maximum Take-Off Weight [kg]
# }
#
# UAV['GEOMETRY'] = {
#     'b': 1.8,  # Wing Span [m]
#     'A': ds.GetValue('FW_aspectratio', 'values_concept')[0],  # Aspect Ratio
#     'S': ds.GetValue('FW_surfacearea', 'values_concept')[0],  # Surface Area [m^2]
#     'S_fuse': ds.GetValue('S_fuse', 'values_preliminary')[0]  # Surface Area [m^2]
# }
#
# UAV['PARAMETERS'] = {
#     'CLmax': ds.GetValue('FW_clmax', 'values_preliminary')[0],
#     'CLtrim': ds.GetValue('FW_cltrim', 'values_preliminary')[0],
#     'CD0_wing': ds.GetValue('FW_cd0', 'values_preliminary')[0],
#     'CD0_fuse': ds.GetValue('CD0_fuse', 'values_preliminary')[0],  # Assumed value of CD0 from the fuselage
#     'rho_bat': ds.GetValue('rho_bat', 'values_preliminary')[0],  # Assumed energy density of batteries
#     'e': ds.GetValue('FW_e', 'values_preliminary')[0],  # Assumed Oswald Efficiency Factor
#     'W/S': (UAV['WEIGHTS']['MTOW'] * g) / (UAV['GEOMETRY']['S']),  # Wing Loading [N/m2]
#     'P_NP': P_NP  # Non-Propulsive Power Draw Power Draw [W]
# }
#
# # Calculating CD0 of Wing + Fuselage
# UAV['PARAMETERS']['CD0'] = ((UAV['PARAMETERS']['CD0_wing'] * UAV['GEOMETRY']['S']) + (
#     UAV['PARAMETERS']['CD0_fuse'] * UAV['GEOMETRY']['S_fuse'])) / (UAV['GEOMETRY']['S'] + UAV['GEOMETRY']['S_fuse'])
#
# # Calculating Speed
# UAV['PARAMETERS']['V_stall'] = np.round(
#     np.sqrt(UAV['PARAMETERS']['W/S'] * (2 / rho_SL) * (1 / UAV['PARAMETERS']['CLmax'])), 1)
# UAV['PARAMETERS']['V_loiter'] = np.round(
#     np.sqrt(UAV['PARAMETERS']['W/S'] * (2 / rho_SL) * (1 / UAV['PARAMETERS']['CLtrim'])), 1)
# ds.UpdateValue('V_loiter', UAV['PARAMETERS']['V_loiter'], '[m/s]', 'values_preliminary')
# UAV['PARAMETERS']['V_cruise'] = 2.4 * np.sqrt(UAV['PARAMETERS']['W/S'])
#
# # Lift & Drag Analysis --> Power Required
# V = np.linspace(0, 50, 300)
# V = V[np.where(V > 0)]  # Gets rid of the zero in order to avoid div0 Error
# C_L = (UAV['PARAMETERS']['W/S']) / (0.5 * rho_SL * (V ** 2))
# C_D_i = (C_L ** 2) / (np.pi * UAV['GEOMETRY']['A'] * UAV['PARAMETERS']['e'])
# C_D = UAV['PARAMETERS']['CD0'] + C_D_i
# C_D_max = (UAV['PARAMETERS']['CD0']) + (UAV['PARAMETERS']['CLmax'] ** 2) / (
#     np.pi * UAV['GEOMETRY']['A'] * UAV['PARAMETERS']['e'])
# D = C_D * (0.5 * rho_SL * (V ** 2) * UAV['GEOMETRY']['S'])
# PR_par = (UAV['PARAMETERS']['CD0']) * (0.5 * rho_SL * (V ** 3) * UAV['GEOMETRY']['S'])
# PR_ind = C_D_i * (0.5 * rho_SL * (V ** 3) * UAV['GEOMETRY']['S'])
# PR_tot = C_D * (0.5 * rho_SL * (V ** 3) * UAV['GEOMETRY']['S'])
# PR_max = C_D_max * (0.5 * rho_SL * (V ** 3) * UAV['GEOMETRY']['S'])
# LiftRatio = C_L / C_D
# EnduranceRatio = C_L ** 3 / C_D ** 2
#
# # Finding Critical Points
# idx1 = np.argmax(LiftRatio)
# UAV['PARAMETERS']['P_ldmax'] = PR_tot[idx1]
# UAV['PARAMETERS']['V_ldmax'] = V[idx1]
#
# idx2 = np.argmin(np.abs(UAV['PARAMETERS']['V_loiter'] - V))
# UAV['PARAMETERS']['LD_loiter'] = C_L[idx2] / C_D[idx2]
# UAV['PARAMETERS']['P_loiter'] = PR_tot[idx2]
# UAV['PARAMETERS']['CL3/CD2'] = EnduranceRatio[idx2]
# UAV['PARAMETERS']['hdot'] = (330 - PR_tot[idx2]) / (UAV['WEIGHTS']['MTOW'] * g)
#
# idx3 = np.argmin(np.abs(UAV['PARAMETERS']['V_cruise'] - V))
# UAV['PARAMETERS']['LD_cruise'] = C_L[idx3] / C_D[idx3]
# UAV['PARAMETERS']['P_cruise'] = PR_tot[idx3]
#
# idx4 = np.argmin(np.abs(np.array(MAXETA['PER3_10x10E']['V']) - UAV['PARAMETERS']['V_loiter']))
# eta_prop = np.round(MAXETA['PER3_10x10E']['ETA'][idx4], 2)
#
# # Power Required for Climb Requirements
# CLclimb = 0.8 * UAV['PARAMETERS']['CLmax']
# CDclimb = (UAV['PARAMETERS']['CD0']) + ((CLclimb ** 2) / (np.pi * UAV['GEOMETRY']['A'] * UAV['PARAMETERS']['e']))
# WP_CR = eta_prop / (CR + (np.sqrt(UAV['PARAMETERS']['W/S'] * (2 / rho_ceil) * (
#     1 / (
#         1.8084 * (((UAV['GEOMETRY']['A'] * UAV['PARAMETERS']['e']) ** (3 / 2)) / np.sqrt(UAV['PARAMETERS']['CD0'])))))))
# WP_CG = eta_prop / (
#     np.sqrt(UAV['PARAMETERS']['W/S'] * (CG + (CDclimb / CLclimb)) * np.sqrt((2 / rho_SL) * (1 / CLclimb))))
# P_CR = (UAV['WEIGHTS']['MTOW'] * g) / (WP_CR)
# P_CG = (UAV['WEIGHTS']['MTOW'] * g) / (WP_CG)
#
# # Turn Performance
# V_corner = 20
# UAV['PARAMETERS']['n_max'] = ((0.5 * rho_SL * (V_corner ** 2) * UAV['GEOMETRY']['S']) * UAV['PARAMETERS']['CLmax']) / (
#     UAV['WEIGHTS']['MTOW'] * g)
# UAV['PARAMETERS']['PsiDot'] = (g * np.sqrt(UAV['PARAMETERS']['n_max'] ** 2 - 1)) / V_corner
# UAV['PARAMETERS']['R'] = (V_corner ** 2) / (g * np.sqrt((UAV['PARAMETERS']['n_max'] ** 2) - 1))
#
# # Endurance vs. Altitude
# h = np.linspace(0, 3000, 1000)
# rho = []
# for i in h:
#     rho_current = ISA.ISA_m(i)[0]
#     rho.append(rho_current)
# print rho
# P_R_alt = C_D[idx2] * np.sqrt((rho_SL ** 3) / (4 * np.array(rho))) * UAV['GEOMETRY']['S'] * V[idx2] ** 3
#
# print P_R_alt
#
# del WP_CG, WP_CR
#
# # Calculating Range & Endurance
# E_bat = UAV['PARAMETERS']['rho_bat'] * UAV['WEIGHTS']['BAT']
# UAV['PARAMETERS']['Endurance'] = UAV['PARAMETERS']['Endurance'] = (eta_elec * eta_prop * E_bat) / (
#     UAV['PARAMETERS']['P_NP'] + UAV['PARAMETERS']['P_loiter'])
# UAV['PARAMETERS']['Range'] = (eta_elec * eta_prop * E_bat) / (
#     UAV['PARAMETERS']['P_NP'] + UAV['PARAMETERS']['P_cruise']) * UAV['PARAMETERS']['V_cruise'] * 3.6
# UAV['PARAMETERS']['Range_LDMAX'] = (eta_elec * eta_prop * E_bat) / (
#     UAV['PARAMETERS']['P_NP'] + UAV['PARAMETERS']['P_ldmax']) * UAV['PARAMETERS']['V_ldmax'] * 3.6
# t_tot = (eta_elec * eta_prop * E_bat) / (UAV['PARAMETERS']['P_NP'] + P_R_alt)
#
#
# # df = pd.read_csv('PER3_10x7.dat', sep='\s+')
#
# # Printing Outputs for Ease of Reading
# def printdict(obj):
#     if type(obj) == dict:
#         for k, v in obj.items():
#             if hasattr(v, '__iter__'):
#                 print k
#                 printdict(v)
#                 print('')
#             else:
#                 print '%s : %s' % (k, v)
#     elif type(obj) == list:
#         for v in obj:
#             if hasattr(v, '__iter__'):
#                 printdict(v)
#             else:
#                 print v
#     else:
#         print obj
#
# printdict(UAV)
#
# # Plotting
# plt.style.use('ggplot')
#
# plt.figure('AltitudevsPR')
# plt.plot(h, P_R_alt)
# plt.xlabel('Altitude [m]')
# plt.ylabel('Loiter Power Required [W]')
# plt.show()
#
# plt.figure('LDAirspeed')
# plt.plot(V, LiftRatio)
# plt.xlabel('Equivalent Airspeed [m/s]')
# plt.ylabel('Lift to Drag Ratio [-]')
# plt.show()
#
# plt.figure('EndurancevsAltitude')
# plt.plot(t_tot, h)
# plt.xlabel('Endurance [h]')
# plt.ylabel('Altitude [m]')
# plt.show()
#
# # fig = plt.figure('RPMvsAIRSPEEDvsETA')
# # ax = fig.gca(projection='3d')
# # for RPM in sorted(PROP[i].iterkeys(), key=lambda x: float(x)):
# #     RPM_array = np.ones((1,len(PROP['PER3_10x10E'][RPM]['V'][0])))*([float(RPM)])
# #     V_array = 0.44704*np.array(PROP['PER3_10x10E'][RPM]['V'][0])
# #     eta_array = np.array(PROP['PER3_10x10E'][RPM]['Pe'][0])
# #     ax.scatter(RPM_array, V_array, eta_array)
# # ax.set_xlabel('RPM')
# # ax.set_ylabel('Velocity [m/s]')
# # ax.set_zlabel('Propeller Efficiency [-]')
# # plt.plot(0.44704*np.array(PROP['PER3_10x10E']['1000']['V'][0][0:10]),P_BR[1]*np.array(PROP['PER3_10x10E']['1000']['Pe'][0][0:10]))
# # plt.xlabel('Equivalent Airspeed [m/s]')
# # plt.show()
#
#
# plt.figure('AirspeedvsPower')
# # for RPM in sorted(PROP['PER3_10x10E'].iterkeys(), key=lambda x: float(x)):
# #     plt.plot(0.44704*np.array(PROP['PER3_10x10E'][RPM]['V'][0]),(P_BR[0]*np.array(PROP['PER3_10x10E'][RPM]['Pe'][0])), linestyle='--', color='k', linewidth=0.5)
# plt.plot(V, PR_ind, linestyle='--', label='$P_\\mathrm{ind}$')
# plt.plot(V, PR_par, linestyle='--', label='$P_\\mathrm{par}$')
# plt.plot(V, PR_tot, label='$P_R$')
# plt.plot(V, PR_max, label='$P_{R_\\mathrm{max}}$')
# plt.plot(np.append((0.44704*np.array(PROP['PER3_10x10E']['1000']['V'][0])[0:26]),MAXETA['PER3_10x10E']['V']), np.append(P_BR[0]*np.array(PROP['PER3_10x10E']['1000']['Pe'][0][0:26]),P_BR[0]*np.array(MAXETA['PER3_10x10E']['ETA'])), label='$P_A$')
# plt.plot(np.append((0.44704*np.array(PROP['PER3_10x10E']['1000']['V'][0])[0:26]),MAXETA['PER3_10x10E']['V']), np.append(P_BR[1]*np.array(PROP['PER3_10x10E']['1000']['Pe'][0][0:26]),P_BR[1]*np.array(MAXETA['PER3_10x10E']['ETA'])), label='$P_{A_\\mathrm{burst}}$')
# plt.plot(MAXETA['PER3_10x10E']['V'],P_BR[0]*np.array(MAXETA['PER3_10x10E']['ETA']), label='$P_{A_\\mathrm{burst}}$')
# # plt.plot(0.44704*np.array(PROP['PER3_10x10E']['1000']['V'][0])[0:26],P_BR[0]*np.array(PROP['PER3_10x10E']['1000']['Pe'][0][0:26]))
# # # plt.plot(0.44704*np.array(PROP['PER3_10x10E']['1000']['V'][0])[0:26],P_BR[1]*np.array(PROP['PER3_10x10E']['1000']['Pe'][0][0:26]))
# plt.ylabel('Power [W]')
# plt.axis([0, 40, 0, 1000])
# plt.interactive(False)
# plt.grid(True)
# plt.legend()
# tikz_save('AirspeedvsPower.tex')
# plt.show()
#
# plt.figure('ETAvsV')
# for i in MAXETA:
#     plt.plot(MAXETA[i]['V'],MAXETA[i]['ETA'],label=i)
# plt.xlabel('Velocity [m/s]')
# plt.ylabel('Propeller Efficiency [-]')
# plt.axis([0, 50, 0, 1])
# plt.interactive(False)
# plt.grid(True)
# plt.legend(loc='lower right')
# tikz_save('ETAvsV.tex')
# plt.show()
#
#
# np.savetxt('file1.txt', np.c_[V[::3],PR_ind[::3],PR_par[::3],PR_tot[::3],PR_max[::3]], delimiter=',', fmt='%.4e', header='v,pi,pp,pt,pm')
# np.savetxt('file2.txt', np.c_[np.array(MAXETA['PER3_10x10E']['V']),P_BR[0]*np.array(MAXETA['PER3_10x10E']['ETA']),P_BR[1]*np.array(MAXETA['PER3_10x10E']['ETA'])], delimiter=',', fmt='%.4e', header='v,pa,pab')


if __name__ == '__main__':
    from parapy.gui import display

    obj = Performance(label='Performance Analysis')
    display(obj)