import numpy as np
import matplotlib.pyplot as plt

# Définir l'intervalle x de 0.01 à 10 (éviter x=0 pour éviter la division par zéro)
x = np.linspace(0.01, 10, 1000)

# Calculer tanh(x)/x
y = np.tanh(x) / x

# Créer le graphique
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label=r'$\frac{\tanh(x)}{x}$')

# Ajouter le point limite en x=0 (limite de tanh(x)/x quand x→0 est 1)
plt.plot(0, 1, 'ro', markersize=8, label='Limite en x=0: 1')

# Configuration du graphique
plt.xlabel('x', fontsize=12)
plt.ylabel(r'$\frac{\tanh(x)}{x}$', fontsize=14)
plt.title(r'Graphique de la fonction $\frac{\tanh(x)}{x}$', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)

# Définir les limites des axes
plt.xlim(0, 10)
plt.ylim(0, 1.1)

# Ajouter quelques annotations pour les valeurs importantes
plt.axhline(y=1, color='r', linestyle='--', alpha=0.5)
plt.text(5, 0.95, 'Limite: 1', fontsize=10, ha='center')

# Afficher le graphique
plt.tight_layout()
plt.show()

# Afficher quelques valeurs numériques
print("Quelques valeurs de tanh(x)/x:")
print("x\t\ttanh(x)/x")
print("-" * 20)
for val in [0.1, 0.5, 1, 2, 5, 10]:
    result = np.tanh(val) / val
    print(f"{val:.1f}\t\t{result:.6f}")

print(f"\nLimite quand x→0: {np.tanh(0.001)/0.001:.6f}")
print(f"Valeur à x=10: {np.tanh(10)/10:.6f}")