lc  = 0.02;
a=1;
b=2;
h=0.1;

Point(1) = {  -a  , -h, 0, lc};
Point(2) = {   0  , -h , 0, lc};
Point(3) = {  +b  , -h, 0, lc};
Point(4) = {  +b  , h , 0, lc};
Point(5) = {  +0  , h , 0, lc};
Point(6) = {  -a  , h , 0, lc};

//+
Line(1) = {1, 2};
//+
Line(2) = {2, 3};
//+
Line(3) = {3, 4};
//+
Line(4) = {4, 5};
//+
Line(5) = {5, 6};
//+
Line(6) = {6, 1};
//+
Line(7) = {2, 5};

Curve Loop(1) = {5, 6, 1, 7};
Plane Surface(1) = {1};
Curve Loop(2) = {4, -7, 2, 3};
Plane Surface(2) = {2};

Physical Surface("square", 8) = {1};
Physical Surface("rectangle", 9) = {2};
Physical Curve("left",  10) = {6};
Physical Curve("right", 11) = {3};