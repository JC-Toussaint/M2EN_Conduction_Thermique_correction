from scipy.optimize import root
from scipy.optimize import approx_fprime
import numpy as np

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

# Valeurs initiales
initial_guess = [Tsur, Tsur]

# Appel à root
# hybr est l'abréviation de Hybrid Powell method.
# méthode par défaut dans scipy.optimize.root 
# Elle combine :
# la méthode de Newton modifiée (si le Jacobien est fourni ou approché),
# des techniques de moindres carrés pour la robustesse (similaire à Levenberg–Marquardt),
# une mise à l’échelle adaptative des variables.

sol = root(equations, initial_guess)

# Affichage
if sol.success:
    Tg_top_sol, Tsi_sol = sol.x
    print(f"Solution trouvée : Tg_top = {Tg_top_sol:.4f}, Tsi = {Tsi_sol:.4f}")
    print(f"Residu : {equations(sol.x)}")
    
    J = np.zeros((2, 2))
    for i in range(2):
        def fi(x):
            return equations(x)[i]
        J[i, :] = approx_fprime(sol.x, fi, epsilon= 1e-6)
     
    # estimer la variance résiduelle
    res = np.array(equations(sol.x))
    sigma2 = np.sum(res**2) / (len(sol.x) - 1)

    # covariance (si J bien conditionnée)
    cov = sigma2 * np.linalg.inv(J.T @ J)

    # erreur standard (barres d'erreur)
    errors = np.sqrt(np.diag(cov))

    print(f"Tg_top = {sol.x[0]:.4f} ± {errors[0]:.4g}")
    print(f"Tsi    = {sol.x[1]:.4f} ± {errors[1]:.4g}")
        
else:
    print("Échec de la résolution :", sol.message)

