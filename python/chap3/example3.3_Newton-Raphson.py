#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Résolution d’un système non linéaire par Newton–Raphson
— version minimale : Jacobien analytique uniquement.
"""

import numpy as np

# --- constantes physiques ---------------------------------------------------
epsilon = 0.9
sigma   = 5.67e-8           # constante de Stefan‑Boltzmann (SI)
Tinf, Tsur = 293, 293       # K
h  = 35                      # W m⁻² K⁻¹
A  = 0.1                     # m²
Gs = 700                     # W m⁻²

Lg, La = 3.0e-3, 0.1e-3      # m
kg, ka = 1.4,     145        # W m⁻¹ K⁻¹
Ra, Rg = La/(ka*A), Lg/(kg*A)

# --- modèle ------------------------------------------------------------------
def eta(T):
    """Indice d’absorption (linéaire en T)."""
    return 0.553 - 1e-3*T

def equations(vars):
    """Système F(x) = 0 : [f₁, f₂]."""
    Tg_top, Tsi = vars

    # Bilan sur la surface supérieure du verre
    rhs1 = h*A*(Tg_top-Tinf) + epsilon*sigma*A*(Tg_top**4 - Tsur**4) - 0.1*Gs*A
    f1   = (Tsi - Tg_top)/(Ra + Rg) - rhs1

    # Bilan sur le silicium
    rhs2 = 0.83*Gs*A*(1 - eta(Tsi))
    f2   = (Tsi - Tg_top)/(Ra + Rg) - rhs2

    return np.array([f1, f2])

def jacobian_analytical(vars):
    """Jacobien analytique du système F(x)."""
    Tg_top, Tsi = vars
    J = np.zeros((2, 2))

    # df₁/dTg_top
    J[0, 0] = -1/(Ra+Rg) - h*A - 4*epsilon*sigma*A*Tg_top**3
    # df₁/dTsi
    J[0, 1] =  1/(Ra+Rg)

    # df₂/dTg_top
    J[1, 0] = -1/(Ra+Rg)
    # df₂/dTsi
    J[1, 1] =  1/(Ra+Rg) - 0.83*Gs*A*1e-3

    return J    # :contentReference[oaicite:0]{index=0}

# --- méthode de Newton–Raphson ----------------------------------------------
def newton_raphson(f, x0, tol=1e-8, max_iter=50, verbose=True):
    """
    Résout f(x)=0.
    Toujours avec le Jacobien analytique.
    """
    x = np.array(x0, dtype=float)

    if verbose:
        print("Itér. |  Tg_top (K) |    Tsi (K) | ||F(x)||")
        print("-"*46)

    for k in range(max_iter):
        F = f(x)
        normF = np.linalg.norm(F)

        if verbose:
            print(f"{k:4d}  | {x[0]:11.4f} | {x[1]:11.4f} | {normF:.2e}")

        if normF < tol:
            if verbose:
                print(f"\nConvergence atteinte en {k} itérations.")
            return x, True

        J = jacobian_analytical(x)
        try:
            delta = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            raise RuntimeError("Jacobien singulier : échec de Newton.")

        x += delta  # pas complet ; amortissement inutile ici

        if np.linalg.norm(delta) < tol:
            if verbose:
                print(f"\nConvergence sur delta_x atteinte en {k+1} itérations.")
            return x, True

    return x, False

# --- exécution ---------------------------------------------------------------
if __name__ == "__main__":
    init = [Tsur, Tsur]  # estimation initiale
    sol, ok = newton_raphson(equations, init)

    if ok:
        print(f"\nSolution : Tg_top = {sol[0]:.4f} K,  Tsi = {sol[1]:.4f} K")
        print(f"Résidu   : {equations(sol)}")
    else:
        print("Échec de convergence.")
