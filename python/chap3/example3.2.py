import matplotlib.pyplot as plt
import numpy as np

Tinf = 298
qc_pp = 1e4 
h =100
L = 8e-3
k = 239

def solve(Rtc_pp_vec):
    Tc_vec =[] 
    for Rtc_pp in Rtc_pp_vec:       
        Tc = Tinf + qc_pp/(h+ 1/(Rtc_pp + L/k +1/h))
        Tc_vec.append(Tc)
    return np.array(Tc_vec)

Rtc_pp_vec = np.linspace(0.2e-4, 0.9e-4, 100)
Tc_vec = solve(Rtc_pp_vec)
       
plt.plot(Rtc_pp_vec, Tc_vec-273, 'r')
plt.xlabel('$R_{tc}'' (m^{2}.K.W^{-1})$')
plt.ylabel('$Tc$ (°C)')
plt.grid()
plt.show()
