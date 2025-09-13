import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Paramètres physiques pour le cuivre
rho = 8960  # kg/m³
c = 385  # J/(kg·K)

# Paramètres du problème
D = 1e-3  # m
Re = 0.4  # Ω/m
Tsur = 300  # K
Tinf = 300  # K
h = 10  # W/(m²·K)
epsilon = 0.8
sigma = 5.67e-8  # W/(m²·K⁴)

# Courant électrique
I = 10  # A

def dT_dt(t, T):
    Tval = T[0]
    terme_joule = Re * I**2
    terme_convection = h * (Tval - Tinf) * np.pi * D
    terme_rayonnement = epsilon * sigma * (Tval**4 - Tsur**4) * np.pi * D
    capacite_thermique = rho * c * (np.pi * D**2) / 4
    dTdt = (terme_joule - terme_convection - terme_rayonnement) / capacite_thermique
    return [dTdt]

# Conditions initiales et temps
T0 = [300]  # K
t_span = (0, 1000)  # intervalle de temps
t_eval = np.linspace(t_span[0], t_span[1], 1000)  # points d'évaluation

# Résolution avec RK45
solution_rk45 = solve_ivp(dT_dt, t_span, T0, t_eval=t_eval, method='RK45', rtol=1e-8, atol=1e-10)

# Tracé de l'évolution de la température avec le temps
plt.figure(figsize=(10, 6))
plt.plot(solution_rk45.t, solution_rk45.y[0]-273, 'b-', linewidth=2, label='RK45')
plt.xlabel('Temps (s)')
plt.ylabel('Température (C)')
plt.title(f'Évolution de la température avec le temps I={I:.2f} A, h={h:.2f}')
plt.grid(True, alpha=0.3)


tau = rho*c*(0.25*np.pi*D**2)/(h*np.pi*D)
Tana = Tinf + Re*I**2/(h*np.pi*D) *(1-np.exp(-t_eval/tau))
plt.plot(t_eval, Tana-273, 'r-', linewidth=2, label='ana')
plt.legend()
plt.show()