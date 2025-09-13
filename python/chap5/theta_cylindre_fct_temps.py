import numpy as np
import matplotlib.pyplot as plt
from scipy.special import jv

# Définir la fonction f(zeta) = zeta * J1(zeta) / J0(zeta)
def f(zeta):
    """
    Calcule f(ζ) = ζ * J₁(ζ) / J₀(ζ)
    où J₀ et J₁ sont les fonctions de Bessel de première espèce
    """
    J0 = jv(0, zeta)  # Fonction de Bessel J₀
    J1 = jv(1, zeta)  # Fonction de Bessel J₁
    
    # Éviter la division par zéro
    result = np.where(J0 != 0, zeta * J1 / J0, 0)
    return result

# Créer un tableau de valeurs pour ζ
zeta = np.linspace(0.1, 20, 100000)  # Éviter ζ = 0 pour éviter les problèmes numériques

# Calculer f(ζ)
f_values = f(zeta)

# Valeur de Bi
Bi = 0.1

# Créer le graphique
plt.figure(figsize=(10, 6))

# Tracer f(ζ)
plt.plot(zeta, f_values, 'r-', linewidth=1) # ATTENTION abscisses des divergences sont à exclure
plt.plot(zeta, f_values, 'b.', linewidth=1, label=r'$f(\zeta) = \zeta \frac{J_1(\zeta)}{J_0(\zeta)}$')

# Tracer la ligne horizontale y = Bi
plt.axhline(y=Bi, color='r', linestyle='--', linewidth=2, label=f'Bi = {Bi}')

# Configuration du graphique
plt.xlabel(r'$\zeta$', fontsize=14)
plt.ylabel(r'$f(\zeta)$', fontsize=14)
plt.title(r'Tracé de $f(\zeta) = \zeta \frac{J_1(\zeta)}{J_0(\zeta)}$', fontsize=16)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12)

# Limites des axes pour une meilleure visualisation
plt.xlim(0, 20)
plt.ylim(-0.5, 10)

# Afficher le graphique
plt.tight_layout()
plt.show()

# Optionnel : trouver les intersections approximatives avec y = Bi
intersections = []
for i in range(1, len(f_values)):
    # Vérifier s'il y a un changement de signe
    if (f_values[i-1] - Bi) * (f_values[i] - Bi) < 0:
        # Vérifier que ce n'est pas une divergence (valeurs très grandes en valeur absolue)
        max_val = max(abs(f_values[i-1]), abs(f_values[i]))
        # Si les valeurs ne sont pas trop grandes, c'est probablement une vraie intersection
        if max_val < 100:  # Seuil pour éviter les divergences
            # Interpolation linéaire pour trouver l'intersection
            zeta_intersection = zeta[i-1] + (zeta[i] - zeta[i-1]) * (Bi - f_values[i-1]) / (f_values[i] - f_values[i-1])
            intersections.append(zeta_intersection)

if intersections:
    print(f"Intersections approximatives avec y = {Bi}:")
    for i, intersection in enumerate(intersections):
        print(f"  ζ_{i+1} ≈ {intersection:.4f}")
else:
    print(f"Aucune intersection trouvée avec y = {Bi} dans l'intervalle considéré.")

print("\n" + "="*60)
print("TRACÉ DE LA SÉRIE INFINIE θ*(r*, Fo)")
print("="*60)

# Fonction pour calculer la série θ*(r*, Fo)
def theta_star(r_star, Fo, zeta_roots, n_terms=50):
    """
    Calcule θ*(r*, Fo) selon la série infinie donnée
    
    Paramètres:
    r_star : position radiale normalisée (0 ≤ r* ≤ 1)
    Fo : nombre de Fourier
    zeta_roots : racines de l'équation f(ζ) = Bi
    n_terms : nombre de termes dans la série
    """
    theta = 0
    
    for n in range(min(n_terms, len(zeta_roots))):
        zeta_n = zeta_roots[n]
        
        # Calculer les fonctions de Bessel
        J0_zeta_n = jv(0, zeta_n)
        J1_zeta_n = jv(1, zeta_n)
        J0_zeta_n_r = jv(0, zeta_n * r_star)
        
        # Terme de la série
        if J0_zeta_n**2 + J1_zeta_n**2 != 0:  # Éviter division par zéro
            coefficient = (2 / zeta_n) * (J1_zeta_n / (J0_zeta_n**2 + J1_zeta_n**2))
            terme = coefficient * np.exp(-zeta_n**2 * Fo) * J0_zeta_n_r
            theta += terme
    
    return theta

# Trouver les racines ζ_n plus précisément (racines de f(ζ) - Bi = 0)
from scipy.optimize import fsolve

def equation_to_solve(zeta):
    """Équation f(ζ) - Bi = 0"""
    J0 = jv(0, zeta)
    J1 = jv(1, zeta)
    if J0 != 0:
        return zeta * J1 / J0 - Bi
    else:
        return float('inf')

# Chercher les premières racines en utilisant les intersections approximatives comme points de départ
zeta_roots = []
for intersection in intersections[:10]:  # Limiter aux 10 premières
    try:
        root = fsolve(equation_to_solve, intersection)[0]
        # Vérifier que c'est bien une racine
        if abs(equation_to_solve(root)) < 1e-6:
            zeta_roots.append(root)
    except:
        continue

# Si on n'a pas assez de racines, en chercher d'autres par balayage
if len(zeta_roots) < 5:
    print("Recherche de racines supplémentaires...")
    for zeta_guess in np.linspace(0.1, 50, 500):
        if abs(equation_to_solve(zeta_guess)) < 0.1:  # Proche d'une racine
            try:
                root = fsolve(equation_to_solve, zeta_guess)[0]
                if abs(equation_to_solve(root)) < 1e-6:
                    # Vérifier que cette racine n'est pas déjà trouvée
                    if not any(abs(root - existing_root) < 1e-3 for existing_root in zeta_roots):
                        zeta_roots.append(root)
            except:
                continue

zeta_roots = sorted(zeta_roots)[:10]  # Garder les 10 premières racines triées

print(f"Racines ζ_n trouvées (premières {len(zeta_roots)}):")
for i, root in enumerate(zeta_roots):
    print(f"  ζ_{i+1} = {root:.6f}")

# Paramètres pour le tracé
# Créer un nouveau graphique pour θ*(r*, Fo)
plt.figure(figsize=(10, 6))
colors = plt.cm.viridis(np.linspace(0, 1, 10))  # 10 couleurs différentes

for i, Fo in enumerate(range(1, 11)):
    r_star_values = np.linspace(0, 1, 100)
    theta_values = np.array([theta_star(r, Fo, zeta_roots) for r in r_star_values])
    print(f"Fo={Fo}: theta_values[0] = {theta_values[0]}")
    
    plt.plot(r_star_values, theta_values, 
             color=colors[i], linewidth=2,
             label=f'Fo = {Fo}')  # Label différent pour chaque courbe

plt.xlabel(r'$r^*$')
plt.ylabel(r'$\theta^*(r^*, Fo)$')
plt.legend(loc='lower left')
plt.grid(True)
plt.show()  # Une seule fois à la fin

print(f"\nValeurs particulières:")
print(f"θ*(0, Fo={Fo}) = {theta_star(0, Fo, zeta_roots):.6f} (centre)")
print(f"θ*(1, Fo={Fo}) = {theta_star(1, Fo, zeta_roots):.6f} (surface)")