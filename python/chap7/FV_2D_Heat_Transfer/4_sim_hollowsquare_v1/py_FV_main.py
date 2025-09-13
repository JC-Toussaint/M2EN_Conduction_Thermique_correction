import numpy as np
import scipy.sparse.linalg
from scipy.sparse import csr_matrix

from collections import defaultdict
import sys
import os

# Ajouter le chemin du dossier parent dans sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from FV_lib.struct import Struct
from FV_lib.mesh import select_file, read_gmsh_msh
from FV_lib.post import cutline, plot_raw_sol, plot_smoothed_sol, plot_regions

# Définit le répertoire courant comme celui où le script est exécuté
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def build_diffusion_matrix(cfd):
    """
    Construit la matrice de diffusion pour la méthode des volumes finis
    
    Description:
        Cette fonction construit la matrice associée au terme de diffusion dans la
        méthode des volumes finis (FVM). La matrice est construite basée sur les
        interactions cellule-à-cellule définies par les segments du maillage.
        
    Étapes:
        1. Initialise une matrice creuse MD avec une taille égale au nombre de cellules
        2. Boucle sur chaque segment du maillage:
           - Détermine le propriétaire (own) et la cellule voisine (ngh)
           - Calcule la distance projetée entre les deux cellules le long de la normale
           - Met à jour les entrées de la matrice de diffusion
        3. La matrice est symétrique
        
    Args:
        cfd (Struct): Structure contenant les données du maillage
        
    Returns:
        Struct: Structure mise à jour avec la matrice de diffusion (MD)
        
    Notes:
        - La matrice MD représente les coefficients de diffusion entre cellules adjacentes
        - Le terme de diffusion est calculé en utilisant la longueur de chaque segment
          et la distance projetée entre les centres des cellules adjacentes
    """
    NV = len(cfd.cell)
    
    # Initialiser les listes pour la matrice creuse
    row_indices = []
    col_indices = []
    data = []
        
    for nseg in range(len(cfd.edge)):  # chaque segment est partagé par deux cellules adjacentes
        seg = cfd.edge[nseg]
        ncell = seg.ncell
        own = ncell[0]  # propriétaire
        ngh = ncell[1]  # voisin
        
        # Obtenir les propriétés des matériaux
        nrg_own = cfd.cell[own].nrg
        nrg_ngh = cfd.cell[ngh].nrg
        
        K_own = cfd.properties[nrg_own].K
        K_ngh = cfd.properties[nrg_ngh].K
        
        f = np.array(seg.f)  # point milieu du segment
        C = np.array(cfd.cell[own].C)  # centre de la cellule propriétaire
        F = np.array(cfd.cell[ngh].C)  # centre de la cellule voisine
        normal = np.array(seg.normal)
        
        dCF = np.linalg.norm(F - C)  # distance entre centres
        hCF = abs(np.dot(F - C, normal))  # distance projetée le long de la normale
        hCf = abs(np.dot(f - C, normal))  # distance projetée C->f
        hfF = hCF - hCf  # distance projetée f->F
        
        # Coefficient de diffusion effectif (moyenne harmonique)
        K = hCF / (hCf/K_own + hfF/K_ngh)

        cos_tf = hCF / dCF   # cos(θf)
        
        # Coefficient de diffusion pour cette arête
        diff_coeff = K * seg.length / dCF * cos_tf
        
        # Ajouter les contributions à la matrice
        # Diagonal (own, own)
        row_indices.append(own)
        col_indices.append(own)
        data.append(diff_coeff)
        
        # Off-diagonal (own, ngh)
        row_indices.append(own)
        col_indices.append(ngh)
        data.append(-diff_coeff)
        
        # Symétrique: diagonal (ngh, ngh)
        row_indices.append(ngh)
        col_indices.append(ngh)
        data.append(diff_coeff)
        
        # Symétrique: off-diagonal (ngh, own)
        row_indices.append(ngh)
        col_indices.append(own)
        data.append(-diff_coeff)
    
    # Créer la matrice creuse et sommer les contributions multiples
    cfd.MD = csr_matrix((data, (row_indices, col_indices)), shape=(NV, NV))
    cfd.MD.sum_duplicates()  # Sommer les entrées dupliquées
    
    return cfd

def build_source_vector(cfd):
    """
    BUILD_SOURCE_VECTOR - Construit le vecteur source pour le maillage CFD
    
    Parameters:
        cfd : Struct - Structure contenant les données du maillage et des champs
    
    Returns:
        cfd : Struct - Structure mise à jour avec le vecteur source VQ
    
    Author: Adaptation Python de JC Toussaint Grenoble-INP
    """
    
    NV = len(cfd.cell)
    cfd.VQ = np.zeros(NV)
    
    for nvc in range(NV):
        cell = cfd.cell[nvc]
        xc = cell.C[0]  # Coordonnée x du centre de la cellule
        yc = cell.C[1]  # Coordonnée y du centre de la cellule
        nrg = cfd.cell[nvc].nrg  # Numéro de région
        Q = cfd.properties[nrg].Q  # Source de la région
        
        # Vérifier si Q est une fonction ou une valeur constante
        value = Q(xc, yc) if callable(Q) else Q
        
        cfd.VQ[nvc] = value * cell.S  # Multiplier par la surface de la cellule
    
    return cfd

def apply_BCs_to_diffusion(cfd):
    """
    APPLY_BCS_TO_DIFFUSION - Applique les conditions aux limites au terme de diffusion
    
    Description:
        Cette fonction construit le vecteur du membre de droite (RHS) pour l'équation de diffusion
        en incorporant les conditions aux limites dans la matrice de la méthode des volumes finis (FVM).
        La fonction ajuste la matrice de diffusion et le vecteur du terme source (VD) basé sur les
        conditions aux limites spécifiées dans la configuration CFD.
        Elle gère à la fois les conditions aux limites de Dirichlet et de robinn pour le terme de diffusion.
    
    Étapes:
        1. Initialise le vecteur RHS `VD` à zéro.
        2. Boucle à travers chaque frontière du maillage:
           - Pour chaque frontière, détermine la région associée et le nom physique.
           - Vérifie si le type de condition aux limites est Dirichlet ou robinn en utilisant
             `dirichlet_map` et `robin_map`.
        3. Pour les frontières Dirichlet:
           - Met à jour la matrice de diffusion (`MD`) et le vecteur RHS (`VD`) en utilisant
             la valeur de la condition de Dirichlet.
        4. Pour les frontières robinn:
           - Utilise les valeurs de frontière robinn (`hcv` pour le coefficient et `Ta` pour
             la température) pour mettre à jour la matrice de diffusion et le vecteur RHS.
    
    Parameters:
        cfd : Struct - Structure contenant les données du maillage, incluant les informations
                       de frontière, les informations de cellule, et les cartes de conditions
                       aux limites (`dirichlet_map` et `robin_map`).
    
    Returns:
        cfd : Struct - Structure `cfd` mise à jour avec la matrice de diffusion modifiée (`MD`)
                       et le vecteur RHS (`VD`).
    
    Notes:
        - Les conditions aux limites de Dirichlet sont gérées en assignant directement une valeur
          spécifiée au vecteur RHS à la frontière. La matrice de diffusion est mise à jour en conséquence.
        - Les conditions aux limites de robinn impliquent un terme de flux de chaleur (`hcv`) et
          un terme de température (`Ta`), qui contribuent au vecteur RHS et à la matrice de diffusion.
        - Cette fonction suppose que les conditions aux limites d'entrée sont correctement définies
          dans `dirichlet_map` et `robin_map` pour chaque frontière.
    
    Author: Adaptation Python de JC Toussaint Grenoble-INP
    """
    
    NV = len(cfd.cell)
    cfd.VD = np.zeros(NV)

    for nbnd in range(len(cfd.bnd_edge)):
        bnd = cfd.bnd_edge[nbnd]
        reg = bnd.nrg
        
        if reg == -1:
            continue  # région non nommée -> condition robinn nulle

        name = (cfd.physicalNames[reg]).name # physicalNames est un dict
        print('NAME ', name)
        own = bnd.ncell[0]  # Premier élément (indexation Python 0-based)
        C = cfd.cell[own].C
        f = bnd.f
        xf = f[0]
        yf = f[1]
        normal = bnd.normal
        
        # Vérifier si c'est une condition de Dirichlet
        if name in cfd.dirichlet_map:
            f_array = np.array(f)
            C_array = np.array(C)
            
            dCf = np.linalg.norm(f_array - C_array)
            hCf = abs(np.dot(f_array - C_array, normal))  # distance projetée le long de la normale
            cos_tf = hCf / dCf  # cos_θf
            
            bc = cfd.dirichlet_map[name]
            
            # Vérifier si Td est une fonction ou une valeur constante
            value = bc.Td(xf, yf) if callable(bc.Td) else bc.Td
            
            nrg = cfd.cell[own].nrg
            K = cfd.properties[nrg].K  # properties est un dict
            
            cfd.MD[own, own] += K * bnd.length / dCf * cos_tf
            cfd.VD[own]      += K * bnd.length / dCf * value * cos_tf
        
        # Vérifier si c'est une condition de robinn
        if name in cfd.robin_map:
            print('DEBUG robin ', name)
            f_array = np.array(f)
            C_array = np.array(C)
            
            hCf = abs(np.dot(f_array - C_array, normal))  # distance projetée le long de la normale
            hcv = cfd.robin_map[name].hcv
            Ta = cfd.robin_map[name].Ta
            
            cfd.MD[own, own] += bnd.length * hcv
            cfd.VD[own]      += bnd.length * hcv * Ta
    
    return cfd

def solve_linear_system(cfd):
    """
    Résout le système linéaire et stocke la solution dans cfd.T
    
    Parameters:
        cfd : Struct - Structure contenant la matrice de diffusion MD,
                       le vecteur source VQ, et le vecteur des conditions aux limites VD
    
    Returns:
        cfd : Struct - Structure mise à jour avec la solution stockée dans cfd.T
    """
    print(f"\nMatrice de diffusion construite:")
    print(f"  - Taille: {cfd.MD.shape}")
    print(f"  - Éléments non-nuls: {cfd.MD.nnz}")
    print(f"  - Sparsité: {cfd.MD.nnz / (cfd.MD.shape[0] * cfd.MD.shape[1]) * 100:.2f}%")
    
    # Résolution du système linéaire
    cfd.T = scipy.sparse.linalg.spsolve(cfd.MD, cfd.VD + cfd.VQ)
    
    return cfd

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
    cfd.dirichlet_map['left']  = Struct(Td = 300)
    cfd.dirichlet_map['right'] = Struct(Td = 500)
    
    # Dictionnaire pour les conditions de Robin : clé = nom de région, valeur = [scalaire, scalaire]
    cfd.robin_map = {}    
    # cfd.robin_map['left']  = Struct(hcv=10, Ta=300)
    # cfd.robin_map['right'] = Struct(hcv=10, Ta=300)
    # cfd.robin_map['top']   = Struct(hcv=10, Ta=300)
    # cfd.robin_map['down']  = Struct(hcv=10, Ta=300)
        
    # Dictionnaire pour les conditions de gradient normal
    cfd.normal_grad_map = {}
    cfd.normal_grad_map['outlet'] = Struct(gn=0)
    
    return cfd

def assign_properties(cfd):
    """
    Assigne les propriétés des matériaux aux régions du maillage CFD
    
    Author: JC Toussaint Grenoble-INP (traduit en Python)
    
    Args:
        cfd: objet Struct contenant les données du maillage
        
    Returns:
        cfd: objet Struct avec les propriétés assignées
    """
                
    # Dictionnaire pour les propriétés : clé = nom de région, valeur = dict des propriétés
    cfd.properties_map = {}
        
    # Définition des propriétés par région
    cfd.properties_map['square'] = Struct(K=200,  Q = lambda x, y: 0)

    # NE PAS MODIFIER CI-DESSOUS
    # cfd.regionNumber["square"] retourne 17 par exemple
    # cfd.physicalNames[17]["name"] retourne le nom de la région 'square'
    # cfd.properties[17].K permet d'obtenir le coefficient de diffusion 200
    # cfd.properties_map["square"].K retourne 200
    
    # Assigner les propriétés aux régions numérotées
    cfd.properties = {}
    for region_name in cfd.properties_map.keys():
        try:
            # Récupérer le numéro de région
            if region_name in cfd.regionNumber:
                nrg = cfd.regionNumber[region_name]
                cfd.properties[nrg] = cfd.properties_map[region_name]
            else:
                print(f'Attention: Région inconnue "{region_name}" - non trouvée dans regionNumber')
        except Exception as e:
            print(f'Attention: Région inconnue "{region_name}" : {str(e)}')
    
    return cfd

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple d'utilisation
    cfd = Struct()    
    try:
        cfd.mesh_name = select_file()  
        cfd = read_gmsh_msh(cfd)
        
        print(f"Maillage lu avec succès:")
        print(f"  - Nombre de nœuds: {len(cfd.node)}")
        print(f"  - Nombre de cellules: {len(cfd.cell)}")
        print(f"  - Nombre d'arêtes internes: {len(cfd.edge)}")
        print(f"  - Nombre d'arêtes de bord: {len(cfd.bnd_edge)}")
        print(f"  - Domaine: [{cfd.xmin:.3f}, {cfd.xmax:.3f}] x [{cfd.ymin:.3f}, {cfd.ymax:.3f}]")
        
        # Affiche les groupes physiques
        print("\nGroupes physiques:")
        for tag, info in cfd.physicalNames.items():
            print(f"  - {info.name} (dim={info.dim}, tag={tag})")
        
        # Affiche le maillage et les régions surfaciques    
        plot_regions(cfd)
                        
        # Définit les propriétés physiques par région
        cfd = assign_properties(cfd)

        # Définit les conditions aux limites
        cfd = assign_BCs(cfd)
                
        # Construit la matrice de diffusion
        cfd = build_diffusion_matrix(cfd)
        
        # Construit le vecteur source
        cfd = build_source_vector(cfd)
        
        # Applique les conditions aux limites Dirichlet ou Robin        
        cfd = apply_BCs_to_diffusion(cfd)
                
        # Résout le système linéaire
        cfd = solve_linear_system(cfd)
        
        # Représente les données brutes
        plot_raw_sol(cfd)
        
        # Représente les données lissés et isovaleurs
        plot_smoothed_sol(cfd)

        # Trace le profil de température de [xmin, 0] à [xmax, 0]
        cutline(cfd, 100, cfd.xmin, 0, cfd.xmax, 0);
        
    except Exception as e:
        print(f"Erreur lors de la lecture du maillage: {e}")
        import traceback
        traceback.print_exc()