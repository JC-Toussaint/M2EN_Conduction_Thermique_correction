from FV_lib.struct import Struct
import numpy as np
import scipy.sparse.linalg
from scipy.sparse import csr_matrix

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
        xc = cell.C[0]   # Coordonnée x du centre de la cellule
        yc = cell.C[1]   # Coordonnée y du centre de la cellule
        radius = abs(xc) # rayon axi
        nrg = cfd.cell[nvc].nrg  # Numéro de région
        Q = cfd.properties[nrg].Q  # Source de la région
        
        # Vérifier si Q est une fonction ou une valeur constante
        value = Q(xc, yc) if callable(Q) else Q
        
        cfd.VQ[nvc] = value * cell.S * radius # Multiplier par la surface de la cellule
    
    return cfd