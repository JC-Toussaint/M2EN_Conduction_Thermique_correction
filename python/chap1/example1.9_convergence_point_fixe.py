import sympy as sp
import numpy as np
import matplotlib.pyplot as plt

# Définir les symboles
Ts, Tsur, alpha, epsilon, G, h, sigma = sp.symbols('Ts Tsur alpha epsilon G h sigma', real=True, positive=True)

# Définir hr(Ts) = ε·σ·(Ts + Tsur)·(Ts² + Tsur²)
# Pour simplifier, on utilise hr_coeff au lieu de ε·σ
hr = epsilon * sigma * (Ts + Tsur) * (Ts**2 + Tsur**2)

print("Expression de hr(Ts):")
print(f"hr(Ts) = {hr}")
print()

# Définir l'expression g(Ts) à partir de l'équation Ts = g(Ts)
# Ts = (αG + hT∞ + hr(Ts)Tsur) / (h + hr(Ts))
# On définit Tinf comme un symbole supplémentaire
Tinf = sp.symbols('Tinf', real=True)

numerateur = alpha * G + h * Tinf + hr * Tsur
denominateur = h + hr

g_Ts = numerateur / denominateur

print("Expression de g(Ts):")
print(f"g(Ts) = {g_Ts}")
print()

# Calculer la dérivée g'(Ts)
g_prime = sp.diff(g_Ts, Ts)

print("Dérivée g'(Ts):")
print(f"g'(Ts) = {g_prime}")
print()

# Simplifier l'expression
g_prime_simplified = sp.simplify(g_prime)
print("Dérivée simplifiée:")
print(f"g'(Ts) = {g_prime_simplified}")
print()

# Valeurs numériques pour le tracé (exemple)
# Vous pouvez ajuster ces valeurs selon votre problème
valeurs_numeriques = {
    alpha: 0.8,
    epsilon: 0.5,
    G: 2000,  # W/m²
    h: 2,    # W/m²K
    sigma: 5.67e-8, 
    Tsur: 293,  # K
    Tinf: 293  # K
}

# Substituer les valeurs numériques
g_prime_num = g_prime_simplified.subs(valeurs_numeriques)

print("Dérivée avec valeurs numériques:")
print(f"g'(Ts) = {g_prime_num}")
print()

# Convertir en fonction NumPy pour le tracé
g_prime_func = sp.lambdify(Ts, g_prime_num, 'numpy')

# Définir l'intervalle [Ta=0, Tb=500]
Ta, Tb = 0, 500
Ts_values = np.linspace(Ta, Tb, 1000)

# Calculer |g'(Ts)|
g_prime_abs = np.abs(g_prime_func(Ts_values))

# Créer le graphique
plt.figure(figsize=(10, 6))
plt.plot(Ts_values, g_prime_abs, 'b-', linewidth=2, label="|g'(Ts)|")
plt.axhline(y=1, color='r', linestyle='--', alpha=0.7, label='|g\'(Ts)| = 1')
plt.xlabel('Ts (K)')
plt.ylabel("|g'(Ts)|")
plt.title("Évolution de |g'(Ts)| en fonction de Ts")
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(Ta, Tb)

# Ajouter des informations sur le graphique
plt.text(0.02, 0.98, f'Paramètres:\nα = {valeurs_numeriques[alpha]}\nG = {valeurs_numeriques[G]} W/m²\nh = {valeurs_numeriques[h]} W/m²K\nTsur = {valeurs_numeriques[Tsur]} K\nT∞ = {valeurs_numeriques[Tinf]} K', 
         transform=plt.gca().transAxes, verticalalignment='top', 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

plt.tight_layout()
plt.show()

# Analyser la convergence
print("Analyse de convergence:")
print(f"Valeur minimale de |g'(Ts)| sur [{Ta}, {Tb}]: {np.min(g_prime_abs):.6f}")
print(f"Valeur maximale de |g'(Ts)| sur [{Ta}, {Tb}]: {np.max(g_prime_abs):.6f}")

if np.max(g_prime_abs) < 1:
    print("Convergence assurée sur tout l'intervalle (|g'(Ts)| < 1)")
elif np.min(g_prime_abs) > 1:
    print("Pas de convergence sur l'intervalle (|g'(Ts)| > 1)")
else:
    print("Convergence partielle sur l'intervalle")
    
# Trouver les points où |g'(Ts)| = 1 (critère de convergence)
indices_critique = np.where(np.abs(g_prime_abs - 1) < 0.01)[0]
if len(indices_critique) > 0:
    print(f"Points critiques (|g'(Ts)| ≈ 1): Ts ≈ {Ts_values[indices_critique]} K")