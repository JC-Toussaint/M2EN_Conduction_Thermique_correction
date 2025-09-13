import numpy as np
import matplotlib.pyplot as plt

# Paramètres du problème
k1 = 200    # Conductivité thermique du cœur (W/m·K)
k2 = 10     # Conductivité thermique de la coque (W/m·K)
Q = 1000    # Densité volumique de puissance (W/m³)
h = 10      # Coefficient d'échange convectif (W/m²·K)
Ta = 300    # Température ambiante (K)
Ri = 1      # Rayon intérieur (m)
Re = 2      # Rayon extérieur (m)

# Calcul des coefficients
a1 = -Q / (6 * k1)
a2 = -Q * Ri**3 / (3 * k2)

# Coefficient b2
b2 = Ta + (Q * Ri**3) / (3 * h * Re**2) - (Q * Ri**3) / (3 * k2 * Re)

# Coefficient b1
b1 = Ta + (Q * Ri**3) / (3 * h * Re**2) + (Q * Ri**2) / (6 * k1) + (Q * Ri**2) / (3 * k2) * (1 - Ri / Re)

print("Paramètres du problème:")
print(f"k1 = {k1} W/m·K")
print(f"k2 = {k2} W/m·K")
print(f"Q = {Q} W/m³")
print(f"h = {h} W/m²·K")
print(f"Ta = {Ta} K")
print(f"Ri = {Ri} m")
print(f"Re = {Re} m")
print()
print("Coefficients calculés:")
print(f"a1 = {a1:.6f}")
print(f"a2 = {a2:.3f}")
print(f"b1 = {b1:.3f} K")
print(f"b2 = {b2:.3f} K")
print()

# Température de surface (vérification)
T_surface = Ta + (Q * Ri**3) / (3 * h * Re**2)
print(f"Température de surface T(Re) = {T_surface:.3f} K")
print(f"Vérification avec T2(Re) = {-a2/Re + b2:.3f} K")
print()

# Définition des domaines
r1 = np.linspace(0.01, Ri, 100)  # Cœur (éviter r=0 pour l'affichage)
r2 = np.linspace(Ri, Re, 100)    # Coque

# Calcul des températures
T1 = a1 * r1**2 + b1  # Température dans le cœur
T2 = -a2 / r2 + b2    # Température dans la coque

# Calcul des températures aux interfaces pour vérification
T1_interface = a1 * Ri**2 + b1
T2_interface = -a2 / Ri + b2
print(f"Continuité en r=Ri:")
print(f"T1(Ri) = {T1_interface:.3f} K")
print(f"T2(Ri) = {T2_interface:.3f} K")
print(f"Différence = {abs(T1_interface - T2_interface):.6f} K")
print()

# Calcul des gradients aux interfaces pour vérification
dT1_dr_interface = 2 * a1 * Ri
dT2_dr_interface = a2 / Ri**2
flux1 = -k1 * dT1_dr_interface
flux2 = -k2 * dT2_dr_interface
print(f"Continuité du flux en r=Ri:")
print(f"Flux1 = {flux1:.3f} W/m²")
print(f"Flux2 = {flux2:.3f} W/m²")
print(f"Différence = {abs(flux1 - flux2):.6f} W/m²")
print()

# Création du graphique
plt.figure(figsize=(12, 8))

# Tracé des températures
plt.subplot(2, 1, 1)
plt.plot(r1, T1, 'b-', linewidth=2, label='Cœur (D1)')
plt.plot(r2, T2, 'r-', linewidth=2, label='Coque (D2)')

# Points particuliers
plt.plot(0, b1, 'bo', markersize=8, label=f'Centre: T(0) = {b1:.1f} K')
plt.plot(Ri, T1_interface, 'go', markersize=8, label=f'Interface: T(Ri) = {T1_interface:.1f} K')
plt.plot(Re, T_surface, 'ro', markersize=8, label=f'Surface: T(Re) = {T_surface:.1f} K')

# Lignes verticales aux interfaces
plt.axvline(x=Ri, color='gray', linestyle='--', alpha=0.7, label='Interface cœur/coque')
plt.axhline(y=Ta, color='orange', linestyle=':', alpha=0.7, label=f'T ambiante = {Ta} K')

plt.xlabel('Rayon r (m)')
plt.ylabel('Température T (K)')
plt.title('Distribution de température dans le système sphérique composite')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(0, Re * 1.1)

# Tracé des gradients de température
plt.subplot(2, 1, 2)
dT1_dr = 2 * a1 * r1
dT2_dr = a2 / r2**2

plt.plot(r1, dT1_dr, 'b-', linewidth=2, label='Gradient dans le cœur')
plt.plot(r2, dT2_dr, 'r-', linewidth=2, label='Gradient dans la coque')
plt.axvline(x=Ri, color='gray', linestyle='--', alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)

plt.xlabel('Rayon r (m)')
plt.ylabel('Gradient dT/dr (K/m)')
plt.title('Gradient de température')
plt.grid(True, alpha=0.3)
plt.legend()
plt.xlim(0, Re * 1.1)

plt.tight_layout()
plt.show()

# Analyse énergétique
print("Analyse énergétique:")
puissance_totale = Q * (4/3) * np.pi * Ri**3
print(f"Puissance totale générée = {puissance_totale:.1f} W")

flux_surface = h * (T_surface - Ta)
puissance_evacuee = flux_surface * 4 * np.pi * Re**2
print(f"Puissance évacuée en surface = {puissance_evacuee:.1f} W")
print(f"Bilan énergétique (différence) = {abs(puissance_totale - puissance_evacuee):.2e} W")