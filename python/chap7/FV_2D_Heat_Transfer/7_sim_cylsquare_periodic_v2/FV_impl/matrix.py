from FV_lib.struct import Struct
import numpy as np
import scipy.sparse.linalg
from scipy.sparse import csr_matrix

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
            f_array = np.array(f)
            C_array = np.array(C)
            
            hCf = abs(np.dot(f_array - C_array, normal))  # distance projetée le long de la normale
            hcv = cfd.robin_map[name].hcv
            Ta = cfd.robin_map[name].Ta
            
            cfd.MD[own, own] += bnd.length * hcv
            cfd.VD[own]      += bnd.length * hcv * Ta
    
    return cfd

def apply_periodic_BCs_to_diffusion_matrix(cfd):
    """
    APPLY_PERIODIC_BCS_TO_DIFFUSION - Applique les conditions periodiques au terme de diffusion
    
    Cette fonction traite les arêtes périodiques pour construire la matrice de diffusion
    en tenant compte de la périodicité du domaine le long de l'axe x. Elle ajuste les
    coordonnées des centroïdes des cellules pour gérer la connectivité périodique et
    calcule les coefficients de diffusion appropriés.
    
    Paramètres
    ----------
    cfd : objet CFD
        Objet contenant les données du maillage CFD avec les attributs suivants :
        - per_edge : list
            Liste des arêtes périodiques, chaque arête ayant :
            - ncell : list de 2 entiers (indices des cellules adjacentes)
            - f : coordonnées du point milieu de l'arête
            - normal : vecteur normal à l'arête
            - length : longueur de l'arête
        - cell : list
            Liste des cellules avec :
            - C : coordonnées du centroïde
            - nrg : indice de la région/matériau
        - properties : list
            Propriétés des matériaux avec :
            - K : conductivité thermique
        - xmin, xmax : float
            Limites du domaine selon x
        - MD : scipy.csr_matrix
            Matrice de diffusion (modifiée en place)
        - periodic_BCs_along_x : bool
            Flag indiquant si les CL périodiques selon x sont activées
    
    Retours
    -------
    cfd : objet CFD
        L'objet CFD modifié avec la matrice de diffusion MD mise à jour
        pour inclure les contributions des arêtes périodiques
    
    Notes
    -----
    La fonction utilise une moyenne harmonique pour calculer la conductivité
    effective entre les cellules adjacentes. Les coordonnées des centroïdes
    sont ajustées temporairement pour tenir compte de la périodicité sans
    modifier les données originales.
    
    Raises
    ------
    AssertionError
        Si periodic_BCs_along_x n'est pas True (apply_periodic_BCs_along_x 
        doit être appelée en premier)
    """
    
    # Pour appliquer les conditions aux limites périodiques, on a ajouté à la liste des arêtes 
    # internes celles situées sur le bord gauche. Le centre de ces arêtes est noté f.
    # Les coordonnées du point f sont accessibles via cfd.edge[nseg].f, et la normale via cfd.edge[nseg].normal.
    # Toutefois, les coordonnées des centroïdes des cellules connectées par périodisation n'ont pas été modifiées.
    # Il est donc nécessaire de translater l’abscisse de C ou de F de ±Tx afin de les ramener dans le voisinage de f.
    # D'où la définition de la fonction wrap_backward
    def wrap_backward(x, x_ref, Tx):
        if x - x_ref > Tx / 2:
            x -= Tx
        return x
     
    Tx = cfd.xmax-cfd.xmin
            
    for nseg in range(len(cfd.per_edge)):  # chaque segment est partagé par deux cellules adjacentes
        seg = cfd.per_edge[nseg]
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
        
        assert cfd.periodic_BCs_along_x, 'apply_periodic_BCs_along_x must be called first !'
        F[0] = wrap_backward(F[0], f[0], Tx)
        C[0] = wrap_backward(C[0], f[0], Tx)
                                    
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
        cfd.MD[own, own] += diff_coeff
        
        # Off-diagonal (own, ngh)
        cfd.MD[own, ngh] -= diff_coeff
        
        # Symétrique: diagonal (ngh, ngh)
        cfd.MD[ngh, ngh] += diff_coeff
        
        # Symétrique: off-diagonal (ngh, own)
        cfd.MD[ngh, own] -= diff_coeff
        
    return cfd


