import matplotlib.pyplot as plt
import numpy as np

epsilon = 0.5
sigma = 5.67e-8
Tinf, Tsur = 293, 303
G= 2000
alpha = 0.8

def hr(Ts):
    return epsilon*sigma*(Ts+Tsur)*(Ts**2+Tsur**2)

def solve(hvec):
    Tvec =[] 
    for h in hvec:    
        # guess value for Ts    
        Ts = Tinf
        # boucle de convergence (point fixe) 
        for n in range(50):    
            Ts = (alpha*G + h*Tinf + hr(Ts)*Tsur)/(h + hr(Ts))
            print(f'h = {h:.0f} iter = {n:d} Ts = {Ts:.3f}')
        Tvec.append(Ts)
        print('-'*20)
    return np.array(Tvec)

hvec = np.linspace(2, 2, 100)
Tvec = solve(hvec)
       
plt.plot(hvec, Tvec-273, 'r')
plt.xlabel('$h (W.m^{-2}.K^{-1})$')
plt.ylabel('$T_s$ (°C)')
plt.grid()
plt.show()
