cl1 = 0.05;
cl2 = 0.05;
cl3 = 0.05;

L = 1;
R=0.5;

Point(1) = {0, 0, 0, cl1};
Point(2) = {+R, 0, 0, cl1};
Point(3) = {-R, 0, 0, cl1};
Point(4) = {0, +R, 0, cl1};
Point(5) = {0, -R, 0, cl1};
Point(6) = {-L, -L, 0, cl3};
Point(7) = {+L, -L, 0, cl3};
Point(8) = {+L, +L, 0, cl3};
Point(9) = {-L, +L, 0, cl3};

Point(10) = {+L, +0, 0, cl2};
Point(11) = {-L, +0, 0, cl2};
Point(12) = {+0, +L, 0, cl2};
Point(13) = {+0, -L, 0, cl2};


//+
Circle(1) = {2, 1, 4};
//+
Circle(2) = {4, 1, 3};
//+
Circle(3) = {3, 1, 5};
//+
Circle(4) = {5, 1, 2};
//+
Line(5) = {13, 7};
//+
Line(6) = {7, 10};
//+
Line(7) = {10, 8};
//+
Line(8) = {8, 12};
//+
Line(9) = {12, 9};
//+
Line(10) = {9, 11};
//+
Line(11) = {11, 6};
//+
Line(12) = {6, 13};
//+
Line(13) = {2, 10};
//+
Line(14) = {4, 12};
//+
Line(15) = {3, 11};
//+
Line(16) = {5, 13};
//+
Curve Loop(1) = {13, 7, 8, -14, -1};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {9, 10, -15, -2, 14};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {11, 12, -16, -3, 15};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {5, 6, -13, -4, 16};
//+
Plane Surface(4) = {4};
//+

//+
Curve Loop(5) = {2, 3, 4, 1};
//+
Plane Surface(5) = {5};
//+
Physical Surface("source", 17) = {5};
Physical Surface("isolant", 22) = {2, 1, 4, 3};
//+
Physical Curve("left", 18) = {10, 11};
Physical Curve("down", 19) = {12, 5};
Physical Curve("right", 20) = {7, 6};
Physical Curve("top", 21) = {9, 8};

