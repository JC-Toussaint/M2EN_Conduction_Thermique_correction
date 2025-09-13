clc
clear all
close all

L=1;
N=10;
K = 200;
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

A = sparse(N, N);
b = zeros(N, 1);
for i=2:N-1
    A(i, i-1) = -K/(x(i)-x(i-1));
    A(i, i  ) = +K/(x(i)-x(i-1))+K/(x(i+1)-x(i));
    A(i, i+1) = -K/(x(i+1)-x(i));
end

A(1, 1) =  2*K/w(1)+K/(x(2)-x(1));
A(1, 2) = -K/(x(2)-x(1));
b(1) = 2*K/w(1)*Tdg;

A(N, N  ) =  H*2*K/(2*K+H*w(N))+K/(x(N)-x(N-1));
A(N, N-1) = -K/(x(N)-x(N-1));
b(N) = H*2*K/(2*K+H*w(N))*Tad;

T = A\b;
plot(x, T, 'r.-')
grid on

TL = (H*Tad+K/L*Tdg)/(K/L+H)
