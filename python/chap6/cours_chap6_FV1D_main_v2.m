clc
clear all
close all

L=1;
N=100;
K1 = 200;
K2 = 400;
H = 10;

Tdg = 0;
Tad = 100;

w = L/N*ones(1, N);

% centres des cellules
x = zeros(1, N);
width = w(1);
x(1)=w(1)/2;
for i=2:N
    x(i) = x(i-1)+w(i);
end
K = K1*(x < L/2) + K2*(x >= L/2);
assert(length(K) == N);

A = sparse(N, N);
b = zeros(N, 1);
for i=2:N-1
    % contribution de l'interface (i-1 | i)
    hm = w(i-1)/2; Km = K(i-1);
    hp = w(i  )/2; Kp = K(i);  
    Keff = (hm+hp)/(hm/Km + hp/Kp);
    A(i, i-1) = -Keff/(x(i)-x(i-1));
    A(i, i  ) = +Keff/(x(i)-x(i-1));
    
    % contribution de l'interface (i | i+1)
    hm = w(i  )/2;  Km = K(i  );
    hp = w(i+1)/2;  Kp = K(i+1);    
    Keff = (hm+hp)/(hm/Km + hp/Kp);
    A(i, i+1) =          -Keff/(x(i+1)-x(i));
    A(i, i  ) = A(i, i) + Keff/(x(i+1)-x(i));
end

% contribution de la CL Dirichlet sur le bord gauche
A(1, 1) =  2*Km/w(1);
b(1)    =  2*Km/w(1)*Tdg;

% contribution de l'interface (1 | 2)
hm = w(1)/2;  Km = K(1);
hp = w(2)/2;  Kp = K(2);
Keff = (hm+hp)/(hm/Km + hp/Kp);

A(1, 1) =  A(1, 1)  +Keff/(x(2)-x(1));
A(1, 2) =           -Keff/(x(2)-x(1));

% contribution de la CL Neumann sur le bord droit
A(N, N) =  H*2*Kp/(2*Kp+H*w(N));
b(N)    =  H*2*Kp/(2*Kp+H*w(N))*Tad;

% contribution de l'interface (N-1 | N)
hm = w(N-1)/2;  Km = K(N-1);   
hp = w(N  )/2;  Kp = K(N  );
Keff = (hm+hp)/(hm/Km + hp/Kp);

A(N, N  ) =  A(N, N) +Keff/(x(N)-x(N-1));
A(N, N-1) =          -Keff/(x(N)-x(N-1));

T = A\b;
plot(x, T, 'r.-')
grid on


