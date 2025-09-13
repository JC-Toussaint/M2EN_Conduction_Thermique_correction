cl1 = 0.05;  // Taille de maille pour le demi-disque intérieur
cl2 = 0.1;   // Taille de maille pour la demi-couronne

R1 = 1;      // Rayon du demi-disque intérieur
R2 = 2;      // Rayon extérieur de la demi-couronne

// Centre commun
Point(1) = {0, 0, 0, cl1};

// Points sur le demi-cercle intérieur (rayon R1, x≥0)
Point(2) = {+R1, 0, 0, cl1};    // Point à droite
Point(3) = {0, +R1, 0, cl1};    // Point en haut
Point(4) = {0, -R1, 0, cl1};    // Point en bas

// Points sur le demi-cercle extérieur (rayon R2, x≥0)
Point(5) = {+R2, 0, 0, cl2};    // Point à droite
Point(6) = {0, +R2, 0, cl2};    // Point en haut
Point(7) = {0, -R2, 0, cl2};    // Point en bas

// Demi-cercle intérieur (rayon R1, de y=-R1 à y=+R1 via x≥0)
Circle(1) = {4, 1, 2};  // Arc de bas à droite
Circle(2) = {2, 1, 3};  // Arc de droite à haut

// Segments sur l'axe y pour fermer le demi-disque
Line(3) = {3, 1};       // De haut au centre
Line(4) = {1, 4};       // Du centre au bas

// Demi-cercle extérieur (rayon R2, de y=-R2 à y=+R2 via x≥0)
Circle(5) = {7, 1, 5};  // Arc de bas à droite
Circle(6) = {5, 1, 6};  // Arc de droite à haut

// Segments sur l'axe y pour la frontière extérieure
Line(7) = {6, 3};       // De R2 à R1 en haut
Line(8) = {4, 7};       // De R1 à R2 en bas

// Boucle pour le demi-disque intérieur (source)
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// Boucle pour la demi-couronne annulaire (isolator)
// Contour extérieur
Curve Loop(2) = {5, 6, 7, -2, -1, 8};
Plane Surface(2) = {2};

// Définition des régions physiques
Physical Surface("source", 10) = {1};        // Demi-disque intérieur
Physical Surface("isolator", 11) = {2};      // Demi-couronne annulaire
Physical Curve("border", 12) = {5, 6};       // Demi-cercle extérieur
Physical Curve("symmetry", 13) = {7, 3, 4, 8}; // Axe de symétrie y (x=0)