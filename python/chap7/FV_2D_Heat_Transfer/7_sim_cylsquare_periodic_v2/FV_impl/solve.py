from FV_lib.struct import Struct
import numpy as np
import scipy.sparse.linalg
from scipy.sparse import csr_matrix

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