% ===========================
% Beamforming with Real Array Factor from Measured Data (Patch Antennas)
% ===========================

clc; clear;

% ---------------------------
% CONFIGURATION
% ---------------------------
frequency = 5.8e9;
lambda = 3e8 / frequency;
element_spacing = lambda / 2;
num_elements = 4;
for i = 1:num_elements
    positions(i,:) = [(i-1)*element_spacing, 0, 0];
end
antenna_files = {'ant1.txt', 'ant2.txt', 'ant3.txt', 'ant4.txt'};
% Posiciones: arreglo lineal en eje X con separación lambda/2



% Observation direction to extract excitation (boresight)
theta0_deg = 0;  % azimuth
phi0_deg = 90;   % elevation

% Steering weights (for beamforming)
phase_shifts_deg = [0, 0, 0, 0];
weights = exp(1j * deg2rad(phase_shifts_deg));

% Calibration offset
calibration_offset_dB = 1.4516;

% ---------------------------
% LOAD ANTENNA DATA AND EXTRACT EXCITATION a_i
% ---------------------------
for i = 1:num_elements
    data = readmatrix(antenna_files{i});
    data = data(data(:,3) == frequency, :);  % Only 5.8 GHz

    az = data(:,1); % theta
    el = data(:,2); % phi
    EH = data(:,4) + 1j * data(:,5);
    EV = data(:,6) + 1j * data(:,7);

    E_total = sqrt(abs(EH).^2 + abs(EV).^2);

    ant(i).theta = az;
    ant(i).phi = el;
    ant(i).EH = EH;
    ant(i).EV = EV;
    ant(i).E = E_total;
    ant(i).position = positions(i,:);  % ← Corrección importante

    % Interpolation to find excitation at (theta0, phi0)
    theta0 = deg2rad(theta0_deg);
    phi0 = deg2rad(phi0_deg);
    a_idx = abs(az - theta0) < 1e-3 & abs(el - phi0) < 1e-3;

    if ~any(a_idx)
        error('Direction (theta0, phi0) not found in file %s', antenna_files{i});
    end

    a_i = E_total(a_idx);  % Complex excitation
    ant(i).a = a_i;

    % Normalize pattern
    ant(i).Enorm = E_total / a_i;
end

% ---------------------------
% COMPUTE ARRAY FACTOR (IDEAL)
% ---------------------------
theta = ant(1).theta;
phi = ant(1).phi;
N = length(theta);
k = 2*pi/lambda;

kx = sin(phi) .* cos(theta);
ky = sin(phi) .* sin(theta);
kz = cos(phi);

AF = zeros(N,1);
for i = 1:num_elements
    r_i = ant(i).pos;
    phase_term = exp(1j * k * (kx*r_i(1) + ky*r_i(2) + kz*r_i(3)));
    AF = AF + ant(i).a * phase_term;
end
AF_mag = abs(AF).^2;
AF_dB = 10*log10(AF_mag);

% ---------------------------
% COMPUTE REALISTIC ARRAY RADIATION PATTERN
% ---------------------------
E_array = zeros(N,1);
for i = 1:num_elements
    r_i = ant(i).pos;
    phase_term = exp(1j * k * (kx*r_i(1) + ky*r_i(2) + kz*r_i(3)));
    E_array = E_array + ant(i).a * ant(i).Enorm .* phase_term;
end

E_mag = abs(E_array).^2;
E_mag_dB = 10 * log10(E_mag) + calibration_offset_dB;
E_mag_dB(E_mag_dB == -Inf) = -100;

% ---------------------------
% RESHAPE TO GRID
% ---------------------------
[unique_theta, ~, ~] = unique(theta);
[unique_phi, ~, ~] = unique(phi);
Nphi = length(unique_phi);

theta_grid = reshape(theta, Nphi, []);
phi_grid = reshape(phi, Nphi, []);
E_mag_grid = reshape(E_mag, Nphi, []);
E_mag_dB_grid = reshape(E_mag_dB, Nphi, []);
AF_dB_grid = reshape(AF_dB, Nphi, []);

% ---------------------------
% MAXIMUM GAIN INFO
% ---------------------------
[max_gain, idx_max] = max(E_mag);
max_gain_dB = 10*log10(max_gain) + calibration_offset_dB;

fprintf('Max gain (realistic pattern): %.2f dB\n', max_gain_dB);
fprintf('At theta = %.2f deg, phi = %.2f deg\n', rad2deg(theta(idx_max)), rad2deg(phi(idx_max)));

% ---------------------------
% PLOTS
% ---------------------------
figure;
subplot(1,2,1);
imagesc(rad2deg(unique_theta), rad2deg(unique_phi), E_mag_dB_grid);
axis xy;
xlabel('\theta (deg)'); ylabel('\phi (deg)');
title('Realistic Array Radiation Pattern (dB)');
colorbar;

subplot(1,2,2);
imagesc(rad2deg(unique_theta), rad2deg(unique_phi), AF_dB_grid);
axis xy;
xlabel('\theta (deg)'); ylabel('\phi (deg)');
title('Ideal Array Factor (dB)');
colorbar;
