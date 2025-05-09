% ===========================
% Simple Array Factor with Beamsteering (1 Antenna, Ideal AF)
% ===========================

clc; clear;

% ---------------------------
% CONFIGURATION
% ---------------------------
frequency = 5.8e9;               % Operating frequency
lambda = 3e8 / frequency;        % Wavelength
k = 2 * pi / lambda;             % Wave number
element_spacing = lambda / 2;    % Uniform spacing
num_elements = 4;                % Number of elements
calibration_offset_dB = 1.4516;  % Calibration offset

% ---------------------------
% BEAMSTEERING CONFIGURATION
% ---------------------------
steering_angle_deg = -10;  % Beam points to this azimuth angle
steering_angle_rad = deg2rad(steering_angle_deg);

% Phase shift per element for steering
phase_shifts = k * element_spacing * sin(steering_angle_rad);
weights = exp(1j * (0:num_elements-1) * phase_shifts);

% ---------------------------
% IDEAL ARRAY FACTOR CALCULATION
% ---------------------------
theta_deg = linspace(-180, 180, 1000);   % Azimuth sweep
theta_rad = deg2rad(theta_deg);

AF_array = zeros(size(theta_rad));
for n = 0:num_elements-1
    AF_array = AF_array + weights(n+1) .* exp(1j * n * k * element_spacing * sin(theta_rad));
end

AF_array_mag = abs(AF_array);
AF_array_mag = AF_array_mag.^2;  % Power
AF_array_dB = 10 * log10(AF_array_mag / max(AF_array_mag)) + calibration_offset_dB;

% ---------------------------
% OUTPUT RESULTS
% ---------------------------
[max_gain, idx_max] = max(AF_array_mag);
max_gain_dB = 10 * log10(max_gain) + calibration_offset_dB;
fprintf('Beamsteering to θ = %.1f°\n', steering_angle_deg);
fprintf('Maximum array factor gain: %.2f dB\n', max_gain_dB);
fprintf('Actual peak at θ = %.2f°\n', theta_deg(idx_max));

% ---------------------------
% PLOT
% ---------------------------
figure;
plot(theta_deg, AF_array_dB, 'LineWidth', 2);
xlabel('Azimuth angle θ (degrees)');
ylabel('Array Factor Gain (dB)');
title(sprintf('Ideal Array Factor (Steered to %.0f°)', steering_angle_deg));
grid on;
ylim([-40 5]);
xlim([-180 180]);
