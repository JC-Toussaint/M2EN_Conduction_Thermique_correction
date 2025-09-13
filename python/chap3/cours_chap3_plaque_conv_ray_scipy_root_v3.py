import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root

epsilon = 0.95
sigma = 5.67e-8
Tinf, Tsur = 283, 283
q = 100
A = 1.8

def hr(Ts):
    return epsilon*sigma*(Ts+Tsur)*(Ts**2+Tsur**2)

def equation(T, h):
    """Équation à résoudre : T = (q/A + h*Tinf + hr(T)*Tsur)/(h + hr(T))
    Réarrangée sous la forme f(T) = 0"""
    return T - (q/A + h*Tinf + hr(T)*Tsur)/(h + hr(T))

def solve(hvec):
    Tvec = []
    for h in hvec:
        # Résolution avec scipy.optimize.root
        result = root(equation, x0=Tinf, args=(h,), method='hybr')
        if result.success:
            Tvec.append(result.x[0])
        else:
            print(f"Convergence échouée pour h={h}")
            Tvec.append(Tinf)  # valeur par défaut
    return np.array(Tvec)

hvec = np.linspace(2, 200, 100)
Tvec = solve(hvec)

plt.figure(figsize=(10, 6))
plt.plot(hvec, Tvec-273, 'r', linewidth=2)
plt.xlabel('$h (W.m^{-2}.K^{-1})$')
plt.ylabel('$T$ (°C)')
plt.title('Température en fonction du coefficient de convection')
plt.grid(True, alpha=0.3)
plt.show()

plt.figure(figsize=(10, 6))
plt.plot(Tvec, hr(Tvec), 'r', linewidth=2)
plt.xlabel('$T$ (K)')
plt.ylabel('$h_r (W.m^{-2}.K^{-1})$')
plt.title('Coefficient de rayonnement en fonction de la température')
plt.grid(True, alpha=0.3)
plt.show()

ksf = 0.3
Lsf = 3e-3
Ti = 308
kins = 0.014
Rsf = Lsf/(ksf*A)
Ts = Ti-q*Rsf
print('Ts = ', Ts-273)

Lins = kins * A* (Ts-Tvec)/q
plt.figure(figsize=(10, 6))
plt.plot(hvec, Lins, 'b', linewidth=2)
plt.xlabel('$h (W.m^{-2}.K^{-1})$')
plt.ylabel('$Lins$ (m)')
plt.title('Épaisseur d\'isolation en fonction du coefficient de convection')
plt.grid(True, alpha=0.3)
plt.show()