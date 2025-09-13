cl1 = 0.005;

L =   1;
e =   0.04;
h =   0.2;


Point(1) = {0, -h, 0, cl1};
Point(2) = {0, +h, 0, cl1};
Point(3) = {0, -h-e, 0, cl1};
Point(4) = {0, +h+e, 0, cl1};
Point(5) = {e, -h, 0, cl1};
Point(6) = {e, +h, 0, cl1};
Point(7) = {L, -h, 0, cl1};
Point(8) = {L, +h, 0, cl1};
Point(9) = {L, -h-e, 0, cl1};
Point(10)= {L, +h+e, 0, cl1};
Point(11) ={e, -h-e, 0, cl1};
Point(12)= {e, +h+e, 0, cl1};

//+
Line(1) = {3, 11};
//+
Line(2) = {11, 9};
//+
Line(3) = {9, 7};
//+
Line(4) = {7, 8};
//+
Line(5) = {8, 10};
//+
Line(6) = {10, 12};
//+
Line(7) = {12, 4};
//+
Line(8) = {4, 2};
//+
Line(9) = {2, 1};
//+
Line(10) = {1, 3};
//+
Line(11) = {6, 6};
//+
Line(12) = {6, 8};
//+
Line(13) = {2, 6};
//+
Line(14) = {6, 12};
//+
Line(15) = {6, 5};
//+
Line(16) = {5, 1};
//+
Line(17) = {5, 11};
//+
Line(18) = {5, 7};
//+
Curve Loop(1) = {12, -4, -18, -15};
//+
Plane Surface(1) = {1};
//+
Curve Loop(2) = {6, -14, 12, 5};
//+
Plane Surface(2) = {2};
//+
Curve Loop(3) = {7, 8, 13, 14};
//+
Plane Surface(3) = {3};
//+
Curve Loop(4) = {9, -16, -15, -13};
//+
Plane Surface(4) = {4};
//+
Curve Loop(5) = {10, 1, -17, 16};
//+
Plane Surface(5) = {5};
//+
Curve Loop(6) = {18, -3, -2, -17};
//+
Plane Surface(6) = {6};
//+
Physical Surface("isolator", 19) = {1};
//+
Physical Surface("metal", 20) = {2, 3, 4, 5, 6};
//+
Physical Curve("left", 21) = {8, 9, 10};
//+
Physical Curve("right", 22) = {5, 4, 3};
//+
Physical Curve("top", 23) = {7, 6};
//+
Physical Curve("down", 24) = {1, 2};
