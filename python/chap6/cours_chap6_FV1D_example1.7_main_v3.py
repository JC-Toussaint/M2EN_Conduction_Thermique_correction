import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

# Paramètres
L = 3e-3        # [m] - longueur du domaine
N = 100         # [-] - nombre de cellules
K = 0.3         # [W/m·K] - conductivité thermique
H = 2           # [W/m²·K] - coefficient de convection

Tdg  = 308      # [K] - température dirichlet a gauche
Tad  = 297      # [K] - température ambiante a droite
Tsur = 297      # [K] - température de l'environnement
eps = 0.95      # [-] - émissivité
sigma = 5.670374419e-8  # [W/m²·K⁴] - constante de Stefan-Boltzmann

def buid_msh(N):
    # Largeurs des cellules (uniformes)
    w = np.ones(N) * L/N

    # Centres des cellules
    x = np.zeros(N)
    width = w[0]
    x[0] = w[0]/2
    for i in range(1, N):
        x[i] = x[i-1] + w[i]
    return w, x

def solve(w, x, T):
    N = len(w)    
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

    # calcul du coefficient effectif de convection + radiation
    Heff = H + eps*sigma*(T[N-1]+Tsur)*(T[N-1]**2+Tsur**2)
    
    # Condition aux limites sur le bord droit
    A[N-1, N-1] = Heff*2*K/(2*K + Heff*w[N-1]) + K/(x[N-1] - x[N-2])
    A[N-1, N-2] = -K/(x[N-1] - x[N-2])
    b[N-1] = Heff*2*K/(2*K + Heff*w[N-1]) * Tad

    # Résolution du système linéaire
    T = np.linalg.solve(A, b)
    return T

w, x = buid_msh(N)
T = Tsur * np.ones(N) # Guess value
for n in range(20):
    T = solve(w, x, T)

# Affichage des résultats
plt.figure(figsize=(10, 6))
plt.plot(x, T, 'r.-', linewidth=2, markersize=8)
plt.grid(True)
plt.xlabel('Position x')
plt.ylabel('Température T')
plt.title('Distribution de température 1D - Matériau homogène')
plt.show()

# Calcul de la solution analytique
TL = Tsur # guess value
for n in range(20):
    # calcul du coefficient effectif de convection + radiation
    Heff = H + eps*sigma*(TL+Tsur)*(TL**2+Tsur**2)
    TL = (Heff*Tad + K/L*Tdg) / (K/L + Heff)

print(f"Température au bord droit (numérique): {T[-1]:.6f}")
print(f"Température limite analytique (TL): {TL:.6f}")
print(f"Erreur relative: {abs(T[-1] - TL)/TL*100:.4f}%")
print(f"Température minimale: {T.min():.2f}")
print(f"Température maximale: {T.max():.2f}")