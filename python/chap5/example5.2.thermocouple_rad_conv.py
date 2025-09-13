import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Constantes physiques
sigma = 5.67e-8  # Constante de Stefan-Boltzmann [W/(m²·K⁴)]

# Paramètres du thermocouple
D = 0.7e-3       # Diamètre [m]
rho = 8500       # Densité [kg/m³]
c = 400          # Capacité calorifique [J/(kg·K)]
epsilon = 0.9    # Émissivité

# Conditions aux limites
T_infty = 200 + 273.15    # Température du gaz [K]
T_sur = 400 + 273.15      # Température des parois [K]
h = 400                   # Coefficient de convection [W/(m²·K)]

# Condition initiale
T_i = 25 + 273.15         # Température initiale [K]

# Calcul des surfaces et volume
A_s = np.pi * D**2        # Surface [m²]
V = np.pi * D**3 / 6      # Volume [m³]

def ode(t, y):
    """
    Équation différentielle à résoudre:
    -[h(T - T_∞) + εσ(T⁴ - T_sur⁴)]A_s = ρVc dT/dt
    
    Réarrangée:
    dT/dt = -[h(T - T_∞) + εσ(T⁴ - T_sur⁴)]A_s / (ρVc)
    
    Note: solve_ivp utilise la signature (t, y) contrairement à odeint qui utilisait (y, t)
    """
    T = y[0]  # Température actuelle
    
    convection = h * (T - T_infty)
    radiation = epsilon * sigma * (T**4 - T_sur**4)
    
    dT_dt = -(convection + radiation) * A_s / (rho * V * c)
    
    return [dT_dt]

# Temps de simulation
t_max = 10  # secondes
t_span = (0, t_max)  # Intervalle de temps
t_eval = np.linspace(0, t_max, 1000)  # Points d'évaluation

# Résolution de l'équation différentielle avec solve_ivp
solution = solve_ivp(ode, t_span, [T_i], t_eval=t_eval, 
                    method='RK45', rtol=1e-8, atol=1e-10)

# Extraction des résultats
t = solution.t
T_solution = solution.y[0]

# Conversion en Celsius pour l'affichage
T_celsius = T_solution - 273.15

# Calcul de la température de régime permanent
# À l'équilibre: dT/dt = 0, donc h(T_ss - T_∞) + εσ(T_ss⁴ - T_sur⁴) = 0
def equilibrium_equation(T):
    return h * (T - T_infty) + epsilon * sigma * (T**4 - T_sur**4)

# Résolution numérique pour trouver T_steady_state
from scipy.optimize import fsolve
T_ss = fsolve(equilibrium_equation, T_infty)[0]
T_ss_celsius = T_ss - 273.15

# Trouver le temps pour atteindre T_ss - 1°C
target_temp = T_ss - 1.0  # 1°C de moins que la température de régime permanent
idx = np.where(T_solution >= target_temp)[0]
if len(idx) > 0:
    t_target = t[idx[0]]
else:
    t_target = None

# Affichage des résultats
print("=== RÉSULTATS ===")
print(f"Température de régime permanent: {T_ss_celsius:.2f} °C")
print(f"Température initiale: {T_i - 273.15:.2f} °C")
print(f"Température finale simulée: {T_celsius[-1]:.2f} °C")
print(f"Statut de l'intégration: {solution.message}")

if t_target is not None:
    print(f"Temps pour atteindre {T_ss_celsius - 1:.2f} °C: {t_target:.2f} secondes")
else:
    print("Temps pour atteindre la température cible: > 300 secondes")

# Graphique
plt.figure(figsize=(10, 6))
plt.plot(t, T_celsius, 'b-', linewidth=2, label='Température de la jonction')
plt.axhline(y=T_ss_celsius, color='r', linestyle='--', label=f'Régime permanent ({T_ss_celsius:.1f} °C)')
plt.axhline(y=T_ss_celsius - 1, color='g', linestyle=':', label=f'Cible ({T_ss_celsius - 1:.1f} °C)')

if t_target is not None:
    plt.axvline(x=t_target, color='g', linestyle=':', alpha=0.7)
    plt.plot(t_target, T_ss_celsius - 1, 'go', markersize=8)

plt.xlabel('Temps (s)')
plt.ylabel('Température (°C)')
plt.title('Évolution de la température du thermocouple')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(0, t_max)
plt.show()

# Vérification du bilan énergétique à l'équilibre
print("\n=== VÉRIFICATION ===")
conv_equilibrium = h * (T_ss - T_infty) * A_s
rad_equilibrium = epsilon * sigma * (T_ss**4 - T_sur**4) * A_s
print(f"Flux de convection à l'équilibre: {conv_equilibrium:.6f} W")
print(f"Flux de rayonnement à l'équilibre: {rad_equilibrium:.6f} W")
print(f"Somme (doit être ≈ 0): {conv_equilibrium + rad_equilibrium:.2e} W")