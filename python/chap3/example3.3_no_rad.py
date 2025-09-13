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

a, b = 0.553, 1e-3

# --- Coefficients utiles ---
R_tot_inv = 1 / (Ra + Rg)          # 1 / (Ra + Rg)

# --- Matrice du système Ax = b ---
A_mat = np.array([
    [ R_tot_inv,                     -(R_tot_inv + h*A) ],
    [ R_tot_inv - 0.83*Gs*A*b,      -R_tot_inv         ]
])

b_vec = np.array([
    -h*A*Tinf - 0.1*Gs*A,
    0.83*Gs*A*(1 - a)
])

# --- Résolution ---
solution = np.linalg.solve(A_mat, b_vec)

# --- Affichage ---
Tsi = solution[0]
Tg_top = solution[1]

print(f"Tg_top = {Tg_top:.4f}")
print(f"Tsi = {Tsi:.4f}")
