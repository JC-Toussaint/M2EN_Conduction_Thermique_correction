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
    f1 = (Tsi-Tg_top)/(Ra+Rg) - RHS

    RHS = 0.83*Gs*A*(1-eta(Tsi))     
    f2 = (Tsi-Tg_top)/(Ra+Rg) - RHS
        
    return np.array([f1, f2])

def jacobian_analytical(vars):
    """Calcule le Jacobien analytique du système d'équations"""
    Tg_top, Tsi = vars
    
    # Initialisation de la matrice Jacobienne 2x2
    J = np.zeros((2, 2))
    
    # Dérivées pour f1 = (Tsi-Tg_top)/(Ra+Rg) - [h*A*(Tg_top-Tinf)+epsilon*sigma*A*(Tg_top**4-Tsur**4)-0.1*Gs*A]
    
    # ∂f1/∂Tg_top
    df1_dTg_top = -1/(Ra+Rg) - h*A - epsilon*sigma*A*4*Tg_top**3
    J[0, 0] = df1_dTg_top
    
    # ∂f1/∂Tsi
    df1_dTsi = 1/(Ra+Rg)
    J[0, 1] = df1_dTsi
    
    # Dérivées pour f2 = (Tsi-Tg_top)/(Ra+Rg) - 0.83*Gs*A*(1-eta(Tsi))
    # avec eta(Tsi) = 0.553 - 1e-3*Tsi
    # donc (1-eta(Tsi)) = 1 - (0.553 - 1e-3*Tsi) = 0.447 + 1e-3*Tsi
    # et ∂(1-eta(Tsi))/∂Tsi = 1e-3
    
    # ∂f2/∂Tg_top
    df2_dTg_top = -1/(Ra+Rg)
    J[1, 0] = df2_dTg_top
    
    # ∂f2/∂Tsi
    df2_dTsi = 1/(Ra+Rg) - 0.83*Gs*A*1e-3
    J[1, 1] = df2_dTsi
    
    return J

def jacobian_numerical(vars, h=1e-6):
    """Calcule le Jacobien par différences finies (pour validation)"""
    n = len(vars)
    m = len(equations(vars))
    J = np.zeros((m, n))
    
    for j in range(n):
        vars_plus = vars.copy()
        vars_minus = vars.copy()
        vars_plus[j] += h
        vars_minus[j] -= h
        
        f_plus = equations(vars_plus)
        f_minus = equations(vars_minus)
        
        J[:, j] = (f_plus - f_minus) / (2 * h)
    
    return J

def newton_raphson(f, x0, tol=1e-8, max_iter=100, verbose=True, use_analytical=True):
    """
    Méthode de Newton-Raphson pour résoudre f(x) = 0
    
    Parameters:
    -----------
    f : fonction qui retourne f(x)
    x0 : estimation initiale
    tol : tolerance pour la convergence
    max_iter : nombre maximum d'itérations
    verbose : affichage des itérations
    use_analytical : utiliser le jacobien analytique (True) ou numérique (False)
    
    Returns:
    --------
    x : solution
    success : booléen indiquant le succès
    iterations : nombre d'itérations
    """
    x = np.array(x0, dtype=float)
    
    if verbose:
        jacobian_type = "analytique" if use_analytical else "numérique"
        print(f"Utilisation du Jacobien {jacobian_type}")
        print("Itération | Tg_top      | Tsi         | ||F(x)||")
        print("-" * 50)
    
    for i in range(max_iter):
        # Évaluation de la fonction
        F = f(x)
        norm_F = np.linalg.norm(F)
        
        if verbose:
            print(f"{i:8d} | {x[0]:10.4f} | {x[1]:10.4f} | {norm_F:.2e}")
        
        # Test de convergence
        if norm_F < tol:
            if verbose:
                print(f"\nConvergence atteinte en {i} itérations")
            return x, True, i
        
        # Calcul du Jacobien (analytique ou numérique)
        if use_analytical:
            J = jacobian_analytical(x)
        else:
            J = jacobian_numerical(x)
        
        # Vérification de la singularité
        try:
            det_J = np.linalg.det(J)
            if abs(det_J) < 1e-12:
                print(f"Jacobien singulier (det = {det_J:.2e})")
                return x, False, i
            
            # Résolution du système linéaire J * delta_x = -F
            delta_x = np.linalg.solve(J, -F)
            
        except np.linalg.LinAlgError:
            print("Erreur lors de la résolution du système linéaire")
            return x, False, i
        
        # Mise à jour avec facteur d'amortissement (damping)
        # Pour améliorer la robustesse
        damping = 1.0
        x_new = x + damping * delta_x
        
        # Vérification que la nouvelle solution améliore la norme
        F_new = f(x_new)
        norm_F_new = np.linalg.norm(F_new)
        
        # Si la norme augmente, on réduit le pas
        attempts = 0
        while norm_F_new > norm_F and attempts < 10:
            damping *= 0.5
            x_new = x + damping * delta_x
            F_new = f(x_new)
            norm_F_new = np.linalg.norm(F_new)
            attempts += 1
        
        x = x_new
        
        # Test de convergence sur la variation
        if np.linalg.norm(delta_x) < tol:
            if verbose:
                print(f"\nConvergence sur delta_x atteinte en {i+1} itérations")
            return x, True, i+1
    
    print(f"\nNombre maximum d'itérations ({max_iter}) atteint")
    return x, False, max_iter

# Estimation de l'incertitude
def estimate_uncertainty(x_sol, f, use_analytical=True, h=1e-6):
    """Estime l'incertitude sur la solution"""
    # Calcul du Jacobien à la solution
    if use_analytical:
        J = jacobian_analytical(x_sol)
    else:
        J = jacobian_numerical(x_sol, h)
    
    # Résidu à la solution
    res = f(x_sol)
    
    # Estimation de la variance résiduelle
    sigma2 = np.sum(res**2) / max(1, len(x_sol) - 1)
    
    try:
        # Matrice de covariance
        cov = sigma2 * np.linalg.inv(J.T @ J)
        
        # Erreurs standard
        errors = np.sqrt(np.diag(cov))
        
        return errors, cov
    except np.linalg.LinAlgError:
        print("Impossible de calculer l'incertitude (matrice singulière)")
        return None, None

# ============= RÉSOLUTION =============

# Valeurs initiales
initial_guess = [Tsur, Tsur]

print("Résolution par méthode de Newton-Raphson personnalisée")
print("=" * 55)

# Résolution avec Jacobien analytique
print("\n1. RÉSOLUTION AVEC JACOBIEN ANALYTIQUE")
print("-" * 40)
solution, success, iterations = newton_raphson(equations, initial_guess, 
                                             tol=1e-8, max_iter=50, verbose=True, use_analytical=True)

# Affichage des résultats
if success:
    print(f"\nSolution trouvée : Tg_top = {solution[0]:.4f}, Tsi = {solution[1]:.4f}")
    print(f"Résidu final : {equations(solution)}")
    
    # Estimation de l'incertitude
    errors, cov = estimate_uncertainty(solution, equations, use_analytical=True)
    
    if errors is not None:
        print(f"\nIncertitudes estimées :")
        print(f"Tg_top = {solution[0]:.4f} ± {errors[0]:.4g}")
        print(f"Tsi    = {solution[1]:.4f} ± {errors[1]:.4g}")
        
        print(f"\nMatrice de covariance :")
        print(cov)
        
        # Coefficient de corrélation
        if len(errors) == 2:
            corr = cov[0,1] / (errors[0] * errors[1])
            print(f"\nCoefficient de corrélation : {corr:.4f}")
    
    solution_analytical = solution.copy()
    
else:
    print("Échec de la résolution")
    print(f"Dernière estimation : Tg_top = {solution[0]:.4f}, Tsi = {solution[1]:.4f}")

# Comparaison avec le Jacobien numérique
print("\n\n2. COMPARAISON AVEC JACOBIEN NUMÉRIQUE")
print("-" * 42)

# Point de comparaison (utilisons la solution trouvée)
if success:
    test_point = solution_analytical
    
    J_analytical = jacobian_analytical(test_point)
    J_numerical = jacobian_numerical(test_point)
    
    print(f"Point de comparaison : Tg_top = {test_point[0]:.4f}, Tsi = {test_point[1]:.4f}")
    print(f"\nJacobien analytique :")
    print(J_analytical)
    print(f"\nJacobien numérique :")
    print(J_numerical)
    print(f"\nDifférence absolue :")
    print(np.abs(J_analytical - J_numerical))
    print(f"\nDifférence relative (%) :")
    print(100 * np.abs(J_analytical - J_numerical) / (np.abs(J_analytical) + 1e-16))
    
    # Résolution avec Jacobien numérique pour comparaison
    print(f"\n3. RÉSOLUTION AVEC JACOBIEN NUMÉRIQUE (pour comparaison)")
    print("-" * 58)
    solution_num, success_num, iterations_num = newton_raphson(equations, initial_guess, 
                                                             tol=1e-8, max_iter=50, verbose=False, use_analytical=False)
    
    if success_num:
        print(f"Solution numérique : Tg_top = {solution_num[0]:.4f}, Tsi = {solution_num[1]:.4f}")
        print(f"Différence avec analytique : ΔTg_top = {abs(solution_num[0] - solution_analytical[0]):.2e}")
        print(f"                            ΔTsi = {abs(solution_num[1] - solution_analytical[1]):.2e}")
        print(f"Nombre d'itérations (analytique) : {iterations}")
        print(f"Nombre d'itérations (numérique)  : {iterations_num}")
    else:
        print("Échec de la résolution numérique")