
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
    % Only keep the rows for desired frequency (e.g., 5.8 GHz)
    freq_mask = data(:,3) == frequency;
    data = data(freq_mask, :);
    
    azimuth = data(:,1);          % Theta (Azimuth)
    elevation = data(:,2);        % Phi (Elevation)
    EH = data(:,4) + 1j*data(:,5); 
    EV = data(:,6) + 1j*data(:,7); 
    E_total = sqrt(abs(EH).^2 + abs(EV).^2);
    
    % Store positions and fields
    ant(i).azimuth = azimuth;
    ant(i).elevation = elevation;
    ant(i).E = E_total;
    ant(i).position = [(i-1)*element_spacing, 0, 0];  % Linear x-axis array
end

% ---------------------------
% BEAMFORMING CALCULATION
% ---------------------------
% Assume common theta/phi grid
theta = ant(1).azimuth;
phi = ant(1).elevation;
num_points = length(theta);
AF = zeros(num_points, 1);

for i = 1:num_elements
    % Convert spherical to Cartesian unit vectors
    kx = sin(phi) .* cos(theta);
    ky = sin(phi) .* sin(theta);
    kz = cos(phi);
    
    pos = ant(i).position;
    phase_shift = exp(1j * 2*pi/lambda * (kx*pos(1) + ky*pos(2) + kz*pos(3)));
    AF = AF + weights(i) * ant(i).E .* phase_shift;
end

AF_mag = abs(AF);
AF_norm = AF_mag / max(AF_mag); % Normalize
AF_dB = 20*log10(AF_norm);

% ---------------------------
% RESHAPE GRID AUTOMATICALLY
% ---------------------------
[unique_theta, ~, idx_theta] = unique(theta);
[unique_phi, ~, idx_phi] = unique(phi);

try
    theta_grid = reshape(theta, length(unique_phi), []);
    phi_grid = reshape(phi, length(unique_phi), []);
    AF_norm_grid = reshape(AF_norm, length(unique_phi), []);
    AF_mag_grid = reshape(AF_mag, length(unique_phi), []);
catch
    error('Could not reshape. The angular sampling is likely not uniform or rectangular.');
end

% ---------------------------
% PLOT 3D NORMALIZED RADIATION PATTERN
% ---------------------------
[X,Y,Z] = sph2cart(theta_grid, pi/2 - phi_grid, AF_norm_grid);

figure;
surf(X, Y, Z, AF_norm_grid, 'EdgeColor', 'none');
title('3D Normalized Radiation Pattern');
xlabel('X'); ylabel('Y'); zlabel('Z');
colorbar; axis equal; view(3);
camlight; lighting gouraud;

% ---------------------------
% PLOT POLAR CUTS
% ---------------------------
figure;
subplot(1,2,1);
cut_phi = 0;  % phi = 0
mask_phi = abs(phi_grid(:,1) - deg2rad(cut_phi)) < 1e-3;
polarplot(unique_theta, AF_norm_grid(mask_phi,:)');
title('Polar Plot at \phi = 0');

subplot(1,2,2);
cut_theta = 0;  % theta = 0
mask_theta = abs(theta_grid(1,:) - deg2rad(cut_theta)) < 1e-3;
polarplot(unique_phi, AF_norm_grid(:,mask_theta));
title('Polar Plot at \theta = 0');

% ---------------------------
% MAXIMUM GAIN (NOT NORMALIZED)
% ---------------------------
[max_gain, idx_max] = max(AF_mag);
fprintf('Maximum unnormalized gain: %.4f\n', max_gain);
fprintf('At theta = %.2f deg, phi = %.2f deg\n', ...
        rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));

% Plot unnormalized 3D pattern
[X2,Y2,Z2] = sph2cart(theta_grid, pi/2 - phi_grid, AF_mag_grid);
figure;
surf(X2, Y2, Z2, AF_mag_grid, 'EdgeColor', 'none');
title('3D Unnormalized Radiation Pattern');
xlabel('X'); ylabel('Y'); zlabel('Z');
colorbar; axis equal; view(3);
camlight; lighting gouraud;
