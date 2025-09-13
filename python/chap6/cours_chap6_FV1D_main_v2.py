import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

# Paramètres
L = 1
N = 100
K1 = 200
K2 = 400
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

# Conductivité thermique (K1 pour x < L/2, K2 pour x >= L/2)
K = np.where(x < L/2, K1, K2)
assert len(K) == N

# Initialisation de la matrice A et du vecteur b
A = np.zeros((N, N))
b = np.zeros(N)

# Remplissage de la matrice pour les cellules intérieures (i = 1 à N-2)
for i in range(1, N-1):
    # Contribution de l'interface (i-1 | i)
    hm, hp = w[i-1]/2, w[i]/2
    Km, Kp = K[i-1]  , K[i]
    Keff = (hm + hp) / (hm/Km + hp/Kp)
    A[i, i-1] = -Keff / (x[i] - x[i-1])
    A[i, i  ] = +Keff / (x[i] - x[i-1])
    
    # Contribution de l'interface (i | i+1)
    hm, hp = w[i]/2, w[i+1]/2
    Km, Kp = K[i],   K[i+1]
    Keff = (hm + hp) / (hm/Km + hp/Kp)
    A[i, i+1] = -Keff / (x[i+1] - x[i])
    A[i, i]  += +Keff / (x[i+1] - x[i])

# Condition aux limites Dirichlet sur le bord gauche
Km = K[0]
A[0, 0] = 2*Km/w[0]
b[0] = 2*Km/w[0]*Tdg

# Contribution de l'interface (1 | 2)
hm, hp = w[0]/2,  w[1]/2
Km, Kp = K[0],    K[1]
Keff = (hm + hp) / (hm/Km + hp/Kp)

A[0, 0] += +Keff / (x[1] - x[0])
A[0, 1]  = -Keff / (x[1] - x[0])

# Condition aux limites Neumann sur le bord droit
Kp = K[N-1]
A[N-1, N-1] = H*2*Kp / (2*Kp + H*w[N-1])
b[N-1] = H*2*Kp / (2*Kp + H*w[N-1]) * Tad

# Contribution de l'interface (N-1 | N)
hm, hp = w[N-2]/2, w[N-1]/2
Km, Kp = K[N-2],   K[N-1]
Keff = (hm + hp) / (hm/Km + hp/Kp)

A[N-1, N-1] = A[N-1, N-1] + Keff / (x[N-1] - x[N-2])
A[N-1, N-2] = -Keff / (x[N-1] - x[N-2])

# Résolution du système linéaire
T = np.linalg.solve(A, b)

# Affichage des résultats
plt.figure(figsize=(10, 6))
plt.plot(x, T, 'r.-', linewidth=2, markersize=4)
plt.grid(True)
plt.xlabel('Position x')
plt.ylabel('Température T')
plt.title('Distribution de température 1D')
plt.show()

print(f"Température minimale: {T.min():.2f}")
print(f"Température maximale: {T.max():.2f}")
print(f"Température au centre (x=0.5): {T[N//2]:.2f}")