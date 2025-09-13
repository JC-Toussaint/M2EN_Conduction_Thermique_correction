import numpy as np
import matplotlib.pyplot as plt

# Paramètres
T_s = 100     # Température de surface à adapter
Q = 10      # Source de chaleur
L = 1       # Longueur
k = 0.26    # Conductivité thermique

# Création du vecteur x
x = np.linspace(0, L, 100)

# Calcul de T(x)
T = T_s + (Q * L**2)/(2 * k) * (1 - (x**2)/(L**2))

# Tracé du graphique
plt.figure(figsize=(10, 6))
plt.plot(T, x, 'b-', linewidth=2)
plt.ylabel('x', fontsize=18)
plt.xlabel('T(x)', fontsize=18)
plt.title('Distribution de température T(x)')
plt.grid(True, alpha=0.3)
plt.legend()

# Ajout des valeurs des paramètres sur le graphique
plt.text(100, 0.5, f'$T_s$ = {T_s} par ex.\n$Q$ = {Q}\n$L$ = {L}\n$k$ = {k}', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat", alpha=0.8), fontsize=18)

# Affichage des valeurs particulières
print(f"T(0) = {T[0]:.3f}")
print(f"T(L/2) = {T[len(T)//2]:.3f}")
print(f"T(L) = {T[-1]:.3f}")

plt.tight_layout()
plt.show()