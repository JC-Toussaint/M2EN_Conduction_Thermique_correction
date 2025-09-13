import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erf, erfc
from scipy.integrate import quad

def ierfc(u):
    """
    Calcule l'intégrale de la fonction d'erreur complémentaire (ierfc)
    ierfc(u) = ∫[u to ∞] erfc(t) dt
    
    Utilise la formule analytique : ierfc(u) = (1/√π) * exp(-u²) - u * erfc(u)
    """
    return (1 / np.sqrt(np.pi)) * np.exp(-u**2) - u * erfc(u)

def plot_error_functions():
    """
    Trace les fonctions d'erreur erf(u), erfc(u), et ierfc(u)
    """
    # Définir la plage de valeurs
    u = np.linspace(-3, 3, 1000)
    
    # Calculer les fonctions
    erf_values = erf(u)
    erfc_values = erfc(u)
    ierfc_values = ierfc(u)
    
    # Créer la figure avec subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Premier graphique : erf et erfc
    ax1.plot(u, erf_values, 'b-', linewidth=2, label='erf(u)')
    ax1.plot(u, erfc_values, 'r-', linewidth=2, label='erfc(u)')
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax1.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlabel('u')
    ax1.set_ylabel('Valeur')
    ax1.set_title('Fonctions d\'erreur erf(u) et erfc(u)')
    ax1.legend()
    ax1.set_ylim(-1.2, 2.2)
    
    # Deuxième graphique : ierfc
    ax2.plot(u, ierfc_values, 'g-', linewidth=2, label='ierfc(u)')
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax2.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlabel('u')
    ax2.set_ylabel('Valeur')
    ax2.set_title('Intégrale de la fonction d\'erreur complémentaire ierfc(u)')
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

def plot_all_functions():
    """
    Trace toutes les fonctions sur le même graphique
    """
    u = np.linspace(-3, 3, 1000)
    
    erf_values = erf(u)
    erfc_values = erfc(u)
    ierfc_values = ierfc(u)
    
    plt.figure(figsize=(12, 8))
    plt.plot(u, erf_values, 'b-', linewidth=2, label='erf(u)')
    plt.plot(u, erfc_values, 'r-', linewidth=2, label='erfc(u)')
    plt.plot(u, ierfc_values, 'g-', linewidth=2, label='ierfc(u)')
    
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    plt.grid(True, alpha=0.3)
    plt.xlabel('u', fontsize=12)
    plt.ylabel('Valeur', fontsize=12)
    plt.title('Fonctions d\'erreur : erf(u), erfc(u), ierfc(u)', fontsize=14)
    plt.legend(fontsize=12)
    plt.show()

def print_function_values():
    """
    Affiche les valeurs des fonctions pour quelques points spécifiques
    """
    print("Valeurs des fonctions d'erreur pour quelques points :")
    print("-" * 60)
    print(f"{'u':>8} {'erf(u)':>12} {'erfc(u)':>12} {'ierfc(u)':>12}")
    print("-" * 60)
    
    test_values = [-3, -2, -1, 0, 1, 2, 3]
    
    for u in test_values:
        erf_val = erf(u)
        erfc_val = erfc(u)
        ierfc_val = ierfc(u)
        print(f"{u:8.1f} {erf_val:12.6f} {erfc_val:12.6f} {ierfc_val:12.6f}")

def mathematical_properties():
    """
    Vérifie quelques propriétés mathématiques des fonctions
    """
    print("\nVérification des propriétés mathématiques :")
    print("-" * 50)
    
    # Propriété : erf(u) + erfc(u) = 1
    u_test = 1.5
    sum_check = erf(u_test) + erfc(u_test)
    print(f"erf({u_test}) + erfc({u_test}) = {sum_check:.10f} (doit être ≈ 1)")
    
    # Propriété : erf(-u) = -erf(u)
    u_test = 2.0
    antisym_check = erf(-u_test) + erf(u_test)
    print(f"erf(-{u_test}) + erf({u_test}) = {antisym_check:.10f} (doit être ≈ 0)")
    
    # Valeurs limites
    print(f"erf(0) = {erf(0):.10f} (doit être 0)")
    print(f"erfc(0) = {erfc(0):.10f} (doit être 1)")
    print(f"ierfc(0) = {ierfc(0):.10f}")

def main():
    """
    Fonction principale qui exécute tous les exemples
    """
    print("Programme de représentation des fonctions d'erreur")
    print("=" * 55)
    
    # Afficher les valeurs numériques
    print_function_values()
    
    # Vérifier les propriétés mathématiques
    mathematical_properties()
    
    # Créer les graphiques
    print("\nGénération des graphiques...")
    
    # Graphiques séparés
    plot_error_functions()
    
    # Graphique combiné
    plot_all_functions()
    
    print("\nGraphiques générés avec succès !")
    
    # Afficher les définitions mathématiques
    print("\nDéfinitions mathématiques :")
    print("-" * 30)
    print("erf(u) = (2/√π) ∫₀ᵘ exp(-t²) dt")
    print("erfc(u) = 1 - erf(u) = (2/√π) ∫ᵘ∞ exp(-t²) dt")
    print("ierfc(u) = ∫ᵘ∞ erfc(t) dt = (1/√π)exp(-u²) - u·erfc(u)")

if __name__ == "__main__":
    main()