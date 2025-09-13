cl1 = 0.05;

a = 1;
b = 2;

Point(1) = {-b, -a, 0, cl1};
Point(2) = {-a, -a, 0, cl1};
Point(3) = {+a, -a, 0, cl1};
Point(4) = {+b, -a, 0, cl1};
Point(5) = {-a,  0, 0, cl1};
Point(6) = {+a,  0, 0, cl1};
Point(7) = {-b, +a, 0, cl1};
Point(8) = {-a, +a, 0, cl1};
Point(9) = {+a, +a, 0, cl1};
Point(10)= {+b, +a, 0, cl1};
Point(11) = {-b,  0, 0, cl1};
Point(12) = {+b,  0, 0, cl1};//+
Line(1) = {1, 2};
//+
Line(2) = {2, 3};
//+
Line(3) = {3, 4};
//+
Line(4) = {4, 12};
//+
Line(5) = {12, 10};
//+
Line(6) = {10, 9};
//+
Line(7) = {9, 8};
//+
Line(8) = {8, 7};
//+
Line(9) = {7, 11};
//+
Line(10) = {11, 1};
//+
Line(11) = {11, 5};
//+
Line(12) = {5, 6};
//+
Line(13) = {6, 12};
//+
Line(14) = {8, 5};
//+
Line(15) = {9, 6};
//+
Line(16) = {5, 2};
//+
Line(17) = {6, 3};
//+
Curve Loop(1) = {8, 9, 11, -14};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {10, 1, -16, -11};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {7, 14, 12, -15};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {16, 2, -17, -12};
//+
Plane Surface(4) = {4};
//+
Curve Loop(5) = {13, 5, 6, 15};
//+
Plane Surface(5) = {5};
//+
Curve Loop(6) = {17, 3, 4, -13};
//+
Plane Surface(6) = {6};
//+
Physical Surface("material1", 18) = {2, 1, 3, 5, 6};
//+
Physical Surface("material2", 19) = {4};
//+
Physical Curve("left", 20) = {9, 10};
//+
Physical Curve("right", 21) = {5, 4};
//+
Physical Curve("top", 22) = {8, 7, 6};
//+
Physical Curve("down", 23) = {1, 2, 3};
