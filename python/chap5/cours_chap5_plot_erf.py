import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf, erfc

# Configuration des paramètres du graphique
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Création de l'intervalle [-10, 10] avec 1000 points
x = np.linspace(-10, 10, 1000)

# Calcul des fonctions erf et erfc
y_erf = erf(x)
y_erfc = erfc(x)

# Création de la figure avec deux sous-graphiques
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

# Graphique de la fonction erf
ax1.plot(x, y_erf, 'b-', linewidth=2, label='erf(x)')
ax1.grid(True, alpha=0.3)
ax1.set_xlabel('x')
ax1.set_ylabel('erf(x)')
ax1.set_title('Fonction d\'erreur erf(x)', fontsize=14, fontweight='bold')
ax1.legend()
ax1.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax1.axvline(x=0, color='k', linestyle='-', alpha=0.3)
ax1.set_ylim(-1.1, 1.1)
ax1.text(0.02, 0.95, 'erf(x) = (2/√π) ∫₀ˣ e⁻ᵗ² dt', 
         transform=ax1.transAxes, fontsize=10, 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))

# Graphique de la fonction erfc
ax2.plot(x, y_erfc, 'r-', linewidth=2, label='erfc(x)')
ax2.grid(True, alpha=0.3)
ax2.set_xlabel('x')
ax2.set_ylabel('erfc(x)')
ax2.set_title('Fonction d\'erreur complémentaire erfc(x)', fontsize=14, fontweight='bold')
ax2.legend()
ax2.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax2.axvline(x=0, color='k', linestyle='-', alpha=0.3)
ax2.set_ylim(-0.1, 2.1)
ax2.text(0.02, 0.95, 'erfc(x) = 1 - erf(x)', 
         transform=ax2.transAxes, fontsize=10,
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.7))

# Ajustement de l'espacement entre les sous-graphiques
plt.tight_layout()

# Création d'un graphique combiné
fig2, ax3 = plt.subplots(1, 1, figsize=(12, 8))
ax3.plot(x, y_erf, 'b-', linewidth=2, label='erf(x)')
ax3.plot(x, y_erfc, 'r-', linewidth=2, label='erfc(x)')
ax3.grid(True, alpha=0.3)
ax3.set_xlabel('x', fontsize=12)
ax3.set_ylabel('y', fontsize=12)
ax3.set_title('Fonctions erf(x) et erfc(x) sur [-10, 10]', fontsize=14, fontweight='bold')
ax3.legend(fontsize=12)
ax3.axhline(y=0, color='k', linestyle='-', alpha=0.3)
ax3.axvline(x=0, color='k', linestyle='-', alpha=0.3)
ax3.axhline(y=1, color='k', linestyle='--', alpha=0.5)

# Ajout de points remarquables
ax3.plot(0, erf(0), 'go', markersize=8, label='erf(0) = 0')
ax3.plot(0, erfc(0), 'mo', markersize=8, label='erfc(0) = 1')

# Ajout d'annotations
ax3.annotate('erf(0) = 0', xy=(0, 0), xytext=(2, 0.3),
            arrowprops=dict(arrowstyle='->', color='green', alpha=0.7),
            fontsize=10, color='green')
ax3.annotate('erfc(0) = 1', xy=(0, 1), xytext=(2, 1.3),
            arrowprops=dict(arrowstyle='->', color='purple', alpha=0.7),
            fontsize=10, color='purple')

# Information sur les propriétés
info_text = """Propriétés importantes :
• erf(x) + erfc(x) = 1
• erf(-x) = -erf(x) (fonction impaire)
• erfc(-x) = 2 - erfc(x)
• lim(x→∞) erf(x) = 1
• lim(x→∞) erfc(x) = 0"""

ax3.text(0.65, 0.15, info_text, transform=ax3.transAxes, fontsize=10,
         bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
         verticalalignment='bottom')

plt.tight_layout()

# Affichage des graphiques
plt.show()

# Affichage de quelques valeurs remarquables
print("Valeurs remarquables :")
print(f"erf(0) = {erf(0):.6f}")
print(f"erfc(0) = {erfc(0):.6f}")
print(f"erf(1) = {erf(1):.6f}")
print(f"erfc(1) = {erfc(1):.6f}")
print(f"erf(2) = {erf(2):.6f}")
print(f"erfc(2) = {erfc(2):.6f}")
print(f"erf(-1) = {erf(-1):.6f}")
print(f"erfc(-1) = {erfc(-1):.6f}")

# Vérification de la relation erf(x) + erfc(x) = 1
x_test = np.array([0, 1, -1, 2, -2])
for val in x_test:
    somme = erf(val) + erfc(val)
    print(f"erf({val}) + erfc({val}) = {somme:.10f}")