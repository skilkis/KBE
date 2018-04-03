#test
import numpy as np
from math import *
import matplotlib.pyplot as plt



C_Lmax = [1, 1.25, 1.5]


rho = 1.225             #ISA SL Density
rho_cr = 0.9091         #ISA density at 3000m.

V_s_hand = 8            #Assumed Hand Launched Stall Speed
V_s_nonhand = 20        #Assiumed Non-Hand-Launched Stall Speed
## Wing Loading Requirements For Stall Speed for Various C_Lmax
WsStall_hand_1 = 0.5*rho*C_Lmax[0]*V_s_hand**2 #Array of 3 wing loadings with various cl max
WsStall_hand_2 = 0.5*rho*C_Lmax[1]*V_s_hand**2 #Array of 3 wing loadings with various cl max
WsStall_hand_3 = 0.5*rho*C_Lmax[2]*V_s_hand**2 #Array of 3 wing loadings with various cl max
# at hand launched stall speed.
WsStall_nonhand_1 = 0.5*rho*C_Lmax[0]*V_s_nonhand**2 #Array of 3 wing loadings with various cl max
WsStall_nonhand_2 = 0.5*rho*C_Lmax[1]*V_s_nonhand**2 #Array of 3 wing loadings with various cl max
WsStall_nonhand_3 = 0.5*rho*C_Lmax[2]*V_s_nonhand**2 #Array of 3 wing loadings with various cl max
# at non hand launched stall speed.




##Power Loading
RC = 1.524              #Climb rate assumed equal to thst of Sparta UAV 1.1.2.
n_p = 0.7               #Assumed Propellor Efficiency.
C_D0 = 0.02             #Assumed Zero Lift Drag Coefficient.
AR = [6 , 9 , 12]       #Assumed Range for Aspect Ratio to create design space.
G = 0.507               #Climb Gradient to just clear 10m high object 17m away
e_factor = 0.8



Ws_range = np.linspace(1,400,100)  #Dummy array for iterating in W/P Equations Below.

## Calculate Required Power for Climb Rate Requirement at 3000 m for various AR.
WpCr_1 = []  #Empty List for appending W/P Data for AR[0]
for i in range(0,len(Ws_range)):
    WpCri_1 = n_p/(RC+ sqrt(Ws_range[i]*(2.0/rho_cr)*(sqrt(C_D0)/(1.81*((AR[0]*e)**(3.0/2.0))))))
    WpCr_1.append(WpCri_1)  #Above is calculation of W/P for Rate of Climb at 3km alt.

WpCr_2 = []  #Empty List for appending W/P Data for AR[1].
for i in range(0,len(Ws_range)):
    WpCri_2 = n_p/(RC+ sqrt(Ws_range[i]*(2.0/rho_cr)*(sqrt(C_D0)/(1.81*((AR[1]*e)**(3.0/2.0))))))
    WpCr_2.append(WpCri_2) #Above is calculation of W/P for Rate of Climb at 3km alt.

WpCr_3 = []  #Empty List for appending W/P Data for AR[2].
for i in range(0,len(Ws_range)):
    WpCri_3 = n_p/(RC+ sqrt(Ws_range[i]*(2.0/rho_cr)*(sqrt(C_D0)/(1.81*((AR[2]*e)**(3.0/2.0))))))
    WpCr_3.append(WpCri_3)  #Above is calculation of W/P for Rate of Climb at 3km alt.



## Below are the Equations for the Required Climb Gradient of G

C_Lcg = [C_Lmax[0] - 0.2, C_Lmax[1] - 0.2, C_Lmax[2] - 0.2 ]  #subtracting 0.2 from climb gradient C_l to keep away from stall during climb out


C_D = [] #For loop to generate C_D for Climb Gradient Equation, assuming
for i in range(0, len(C_Lcg)):
    C_D1 = C_D0 + C_Lcg[i]**2/ (pi*AR[i]*e_factor)
    C_D.append(C_D1)

WpCg_1 = []
for i in range(0,len(Ws_range)):
    WpCgi_1 = n_p/(sqrt(Ws_range[i]*(2.0/rho)*(1/C_Lcg[0]))*(G+(C_D[0]/C_Lcg[0])))
    WpCg_1.append(WpCgi_1)
WpCg_2 = []
for i in range(0,len(Ws_range)):
    WpCgi_2 = n_p/(sqrt(Ws_range[i]*(2.0/rho)*(1/C_Lcg[1]))*(G+(C_D[1]/C_Lcg[1])))
    WpCg_2.append(WpCgi_2)
WpCg_3 = []
for i in range(0,len(Ws_range)):
    WpCgi_3 = n_p/(sqrt(Ws_range[i]*(2.0/rho)*(1/C_Lcg[2]))*(G+(C_D[2]/C_Lcg[2])))
    WpCg_3.append(WpCgi_3)


plt.plot(Ws_range,WpCr_1,'b', label = 'RC, AR = 6')
plt.plot(Ws_range,WpCr_2,'g', label = 'RC, AR = 9')
plt.plot(Ws_range,WpCr_3,'r', label = 'RC, AR = 12')

plt.plot(Ws_range,WpCg_1,'b.', label = 'Gradient, C_L = 0.8')
plt.plot(Ws_range,WpCg_2,'g.', label = 'Gradient, C_L = 1.05')
plt.plot(Ws_range,WpCg_3,'r.', label = 'Gradient, C_L = 1.3')

plt.axvline(x= WsStall_hand_1, label = 'C_Lmax_h = 1', color = 'c')
plt.axvline(x= WsStall_hand_2, label = 'C_Lmax_h = 1.25', color = 'm')
plt.axvline(x= WsStall_hand_3,  label = 'C_Lmax_h = 1.5', color = 'y')
plt.axvline(x= WsStall_nonhand_1, label = 'C_Lmax_nh = 1', color = 'c')
plt.axvline(x= WsStall_nonhand_2, label = 'C_Lmax_nh = 1.25', color = 'm')
plt.axvline(x= WsStall_nonhand_3,  label = 'C_Lmax_nh = 1.5', color = 'y')
plt.ylabel('W/P [N*W^-1]')
plt.xlabel('W/S [N*m^-2]')
plt.legend()
plt.title('Wing and Power Loading (RC = 1 m/s)')
plt.show()



