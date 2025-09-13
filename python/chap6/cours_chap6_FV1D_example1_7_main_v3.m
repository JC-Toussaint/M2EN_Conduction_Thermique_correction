% Paramètres
L = 3e-3;       % [m] - longueur du domaine
N = 100;        % [-] - nombre de cellules
K = 0.3;        % [W/m·K] - conductivité thermique
H = 2;          % [W/m²·K] - coefficient de convection

Tdg = 308;      % [K] - température dirichlet à gauche
Tad = 297;      % [K] - température ambiante à droite
Tsur = 297;     % [K] - température de l'environnement
eps = 0.95;     % [-] - émissivité
sigma = 5.670374419e-8;  % [W/m²·K⁴] - constante de Stefan-Boltzmann

% Construction du maillage
[w, x] = build_mesh(N, L);

% Initialisation de la température
T = Tsur * ones(N, 1);  % Valeur initiale

% Résolution itérative
for n = 1:20
    T = solve_system(w, x, T, K, H, Tdg, Tad, Tsur, eps, sigma);
end

% Affichage des résultats
figure('Position', [100, 100, 800, 600]);
plot(x, T, 'r.-', 'LineWidth', 2, 'MarkerSize', 8);
grid on;
xlabel('Position x [m]');
ylabel('Température T [K]');
title('Distribution de température 1D - Matériau homogène');

% Calcul de la solution analytique
TL = Tsur;  % valeur initiale
for n = 1:20
    % calcul du coefficient effectif de convection + radiation
    Heff = H + eps*sigma*(TL+Tsur)*(TL^2+Tsur^2);
    TL = (Heff*Tad + K/L*Tdg) / (K/L + Heff);
end

% Affichage des résultats
fprintf('Température au bord droit (numérique): %.6f K\n', T(end));
fprintf('Température limite analytique (TL): %.6f K\n', TL);
fprintf('Erreur relative: %.4f%%\n', abs(T(end) - TL)/TL*100);
fprintf('Température minimale: %.2f K\n', min(T));
fprintf('Température maximale: %.2f K\n', max(T));

%% Fonctions

function [w, x] = build_mesh(N, L)
    % Construction du maillage uniforme
    
    % Largeurs des cellules (uniformes)
    w = ones(N, 1) * L/N;
    
    % Centres des cellules
    x = zeros(N, 1);
    x(1) = w(1)/2;
    for i = 2:N
        x(i) = x(i-1) + w(i);
    end
end

function T = solve_system(w, x, T, K, H, Tdg, Tad, Tsur, eps, sigma)
    % Résolution du système linéaire pour la conduction thermique
    
    N = length(w);
    
    % Initialisation de la matrice A et du vecteur b
    A = zeros(N, N);
    b = zeros(N, 1);
    
    % Remplissage de la matrice pour les cellules intérieures (i = 2 à N-1)
    for i = 2:N-1
        A(i, i-1) = -K / (x(i) - x(i-1));
        A(i, i) = +K / (x(i) - x(i-1)) + K / (x(i+1) - x(i));
        A(i, i+1) = -K / (x(i+1) - x(i));
    end
    
    % Condition aux limites sur le bord gauche (Dirichlet)
    A(1, 1) = 2*K/w(1) + K/(x(2) - x(1));
    A(1, 2) = -K/(x(2) - x(1));
    b(1) = 2*K/w(1) * Tdg;
    
    % Calcul du coefficient effectif de convection + radiation
    Heff = H + eps*sigma*(T(N)+Tsur)*(T(N)^2+Tsur^2);
    
    % Condition aux limites sur le bord droit (convection + radiation)
    A(N, N) = Heff*2*K/(2*K + Heff*w(N)) + K/(x(N) - x(N-1));
    A(N, N-1) = -K/(x(N) - x(N-1));
    b(N) = Heff*2*K/(2*K + Heff*w(N)) * Tad;
    
    % Résolution du système linéaire
    T = A \ b;
end