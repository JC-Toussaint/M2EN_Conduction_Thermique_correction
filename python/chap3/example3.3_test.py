import numpy as np
import matplotlib.pyplot as plt

# Paramètres du problème
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

def equations(vars, lambda_param=1.0):
    """
    Système avec paramètre de continuation λ
    λ=0: système linéarisé facile
    λ=1: système complet
    """
    Tg_top, Tsi = vars
    
    # Terme radiatif avec continuation
    rad_term = lambda_param * epsilon*sigma*A*(Tg_top**4-Tsur**4) + (1-lambda_param) * 4*epsilon*sigma*A*Tsur**3*(Tg_top-Tsur)
    
    RHS = h*A*(Tg_top-Tinf) + rad_term - 0.1*Gs*A
    f1 = (Tsi-Tg_top)/(Ra+Rg) - RHS

    # Terme eta avec continuation  
    eta_term = lambda_param * eta(Tsi) + (1-lambda_param) * eta(Tsur)
    RHS = 0.83*Gs*A*(1-eta_term)     
    f2 = (Tsi-Tg_top)/(Ra+Rg) - RHS
        
    return np.array([f1, f2])

def jacobian(vars, lambda_param=1.0):
    """Jacobien analytique avec continuation"""
    Tg_top, Tsi = vars
    
    # Dérivées partielles de f1
    df1_dTg = -1/(Ra+Rg) - h*A
    if lambda_param > 0:
        df1_dTg -= lambda_param * 4*epsilon*sigma*A*Tg_top**3
    else:
        df1_dTg -= (1-lambda_param) * 4*epsilon*sigma*A*Tsur**3
        
    df1_dTsi = 1/(Ra+Rg)
    
    # Dérivées partielles de f2  
    df2_dTg = -1/(Ra+Rg)
    df2_dTsi = 1/(Ra+Rg) 
    if lambda_param > 0:
        df2_dTsi += lambda_param * 0.83*Gs*A*1e-3  # dérivée de eta
    
    return np.array([[df1_dTg, df1_dTsi],
                     [df2_dTg, df2_dTsi]])

def newton_step(vars, lambda_param=1.0, alpha=1.0):
    """Un pas de Newton avec amortissement"""
    f = equations(vars, lambda_param)
    jac = jacobian(vars, lambda_param)
    
    try:
        dx = np.linalg.solve(jac, -f)
        return vars + alpha * dx, np.linalg.norm(f)
    except np.linalg.LinAlgError:
        # Matrice singulière, utiliser pseudo-inverse
        dx = -np.linalg.pinv(jac) @ f
        return vars + alpha * dx, np.linalg.norm(f)

def continuation_solver(x0, tol=1e-8):
    """Résolveur par continuation avec Newton"""
    print("=== Méthode de continuation + Newton ===")
    
    # Étapes de continuation
    lambda_steps = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    
    x = np.array(x0, dtype=float)
    
    for i, lam in enumerate(lambda_steps):
        print(f"\nÉtape {i+1}: λ = {lam:.1f}")
        
        # Newton iterations pour ce λ
        for newton_iter in range(50):
            # Essayer pas complet d'abord
            x_new, residual = newton_step(x, lam, alpha=1.0)
            
            # Si ça diverge, réduire le pas
            if residual > 1e3 or np.any(np.isnan(x_new)) or np.any(x_new < 200) or np.any(x_new > 2000):
                for alpha in [0.5, 0.1, 0.01]:
                    x_new, residual = newton_step(x, lam, alpha)
                    if residual < 1e3 and not np.any(np.isnan(x_new)):
                        break
                else:
                    print(f"  Newton diverge à λ={lam}")
                    return None, False
            
            error = np.linalg.norm(x_new - x)
            
            if newton_iter % 5 == 0:
                print(f"  Newton {newton_iter:2d}: Tg={x_new[0]:6.1f}, Tsi={x_new[1]:6.1f}, "
                      f"res={residual:.2e}")
            
            if residual < tol:
                print(f"  ✓ Convergence Newton en {newton_iter} itérations")
                break
                
            x = x_new
    
    # Vérification finale
    final_residual = np.linalg.norm(equations(x, 1.0))
    print(f"\n✓ Solution finale:")
    print(f"Tg_top = {x[0]:.4f} K")
    print(f"Tsi = {x[1]:.4f} K") 
    print(f"Résidu final = {final_residual:.2e}")
    print(f"Flux = {(x[1]-x[0])/(Ra+Rg):.1f} W")
    
    return x, final_residual < tol

# =====================================================================
# MÉTHODE DE POINT FIXE ROBUSTE (BASÉE SUR NEWTON)
# =====================================================================

def robust_fixed_point(vars):
    """
    Point fixe robuste: x_{n+1} = x_n - α * J^{-1} * f(x_n)
    où α est choisi adaptivement et J est mis à jour périodiquement
    """
    return newton_step(vars, lambda_param=1.0, alpha=0.1)[0]

def adaptive_fixed_point_solver(x0, tol=1e-6, max_iter=200):
    """Solveur de point fixe avec stratégie adaptive"""
    print("\n=== Point fixe robuste (Newton amorti) ===")
    
    x = np.array(x0, dtype=float)
    jac = None
    update_jac_freq = 10  # Mettre à jour jacobien tous les 10 pas
    
    for i in range(max_iter):
        # Mettre à jour Jacobien périodiquement
        if i % update_jac_freq == 0:
            jac = jacobian(x, 1.0)
        
        f = equations(x, 1.0)
        residual = np.linalg.norm(f)
        
        if residual < tol:
            print(f"✓ Convergence en {i} itérations")
            print(f"Solution: Tg_top={x[0]:.4f}, Tsi={x[1]:.4f}")
            print(f"Résidu final: {residual:.2e}")
            return x, True
        
        # Pas de Newton amorti
        try:
            dx = np.linalg.solve(jac, -f)
            
            # Amortissement adaptatif
            alpha = min(0.3, 1.0 / max(1.0, np.linalg.norm(dx)))
            x_new = x + alpha * dx
            
            # Vérifier que la solution reste physique
            if np.any(x_new < 200) or np.any(x_new > 2000):
                alpha *= 0.1
                x_new = x + alpha * dx
            
            x = x_new
            
        except np.linalg.LinAlgError:
            print(f"Matrice singulière à l'itération {i}")
            return x, False
        
        if i % 10 == 0:
            print(f"Iter {i:3d}: Tg={x[0]:6.1f}, Tsi={x[1]:6.1f}, res={residual:.2e}")
    
    print("Nombre maximum d'itérations atteint")
    return x, False

# =====================================================================
# TESTS ET COMPARAISONS
# =====================================================================

# Solution de référence
from scipy.optimize import root
sol_ref = root(lambda x: equations(x, 1.0), [293, 293])
if sol_ref.success:
    print("=== Référence scipy ===")
    print(f"Tg_top = {sol_ref.x[0]:.4f} K, Tsi = {sol_ref.x[1]:.4f} K")
    print(f"Résidu = {np.linalg.norm(equations(sol_ref.x, 1.0)):.2e}")

# Test de la méthode de continuation
print("\n" + "="*60)
x0 = [300, 400]
sol_cont, success_cont = continuation_solver(x0)

# Test du point fixe robuste
print("\n" + "="*60)
sol_robust, success_robust = adaptive_fixed_point_solver(x0)

# =====================================================================
# VISUALISATION DE LA CONVERGENCE
# =====================================================================

def visualize_basins():
    """Visualiser les bassins d'attraction"""
    print("\n=== Analyse des bassins d'attraction ===")
    
    # Grille de points initiaux
    Tg_range = np.linspace(280, 400, 20)
    Tsi_range = np.linspace(280, 500, 20)
    
    success_map = np.zeros((len(Tsi_range), len(Tg_range)))
    
    for i, Tsi in enumerate(Tsi_range):
        for j, Tg in enumerate(Tg_range):
            try:
                sol = root(lambda x: equations(x, 1.0), [Tg, Tsi], method='hybr')
                if sol.success and np.linalg.norm(equations(sol.x, 1.0)) < 1e-6:
                    success_map[i, j] = 1
                else:
                    success_map[i, j] = 0
            except:
                success_map[i, j] = 0
    
    plt.figure(figsize=(10, 8))
    plt.imshow(success_map, extent=[Tg_range[0], Tg_range[-1], Tsi_range[0], Tsi_range[-1]], 
               origin='lower', cmap='RdYlBu', alpha=0.7)
    plt.colorbar(label='Convergence (1=oui, 0=non)')
    
    # Marquer la solution
    if sol_ref.success:
        plt.plot(sol_ref.x[0], sol_ref.x[1], 'r*', markersize=15, label='Solution vraie')
    
    plt.xlabel('Tg_top initial (K)')
    plt.ylabel('Tsi initial (K)')
    plt.title('Bassins d\'attraction pour la convergence')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    convergence_rate = np.mean(success_map)
    print(f"Taux de convergence global: {convergence_rate*100:.1f}%")

# Lancer l'analyse des bassins
visualize_basins()