import numpy as np
import matplotlib.pyplot as plt

# Données du problème
A = 20.25 * np.pi  # Surface totale (m²)
epsilon = 0.83     # Émissivité
sigma = 5.67e-8    # Constante de Stefan-Boltzmann (W/m²·K⁴)
epsilon_sigma = epsilon * sigma  # ε·σ ≈ 4.71e-8 W/m²·K⁴
h = 35             # Coefficient de convection (W/m²·K)
T_infty = 298      # Température ambiante (K)
T_sur = 293        # Température environnement (K)
q_dot = 0.33e6     # Transfert thermique total (W)

# Plage de températures Ts
Ts = np.linspace(273, 500, 1000)

# Calcul du terme de gauche (transfert thermique calculé)
terme_gauche = A * (epsilon_sigma * (Ts**4 - T_sur**4) + h * (Ts - T_infty))

# Terme de droite (valeur cible)
terme_droite = q_dot * np.ones_like(Ts)

# Différence (terme de gauche - terme de droite)
difference = terme_gauche - terme_droite

# Création du graphique
plt.figure(figsize=(10, 6))
plt.plot(Ts, difference, 'b-', linewidth=2, label='Terme gauche - Terme droite')
plt.axhline(y=0, color='r', linestyle='--', alpha=0.7, label='y = 0')
plt.xlabel('Température de surface Ts (K)')
plt.ylabel('Différence (W)')
plt.title('Résolution graphique de l\'équation de transfert thermique')
plt.grid(True, alpha=0.3)
plt.legend()

# Recherche de la solution (zéro de la fonction)
# Trouvons l'indice où la différence change de signe
zero_crossings = np.where(np.diff(np.sign(difference)))[0]
if len(zero_crossings) > 0:
    idx = zero_crossings[0]
    Ts_solution = Ts[idx]
    print(f"Solution approximative: Ts ≈ {Ts_solution:.1f} K ({Ts_solution-273:.1f}°C)")
    
    # Marquage de la solution sur le graphique
    plt.plot(Ts_solution, 0, 'ro', markersize=8, label=f'Solution: {Ts_solution:.1f} K')
    plt.legend()

plt.tight_layout()
plt.show()

# Affichage des valeurs numériques utilisées
print(f"\nValeurs utilisées:")
print(f"A = {A:.2f} m²")
print(f"ε·σ = {epsilon_sigma:.2e} W/m²·K⁴")
print(f"h = {h} W/m²·K")
print(f"T∞ = {T_infty} K")
print(f"T_sur = {T_sur} K")
print(f"q̇ = {q_dot:.2e} W")