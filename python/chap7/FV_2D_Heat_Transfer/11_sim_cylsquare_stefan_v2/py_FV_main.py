import sys
import os

# Ajouter le chemin du dossier parent dans sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from FV_lib.struct import Struct
from FV_lib.mesh import select_file, read_gmsh_msh, apply_periodic_BCs_along_x
from FV_lib.post import cutline, plot_raw_sol, plot_smoothed_sol, plot_regions

# Définit le répertoire courant comme celui où le script est exécuté
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from FV_impl.matrix import build_diffusion_matrix, apply_BCs_to_diffusion, apply_periodic_BCs_to_diffusion_matrix
from FV_impl.source import build_source_vector
from FV_impl.bc import assign_BCs
from FV_impl.solve import solve_linear_system, solve_nonlinear_system
from FV_impl.properties import assign_properties

if __name__ == "__main__":
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
                        
        # Construit le vecteur source
        cfd = build_source_vector(cfd)
                            
        # Résout le système linéaire
        cfd = solve_nonlinear_system(cfd)
        
        # Représente les données brutes
        plot_raw_sol(cfd)
        
        # Représente les données lissés et isovaleurs
        plot_smoothed_sol(cfd)

        # Trace le profil de température de [xmin, 0] à [xmax, 0]
        cutline(cfd, 100, 0, cfd.ymin, 0, cfd.ymax)
        
    except Exception as e:
        print(f"Erreur lors de la lecture du maillage: {e}")
        import traceback
        traceback.print_exc()