% ===========================
% Full Array Gain Analysis Script
% ===========================

clc; clear;

% ---------------------------
% CONFIGURATION
% ---------------------------
filename = 'TX Combined 0deg Spherical FieldsGain_ETotal_ETheta_EPhi.txt';     % <-- Update with your filename
frequency = 5.8e9;
gain_offset_dB = 5.64;           % Splitter loss compensation

% ---------------------------
% LOAD DATA
% ---------------------------
data = readmatrix(filename, 'NumHeaderLines', 1);
data = data(data(:,3) == frequency, :);  % Filter 5.8 GHz only

theta = data(:,1);        % Azimuth
phi   = data(:,2);        % Elevation
EH    = data(:,5) + 1j * data(:,6);
EV    = data(:,7) + 1j * data(:,8);

E_total = sqrt(abs(EH).^2 + abs(EV).^2);   % Magnitude in linear volts

% ---------------------------
% GAIN CALCULATION
% ---------------------------
AF_mag = abs(E_total);
AF_mag_dB = 20 * log10(AF_mag) + gain_offset_dB;

% ---------------------------
% MAXIMUM GAIN
% ---------------------------
[max_gain, idx_max] = max(AF_mag);
max_gain_dB = 20 * log10(max_gain) + gain_offset_dB;

fprintf('Maximum calibrated gain: %.2f dB\n', max_gain_dB);
fprintf('At theta = %.2f°, phi = %.2f°\n', ...
    rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));

% ---------------------------
% GRID RESHAPING
% ---------------------------
[unique_theta, ~, ~] = unique(theta);
[unique_phi, ~, ~] = unique(phi);
Nphi = length(unique_phi);

theta_grid = reshape(theta, Nphi, []);
phi_grid   = reshape(phi, Nphi, []);
AF_mag_grid = reshape(AF_mag, Nphi, []);
AF_mag_dB_grid = reshape(AF_mag_dB, Nphi, []);

% ---------------------------
% 3D UNNORMALIZED (LINEAR)
% ---------------------------
r_linear = AF_mag_grid / max(AF_mag_grid(:)) * 10^(max_gain_dB / 20);  % Reescalado
[X,Y,Z] = sph2cart(theta_grid, pi/2 - phi_grid, r_linear);

figure;
surf(real(X), real(Y), real(Z), r_linear, 'EdgeColor', 'none');
title('3D Unnormalized Radiation Pattern (Linear - Calibrated Scale)');
xlabel('X'); ylabel('Y'); zlabel('Z (Gain)');
axis equal; view(3); colorbar; camlight; lighting gouraud;



% ---------------------------
% 3D UNNORMALIZED (dB)
% ---------------------------
AF_mag_dB_grid(AF_mag_dB_grid == -Inf) = -100;
threshold_dB = -10;  % Umbral para recortar ruido
AF_mag_dB_grid(AF_mag_dB_grid < threshold_dB) = threshold_dB;

r_db = AF_mag_dB_grid;  % Usamos los valores ya truncados
[Xdb, Ydb, Zdb] = sph2cart(theta_grid, pi/2 - phi_grid, r_db);

figure;
surf(real(Xdb), real(Ydb), real(Zdb), r_db, 'EdgeColor', 'none');
title('3D Radiation Pattern (dB, Calibrated & Thresholded)');
xlabel('X (dB)'); ylabel('Y (dB)'); zlabel('Z (dB)');
axis equal; view(3); colorbar; camlight; lighting gouraud;
caxis([threshold_dB max(r_db(:))]);  % Ajuste de colores

