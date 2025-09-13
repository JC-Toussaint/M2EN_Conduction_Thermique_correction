import numpy as np
import matplotlib.pyplot as plt

# Données du problème
T1 = 400  # K - Température à la petite extrémité
T2 = 600  # K - Température à la grande extrémité
x1 = 50   # mm - Position de la petite extrémité
x2 = 250  # mm - Position de la grande extrémité
a = 0.25  # Coefficient pour le diamètre D = ax

# Fonction pour calculer la distribution de température
def temperature_distribution(x, T1, T2, x1, x2):
    """
    Calcule la distribution de température dans la section conique
    
    Paramètres:
    x : position (mm)
    T1, T2 : températures aux extrémités (K)
    x1, x2 : positions des extrémités (mm)
    
    Retourne:
    T : température à la position x (K)
    """
    term1 = (1/x) - (1/x1)
    term2 = (1/x1) - (1/x2)
    T = T1 + (T1 - T2) * (term1 / term2)
    return T

# Création du vecteur de positions
x = np.linspace(x1, x2, 1000)

# Calcul de la distribution de température
T = temperature_distribution(x, T1, T2, x1, x2)

# Calcul du diamètre pour référence
D = a * x

# Création du graphique
plt.figure(figsize=(12, 8))

# Graphique principal - Distribution de température
plt.plot(x, T, 'b-', linewidth=2, label='T(x)')
plt.scatter([x1, x2], [T1, T2], color='red', s=100, zorder=5, 
           label=f'Conditions aux limites\nT₁={T1}K à x₁={x1}mm\nT₂={T2}K à x₂={x2}mm')
plt.xlabel('Position x (mm)')
plt.ylabel('Température T (K)')
plt.title('Distribution de température dans la section conique en pyrocéram')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(x1, x2)

plt.show()

# Calcul de quelques valeurs particulières
print("=== ANALYSE DE LA DISTRIBUTION DE TEMPÉRATURE ===")
print(f"Données d'entrée:")
print(f"  T₁ = {T1} K à x₁ = {x1} mm")
print(f"  T₂ = {T2} K à x₂ = {x2} mm")
print(f"  Coefficient a = {a}")
print()

