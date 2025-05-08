% ===========================
% Beamforming Simulation Script
% ===========================

clc; clear;

% ---------------------------
% CONFIGURATION
% ---------------------------
frequency = 5.8e9;                     % Operating frequency (Hz)
lambda = 3e8 / frequency;             % Wavelength (m)
element_spacing = lambda / 2;        % Spacing between Tx elements
num_elements = 4;                    % Number of Tx antennas

% Antenna file names (assumed format)
antenna_files = {'ant1.txt', 'ant2.txt', 'ant3.txt', 'ant4.txt'};

% Beamforming weights (adjust phases here)
phase_shifts_deg = [0, 90, 180, 270]; % Phase shifts in degrees
weights = exp(1j * deg2rad(phase_shifts_deg));

% ---------------------------
% LOAD FAR FIELD DATA
% ---------------------------
for i = 1:num_elements
    data = readmatrix(antenna_files{i});
    freq_mask = data(:,3) == frequency;
    data = data(freq_mask, :);
    
    azimuth = data(:,1);          % Theta (Azimuth)
    elevation = data(:,2);        % Phi (Elevation)
    EH = data(:,4) + 1j*data(:,5); 
    EV = data(:,6) + 1j*data(:,7); 
    E_total = sqrt(abs(EH).^2 + abs(EV).^2);
    
    ant(i).azimuth = azimuth;
    ant(i).elevation = elevation;
    ant(i).E = E_total;
    ant(i).position = [(i-1)*element_spacing, 0, 0];  % Linear x-axis array
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
AF_norm = AF_mag / max(AF_mag); % Normalize
AF_dB = 20 * log10(AF_norm);
AF_mag_dB = 20 * log10(AF_mag); % Unnormalized dB

% ---------------------------
% RESHAPE GRIDS
% ---------------------------
[unique_theta, ~, ~] = unique(theta);
[unique_phi, ~, ~] = unique(phi);

try
    theta_grid = reshape(theta, length(unique_phi), []);
    phi_grid = reshape(phi, length(unique_phi), []);
    AF_norm_grid = reshape(AF_norm, length(unique_phi), []);
    AF_mag_grid = reshape(AF_mag, length(unique_phi), []);
    AF_dB_grid = reshape(AF_dB, length(unique_phi), []);
    AF_mag_dB_grid = reshape(AF_mag_dB, length(unique_phi), []);
catch
    error('Could not reshape. The angular sampling is likely not uniform or rectangular.');
end

% ---------------------------
% 3D NORMALIZED PATTERN (LINEAR)
% ---------------------------
[X,Y,Z] = sph2cart(theta_grid, pi/2 - phi_grid, AF_norm_grid);

figure;
surf(X, Y, Z, AF_norm_grid, 'EdgeColor', 'none');
title('3D Normalized Radiation Pattern (Linear)');
xlabel('X'); ylabel('Y'); zlabel('Z');
colorbar; axis equal; view(3);
camlight; lighting gouraud;

% ---------------------------
% 3D UNNORMALIZED PATTERN (LINEAR)
% ---------------------------
[X2,Y2,Z2] = sph2cart(theta_grid, pi/2 - phi_grid, AF_mag_grid);

figure;
surf(X2, Y2, Z2, AF_mag_grid, 'EdgeColor', 'none');
title('3D Unnormalized Radiation Pattern (Linear)');
xlabel('X'); ylabel('Y'); zlabel('Z');
colorbar; axis equal; view(3);
camlight; lighting gouraud;

% ---------------------------
% 3D UNNORMALIZED PATTERN (dB)
% ---------------------------
AF_mag_dB_grid(AF_mag_dB_grid == -Inf) = -100;  % Avoid -Inf
AF_mag_shifted = AF_mag_dB_grid - min(AF_mag_dB_grid(:));  % Shift to positive values for radius

[X3, Y3, Z3] = sph2cart(theta_grid, pi/2 - phi_grid, AF_mag_shifted);

figure;
surf(X3, Y3, Z3, AF_mag_dB_grid, 'EdgeColor', 'none');
title('3D Unnormalized Radiation Pattern (dB)');
xlabel('X'); ylabel('Y'); zlabel('Z');
colorbar; axis equal; view(3);
camlight; lighting gouraud;
caxis([-40 0]);  % Adjust based on dynamic range

% ---------------------------
% POLAR CUTS
% ---------------------------
figure;

% Cut at phi = 0°
subplot(2,2,1);
cut_phi = 0;
mask_phi = abs(phi_grid(:,1) - deg2rad(cut_phi)) < 1e-3;
polarplot(unique_theta, AF_norm_grid(mask_phi,:)');
title('Normalized Polar Plot at \phi = 0');

subplot(2,2,2);
polarplot(unique_theta, AF_mag_dB_grid(mask_phi,:)');
title('Unnormalized dB Polar Plot at \phi = 0');

% Cut at theta = 0°
subplot(2,2,3);
cut_theta = 0;
mask_theta = abs(theta_grid(1,:) - deg2rad(cut_theta)) < 1e-3;
polarplot(unique_phi, AF_norm_grid(:,mask_theta));
title('Normalized Polar Plot at \theta = 0');

subplot(2,2,4);
polarplot(unique_phi, AF_mag_dB_grid(:,mask_theta));
title('Unnormalized dB Polar Plot at \theta = 0');

% ---------------------------
% MAXIMUM GAIN
% ---------------------------
[max_gain, idx_max] = max(AF_mag);
max_gain_dB = 20 * log10(max_gain);
fprintf('Maximum unnormalized gain: %.2f dB\n', max_gain_dB);
fprintf('At theta = %.2f°, phi = %.2f°\n', ...
        rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));

% ---------------------------
% DIRECTIVITY CALCULATION
% ---------------------------
% Convert linear gain to power pattern
U = AF_mag_grid.^2;

% Integration steps (assume uniform angular grid)
dtheta = abs(theta_grid(1,2) - theta_grid(1,1));
dphi   = abs(phi_grid(2,1) - phi_grid(1,1));

% Compute radiated power Prad (∬ U * sin(phi) dtheta dphi)
Prad = sum(sum(U .* sin(phi_grid))) * dtheta * dphi;

% Maximum radiation intensity
U_max = max(U(:));

% Directivity
D = 4 * pi * U_max / Prad;
D_dB = 10 * log10(D);

fprintf('Directivity (linear): %.2f\n', D);
fprintf('Directivity (dB): %.2f dB\n', D_dB);

% ---------------------------
% 3D DIRECTIVITY PATTERN (dB)
% ---------------------------

% Assume your AF_mag already includes element pattern
% Compute total radiated power
dtheta = abs(theta_grid(1,2) - theta_grid(1,1));
dphi   = abs(phi_grid(2,1) - phi_grid(1,1));

% Convert spherical to solid angle weight
dOmega = sin(phi_grid) * dtheta * dphi;  % Element-wise sin(phi) * dθ * dφ
Prad = sum(sum((AF_mag_grid.^2) .* dOmega));  % Radiated power (integrated over sphere)

% Directivity = 4*pi * |E|^2 / Prad
D_linear = (4 * pi) * (AF_mag_grid.^2) ./ Prad;
D_dB = 10 * log10(D_linear);
D_dB(D_dB == -Inf | isnan(D_dB)) = -100;  % Avoid display issues

% Shift directivity magnitude to positive radius for plotting
D_shifted = D_dB - min(D_dB(:));  % Shift to positive radii

% Convert to 3D surface
[Xd, Yd, Zd] = sph2cart(theta_grid, pi/2 - phi_grid, D_shifted);

figure;
surf(Xd, Yd, Zd, D_dB, 'EdgeColor', 'none');
title('3D Directivity Pattern (dB)');
xlabel('X'); ylabel('Y'); zlabel('Z');
colorbar; axis equal; view(3);
camlight; lighting gouraud;
caxis([-40 max(D_dB(:))]);  % Adjust dynamic range


