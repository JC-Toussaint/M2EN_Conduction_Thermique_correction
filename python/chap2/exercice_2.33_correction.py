import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

Q = 10
L = 1
h = 8
Tinf = 30 + 273.15
Tsur = 20 + 273.15
sigma = 5.67e-8
eps = 0.95
Gs = 500

def equation(Ts):
    """
    Équation à résoudre: Q×L - h(Ts - Tinf) + eps × Gs - eps × sigma × (Ts^4 - Tsur^4) = 0
    """
    term1 = Q * L
    term2 = -h * (Ts - Tinf)
    term3 = eps * Gs
    term4 = -eps * sigma * (Ts**4 - Tsur**4)
    
    return term1 + term2 + term3 + term4

# Résolution numérique
# Estimation initiale proche de 303K (température de référence dans l'équation)
initial_guess = 350  # Kelvin

solution = fsolve(equation, initial_guess)[0]

print("=== RÉSOLUTION DE L'ÉQUATION THERMIQUE ===")
print(f"Équation: 10×1 - 8(Ts - 303) + 0.95×500 - 0.95×5.67×10⁻⁸×(Ts⁴ - 293⁴) = 0")
print()
print(f"Solution trouvée: Ts = {solution:.2f} K")
print(f"                    = {solution - 273.15:.2f} °C")
print()

# Vérification de la solution
result = equation(solution)
print(f"Vérification: f({solution:.2f}) = {result:.2e}")

# Décomposition des termes pour analyse
print("\n=== ANALYSE DES TERMES ===")
Ts = solution
term1 = Q * L
term2 = -h * (Ts - Tinf)
term3 = eps * Gs
term4 = -eps * sigma * (Ts**4 - Tsur**4)

print(f"Terme 1 (Q L):                     {term1:.2f}")
print(f"Terme 2 (-h (Ts-Tinf)):               {term2:.2f}")
print(f"Terme 3 (eps Gs):                 {term3:.2f}")
print(f"Terme 4 (-eps sigma (Ts⁴-Tsur⁴)): {term4:.2f}")
print(f"Somme totale:                        {term1 + term2 + term3 + term4:.2f}")

# Graphique de la fonction
Ts_range = np.linspace(250, 450, 1000)
y_values = [equation(T) for T in Ts_range]

plt.figure(figsize=(10, 6))
plt.plot(Ts_range, y_values, 'b-', linewidth=2, label='f(Ts)')
plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
plt.axvline(x=solution, color='r', linestyle='--', alpha=0.7, label=f'Solution: Ts = {solution:.2f} K')
plt.plot(solution, equation(solution), 'ro', markersize=8, label=f'Racine')
plt.xlabel('Température Ts (K)')
plt.ylabel('f(Ts)')
plt.title('Graphique de la fonction thermique')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(280, 400)
plt.ylim(-100, 100)

# Zoomer autour de la solution
y_min = min([abs(y) for y in y_values if abs(y) < 50])
plt.ylim(-50, 50)

plt.tight_layout()
plt.show()

print(f"\n=== INTERPRÉTATION PHYSIQUE ===")
print(f"- La température d'équilibre est: {solution:.1f} K ({solution-273.15:.1f}°C)")