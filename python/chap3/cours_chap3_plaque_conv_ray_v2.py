import matplotlib.pyplot as plt
import numpy as np

epsilon = 0.95
sigma = 5.67e-8
Tinf, Tsur = 283, 283
q = 100 
A = 1.8
def hr(Ts):
    return epsilon*sigma*(Ts+Tsur)*(Ts**2+Tsur**2)

def solve(hvec):
    Tvec =[] 
    for h in hvec:
        # guess value for T   
        T = Tinf
        # boucle de convergence (point fixe) 
        for n in range(10): 
            T = (q/A + h*Tinf + hr(T)*Tsur)/(h + hr(T))
        Tvec.append(T)
    return np.array(Tvec)

hvec = np.linspace(2, 200, 100)
Tvec = solve(hvec)

plt.plot(hvec, Tvec-273, 'r')
plt.xlabel('$h (W.m^{-2}.K^{-1})$')
plt.ylabel('$T$ (°C)')
plt.grid()
plt.show()
plt.figure()
plt.plot(Tvec, hr(Tvec), 'r')
plt.grid()
plt.show()

ksf = 0.3 
Lsf = 3e-3
Ti = 308
kins = 0.014
Rsf = Lsf/(ksf*A)
Ts = Ti-q*Rsf
print('Ts = ', Ts-273)

Lins = kins * A* (Ts-Tvec)/q
plt.plot(hvec, Lins, 'b')
plt.xlabel('$h (W.m^{-2}.K^{-1})$')
plt.ylabel('$Lins$ (m)')
plt.grid()
plt.show()

