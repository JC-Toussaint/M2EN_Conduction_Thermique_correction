cl1 = 0.05;  // Taille de maille pour le disque intérieur
cl2 = 0.1;   // Taille de maille pour la couronne

R1 = 1;      // Rayon du disque intérieur
R2 = 2;      // Rayon extérieur de la couronne

// Centre commun
Point(1) = {0, 0, 0, cl1};

// Points sur le cercle intérieur (rayon R1)
Point(2) = {+R1, 0, 0, cl1};
Point(3) = {0, +R1, 0, cl1};
Point(4) = {-R1, 0, 0, cl1};
Point(5) = {0, -R1, 0, cl1};

// Points sur le cercle extérieur (rayon R2)
Point(6) = {+R2, 0, 0, cl2};
Point(7) = {0, +R2, 0, cl2};
Point(8) = {-R2, 0, 0, cl2};
Point(9) = {0, -R2, 0, cl2};

// Cercle intérieur (rayon R1)
Circle(1) = {2, 1, 3};
Circle(2) = {3, 1, 4};
Circle(3) = {4, 1, 5};
Circle(4) = {5, 1, 2};

// Cercle extérieur (rayon R2)
Circle(5) = {6, 1, 7};
Circle(6) = {7, 1, 8};
Circle(7) = {8, 1, 9};
Circle(8) = {9, 1, 6};

// Boucle pour le disque intérieur (source)
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};

// Boucle pour la couronne annulaire (isolator)
// Contour extérieur moins contour intérieur
Curve Loop(2) = {5, 6, 7, 8};
Curve Loop(3) = {1, 2, 3, 4};
Plane Surface(2) = {2, 3};  // Surface avec trou

// Définition des régions physiques
Physical Surface("source", 10) = {1};     // Disque intérieur
Physical Surface("isolator", 11) = {2};   // Couronne annulaire
Physical Curve("border", 12) = {5, 6, 7, 8};  // Cercle extérieur