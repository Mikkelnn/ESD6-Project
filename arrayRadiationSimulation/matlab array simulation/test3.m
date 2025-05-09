% ===========================
% Beamforming Script (4 antennas, Realistic Gain in dBi)
% ===========================

clc; clear;

% ---------------------------
% CONFIGURATION
% ---------------------------
frequency = 5.8e9;
lambda = 3e8 / frequency;
element_spacing = lambda / 2;
num_elements = 4;
antenna_files = {'ant1.txt', 'ant2.txt', 'ant3.txt', 'ant4.txt'};

% Beamforming weights (steering angles)
phase_shifts_deg = [0, 0, 0, 0];
weights = exp(1j * deg2rad(phase_shifts_deg));

% ---------------------------
% CALIBRATION OFFSET
% ---------------------------
calibration_offset_dB = 1.4516;

% ---------------------------
% LOAD FAR FIELD DATA
% ---------------------------
for i = 1:num_elements
    data = readmatrix(antenna_files{i});
    data = data(data(:,3) == frequency, :);  % Filter by 5.8 GHz

    azimuth = data(:,1);       % theta
    elevation = data(:,2);     % phi
    EH = data(:,4) + 1j * data(:,5);
    EV = data(:,6) + 1j * data(:,7);

    E_total = sqrt(abs(EH).^2 + abs(EV).^2);  % Linear field

    ant(i).azimuth = azimuth;
    ant(i).elevation = elevation;
    ant(i).E = E_total;
    ant(i).position = [(i-1)*element_spacing, 0, 0];
end

% ---------------------------
% BEAMFORMING CALCULATION
% ---------------------------
theta = ant(1).azimuth;
phi = ant(1).elevation;
num_points = length(theta);
AF = zeros(num_points, 1);

for i = 1:num_elements
    kx = sin(phi) .* cos(theta);
    ky = sin(phi) .* sin(theta);
    kz = cos(phi);
    pos = ant(i).position;
    phase_shift = exp(1j * 2*pi/lambda * (kx*pos(1) + ky*pos(2) + kz*pos(3)));
    AF = AF + weights(i) * ant(i).E .* phase_shift;
end

% Magnitude as power (proportional to gain)
AF_mag = abs(AF).^2;  % Power
AF_norm = AF_mag / max(AF_mag);
AF_mag_dB = 10 * log10(AF_mag) + calibration_offset_dB;

% ---------------------------
% GRID RESHAPING
% ---------------------------
[unique_theta, ~, ~] = unique(theta);
[unique_phi, ~, ~] = unique(phi);
Nphi = length(unique_phi);

theta_grid = reshape(theta, Nphi, []);
phi_grid = reshape(phi, Nphi, []);
AF_norm_grid = reshape(AF_norm, Nphi, []);
AF_mag_grid = reshape(AF_mag, Nphi, []);
AF_mag_dB_grid = reshape(AF_mag_dB, Nphi, []);

% ---------------------------
% MAXIMUM GAIN
% ---------------------------
[max_gain, idx_max] = max(AF_mag);
max_gain_dB = 10 * log10(max_gain) + calibration_offset_dB;
fprintf('Maximum calibrated gain: %.2f dB\n', max_gain_dB);
fprintf('At theta = %.2f°, phi = %.2f°\n', ...
        rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));

% ---------------------------
% POLAR CUTS
% ---------------------------
figure;

% Normalized at phi = 0
subplot(2,2,1);
cut_phi = 0;
mask_phi = abs(phi_grid(:,1) - deg2rad(cut_phi)) < 1e-3;
polarplot(unique_theta, AF_norm_grid(mask_phi,:)');
title('Normalized Polar Plot at \\phi = 0');

% dB at phi = 0
subplot(2,2,2);
polarplot(unique_theta, AF_mag_dB_grid(mask_phi,:)');
title('dB Polar Plot at \\phi = 0');

% Normalized at theta = 0
subplot(2,2,3);
cut_theta = 0;
mask_theta = abs(theta_grid(1,:) - deg2rad(cut_theta)) < 1e-3;
polarplot(unique_phi, AF_norm_grid(:,mask_theta));
title('Normalized Polar Plot at \\theta = 0');

% dB at theta = 0
subplot(2,2,4);
polarplot(unique_phi, AF_mag_dB_grid(:,mask_theta));
title('dB Polar Plot at \\theta = 0');

% ---------------------------
% 3D UNNORMALIZED PATTERN (LINEAR - Realistic Scale)
% ---------------------------
max_gain_dB_no_offset = 10 * log10(max(AF_mag(:)));
r_linear = AF_mag_grid / max(AF_mag_grid(:)) * sqrt(10^(max_gain_dB_no_offset / 10));
[X1,Y1,Z1] = sph2cart(theta_grid, pi/2 - phi_grid, r_linear);
figure;
surf(real(X1), real(Y1), real(Z1), r_linear, 'EdgeColor', 'none');
title('3D Radiation Pattern (Linear - Scaled)');
xlabel('X'); ylabel('Y'); zlabel('Z (Gain)');
axis equal; view(3); colorbar; camlight; lighting gouraud;

% ---------------------------
% 3D UNNORMALIZED PATTERN (dB - With Threshold)
% ---------------------------
AF_mag_dB_grid(AF_mag_dB_grid == -Inf) = -100;
threshold_dB = -30;
AF_mag_dB_grid(AF_mag_dB_grid < threshold_dB) = threshold_dB;

r_db = AF_mag_dB_grid;
[X2,Y2,Z2] = sph2cart(theta_grid, pi/2 - phi_grid, r_db);
figure;
surf(real(X2), real(Y2), real(Z2), r_db, 'EdgeColor', 'none');
title('3D Radiation Pattern (dB - Thresholded)');
xlabel('X (dB)'); ylabel('Y (dB)'); zlabel('Z (dB)');
axis equal; view(3); colorbar; camlight; lighting gouraud;
caxis([threshold_dB max(r_db(:))]);
