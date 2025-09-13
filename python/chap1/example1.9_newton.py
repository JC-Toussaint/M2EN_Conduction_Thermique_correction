import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root

# Paramètres
epsilon = 0.5
sigma = 5.67e-8
Tinf, Tsur = 293, 303
G = 2000
alpha = 0.8

def f(Ts, h):
    """Fonction scalaire à annuler"""
    return h * (Ts - Tinf) + epsilon * sigma * (Ts**4 - Tsur**4) - alpha * G

def jac(Ts, h):
    """Dérivée de f par rapport à Ts (jacobien)"""
    return h + 4 * epsilon * sigma * Ts**3

def solve_with_root(hvec):
    Tvec = []
    for h in hvec:
        Tguess = Tinf

        #sol = root(fun=f, x0=Tguess, args=(h,), jac=jac, method='hybr')  # méthode compatible avec un jacobien scalaire
        sol = root(fun=f, x0=Tguess, args=(h,), jac=None, method='hybr')  # méthode compatible avec un jacobien scalaire
        if sol.success:
            Tvec.append(sol.x[0])
        else:
            Tvec.append(np.nan)  # échec de la résolution

    return np.array(Tvec)

# Étude pour h ∈ [2, 100]
hvec = np.linspace(2, 100, 100)

# Méthode : root avec jacobien
Tvec = solve_with_root(hvec)

# Graphique
plt.figure(figsize=(10, 6))
plt.plot(hvec, Tvec - 273, 'r-', label='Ts (root jac)', linewidth=2)
plt.xlabel('$h (W.m^{-2}.K^{-1})$')
plt.ylabel('$T_s$ (°C)')
plt.title('Température de surface en fonction du coefficient de convection')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()
