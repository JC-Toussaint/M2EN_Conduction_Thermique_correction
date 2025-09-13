// Script GEO pour GMSH - Disque de rayon R=1 centré en O
// Région surfacique : core
// Région linéique : boundary

// Paramètres
R  = 1.0;  // Rayon du disque
lc = 2.0;  // longueur caractéristique

// Points géométriques
Point(1) = {0, 0, 0, lc};    // Centre O
Point(2) = {R, 0, 0, lc};    // Point sur le cercle (x=R)
Point(3) = {0, R, 0, lc};    // Point sur le cercle (y=R)
Point(4) = {-R, 0, 0, lc};   // Point sur le cercle (x=-R)
Point(5) = {0, -R, 0, lc};   // Point sur le cercle (y=-R)

// Arcs de cercle pour former le contour
Circle(1) = {2, 1, 3};  // Arc de 2 à 3 centré en 1
Circle(2) = {3, 1, 4};  // Arc de 3 à 4 centré en 1
Circle(3) = {4, 1, 5};  // Arc de 4 à 5 centré en 1
Circle(4) = {5, 1, 2};  // Arc de 5 à 2 centré en 1

// Boucle de contour fermée
Curve Loop(1) = {1, 2, 3, 4};

// Surface du disque
Plane Surface(1) = {1};

// Définition des régions physiques

// Région linéique : boundary (le cercle extérieur)
Physical Curve("boundary") = {1, 2, 3, 4};

// Région surfacique : core (la surface du disque)
Physical Surface("core") = {1};
