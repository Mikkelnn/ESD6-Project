% ---------------------------
% Beamforming simulation from measured far-field patterns
% Adaptado al formato de archivo ant1.txt, ant2.txt, etc.
% ---------------------------

clear; clc;

%% Configuración
freq_target = 5.8e9;                    % Frecuencia deseada [Hz]
c = 3e8;
lambda = c / freq_target;
d = lambda / 2;                         % Separación entre antenas (m)

N = 4;                                  % Número de antenas transmisoras
positions = [0:d:(N-1)*d; 0 0 0 0; 0 0 0 0]; % Alineadas en X

% Fases relativas en grados
phases_deg = [0 -90 -180 -270];
phases_rad = deg2rad(phases_deg);

% Archivos de far-field individuales
files = {'ant1.txt', 'ant2.txt', 'ant3.txt', 'ant4.txt'};

% Inicializar campo total
theta_all = [];
phi_all = [];
E_total = [];

for i = 1:N
    % Leer datos y filtrar por frecuencia
    data = readmatrix(files{i}, 'NumHeaderLines', 1);
    data_5800 = data(data(:,3) == freq_target, :);

    az = data_5800(:,1);                % Azimuth (phi)
    el = data_5800(:,2);                % Elevation (theta)
    phi = az; theta = el;

    if i == 1
        phi_unique = unique(phi);
        theta_unique = unique(theta);
        [Phi, Theta] = meshgrid(phi_unique, theta_unique);
        E_total = zeros(size(Phi));
    end

    EH_re = data_5800(:,4);
    EH_im = data_5800(:,5);
    Eth = EH_re + 1i * EH_im;
    Eth_matrix = reshape(Eth, length(theta_unique), length(phi_unique));

    k = 2 * pi / lambda;
    r = positions(:,i);
    phase_shift = exp(1i * (k * (r(1)*sin(Theta).*cos(Phi) + ...
                                 r(2)*sin(Theta).*sin(Phi) + ...
                                 r(3)*cos(Theta)) + phases_rad(i)));

    E_total = E_total + Eth_matrix .* phase_shift;
end

%% Magnitud y ganancia
E_mag = abs(E_total);
[max_val, idx_max] = max(E_mag(:));
max_gain_dB = 20*log10(max_val);

fprintf('Max Field Magnitude: %.3f (rel. units)\n', max_val);
fprintf('Estimated Maximum Gain: %.2f dB\n', max_gain_dB);

%% Patrón 3D sin normalizar
[X,Y,Z] = sph2cart(Phi, pi/2 - Theta, E_mag);

figure;
surf(X, Y, Z, E_mag, 'EdgeColor', 'none');
axis equal;
xlabel('X'); ylabel('Y'); zlabel('Z');
title('Patrón de radiación combinado - Beamforming (5.8 GHz)');
colorbar;
view(30,30);
lighting gouraud;
camlight headlight;

%% ---------------------------
% 3D PATRÓN EN dB UMBRALIZADO
% ---------------------------

umbral_dB = -30; % Umbral de dB
E_mag_dB_grid = 20 * log10(E_mag);
E_mag_dB_grid(isinf(E_mag_dB_grid)) = -100;
E_mag_dB_grid(E_mag_dB_grid < umbral_dB) = umbral_dB;

r_db = E_mag_dB_grid;
[X2,Y2,Z2] = sph2cart(Phi, pi/2 - Theta, r_db);

figure;
surf(real(X2), real(Y2), real(Z2), r_db, 'EdgeColor', 'none');
title('3D Radiation Pattern (dB - Thresholded)');
xlabel('X (dB)'); ylabel('Y (dB)'); zlabel('Z (dB)');
axis equal; view(3); colorbar; camlight; lighting gouraud;
caxis([umbral_dB max(r_db(:))]);

%% Cortes polares
threshold_dB = -30;

% Corte en phi = 0 (theta variable)
cut_phi_deg = 0;
[~, idx_phi] = min(abs(rad2deg(phi_unique) - cut_phi_deg));
E_cut_theta = E_mag(:, idx_phi);
E_cut_theta_dB = 20 * log10(E_cut_theta);
E_cut_theta_dB(~isfinite(E_cut_theta_dB)) = -100;
E_cut_theta_dB = max(E_cut_theta_dB, threshold_dB);

% Corte en theta = 90 (phi variable)
cut_theta_deg = 90;
[~, idx_theta] = min(abs(rad2deg(theta_unique) - cut_theta_deg));
E_cut_phi = E_mag(idx_theta, :);
E_cut_phi_dB = 20 * log10(E_cut_phi);
E_cut_phi_dB(~isfinite(E_cut_phi_dB)) = -50;
E_cut_phi_dB = max(E_cut_phi_dB, threshold_dB);

% Polar plots corregidos con ángulos explícitos
figure;
subplot(2,2,1);
polarplot(deg2rad(rad2deg(theta_unique)), E_cut_theta);
title('Corte \phi = 0° (lineal)');

subplot(2,2,2);
polarplot(deg2rad(rad2deg(theta_unique)), E_cut_theta_dB);
title('Corte \phi = 0° (dB)');

subplot(2,2,3);
polarplot(deg2rad(rad2deg(phi_unique)), E_cut_phi);
title('Corte \theta = 90° (lineal)');

subplot(2,2,4);
polarplot(deg2rad(rad2deg(phi_unique)), E_cut_phi_dB);
title('Corte \theta = 90° (dB)');
