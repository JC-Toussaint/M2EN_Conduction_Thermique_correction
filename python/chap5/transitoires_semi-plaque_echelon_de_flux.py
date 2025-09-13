import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc
import matplotlib.patches as mpatches

# Propriétés thermiques du silicium
rho = 2330  # kg/m³ - densité
c = 700     # J/(kg·K) - chaleur spécifique
k = 149     # W/(m·K) - conductivité thermique
alpha = k / (rho * c)  # m²/s - diffusivité thermique

# Conditions du problème
T_inf = 300  # K - température initiale
q_s = 100    # W/m² - flux de chaleur imposé

def ierfc(u):
    return (1/np.sqrt(np.pi)) * np.exp(-u**2) - u * erfc(u)

def temperature_distribution(x, t):
    if t <= 0:
        return T_inf * np.ones_like(x)
    eta = x / (2 * np.sqrt(alpha * t))
    return T_inf + (2 * q_s * np.sqrt(alpha * t)) / (k * np.sqrt(np.pi)) * ierfc(eta)

# Domaine spatial
x_max = 0.05  # 5 cm
x = np.linspace(0, x_max, 500)

# Temps à représenter
times = [1, 5, 10, 30, 60, 300]

# Tracé
plt.figure(figsize=(8,6))
for t in times:
    T = temperature_distribution(x, t)
    plt.plot(x*1000, T, label=f't = {t} s')

plt.xlabel('Position x (mm)')
plt.ylabel('Température T (K)')
plt.title('Distribution de température dans le silicium')
plt.grid(True)
plt.legend()
plt.show()
