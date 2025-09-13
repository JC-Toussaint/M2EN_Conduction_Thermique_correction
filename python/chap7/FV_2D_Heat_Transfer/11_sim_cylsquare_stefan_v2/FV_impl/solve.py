from FV_lib.struct import Struct
import numpy as np
import scipy.sparse.linalg
from scipy.sparse import csr_matrix
from FV_impl.matrix import build_diffusion_matrix, apply_BCs_to_diffusion, apply_periodic_BCs_to_diffusion_matrix

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

def solve_nonlinear_system(cfd, Tguess=300):
    """
    Résout le système non-linéaire et stocke la solution dans cfd.T
    
    Parameters:
        cfd : Struct - Structure contenant la matrice de diffusion MD,
                       le vecteur source VQ, et le vecteur des conditions aux limites VD
    
    Returns:
        cfd : Struct - Structure mise à jour avec la solution stockée dans cfd.T
    """
    
    cfd.T = Tguess*np.ones(len(cfd.cell))
    Told = cfd.T.copy()
    niter = 0
    rtol = 1e-8
    while True:
        niter +=1
        # Construit la matrice de diffusion
        cfd = build_diffusion_matrix(cfd)
            
        # Applique les conditions aux limites Dirichlet ou Robin        
        cfd = apply_BCs_to_diffusion(cfd)
                    
        # Résolution du système linéaire
        cfd.T = scipy.sparse.linalg.spsolve(cfd.MD, cfd.VD + cfd.VQ)
        print(f'Temperature min : {np.min(cfd.T)} max : {np.max(cfd.T)}')
        err = np.linalg.norm(cfd.T-Told, ord=np.inf)/np.linalg.norm(Told, ord=np.inf)
        if abs(err) < rtol: break
        Told = cfd.T.copy()

    print(f"nombre d'itérations : {niter}")
    return cfd