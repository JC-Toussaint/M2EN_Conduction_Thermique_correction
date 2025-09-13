import numpy as np
from scipy.optimize import approx_fprime

def hybrid_root_simplified(func, x0, tol=1e-6, max_iter=100):
    """
    Version simplifiée de l'algorithme hybride de Powell
    pour illustrer le principe
    """
    x = np.array(x0, dtype=float)
    
    for iteration in range(max_iter):
        # Évaluer la fonction au point courant
        f = func(x)
        
        # Critère de convergence
        if np.linalg.norm(f) < tol:
            print(f"Convergence atteinte en {iteration} itérations")
            return x
        
        # Approximer le Jacobien par différences finies
        eps = 1e-8
        jac = approx_fprime(x, func, eps)
        
        # Résoudre le système linéaire : J * dx = -f
        try:
            dx = np.linalg.solve(jac, -f)
        except np.linalg.LinAlgError:
            # Si le Jacobien est singulier, utiliser pseudo-inverse
            dx = -np.linalg.pinv(jac) @ f
        
        # Recherche linéaire simple (pas adaptatif)
        alpha = 1.0
        x_new = x + alpha * dx
        f_new = func(x_new)
        
        # Si on ne progresse pas, réduire le pas
        while np.linalg.norm(f_new) > np.linalg.norm(f) and alpha > 1e-4:
            alpha *= 0.5
            x_new = x + alpha * dx
            f_new = func(x_new)
        
        # Mettre à jour
        x = x_new
        print(f"Iter {iteration}: x = {x}, ||f|| = {np.linalg.norm(f):.6f}")
    
    print("Nombre maximum d'itérations atteint")
    return x

# Test avec votre exemple
from scipy.optimize import root
import numpy as np

# Reprendre vos paramètres
epsilon = 0.9
sigma = 5.67e-8
Tinf, Tsur = 293, 293
h = 35
A = 0.1
Gs = 700
Lg, La = 3.0e-3, 0.1e-3
kg, ka = 1.4, 145
Ra, Rg = La/(ka*A), Lg/(kg*A)

def eta(T):
    a, b = 0.553, 1e-3
    return a-b*T

def equations(vars):
    Tg_top, Tsi = vars
    
    RHS = h*A*(Tg_top-Tinf)+epsilon*sigma*A*(Tg_top**4-Tsur**4)-0.1*Gs*A
    f1 = (Tsi-Tg_top)/(Ra+Rg) -RHS

    RHS = 0.83*Gs*A*(1-eta(Tsi))     
    f2 = (Tsi-Tg_top)/(Ra+Rg) -RHS
        
    return np.array([f1, f2])

print("=== Algorithme simplifié ===")
result_simple = hybrid_root_simplified(equations, [293, 293], tol=1e-4, max_iter=20)

print("\n=== SciPy officiel ===")
sol = root(equations, [293, 293])
if sol.success:
    print(f"Solution SciPy : {sol.x}")
    print(f"Résidu : {equations(sol.x)}")