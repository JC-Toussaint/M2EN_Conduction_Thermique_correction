import numpy as np
import matplotlib.pyplot as plt
from scipy.special import i0, i1, k0, k1

# Définir l'intervalle
x = np.linspace(0.01, 10, 1000)  # On évite x=0 pour K0 et K1 qui divergent
x_with_zero = np.linspace(0, 10, 1000)  # Pour I0 et I1 qui sont définies en 0

# Calculer les fonctions de Bessel modifiées
I0_vals = i0(x_with_zero)
I1_vals = i1(x_with_zero)
K0_vals = k0(x)
K1_vals = k1(x)

# Créer les graphiques
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 6))

# Fonction I0
ax1.plot(x_with_zero, I0_vals, 'b-', linewidth=2, label='I₀(x)')
ax1.set_xlabel('x')
ax1.set_ylabel('I₀(x)')
ax1.set_title('Fonction de Bessel modifiée I₀(x)')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_xlim(0, 10)

# Fonction I1
ax2.plot(x_with_zero, I1_vals, 'r-', linewidth=2, label='I₁(x)')
ax2.set_xlabel('x')
ax2.set_ylabel('I₁(x)')
ax2.set_title('Fonction de Bessel modifiée I₁(x)')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_xlim(0, 10)

# Fonction K0
ax3.plot(x, K0_vals, 'g-', linewidth=2, label='K₀(x)')
ax3.set_xlabel('x')
ax3.set_ylabel('K₀(x)')
ax3.set_title('Fonction de Bessel modifiée K₀(x)')
ax3.grid(True, alpha=0.3)
ax3.legend()
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 5)  # Limiter l'axe y pour une meilleure visualisation

# Fonction K1
ax4.plot(x, K1_vals, 'm-', linewidth=2, label='K₁(x)')
ax4.set_xlabel('x')
ax4.set_ylabel('K₁(x)')
ax4.set_title('Fonction de Bessel modifiée K₁(x)')
ax4.grid(True, alpha=0.3)
ax4.legend()
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 5)  # Limiter l'axe y pour une meilleure visualisation

plt.tight_layout()
plt.show()

# Afficher quelques valeurs numériques
print("Valeurs des fonctions de Bessel modifiées en quelques points:")
print("x\t\tI₀(x)\t\tI₁(x)\t\tK₀(x)\t\tK₁(x)")
print("-" * 60)
for xi in [0.5, 1.0, 2.0, 5.0, 8.0]:
    if xi == 0:
        print(f"{xi:.1f}\t\t{i0(xi):.4f}\t\t{i1(xi):.4f}\t\t∞\t\t∞")
    else:
        print(f"{xi:.1f}\t\t{i0(xi):.4f}\t\t{i1(xi):.4f}\t\t{k0(xi):.4f}\t\t{k1(xi):.4f}")