% ===========================
% Beamforming Simulation Script (Realistic + Calibrated)
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

% Beamforming weights (adjust for steering)
phase_shifts_deg = [0, 0, 0, 0];
weights = exp(1j * deg2rad(phase_shifts_deg));

% ---------------------------
% CALIBRATION OFFSET (from ref. gain vs measured gain at 5.8 GHz)
% ---------------------------
calibration_offset_dB = 1.4516;

% ---------------------------
% LOAD FAR FIELD DATA
% ---------------------------
for i = 1:num_elements
    data = readmatrix(antenna_files{i});
    data = data(data(:,3) == frequency, :);  % Select only desired frequency

    azimuth = data(:,1);         % theta (Azimuth)
    elevation = data(:,2);       % phi (Elevation)
    
    EH = data(:,4) + 1j * data(:,5);
    EV = data(:,6) + 1j * data(:,7);
    
    % E_total in ant1.txt is in dB, but not used — we use EH + EV
    E_total = sqrt(abs(EH).^2 + abs(EV).^2);  % Linear field [V/m]

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

AF_mag = abs(AF);
AF_norm = AF_mag / max(AF_mag);
AF_dB = 20 * log10(AF_norm);
AF_mag_dB = 20 * log10(AF_mag) + calibration_offset_dB;

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
AF_dB_grid = reshape(AF_dB, Nphi, []);
AF_mag_dB_grid = reshape(AF_mag_dB, Nphi, []);

% ---------------------------
% 3D PLOTS
% ---------------------------
[X,Y,Z] = sph2cart(theta_grid, pi/2 - phi_grid, AF_norm_grid);
[X2,Y2,Z2] = sph2cart(theta_grid, pi/2 - phi_grid, AF_mag_grid);

AF_mag_dB_grid(AF_mag_dB_grid == -Inf) = -100;
radius_shifted = AF_mag_dB_grid - min(AF_mag_dB_grid(:));
[Xd, Yd, Zd] = sph2cart(theta_grid, pi/2 - phi_grid, real(radius_shifted));

figure;
surf(real(X), real(Y), real(Z), AF_norm_grid, 'EdgeColor', 'none');
title('3D Normalized Radiation Pattern (Linear)');
xlabel('X'); ylabel('Y'); zlabel('Z');
axis equal; view(3); colorbar; camlight; lighting gouraud;

figure;
surf(real(X2), real(Y2), real(Z2), AF_mag_grid, 'EdgeColor', 'none');
title('3D Unnormalized Radiation Pattern (Linear)');
xlabel('X'); ylabel('Y'); zlabel('Z');
axis equal; view(3); colorbar; camlight; lighting gouraud;

figure;
surf(Xd, Yd, Zd, AF_mag_dB_grid, 'EdgeColor', 'none');
title('3D Unnormalized Radiation Pattern (dB, Calibrated)');
xlabel('X'); ylabel('Y'); zlabel('Z');
axis equal; view(3); colorbar; camlight; lighting gouraud;
caxis([-40 0]);

% ---------------------------
% POLAR CUTS
% ---------------------------
figure;
subplot(2,2,1);
cut_phi = 0;
mask_phi = abs(phi_grid(:,1) - deg2rad(cut_phi)) < 1e-3;
polarplot(unique_theta, AF_norm_grid(mask_phi,:)');
title('Normalized Polar Plot at \\phi = 0');

subplot(2,2,2);
polarplot(unique_theta, AF_mag_dB_grid(mask_phi,:)');
title('Unnormalized dB Polar Plot at \\phi = 0');

subplot(2,2,3);
cut_theta = 0;
mask_theta = abs(theta_grid(1,:) - deg2rad(cut_theta)) < 1e-3;
polarplot(unique_phi, AF_norm_grid(:,mask_theta));
title('Normalized Polar Plot at \\theta = 0');

subplot(2,2,4);
polarplot(unique_phi, AF_mag_dB_grid(:,mask_theta));
title('Unnormalized dB Polar Plot at \\theta = 0');

% ---------------------------
% MAXIMUM GAIN
% ---------------------------
[max_gain, idx_max] = max(AF_mag);
max_gain_dB = 20 * log10(max_gain) + calibration_offset_dB;
fprintf('Maximum calibrated gain: %.2f dB\n', max_gain_dB);
fprintf('At theta = %.2f°, phi = %.2f°\n', ...
        rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));

% ---------------------------
% DIRECTIVITY CALCULATION
% ---------------------------
dtheta = abs(rad2deg(unique_theta(2) - unique_theta(1)));
dphi = abs(rad2deg(unique_phi(2) - unique_phi(1)));
solid_angle = sum(sum(AF_mag_grid.^2 .* sin(phi_grid))) * deg2rad(dtheta) * deg2rad(dphi);
D = 4 * pi * max(AF_mag.^2) / solid_angle;
D_dB = 10 * log10(D + eps) + calibration_offset_dB;
fprintf('Estimated Directivity (calibrated): %.2f dB\n', D_dB);

% ---------------------------
% 3D DIRECTIVITY PLOT (CALIBRATED)
% ---------------------------
Dir_shifted = 10 * log10(AF_mag_grid.^2 + eps) + calibration_offset_dB;
Dir_shifted(Dir_shifted == -Inf) = -100;
Dir_shifted = Dir_shifted - min(Dir_shifted(:));
[Xd_dir, Yd_dir, Zd_dir] = sph2cart(theta_grid, pi/2 - phi_grid, real(Dir_shifted));

figure;
surf(real(Xd_dir), real(Yd_dir), real(Zd_dir), Dir_shifted, 'EdgeColor', 'none');
title('3D Directivity Pattern (dB, Calibrated)');
xlabel('X'); ylabel('Y'); zlabel('Z');
axis equal; view(3); colorbar; camlight; lighting gouraud;
caxis([-40 0]);
