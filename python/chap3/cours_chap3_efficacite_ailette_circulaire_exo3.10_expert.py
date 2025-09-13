import numpy as np
from scipy.special import i0, i1, k0, k1
import matplotlib.pyplot as plt

def fin_efficiency_annular(r1, r2, t, h, k):
    m = np.sqrt(2 * h / (k * t))

    # Système pour A et B
    M = np.array([
        [    i0(m * r1),      k0(m * r1)],
        [m * i1(m * r2), -m * k1(m * r2)]  # dθ/dr(r2) = 0 (adiabatique)
    ])
    RHS = np.array([1.0, 0.0])  # θ(r1) = 1, dθ/dr(r2) = 0

    A, B = np.linalg.solve(M, RHS)

    # Dérivée en r = r1
    dtheta_dr_r1 = A * m * i1(m * r1) - B * m * k1(m * r1)

    # Efficacité thermique finale
    eta = -k * t * r1 * dtheta_dr_r1 / (h * (r2**2 - r1**2))
    return eta

def areas(r1, r2, t, H, N):
    """
    Calcule les surfaces
    """
    Af = 2 * np.pi * (r2**2 - r1**2)  # aire de surface totale
    At = N * Af + 2*np.pi*r1*(H-N*t)
    
    return Af, At

# Exemple : Problème de la motocyclette
print("=== Problème de la motocyclette ===")
r1 = 0.025  # m (rayon intérieur)
r2 = 0.045  # m (rayon extérieur)
t = 0.004   # m (épaisseur)
h = 75      # W/m²·K
k = 186     # W/m·K (aluminium 2024-T6)
H = 0.1     # m (Hauteur)
N = 10      # nombre d'ailettes

q_t = 2000 
T_inf =300

# Calcul de l'efficacité
eta_f = fin_efficiency_annular(r1, r2, t, h, k)
Af, At = areas(r1, r2, t, H, N);

print(f"Rayon intérieur r1 = {r1:.3f} m")
print(f"Rayon extérieur r2 = {r2:.3f} m")
print(f"Épaisseur t = {t:.3f} m")
print(f"Coefficient h = {h} W/m²·K")
print(f"Conductivité k = {k} W/m·K")
print()
print("=== Paramètres calculés ===")
print(f"Aire total At = {At:.5f} m²")
print(f"Aire de surface Af = {Af:.5f} m²")
print()
print(f"Efficacité ηf = {eta_f:.3f}")

eta_0 = 1-N*Af/At*(1-eta_f)
print(f"Efficacité η0 = {eta_0:.3f}")

theta_b = q_t/(eta_0 *h*At)

print(f"theta_b = {theta_b:.3f}")
T_b = T_inf + theta_b
print(f"T_b = T_inf + theta_b = {T_b:.3f}K  {T_b-273.15:.3f}C")

theta_b = q_t /(h*2*np.pi*r1*H)
print(f"theta_b sans ailette = {theta_b:.3f}")

T_b = T_inf + theta_b
print(f"T_b sans ailette = {T_b:.3f}K  {T_b-273.15:.3f}C")

print("\n" + "="*50)

# Étude paramétrique : effet du rapport r2/r1
print("\n=== Étude paramétrique ===")
xi_range = np.linspace(1.1, 3.0, 50)
eta_range = []

for xi in xi_range:
    r2_var = xi * r1
    eta = fin_efficiency_annular(r1, r2_var, t, h, k)
    eta_range.append(eta)

# Graphique
plt.figure(figsize=(10, 6))
plt.plot(xi_range, eta_range, 'b-', linewidth=2)
plt.axvline(x=r2/r1, color='r', linestyle='--', alpha=0.7, 
           label=f'Cas motocyclette (ξ = {r2/r1:.2f})')
plt.axhline(y=eta_f, color='r', linestyle='--', alpha=0.7)
plt.xlabel('Rapport des rayons ξ = r₂/r₁')
plt.ylabel('Efficacité ηf')
plt.title('Efficacité d\'ailette annulaire en fonction du rapport des rayons')
plt.grid(True, alpha=0.3)
plt.legend()
plt.ylim(0, 1)
plt.tight_layout()
plt.show()

# Effet de l'épaisseur
print("\n=== Effet de l'épaisseur ===")
t_range = np.linspace(0.002, 0.010, 20)
eta_t = []

for t_var in t_range:
    eta = fin_efficiency_annular(r1, r2, t_var, h, k)
    eta_t.append(eta)

plt.figure(figsize=(10, 6))
plt.plot(t_range*1000, eta_t, 'g-', linewidth=2)
plt.axvline(x=t*1000, color='r', linestyle='--', alpha=0.7,
           label=f'Cas motocyclette (t = {t*1000:.0f} mm)')
plt.axhline(y=eta_f, color='r', linestyle='--', alpha=0.7)
plt.xlabel('Épaisseur t (mm)')
plt.ylabel('Efficacité ηf')
plt.title('Efficacité d\'ailette annulaire en fonction de l\'épaisseur')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()

print(f"\nPour t = {t*1000:.0f} mm : ηf = {eta_f:.3f}")