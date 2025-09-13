import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# Constantes
h = 2
epsilon = 0.95
sigma = 5.670374419e-8
Ti, Tinf, Tsur = 308, 297, 297
k = 0.3
L, A = 3e-3, 1.8

# Définition du coefficient de rayonnement
def hr(Ts):
    return epsilon * sigma * (Ts + Tsur) * (Ts**2 + Tsur**2)

# Fonction de point fixe : Ts = f(Ts)
def f_point_fixe(Ts):
    return (k/L*Ti + h*Tinf + hr(Ts)*Tsur) / (k/L + h + hr(Ts))

# Tracé de la fonction Ts = f(Ts)
Ts_vals = np.linspace(295, 310, 300)
f_vals = f_point_fixe(Ts_vals)

plt.figure(figsize=(8,6))
plt.plot(Ts_vals, f_vals, label=r"$f(T_s)$", color='blue')
#plt.plot(Ts_vals, Ts_vals, label=r"$T_s$", color='red', linestyle='--')  # ligne diagonale
plt.xlabel("Ts (K)")
plt.ylabel("f(Ts)")
plt.title("Méthode graphique pour trouver $T_s$")
plt.grid(True)
plt.legend()
plt.show()