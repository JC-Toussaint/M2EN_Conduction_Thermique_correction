lc =0.1;
a=1;

Point(1) = {  0,  0, 0, lc};
Point(2) = { -a, -a, 0, lc};
Point(3) = { +a, -a, 0, lc};
Point(4) = { +a, +a, 0, lc};
Point(5) = { -a, +a, 0, lc};

Line(11) = {2, 3};
Line(12) = {3, 4};
Line(13) = {4, 5};
Line(14) = {5, 2};
Line Loop(15) = {13, 14, 11, 12};
Plane Surface(16) = {15};

//+
Physical Surface("square", 17) = {16};
//+
Physical Curve("top", 18) = {13};
//+
Physical Curve("down", 19) = {11};
//+
Physical Curve("left", 20) = {14};
//+
Physical Curve("right", 21) = {12};
