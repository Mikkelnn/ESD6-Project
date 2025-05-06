% Beamforming simulation from measured far-field patterns
% Adaptado al formato de archivo ant1.txt, ant2.txt, etc.

clear; clc;

%% Configuración
freq_target = 5.8e9;                    % Frecuencia deseada [Hz]
c = 3e8;
lambda = c / freq_target;
d = lambda / 2;                         % Separación entre antenas (m)

N = 4;                                  % Número de antenas transmisoras
positions = [0:d:(N-1)*d; 0 0 0 0; 0 0 0 0]; % Alineadas en X

% Fases relativas en grados (puedes modificarlas)
phases_deg = [0 90 180 270];
phases_rad = deg2rad(phases_deg);

% Archivos de far-field individuales
files = {
    'ant1.txt',
    'ant2.txt',
    'ant3.txt',
    'ant4.txt'
};

% Inicialización de estructuras
theta_all = [];
phi_all = [];

% Inicializar campo total
E_total = [];

for i = 1:N
    % Leer datos y filtrar por frecuencia
    data = readmatrix(files{i}, 'NumHeaderLines', 1);
    data_5800 = data(data(:,3) == freq_target, :);

    az = data_5800(:,1);                % Azimuth (phi)
    el = data_5800(:,2);                % Elevation (theta)
    phi = az; theta = el;
    
    % Guardar rejilla angular (solo en primera iteración)
    if i == 1
        phi_unique = unique(phi);
        theta_unique = unique(theta);
        [Phi, Theta] = meshgrid(phi_unique, theta_unique);
        E_total = zeros(size(Phi));
    end

    % Crear mapa de Etheta (usamos EH = componente H)
    EH_re = data_5800(:,4);
    EH_im = data_5800(:,5);
    Eth = EH_re + 1i * EH_im;

    % Reorganizar a matriz 2D
    Eth_matrix = reshape(Eth, length(theta_unique), length(phi_unique));

    % Factor de fase de posición y excitación
    k = 2 * pi / lambda;
    r = positions(:,i);
    phase_shift = exp(1i * (k * (r(1)*sin(Theta).*cos(Phi) + ...
                                 r(2)*sin(Theta).*sin(Phi) + ...
                                 r(3)*cos(Theta)) + phases_rad(i)));

    % Sumar al campo total
    E_total = E_total + Eth_matrix .* phase_shift;
end

%% Visualización 3D del patrón
E_mag = abs(E_total);
E_mag_norm = E_mag / max(E_mag(:));
R = E_mag_norm;

[X,Y,Z] = sph2cart(Phi, pi/2 - Theta, R);

figure;
surf(X, Y, Z, E_mag_norm, 'EdgeColor', 'none');
axis equal;
xlabel('X'); ylabel('Y'); zlabel('Z');
title('Patrón de radiación combinado - Beamforming (5.8 GHz)');
colorbar;
view(30,30);
lighting gouraud
camlight headlight
