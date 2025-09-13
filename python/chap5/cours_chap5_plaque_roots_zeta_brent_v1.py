import numpy as np
from scipy.optimize import root_scalar, brentq, newton
import matplotlib.pyplot as plt

def transcendental_equation(zeta, Bi):
    """Équation transcendante: ζ * tan(ζ) - Bi = 0"""
    return zeta * np.tan(zeta) - Bi

def transcendental_derivative(zeta, Bi):
    """Dérivée de l'équation transcendante: d/dζ[ζ * tan(ζ) - Bi]"""
    return np.tan(zeta) + zeta * (1 + np.tan(zeta)**2)

def find_initial_brackets(Bi, n_roots=10):
    """
    Trouve des intervalles de bracketing précis pour chaque racine
    en analysant les changements de signe
    """
    brackets = []
    
    for n in range(1, n_roots + 1):
        # Intervalle initial plus serré
        left = (n - 1) * np.pi + 1e-10
        right = n * np.pi - 1e-10
        
        # Recherche dichotomique pour trouver un bracketing précis
        for _ in range(100):  # Raffiner l'intervalle
            mid = (left + right) / 2
            
            # Éviter les points où tan(ζ) explose
            if np.abs(np.cos(mid)) < 1e-12:
                if transcendental_equation(left, Bi) * transcendental_equation(mid - 1e-8, Bi) < 0:
                    right = mid - 1e-8
                else:
                    left = mid + 1e-8
            else:
                if transcendental_equation(left, Bi) * transcendental_equation(mid, Bi) < 0:
                    right = mid
                else:
                    left = mid
                    
            if right - left < 1e-12:
                break
        
        brackets.append((left, right))
    
    return brackets

def method_1_brent(Bi, n_roots=10):
    """
    Méthode 1: Algorithme de Brent (optimal pour les racines avec bracketing)
    Précision: ~1e-15
    """
    print("=== MÉTHODE 1: ALGORITHME DE BRENT ===")
    brackets = find_initial_brackets(Bi, n_roots)
    eigenvalues = []
    
    for i, (a, b) in enumerate(brackets, 1):
        try:
            # Brent est généralement le plus précis pour les fonctions avec bracketing
            zeta = brentq(transcendental_equation, a, b, args=(Bi,), 
                         xtol=1e-15, rtol=1e-15, maxiter=1000)
            eigenvalues.append(zeta)
            residual = abs(transcendental_equation(zeta, Bi))
            print(f"ζ_{i} = {zeta:.15f}, résidu = {residual:.2e}")
        except Exception as e:
            print(f"Erreur pour ζ_{i}: {e}")
    
    return eigenvalues

def main():
    """Programme principal avec interface utilisateur"""
    print("SOLVEUR HAUTE PRÉCISION DES VALEURS PROPRES ζₙ")
    print("=" * 60)
    
    # Saisie des paramètres
    Bi = float(input("Entrez la valeur de Bi: "))
    n_roots = int(input("Nombre de racines à calculer (max 10): ") or "5")
    
    eigenvalues = method_1_brent(Bi, n_roots)

if __name__ == "__main__":
    main()