% ===========================
% Beamforming con campos complejos (todo en uno, corregido y mejorado)
% ===========================

clc; clear;

% ---------------------------
% CONFIGURACIÓN
% ---------------------------
frequency = 5.8e9;
lambda = 3e8 / frequency;
element_spacing = lambda / 2;
num_elements = 4;
calibration_offset_dB = 1.4516;
umbral_dB = -30; % umbral para visualización en dB
antenna_files = {'ant1.txt', 'ant2.txt', 'ant3.txt', 'ant4.txt'};

% Fase de excitación para beamsteering (en grados)
phase_shifts_deg = [0, 0, 0, 0];
weights = exp(1j * deg2rad(phase_shifts_deg));

% ---------------------------
% CARGA DE DATOS Y CAMPOS COMPLEJOS
% ---------------------------
for i = 1:num_elements
    data = readmatrix(antenna_files{i}, 'NumHeaderLines', 2);
    data = data(data(:,3) == frequency, :);

    ant(i).azimuth   = data(:,1);
    ant(i).elevation = data(:,2);
    ant(i).EH = data(:,4) + 1j * data(:,5);
    ant(i).EV = data(:,6) + 1j * data(:,7);
    ant(i).position = [(i-1)*element_spacing, 0, 0];
end

theta = ant(1).azimuth;
phi = ant(1).elevation;
num_points = length(theta);

% ---------------------------
% BEAMFORMING COHERENTE
% ---------------------------
EH_total = zeros(num_points, 1);
EV_total = zeros(num_points, 1);

for i = 1:num_elements
    kx = sin(phi) .* cos(theta);
    ky = sin(phi) .* sin(theta);
    kz = cos(phi);
    pos = ant(i).position;
    steering = exp(1j * 2*pi/lambda * (kx*pos(1) + ky*pos(2) + kz*pos(3)));

    EH_total = EH_total + weights(i) * ant(i).EH .* steering;
    EV_total = EV_total + weights(i) * ant(i).EV .* steering;
end

E_complex = EH_total + EV_total;
E_total = sqrt(abs(EH_total).^2 + abs(EV_total).^2);

% Desnormalizado en escala real
E_power = E_total.^2;
[max_gain, idx_max] = max(E_power);
max_gain_dB = 10 * log10(max_gain) + calibration_offset_dB;

fprintf('Maximum calibrated gain: %.2f dB\n', max_gain_dB);
fprintf('At theta = %.2f°, phi = %.2f°\n', ...
        rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));
fprintf('Maximum electric field amplitude: %.3f\n', E_total(idx_max));

% ---------------------------
% MALLA DE DIRECCIONES
% ---------------------------
[unique_theta, ~, ~] = unique(theta);
[unique_phi, ~, ~] = unique(phi);
Nphi = length(unique_phi);

theta_grid = reshape(theta, Nphi, []);
phi_grid = reshape(phi, Nphi, []);
E_mag_grid = reshape(E_total, Nphi, []);
E_mag_dB_grid = 10 * log10(E_mag_grid.^2) + calibration_offset_dB;

% ---------------------------
% POLAR CUTS
% ---------------------------
figure;

subplot(2,2,1);
cut_phi = 0;
mask_phi = abs(phi_grid(:,1) - deg2rad(cut_phi)) < 1e-3;
polarplot(unique_theta, E_mag_grid(mask_phi,:)');
title('Normalized Polar Plot at \phi = 0');

subplot(2,2,2);
polarplot(unique_theta, E_mag_dB_grid(mask_phi,:)');
title('dB Polar Plot at \phi = 0');

subplot(2,2,3);
cut_theta = 0;
mask_theta = abs(theta_grid(1,:) - deg2rad(cut_theta)) < 1e-3;
polarplot(unique_phi, E_mag_grid(:,mask_theta));
title('Normalized Polar Plot at \theta = 0');

subplot(2,2,4);
polarplot(unique_phi, E_mag_dB_grid(:,mask_theta));
title('dB Polar Plot at \theta = 0');

% ---------------------------
% 3D PATRÓN ESCALADO (LINEAL)
% ---------------------------
r_linear = E_mag_grid;
[X1,Y1,Z1] = sph2cart(theta_grid, pi/2 - phi_grid, r_linear);
figure;
surf(real(X1), real(Y1), real(Z1), r_linear, 'EdgeColor', 'none');
title('3D Radiation Pattern (Linear - Scaled)');
xlabel('X'); ylabel('Y'); zlabel('Z (Gain)');
axis equal; view(3); colorbar; camlight; lighting gouraud;

% ---------------------------
% 3D PATRÓN EN dB UMBRALIZADO
% ---------------------------
E_mag_dB_grid(isinf(E_mag_dB_grid)) = -100;
E_mag_dB_grid(E_mag_dB_grid < umbral_dB) = umbral_dB;

r_db = E_mag_dB_grid;
[X2,Y2,Z2] = sph2cart(theta_grid, pi/2 - phi_grid, r_db);
figure;
surf(real(X2), real(Y2), real(Z2), r_db, 'EdgeColor', 'none');
title('3D Radiation Pattern (dB - Thresholded)');
xlabel('X (dB)'); ylabel('Y (dB)'); zlabel('Z (dB)');
axis equal; view(3); colorbar; camlight; lighting gouraud;
caxis([umbral_dB max(r_db(:))]);
