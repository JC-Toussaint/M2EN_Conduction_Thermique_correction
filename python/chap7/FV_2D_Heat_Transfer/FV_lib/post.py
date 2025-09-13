import numpy as np
import scipy.sparse.linalg

from collections import defaultdict
import sys
import os
import copy

from FV_lib.struct import Struct

# Définit le répertoire courant comme celui où le script est exécuté
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from scipy.spatial import KDTree
from scipy.signal import savgol_filter

# ==================== FONCTIONS UTILITAIRES COMMUNES ====================

def _build_triangles_and_interpolate_values(cfd, return_nodal_values=True):
    """
    Fonction utilitaire commune pour construire les triangles et interpoler les valeurs aux nœuds.
    
    Returns:
        triangles: liste des triangles pour la triangulation
        nodal_T: valeurs interpolées aux nœuds (si return_nodal_values=True)
        xarr, yarr: coordonnées des nœuds
        bounds: (xymin, xymax) limites du domaine
    """
    triangles = []
    
    # Extraction des coordonnées des nœuds
    xarr = cfd.node[:, 0]
    yarr = cfd.node[:, 1]
    
    # Calcul des limites
    xy_combined = np.concatenate([xarr, yarr])
    xymin = np.min(xy_combined)
    xymax = np.max(xy_combined)
    
    if return_nodal_values:
        # Initialisation pour l'interpolation aux nœuds
        nodal_T = np.zeros_like(xarr)
        node_weight_sum = np.zeros_like(xarr)
    
    # Boucle sur les cellules
    for nvc in range(len(cfd.cell)):
        cell = cfd.cell[nvc]
        ind = cell.ind
        NBN = len(ind)
        
        # Traitement selon le type de cellule
        if NBN == 3:
            # Triangle
            triangles.append(ind)
        elif NBN == 4:
            # Quadrilatère - diviser en deux triangles
            triangles.append([ind[0], ind[1], ind[2]])
            triangles.append([ind[0], ind[2], ind[3]])
        else:
            raise ValueError('Neither a triangle nor a quadrangle')
        
        if return_nodal_values:
            # Interpolation aux nœuds
            C = cell.C
            value = cfd.T[nvc]
            
            # Calcul des poids pour chaque nœud de la cellule
            for node_idx in ind:
                d = np.linalg.norm(cfd.node[node_idx, :] - C)
                if d > 0:  # Éviter la division par zéro
                    nodal_T[node_idx] += value / d
                    node_weight_sum[node_idx] += 1 / d
    
    if return_nodal_values:
        # Moyenne pondérée des valeurs par sommet
        valid_weights = node_weight_sum > 0
        nodal_T[valid_weights] = nodal_T[valid_weights] / node_weight_sum[valid_weights]
        return triangles, nodal_T, xarr, yarr, (xymin, xymax)
    else:
        return triangles, None, xarr, yarr, (xymin, xymax)

def _build_3d_polygons(cfd, z_values, color_values, cmap):
    """
    Fonction utilitaire pour construire les polygones 3D avec couleurs.
    
    Parameters:
        cfd: structure CFD
        z_values: valeurs Z pour chaque cellule (fonction ou array)
        color_values: valeurs pour les couleurs (fonction ou array)  
        cmap: colormap matplotlib
        
    Returns:
        polygons: liste des polygones 3D
        colors: liste des couleurs correspondantes
        bounds: dictionnaire avec les limites x, y, z
    """
    polygons = []
    colors = []
    all_x = []
    all_y = []
    all_z = []
    
    # Normaliser les valeurs de couleur
    if hasattr(color_values, '__call__'):
        # Si c'est une fonction, l'appliquer
        color_vals = [color_values(i) for i in range(len(cfd.cell))]
    else:
        # Si c'est un array
        color_vals = color_values
        
    min_color = np.min(color_vals)
    max_color = np.max(color_vals)
    color_range = max_color - min_color if max_color != min_color else 1
    
    for nvc in range(len(cfd.cell)):
        cell = cfd.cell[nvc]
        ind = cell.ind
        NBN = len(ind)
        
        # Calculer la valeur Z
        if hasattr(z_values, '__call__'):
            z_val = z_values(nvc)
        else:
            z_val = z_values[nvc]
            
        # Calculer la couleur
        if hasattr(color_values, '__call__'):
            color_val = color_values(nvc)
        else:
            color_val = color_values[nvc]
            
        normalized_color = (color_val - min_color) / color_range
        color = cmap(normalized_color)
        
        # Construire les coordonnées des nœuds
        x = [cfd.node[ind[j], 0] for j in range(NBN)]
        y = [cfd.node[ind[j], 1] for j in range(NBN)]
        z = [z_val] * NBN
        
        # Traiter selon le nombre de nœuds
        if NBN == 3:
            # Triangle
            vertices = [(x[i], y[i], z[i]) for i in range(3)]
            polygons.append(vertices)
            colors.append(color)
            all_x.extend(x)
            all_y.extend(y)
            all_z.extend(z)
            
        elif NBN == 4:
            # Quadrilatère - diviser en deux triangles
            vertices1 = [(x[i], y[i], z[i]) for i in [0, 1, 2]]
            vertices2 = [(x[i], y[i], z[i]) for i in [0, 2, 3]]
            polygons.extend([vertices1, vertices2])
            colors.extend([color, color])
            all_x.extend(x + x)  # Deux fois pour les deux triangles
            all_y.extend(y + y)
            all_z.extend(z + z)
        else:
            raise ValueError('Neither a triangle nor a quadrangle')
    
    bounds = {
        'x': (min(all_x), max(all_x)),
        'y': (min(all_y), max(all_y)), 
        'z': (min(all_z), max(all_z))
    }
    
    return polygons, colors, bounds

# ==================== FONCTIONS PRINCIPALES ====================

def plot_smoothed_sol(cfd):
    """
    PLOT_SMOOTHED_SOL - Visualise une solution CFD lissée sur un graphique 2D
    
    Parameters:
        cfd : Struct - Structure contenant les données du maillage et la solution T
    """
    # Utiliser la fonction utilitaire commune
    triangles, nodal_T, xarr, yarr, (xymin, xymax) = _build_triangles_and_interpolate_values(cfd, True)
    
    # Conversion en array numpy pour la triangulation
    triangles = np.array(triangles)
    
    # Création de la figure
    fig, ax = plt.subplots()
        
    # Création de la triangulation
    tri = Triangulation(xarr, yarr, triangles)
    
    # Tracé de la surface avec interpolation lisse
    contourf = ax.tricontourf(tri, nodal_T, levels=50, cmap='jet', alpha=0.75)
    
    # Ajout de la barre de couleur
    cbar = plt.colorbar(contourf, ax=ax)
    cbar.set_label('Temperature')
    
    # Ajout des isovaleurs (contours)
    contour_lines = ax.tricontour(tri, nodal_T, levels=21, colors='black', linewidths=2)
    
    # Configuration des axes
    ax.set_xlim([xymin, xymax])
    ax.set_ylim([xymin, xymax])
    ax.set_aspect('equal')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Smoothed CFD Solution')
    
    # Affichage
    plt.tight_layout()
    plt.draw()
    plt.show(block=False)

def plot_raw_sol(cfd):
    """
    PLOT_RAW_SOL - Visualize raw CFD solution on a 3D plot
    
    Parameters:
        cfd : Struct - Structure containing CFD data
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    cmap = plt.cm.jet
    
    # Fonctions pour extraire les valeurs Z et couleur
    z_func = lambda nvc: cfd.T[nvc]
    color_func = lambda nvc: cfd.T[nvc]
    
    polygons, colors, bounds = _build_3d_polygons(cfd, z_func, color_func, cmap)
    
    # Créer la collection de polygones 3D
    poly3d = Poly3DCollection(polygons, facecolors=colors, edgecolors='none')
    ax.add_collection3d(poly3d)
    
    # Définir les limites des axes
    ax.set_xlim(bounds['x'])
    ax.set_ylim(bounds['y'])
    ax.set_zlim(bounds['z'])
    
    # Ajuster le ratio d'aspect
    x_range = bounds['x'][1] - bounds['x'][0]
    y_range = bounds['y'][1] - bounds['y'][0]
    ax.set_box_aspect([1, y_range/x_range, 0.5])
    
    # Configurer la vue et les labels
    ax.set_title('T')
    ax.grid(True)
    
    # Ajouter la colorbar
    mappable = plt.cm.ScalarMappable(cmap=cmap)
    mappable.set_array([bounds['z'][0], bounds['z'][1]])
    mappable.set_clim(*bounds['z'])
    plt.colorbar(mappable, ax=ax, shrink=0.5, aspect=5)
    
    plt.draw()
    plt.show(block=False)

def interpolate_at_nodes(cfd):
    """
    Interpolate cell-centered values to nodes
    
    Returns:
        nodal_T: valeurs interpolées aux nœuds
    """
    # Utiliser la fonction utilitaire commune (seulement pour l'interpolation)
    _, nodal_T, _, _, _ = _build_triangles_and_interpolate_values(cfd, True)
    return nodal_T

def cutline(cfd, Npts, xi, yi, xf, yf):
    """
    CUTLINE - Extraction and filtering of values along a cut line
    
    Parameters:
        cfd   - Structure containing CFD data with values at nodes
        Npts  - Number of sampled points along the line
        xi, yi - Coordinates of the starting point of the line
        xf, yf - Coordinates of the ending point of the line
    
    Returns:
        values           - Interpolated values extracted at the sampled points
        filtered_values  - Smoothed values using a Savitzky-Golay filter
    """
    assert Npts > 1, "Npts must be greater than 1"
    
    # Interpolation of cell-centered values at nodes
    nodal_T = interpolate_at_nodes(cfd)
    
    # Build k-d tree for nearest neighbor search
    tree = KDTree(cfd.node[:, :2])
    
    # Calculate line parameters
    dx = (xf - xi) / (Npts - 1)
    dy = (yf - yi) / (Npts - 1)
    ds = np.sqrt(dx*dx + dy*dy)
    
    # Curvilinear abscissa
    s = np.arange(Npts) * ds
    
    nb_points = 1
    values = []
    
    # Extract values along the line
    for n in range(Npts):
        xp = xi + dx * n
        yp = yi + dy * n
        
        point = np.array([xp, yp])
        
        # Find nearest neighbor(s)
        distances, indices = tree.query(point, k=nb_points)
        
        # Handle single point case
        if nb_points == 1:
            indices = [indices] if not isinstance(indices, (list, np.ndarray)) else indices
        
        # Average the values at nearest points
        values.append(np.mean(nodal_T[indices]))
    
    values = np.array(values)
    
    # Apply Savitzky-Golay filter
    window_length = min(11, len(values) if len(values) % 2 == 1 else len(values) - 1)
    if window_length < 3:
        window_length = 3
    
    polyorder = min(2, window_length - 1)
    filtered_values = savgol_filter(values, window_length, polyorder)
    
    # Plot results
    plt.figure()
    plt.plot(s, values, 'r.', label='raw data')
    plt.plot(s, filtered_values, 'b-', label='Savitzky-Golay filter')
    plt.grid(True)
    plt.xlabel('Curvilinear distance')
    plt.ylabel('Values')
    plt.legend()
    plt.title('Cutline Analysis')
    plt.draw()
    plt.show(block=True)
    
    return values, filtered_values

def plot_regions(cfd):
    """
    PLOT_REGIONS - Visualize region numbers on a 3D plot
    
    Parameters:
        cfd : Struct - Structure containing mesh data and region information
        
    Returns:
        unique_regions: liste des régions uniques
        region_counts: dictionnaire avec le nombre de cellules par région
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    # Extraire tous les numéros de régions uniques
    region_numbers = [cell.nrg for cell in cfd.cell]
    unique_regions = sorted(list(set(region_numbers)))
    num_regions = len(unique_regions)
    
    print(f"Nombre de régions trouvées: {num_regions}")
    print(f"Numéros de régions: {unique_regions}")
    
    cmap = plt.cm.jet
    
    # Créer un mapping région -> index normalisé pour les couleurs
    region_to_normalized = {}
    for i, region_num in enumerate(unique_regions):
        region_to_normalized[region_num] = i / max(1, num_regions - 1)
    
    # Fonctions pour extraire les valeurs Z et couleur
    z_func = lambda nvc: cfd.cell[nvc].nrg  # Numéro de région comme hauteur
    color_func = lambda nvc: region_to_normalized[cfd.cell[nvc].nrg]
    
    polygons, colors, bounds = _build_3d_polygons(cfd, z_func, color_func, cmap)
    
    # Créer la collection de polygones 3D
    poly3d = Poly3DCollection(polygons, facecolors=colors, edgecolors='none', 
                             linewidths=0, alpha=1.0)
    ax.add_collection3d(poly3d)
    
    # Définir les limites des axes
    ax.set_xlim(bounds['x'])
    ax.set_ylim(bounds['y'])
    ax.set_zlim(bounds['z'])
    
    # Ajuster le ratio d'aspect
    x_range = bounds['x'][1] - bounds['x'][0]
    y_range = bounds['y'][1] - bounds['y'][0]
    ax.set_box_aspect([1, y_range/x_range, 0.3])
    
    # Configurer la vue et les labels
    ax.set_title('Region Map')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Region')
    ax.grid(True)
    
    # Configurer l'axe Z pour afficher uniquement des entiers
    z_ticks = sorted(list(set([int(z) for z in [bounds['z'][0], bounds['z'][1]]] + unique_regions)))
    ax.set_zticks(z_ticks)
    ax.set_zticklabels([str(int(z)) for z in z_ticks])
    
    # Afficher des informations sur les régions
    print("\nInformations sur les régions:")
    region_counts = {region: region_numbers.count(region) for region in unique_regions}
    for region_num in unique_regions:
        count = region_counts[region_num]
        print(f"  Région {region_num}: {count} cellules")
    
    plt.tight_layout()
    plt.draw()
    plt.show(block=False)
    
    return unique_regions, region_counts

def plot_cells(cfd, ax=None, show_normals=False, show_centroids=False, alpha=0.1):
    """
    Plots the finite volume mesh, including nodes, segments, and boundaries.
    
    Description:
        This function visualizes the finite volume mesh, showing nodes, segments, and boundaries.
        - Nodes are plotted as points.
        - Segments are plotted as red lines connecting pairs of nodes.
        - Boundaries are plotted as blue lines.
        - Optionally shows normals and cell centroids.
    
    Steps:
        1. Plot the nodes as points (using scatter with dots).
        2. Loop through each segment, extracting node indices and plotting each segment as a red line.
        3. Loop through each boundary, extracting node indices and plotting each boundary as a blue line.
        4. Optionally plot normals and centroids.
        5. The aspect ratio is set to be equal to ensure proper scaling and representation.
    
    Parameters:
    -----------
    cfd : Struct 
        Structure containing mesh data, including node positions, segments, and boundary information.
        Expected attributes/keys:
        - node: array of node coordinates
        - edge: list of edge objects with 'ind' attribute
        - bnd_edge: list of boundary edge objects with 'ind' attribute
        - cell: (optional) list of cell objects with centroids for labeling
        
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None, creates new figure and axes.
        
    show_normals : bool, optional
        Whether to show normal vectors on edges and boundaries. Default False.
        
    show_centroids : bool, optional
        Whether to show cell centroids with labels. Default False.
        
    alpha : float, optional
        Scaling factor for normal vectors. Default 0.1.
    
    Returns:
    --------
    ax : matplotlib.axes.Axes
        The axes object containing the plot.
    
    Notes:
    ------
    - The function assumes the mesh data is stored in the cfd structure.
    - Uses matplotlib for plotting instead of MATLAB's plot functions.
    - The aspect ratio is set to be equal, ensuring accurate geometry representation.
    
    Author: JC Toussaint Grenoble-INP (translated to Python)
    """
    
    # Create figure and axes if not provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # Access attributes whether cfd is a Struct object
    nodes = cfd.node
    edges = cfd.edge
    bnd_edges = cfd.bnd_edge
    cells = getattr(cfd, 'cell', None)
    
    # Plot nodes as points
    ax.scatter(nodes[:, 0], nodes[:, 1], c='black', s=20, marker='.', 
               label='Nodes', zorder=3)
    
    # Plot internal edges (segments) as red lines
    for nseg, edge in enumerate(edges):
        ind = edge.ind
        
        # Get coordinates of the two nodes
        XY = np.array([nodes[ind[0]], nodes[ind[1]]])
        ax.plot(XY[:, 0], XY[:, 1], 'r-', linewidth=1, alpha=0.8)
    
    # Plot boundary edges as blue lines
    for nbnd, bnd_edge in enumerate(bnd_edges):
        ind = bnd_edge.ind
        
        # Get coordinates of the two nodes
        XY = np.array([nodes[ind[0]], nodes[ind[1]]])
        ax.plot(XY[:, 0], XY[:, 1], 'b-', linewidth=2, 
                label='Boundary' if nbnd == 0 else "", zorder=2)
    
    # Optionally plot normals
    if show_normals:
        # Plot normals for internal edges
        for edge in edges:
            center = edge.f 
            normal = edge.normal 
                
            # Scale the normal vector
            scaled_normal = alpha * normal
                
            ax.arrow(center[0], center[1], 
                        scaled_normal[0], scaled_normal[1],
                        head_width=0.02, head_length=0.02, 
                        fc='black', ec='black', alpha=0.7)
        
        # Plot normals for boundary edges
        for bnd_edge in bnd_edges:
            center = bnd_edge.f 
            normal = bnd_edge.normal 
                
            # Scale the normal vector
            scaled_normal = alpha * normal
                
            ax.arrow(center[0], center[1], 
                        scaled_normal[0], scaled_normal[1],
                        head_width=0.02, head_length=0.02, 
                        fc='blue', ec='blue', alpha=0.7)
    
    # Optionally plot cell centroids with labels
    if show_centroids and cells is not None:
        for ncell, cell in enumerate(cells):
            centroid = cell.C
            
            # Plot centroid
            ax.scatter(centroid[0], centroid[1], c='green', s=50, 
                      marker='o', alpha=0.7, zorder=4)
            
            # Add cell index label
            ax.annotate(str(ncell), (centroid[0], centroid[1]), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, color='green', weight='bold')
    
    # Set equal aspect ratio and labels
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Finite Volume Mesh')
    
    # Add legend if there are boundary edges
    if len(bnd_edges) > 0:
        handles, labels = ax.get_legend_handles_labels()
        if labels:
            ax.legend()
    
    plt.draw()
    plt.show(block=False)
    
    return ax


def plot_mesh_extended(cfd, alpha=0.1):
    """
    Extended plotting function that shows mesh with normals and cell centroids.
    
    This is equivalent to the extended functionality described in the MATLAB comments.
    
    Parameters:
    -----------
    cfd : Struct 
        Structure containing complete mesh data
    alpha : float
        Scaling factor for normal vectors
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    fig, ax = plt.subplots()
    
    # Plot with all features enabled
    plot_cells(cfd, ax=ax, show_normals=True, show_centroids=True, alpha=alpha)
    
    ax.set_title('Extended Finite Volume Mesh\n(with normals and centroids)')
    
    return fig, ax
