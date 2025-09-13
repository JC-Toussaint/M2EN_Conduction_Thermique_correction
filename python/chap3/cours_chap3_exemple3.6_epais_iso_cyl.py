import numpy as np
import matplotlib.pyplot as plt

# Paramètres donnés
ri = 0.005 # m  diametre 10 mm
k = 0.055  # W/(m·K)
h = 5      # W/(m²·K)

# Création du vecteur r-ri variant de 0 à 0.05 m
delta_r = np.linspace(0.0, 0.05, 1000)  
r = ri + delta_r  # Rayon extérieur

# Calcul de R'tot
R_tot_prime = np.log(r/ri) / (2*np.pi*k) + 1 / (2*np.pi*r*h)

# Calcul de 1/R'tot
inv_R_tot_prime = 1 / R_tot_prime

# Création du graphique
plt.figure(figsize=(10, 6))
plt.plot(delta_r*1000, inv_R_tot_prime, 'b-', linewidth=2, label="1/R'tot")
plt.xlabel('r - ri (mm)')
plt.ylabel("1/R'tot (W/(m.K))")
#plt.title("Évolution de 1/R'tot en fonction de r-ri")
plt.grid(True, alpha=0.3)
plt.legend()
#plt.ylim(bottom=0)
plt.show()

