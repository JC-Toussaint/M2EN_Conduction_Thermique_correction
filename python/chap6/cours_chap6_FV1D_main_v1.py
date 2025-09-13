import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

# Paramètres
L = 1
N = 10
K = 200
H = 10

Tdg = 0
Tad = 100

# Largeurs des cellules (uniformes)
w = np.ones(N) * L/N

# Centres des cellules
x = np.zeros(N)
width = w[0]
x[0] = w[0]/2
for i in range(1, N):
    x[i] = x[i-1] + w[i]

# Initialisation de la matrice A et du vecteur b
A = np.zeros((N, N))
b = np.zeros(N)

# Remplissage de la matrice pour les cellules intérieures (i = 1 à N-2)
for i in range(1, N-1):
    A[i, i-1] = -K / (x[i] - x[i-1])
    A[i, i] = +K / (x[i] - x[i-1]) + K / (x[i+1] - x[i])
    A[i, i+1] = -K / (x[i+1] - x[i])

# Condition aux limites sur le bord gauche
A[0, 0] = 2*K/w[0] + K/(x[1] - x[0])
A[0, 1] = -K/(x[1] - x[0])
b[0] = 2*K/w[0] * Tdg

# Condition aux limites sur le bord droit
A[N-1, N-1] = H*2*K/(2*K + H*w[N-1]) + K/(x[N-1] - x[N-2])
A[N-1, N-2] = -K/(x[N-1] - x[N-2])
b[N-1] = H*2*K/(2*K + H*w[N-1]) * Tad

# Résolution du système linéaire
T = np.linalg.solve(A, b)

# Affichage des résultats
plt.figure(figsize=(10, 6))
plt.plot(x, T, 'r.-', linewidth=2, markersize=8)
plt.grid(True)
plt.xlabel('Position x')
plt.ylabel('Température T')
plt.title('Distribution de température 1D - Matériau homogène')
plt.show()

# Calcul de la solution analytique
TL = (H*Tad + K/L*Tdg) / (K/L + H)

print(f"Température au bord droit (numérique): {T[-1]:.6f}")
print(f"Température limite analytique (TL): {TL:.6f}")
print(f"Erreur relative: {abs(T[-1] - TL)/TL*100:.4f}%")
print(f"Température minimale: {T.min():.2f}")
print(f"Température maximale: {T.max():.2f}")