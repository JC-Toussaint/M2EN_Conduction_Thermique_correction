cl1 = 0.05;  // Taille de maille pour le demi-disque intérieur
cl2 = 0.1;   // Taille de maille pour la région extérieure

R1 = 1;      // Rayon du demi-disque intérieur
R2 = 2;      // Largeur du demi-carré et demi-hauteur
H  = 4;      // demi-hauteur

// Centre commun
Point(1) = {0, 0, 0, cl1};

// Points sur le demi-cercle intérieur (rayon R1, x≥0)
Point(2) = {+R1, 0, 0, cl1};    // Point à droite
Point(3) = {0, +R1, 0, cl1};    // Point en haut
Point(4) = {0, -R1, 0, cl1};    // Point en bas

// Points du demi-carré extérieur
Point(5) = {0, +H, 0, cl2};    // Coin haut gauche
Point(6) = {+R2, +H, 0, cl2};   // Coin haut droit
Point(7) = {+R2, -H, 0, cl2};   // Coin bas droit
Point(8) = {0, -H, 0, cl2};    // Coin bas gauche

// Demi-cercle intérieur (rayon R1, de y=-R1 à y=+R1 via x≥0)
Circle(1) = {4, 1, 2};  // Arc de bas à droite
Circle(2) = {2, 1, 3};  // Arc de droite à haut

Line(3) = {4, 8};
Line(4) = {8, 7};
Line(5) = {7, 6};
Line(6) = {6, 5};
Line(7) = {5, 3};
Line(8) = {3, 1};
Line(9) = {1, 4};

Curve Loop(1) = {8, 9, 1, 2};
Plane Surface(1) = {1};

Curve Loop(2) = {6, 7, -2, -1, 3, 4, 5};
Plane Surface(2) = {2};

Physical Surface("source", 10) = {1};
Physical Surface("isolator", 11) = {2};
Physical Curve("top", 12) = {6};
Physical Curve("right", 13) = {5};
Physical Curve("down", 14) = {4};
