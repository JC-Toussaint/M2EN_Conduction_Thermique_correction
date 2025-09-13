import numpy as np
from scipy.special import iv, kv

def efficacite_ailette_annulaire(r1, r2, t, h, k, verbose=False):
    """
    Calcule l'efficacité thermique d'une ailette annulaire à bord extérieur adiabatique.
    
    Paramètres :
        r1, r2 : rayons intérieur et extérieur (m)
        t      : épaisseur (m)
        h      : coefficient de convection (W/m²/K)
        k      : conductivité thermique (W/m/K)
        verbose: affiche les constantes A et B si True
        
    Retour :
        eta : efficacité thermique (sans unité)
    """
    m = np.sqrt(2 * h / (k * t))

    # Système pour A et B
    M = np.array([
        [    iv(0, m * r1),      kv(0, m * r1)],
        [m * iv(1, m * r2), -m * kv(1, m * r2)]  # dθ/dr(r2) = 0 (adiabatique)
    ])
    RHS = np.array([1.0, 0.0])  # θ(r1) = 1, dθ/dr(r2) = 0

    A, B = np.linalg.solve(M, RHS)
    if verbose:
        print(f"A = {A}, B = {B}")

    # Dérivée en r = r1
    dtheta_dr_r1 = A * m * iv(1, m * r1) - B * m * kv(1, m * r1)

    # Efficacité thermique finale
    eta = -k * t * r1 * dtheta_dr_r1 / (h * (r2**2 - r1**2))
    return eta


# Exemple : Problème de la motocyclette
print("=== Problème de la motocyclette ===")
r1 = 0.025  # m (rayon intérieur)
r2 = 0.045  # m (rayon extérieur)
t = 0.004   # m (épaisseur)
h = 75      # W/m²·K
k = 186     # W/m·K (aluminium 2024-T6)

eta = efficacite_ailette_annulaire(r1, r2, t, h, k)
print(f"Efficacité thermique de l’ailette : η = {eta:.4f}")
