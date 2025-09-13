import numpy as np

from collections import defaultdict
import sys
import os
import copy

from pathlib import Path
from FV_lib.struct import Struct

# Définit le répertoire courant comme celui où le script est exécuté
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtGui import QFont

import numpy as np
from scipy.spatial import KDTree

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sélection de fichier .pypro")
        self.setGeometry(100, 100, 600, 300)

        # Créer un layout principal (vertical) pour organiser les widgets
        layout = QVBoxLayout()

        # Ajouter un QLabel pour afficher le texte sur deux lignes avec une police de taille 24
        self.label = QLabel("Finite Volume Solver for Heat Transfer,\n© Grenoble-INP Phelma 2025", self)
        self.label.setFont(QFont("Arial", 24))  # Définir la police et la taille
        layout.addWidget(self.label)

        # Ajouter un QLabel pour afficher le nom du fichier sélectionné
        self.file_label = QLabel("", self)
        layout.addWidget(self.file_label)

        # Créer un layout horizontal pour les boutons
        button_layout = QHBoxLayout()

        # Ajouter un bouton "Open"
        self.open_button = QPushButton("Open", self)
        self.open_button.clicked.connect(self.open_file_dialog)  # Connecter le bouton à la méthode open_file_dialog
        button_layout.addWidget(self.open_button)

        # Ajouter un bouton "Run"
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.close_application)  # Connecter le bouton à la méthode close_application
        button_layout.addWidget(self.run_button)

        # Ajouter le layout horizontal à l'interface principale
        layout.addLayout(button_layout)

        # Appliquer le layout à la fenêtre
        self.setLayout(layout)

        # Afficher la fenêtre
        self.show()

    def open_file_dialog(self):
        # Ouvrir la boîte de dialogue de sélection de fichier
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_filter = "Files .msh (*.msh)"
        
        # QFileDialog.getOpenFileName retourne un tuple (nom du fichier, filtre)
        file_name, _ = QFileDialog.getOpenFileName(self, "Select an ascii gmsh v2.0 file", "", file_filter, options=options)
        
        if file_name:
            # Afficher le nom du fichier sélectionné dans le QLabel
            name = Path(file_name).name
            self.file_label.setFont(QFont("Arial", 18))  # Définir la police et la taille
            self.file_label.setText(f"File selected : {name}")
            self.file_name = file_name
        else:
            self.file_label.setText("No Filename.")
            self.file_name = None

    def close_application(self):
        # Fermer l'application
        self.close()

def select_file():
    # Initialiser l'application PyQt5
    app = QApplication(sys.argv) 
    
    try:    
        # Créer une instance de la fenêtre de sélection de fichier
        selector = FileSelector()
        
        # Exécuter l'application
        app.exec_()
        
    except ValueError as e:
        print(e)
        sys.exit(1)  # Exit with status 1 to indicate an error
    del app
    return selector.file_name

def read_gmsh_msh(cfd):
    """
    Lit un fichier de maillage Gmsh et remplit la structure CFD
    
    Args:
        cfd: Instance de la classe Struct
    
    Returns:
        cfd: Structure CFD mise à jour
    """
    filename = cfd.mesh_name
    cfd.physicalNames = {}
    cfd.regionNumber  = {}
    try:
        with (open(filename, 'r') as fid):
            node = []
            elt = []
            cell = []
            
            while True:
                line = fid.readline()
                if not line:
                    break
                line = line.strip()
                
                # Lecture des noms physiques
                if line == '$PhysicalNames':
                    num_phys_names = int(fid.readline().strip())
                    for i in range(num_phys_names):
                        line = fid.readline().strip()
                        parts = line.split()
                        dim = int(parts[0])
                        id_phys = int(parts[1])
                        name = parts[2].strip('"')
                        
                        cfd.physicalNames[id_phys] = Struct()
                        cfd.physicalNames[id_phys].dim = dim
                        cfd.physicalNames[id_phys].name = name
                        cfd.regionNumber[name] = id_phys
                    
                    fid.readline()  # Lire $EndPhysicalNames
                
                # Lecture des nœuds
                elif line == '$Nodes':
                    num_nodes = int(fid.readline().strip())
                    node = np.zeros((num_nodes, 2))  # (X, Y)
                    for i in range(num_nodes):
                        line = fid.readline().strip()
                        data = list(map(float, line.split()))
                        node[i] = [data[1], data[2]]
                    
                    fid.readline()  # Lire $EndNodes
                
                # Lecture des éléments
                elif line == '$Elements':
                    num_elements = int(fid.readline().strip())
                    nvc = 0
                    nbnd = 0
                    
                    for i in range(num_elements):
                        line = fid.readline().strip()
                        line_data = list(map(int, line.split()))
                        
                        elem_id = line_data[0]
                        elem_type = line_data[1]
                        num_tags = line_data[2]
                        num_region = line_data[3]
                        
                        # Indices des nœuds
                        ind = line_data[3 + num_tags:]
                        ind = np.array(ind)-1

                        # Créer l'élément
                        element = {
                            'id': elem_id,
                            'type': elem_type,
                            'ind': ind,
                            'nrg': num_region,
                            'faces': []
                        }
                        elt.append(element)
                        
                        # Si c'est un triangle ou quadrangle
                        if elem_type in [2, 3]:  # 2=triangle, 3=quadrangle
                            nvc += 1
                            
                            # Calcul du centre de gravité et de l'aire
                            x = node[ind, 0]
                            y = node[ind, 1]
                            x = np.append(x, x[0])
                            y = np.append(y, y[0])
                            
                            S = 0
                            xG = 0
                            yG = 0
                            
                            for j in range(len(ind)):
                                cross_prod = x[j] * y[j+1] - y[j] * x[j+1]
                                xG += cross_prod * (x[j] + x[j+1])
                                yG += cross_prod * (y[j] + y[j+1])
                                S += cross_prod
                            
                            S = 0.5 * S
                            xG = xG / (6.0 * S)
                            yG = yG / (6.0 * S)
                            
                            # Créer la cellule
                            cell_data = Struct(
                                id=nvc,
                                type = elem_type,
                                ind = np.array(ind),
                                nrg = num_region,
                                nedge = [],
                                S=abs(S),
                                C = np.array([xG, yG])
                            )

                            cell.append(cell_data)                    
                    fid.readline()  # Lire $EndElements
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Impossible d'ouvrir le fichier {filename}")
    
    # Stocker les données dans la structure CFD
    cfd.node = node
    cfd.elt = elt
    cfd.cell = cell
    
    # Transformer en maillage volumes finis
    cfd = finite_volume_mesh_transform(cfd)
    
    return cfd


def finite_volume_mesh_transform(cfd):
    """
    Transforme le maillage éléments finis en maillage volumes finis
    
    Args:
        cfd: Structure CFD
    
    Returns:
        cfd: Structure CFD transformée
    """
    # Extraire les arêtes
    segment_map = extract_edges(cfd)
    cfd.bnd_edge = []
    cfd.edge = []

    # Recalculer les centres de gravité et aires des cellules
    for i in range(len(cfd.cell)):
        ind = cfd.cell[i].ind

        node_indices = ind
        x = cfd.node[node_indices, 0]
        y = cfd.node[node_indices, 1]
        x = np.append(x, x[0])
        y = np.append(y, y[0])
        
        S = 0
        xG = 0
        yG = 0
        
        for j in range(len(ind)):
            cross_prod = x[j] * y[j+1] -y[j] * x[j+1]
            xG += cross_prod * (x[j] + x[j+1])
            yG += cross_prod * (y[j] + y[j+1])
            S += cross_prod
        
        S = 0.5 * S
        cfd.cell[i].S = abs(S)
        xG = xG / (6.0 * S)
        yG = yG / (6.0 * S)
        cfd.cell[i].C = np.array([xG, yG])
    
    # Traiter les segments partagés
    nseg = 0  # compteur d'arêtes intérieures
    nbnd = 0  # compteur d'arêtes du bord
    
    for key, elements_touching in segment_map.items():
        # Décoder la clé
        nums = key.split('-')
        ind = np.array([int(nums[0]), int(nums[1])])
        
        # Calculer la tangente et la normale
        tangent = cfd.node[ind[1], 0:2] - cfd.node[ind[0], 0:2]
        tangent = tangent / np.linalg.norm(tangent)
        
        # Point milieu de l'arête
        f = np.mean(cfd.node[ind], axis=0)
        
        # Normale (rotation de 90° de la tangente)
        normal = np.array([-tangent[1], tangent[0]])
        
        # Déterminer l'orientation de la normale
        own = elements_touching[0]
        Cf = f - cfd.cell[own].C
        signe = np.sign(np.dot(normal, Cf))
        
        # Longueur de l'arête
        length = np.linalg.norm(cfd.node[ind[1]] - cfd.node[ind[0]])
        
        if len(elements_touching) == 1:
            # Arête de bord
            edge_data = Struct(
                ncell = elements_touching,
                ind   = ind,
                length= length,
                f = f,
                normal = signe * normal,
                nrg = -1
            )
            cfd.bnd_edge.append(edge_data)
            nbnd += 1
        
        elif len(elements_touching) == 2:
            # Arête intérieure
            edge_data = Struct(
                ncell = elements_touching,
                ind = ind,
                length = length,
                f = f,
                normal = signe * normal,
                nrg = -1
            )
            cfd.edge.append(edge_data)
            nseg += 1

    # Calculer les bornes du domaine
    cfd.xmin = np.min(cfd.node[:, 0])
    cfd.xmax = np.max(cfd.node[:, 0])
    cfd.ymin = np.min(cfd.node[:, 1])
    cfd.ymax = np.max(cfd.node[:, 1])
    cfd.lc = min(cfd.xmax - cfd.xmin, cfd.ymax - cfd.ymin)
    
    # Associer les arêtes aux cellules
    for nseg in range(len(cfd.edge)):
        ncell = cfd.edge[nseg].ncell
        cfd.cell[ncell[0]].nedge.append(nseg)
        cfd.cell[ncell[1]].nedge.append(nseg)
    
    # Traiter les régions des arêtes de bord
    segment_map_bnd = {}
    for i, elt in enumerate(cfd.elt):
        if elt['type'] == 1:  # Ligne
            ind = np.sort(elt['ind'])
            nrg = elt['nrg']
            seg_key = f"{ind[0]}-{ind[1]}"
            if seg_key in segment_map_bnd:
                segment_map_bnd[seg_key].append(nrg)
            else:
                segment_map_bnd[seg_key] = nrg
    
    for i in range(len(cfd.bnd_edge)):
        ind = np.sort(cfd.bnd_edge[i].ind)
        seg_key = f"{ind[0]}-{ind[1]}"
        if seg_key in segment_map_bnd:
            nrg = segment_map_bnd[seg_key]
            cfd.bnd_edge[i].nrg = nrg
    
    # Supprimer le champ elt (plus utile)
    delattr(cfd, 'elt')
    
    # Placer la donnée cfd.periodic_BCs_along_x à False par défaut
    cfd.periodic_BCs_along_x = False
    return cfd

def extract_edges(cfd):
    """
    Extrait les arêtes du maillage
    
    Args:
        cfd (Struct): Structure du maillage
        
    Returns:
        dict: Dictionnaire des arêtes
    """
    segment_map = defaultdict(list)
    
    for nvc, cell in enumerate(cfd.cell):
        # Définir les arêtes selon le type d'élément
        if cell.type == 2:  # Triangle
            cell_ind =cell.ind
            edges = [
                [cell_ind[0], cell_ind[1]],
                [cell_ind[1], cell_ind[2]],
                [cell_ind[2], cell_ind[0]]
            ]
        elif cell.type == 3:  # Quadrangle
            cell_ind =cell.ind
            edges = [
                [cell_ind[0], cell_ind[1]],
                [cell_ind[1], cell_ind[2]],
                [cell_ind[2], cell_ind[3]],
                [cell_ind[3], cell_ind[0]]
            ]
        else:
            continue
        
        # Ajouter les arêtes à la table
        for edge in edges:
            seg = sorted(edge)
            seg_key = f"{seg[0]}-{seg[1]}"
            segment_map[seg_key].append(nvc)
    
    return segment_map

import numpy as np

def charac_mesh(cfd):
    """
    CHARAC_MESH - Affiche les caractéristiques détaillées du maillage CFD
    
    Description:
        Cette fonction affiche des informations détaillées sur la structure du maillage
        CFD incluant les cellules, les arêtes intérieures et les arêtes de bord.
        
    Informations affichées:
        - CELLS: numéro de cellule, région, centre, surface, arêtes
        - INNER EDGES: point milieu, cellules propriétaire/voisine, normale
        - BND EDGES: région de bord, point milieu, cellule propriétaire, normale
    
    Parameters:
        cfd : Struct - Structure contenant les données du maillage CFD
                      avec les attributs cell, edge, bnd_edge, physicalNames
    
    Author: Traduction Python de JC Toussaint Grenoble-INP
    """
    
    def format_vector(vec, precision=3):
        """Formate un vecteur comme mat2str de MATLAB"""
        if hasattr(vec, '__len__') and len(vec) > 1:
            # Vecteur - format [x y] ou [x y z]
            formatted = ' '.join([f'{x:.{precision}f}' for x in vec])
            return f'[{formatted}]'
        else:
            # Scalaire
            if hasattr(vec, '__len__'):
                vec = vec[0] if len(vec) > 0 else 0
            return f'{vec:.{precision}f}'
    
    def filter_small_values(vec, threshold=1e-6):
        """Filtre les petites valeurs (équivalent de f(abs(f) < 1e-6) = 0 en MATLAB)"""
        if hasattr(vec, '__len__'):
            filtered = np.array(vec, dtype=float)
            filtered[np.abs(filtered) < threshold] = 0
            return filtered
        else:
            return 0 if abs(vec) < threshold else vec

    NV = len(cfd.cell)

    print('CELLS')
    for nvc in range(NV):
        cell = cfd.cell[nvc]
        nrg = cell.nrg
        
        # Récupération du nom de la région
        try:
            region = cfd.physicalNames[nrg].name
        except (AttributeError, KeyError, IndexError):
            region = f"region_{nrg}"  # Fallback si physicalNames n'existe pas
        
        # Formatage des données de la cellule
        C_str = format_vector(cell.C, 3)
        S_val = cell.S
        
        # Gestion de nedge (peut ne pas exister dans tous les cas)
        try:
            nedge_str = format_vector(cell.nedge, 0)
        except AttributeError:
            nedge_str = "N/A"
        
        # Affichage formaté 
        print(f'cell {nvc}: nrg:{nrg}, reg:{region}, C:{C_str}, S:{S_val:.3f}, nedge:{nedge_str}')
    
    print('---------------------------------------')

    print('INNER EDGES')
    if hasattr(cfd, 'edge') and cfd.edge:
        for nseg in range(len(cfd.edge)):
            seg = cfd.edge[nseg]
            
            # Point milieu de l'arête avec filtrage
            f = filter_small_values(seg.f)
            f_str = format_vector(f, 3)
            
            # Cellules propriétaire et voisine
            ncell = seg.ncell
            own = ncell[0]  # owner (propriétaire)
            ngh = ncell[1]  # neighbour (voisine)
            
            # Normale avec filtrage
            normal = filter_small_values(seg.normal)
            normal_str = format_vector(normal, 3)
            
            # Affichage formaté 
            print(f'edge {nseg}: f:{f_str} own:{own} ngh:{ngh} normal:{normal_str}')
    else:
        print('No inner edges found')
    
    print('---------------------------------------')

    print('BND EDGES')
    if hasattr(cfd, 'bnd_edge') and cfd.bnd_edge:
        for nbnd in range(len(cfd.bnd_edge)):
            seg = cfd.bnd_edge[nbnd]
            nrg = seg.nrg
            
            # Récupération du nom de la région de bord
            try:
                region = cfd.physicalNames[nrg].name
            except (AttributeError, KeyError, IndexError):
                region = f"region_{nrg}"  # Fallback si physicalNames n'existe pas
            
            # Point milieu de l'arête de bord
            f = filter_small_values(seg.f)
            f_str = format_vector(f, 3)
            
            # Cellule propriétaire
            ncell = seg.ncell
            own = ncell[0]  # owner (propriétaire)
            
            # Normale avec filtrage
            normal = filter_small_values(seg.normal)
            normal_str = format_vector(normal, 3)
            
            # Affichage formaté 
            print(f'bnd_edge {nbnd}: nrg:{nrg}, reg:{region}, f:{f_str}, own:{own}, normal:{normal_str}')
    else:
        print('No boundary edges found')

def apply_periodic_BCs_along_x(cfd):
    """
    Applies periodic boundary conditions along the x-axis.
    
    Parameters:
    -----------
    cfd : dict
        Dictionary containing the mesh data, including the boundary information, 
        cell information, and boundary condition maps (dirichlet_map and neuman_map).
    
    Returns:
    --------
    cfd : dict
        The updated cfd dictionary
    
    Author: JC Toussaint Grenoble-INP (translated to Python)
    """
    
    cfd.per_edge=[]
    
    # Collect coordinates from all boundary edges
    coords = []
    for nbnd in range(len(cfd.bnd_edge)):
        bnd = cfd.bnd_edge[nbnd]
        f = bnd.f
        coords.append(f)
    
    coords = np.array(coords)
    
    # Build KD-tree for efficient nearest neighbor search
    tree = KDTree(coords)
    
    eps = 1e-6
    Tx = cfd.xmax - cfd.xmin
    
    # Create mask to track which boundary edges to keep
    mask = np.ones(len(cfd.bnd_edge), dtype=bool)
        
    for nbnd in range(len(cfd.bnd_edge)):
        bnd = cfd.bnd_edge[nbnd]
        x = bnd.f[0]
        y = bnd.f[1]
        
        # Skip if not on the left boundary
        if abs(x - cfd.xmin) > eps * cfd.lc:
            continue
            
        # Search for corresponding point on the right boundary
        pt = np.array([x + Tx, y])
        
        # Find nearest neighbor
        dist, nbnd_img = tree.query(pt)  # Use only x,y coordinates for 2D search
        
        if dist < eps * cfd.lc:
            # Mark both boundary edges for removal
            mask[nbnd] = False
            mask[nbnd_img] = False
            
            # Create internal edge connecting the periodic boundaries
            src_edge = copy.deepcopy(cfd.bnd_edge[nbnd])
            own = src_edge.ncell[0]
            ngh = cfd.bnd_edge[nbnd_img].ncell[0]
            
            if ngh < own:
                src_edge.normal = -src_edge.normal
                src_edge.ncell  = [ngh, own]
            else:
                src_edge.ncell = [own, ngh]
            
            # Add the periodic edge
            cfd.per_edge.append(src_edge)
            
        else:
            raise ValueError(f"Neighbor not found {nbnd} -> {nbnd_img}, distance {dist}")
    
    # Remove all boundary edges that were converted to periodic connections
    cfd.bnd_edge = [cfd.bnd_edge[i] for i in range(len(cfd.bnd_edge)) if mask[i]]
    cfd.periodic_BCs_along_x = True
    return cfd