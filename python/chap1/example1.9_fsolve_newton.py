import matplotlib.pyplot as plt
import numpy as np

epsilon = 0.5
sigma = 5.67e-8
Tinf, Tsur = 293, 303
G= 2000
alpha = 0.8

def f(Ts, h):
    return h*(Ts-Tinf)+epsilon*sigma*(Ts**4-Tsur**4)-alpha*G

def J(Ts, h):
    return h*Ts+4*epsilon*sigma*Ts**3

def solve(hvec):
    tol = 1e-6
    Tvec =[] 
    for h in hvec:    
        # guess value for Ts    
        Ts = Tinf
        # boucle de convergence (point fixe) 
        while True:    
            dTs = -f(Ts, h)/J(Ts, h)
            Ts += dTs 
            if abs(dTs < tol):
                break
        Tvec.append(Ts)
    return np.array(Tvec)

hvec = np.linspace(2, 100, 100)
Tvec = solve(hvec)
       
plt.plot(hvec, Tvec-273, 'r')
plt.xlabel('$h\; (W.m^{-2}.K^{-1})$')
plt.ylabel('$T_s$ (°C)')
plt.grid()
plt.show()
