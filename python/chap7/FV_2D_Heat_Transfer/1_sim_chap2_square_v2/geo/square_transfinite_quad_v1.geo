lc  = 0.02;
lc2 = 0.1;
a=1;

N = 40;              // Nombre de divisions sur chaque côté
r = 0.95;            // Ratio de progression (valeur < 1 affine la maille vers le début)

Point(1) = { -a  , -a , 0, lc};
Point(2) = {  0  , -a , 0, lc};
Point(3) = { +a  , -a , 0, lc};
Point(4) = { +a  ,  0 , 0, lc};
Point(5) = { +a  , +a , 0, lc};
Point(6) = {  0  , +a , 0, lc};
Point(7) = { -a  , +a , 0, lc};
Point(8) = { -a  ,  0 , 0, lc};
Point(9) = {  0  ,  0 , 0, lc};

Line(11) = {1, 2};
Line(12) = {2, 3};

Line(13) = {3, 4};
Line(14) = {4, 5};

Line(15) = {5, 6};
Line(16) = {6, 7};

Line(17) = {7, 8};
Line(18) = {8, 1};

Line(19) = {8, 9};
Line(20) = {9, 6};
Line(21) = {9, 4};
Line(22) = {9, 2};

Curve Loop(1) = {20, 16, 17, 19};
Plane Surface(1) = {1};

Curve Loop(2) = {15, -20, 21, 14};
Plane Surface(2) = {2};

Curve Loop(3) = {19, 22, -11, -18};
Plane Surface(3) = {3};

Curve Loop(4) = {22, 12, 13, -21};
Plane Surface(4) = {4};

Physical Curve("left", 23) = {17, 18};
Physical Curve("down", 24) = {11, 12};
Physical Curve("right", 28) = {14, 13};
Physical Curve("top", 29) = {16, 15};
Physical Surface("square", 27) = {1, 2, 3, 4};

// Transfinite Lines
Transfinite Line{11} = N Using Progression 1/r;      
Transfinite Line{12} = N Using Progression r;    
Transfinite Line{13} = N Using Progression 1/r;    
Transfinite Line{14} = N Using Progression r;      
Transfinite Line{15} = N Using Progression 1/r;    
Transfinite Line{16} = N Using Progression r;      
Transfinite Line{17} = N Using Progression 1/r;    
Transfinite Line{18} = N Using Progression r;

Transfinite Line{19} = N Using Progression 1/r;    
Transfinite Line{20} = N Using Progression r;      
Transfinite Line{21} = N Using Progression r;    
Transfinite Line{22} = N Using Progression r;  

// Transfinite Surface + recombine en quadrangles
Transfinite Surface{1};
Transfinite Surface{2};
Transfinite Surface{3};
Transfinite Surface{4};

Recombine Surface{1}; // Pour générer des quadrangles
Recombine Surface{2}; // Pour générer des quadrangles
Recombine Surface{3}; // Pour générer des quadrangles
Recombine Surface{4}; // Pour générer des quadrangles//+

// Génération automatique du maillage
Mesh 2;

// Configuration du format de sortie
Mesh.Format = 1;          // Format ASCII
Mesh.MshFileVersion = 2.2; // Version 2.2 (compatible avec 2.0)

// Sauvegarde automatique du maillage
Save "../msh/square_quad.msh";