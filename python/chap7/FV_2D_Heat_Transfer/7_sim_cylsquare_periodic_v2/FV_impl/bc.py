from FV_lib.struct import Struct

def assign_BCs(cfd):
    """
    ASSIGN_BCS - Assigne les conditions aux limites de Dirichlet et de robinn
    
    Description:
        Cette fonction configure les conditions aux limites pour la simulation, spécifiquement
        les conditions de Dirichlet et de robinn.
        - Les conditions aux limites de Dirichlet sont assignées en définissant une valeur scalaire
          pour chaque région du domaine.
        - Les conditions aux limites de robinn sont assignées en spécifiant deux valeurs scalaires
          (ex: coefficient de transfert thermique et température) pour chaque région.
    
    Étapes:
        1. Crée un dictionnaire pour les conditions de Dirichlet. Le dictionnaire mappe les noms de
           régions (ex: 'left', 'right') aux valeurs scalaires.
        2. Assigne des valeurs spécifiques aux régions de frontière. 
        3. Crée un dictionnaire pour les conditions de robinn, mappant les noms de régions aux
           tableaux de deux valeurs scalaires (ex: [coefficient de transfert thermique, température]).
        4. Configure toutes les conditions aux limites additionnelles nécessaires en ajoutant aux
           conteneurs `dirichlet_map` et `robin_map`.
    
    Parameters:
        cfd : Struct - Structure contenant les données du maillage et des conditions aux limites.
    
    Returns:
        cfd : Struct - Structure `cfd` mise à jour avec les conteneurs `dirichlet_map` et
                       `robin_map`, qui stockent les assignations de conditions aux limites.
    
    Notes:
        - Les conditions de Dirichlet sont typiquement utilisées pour spécifier des valeurs connues
          aux frontières (ex: température fixe ou concentration).
        - Les conditions de robinn sont utilisées pour spécifier la dérivée (ex: flux ou gradient)
          aux frontières.
        - Les dictionnaires sont flexibles, permettant une extension facile pour des régions et
          conditions additionnelles.
    
    Author: Adaptation Python de JC Toussaint Grenoble-INP
    """
        
    # Dictionnaire pour les conditions de Dirichlet : clé = nom de région, valeur = scalaire
    cfd.dirichlet_map = {}
    
    # Exemples de conditions de Dirichlet (commentés comme dans l'original)
    # cfd.dirichlet_map['left'] = Struct(Td = lambda x, y: 300)
    # cfd.dirichlet_map['down'] = Struct(Td = lambda x, y: (1-x))
    # cfd.dirichlet_map['left'] = Struct(Td = 300)
    # cfd.dirichlet_map['right'] = Struct(Td = 500)
    
    # Dictionnaire pour les conditions de Robin : clé = nom de région, valeur = [scalaire, scalaire]
    cfd.robin_map = {}    
    cfd.robin_map['left']  = Struct(hcv=10, Ta=300)
    cfd.robin_map['right'] = Struct(hcv=10, Ta=300)
    cfd.robin_map['top']   = Struct(hcv=10, Ta=300)
    cfd.robin_map['down']  = Struct(hcv=10, Ta=300)
        
    # Dictionnaire pour les conditions de gradient normal
    cfd.normal_grad_map = {}
    cfd.normal_grad_map['outlet'] = Struct(gn=0)
    
    return cfd