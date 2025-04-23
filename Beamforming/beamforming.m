% MATLAB Script for Visualizing Beamforming of a 4-Element Linear Antenna Array

% Load the radiation pattern data from a CSV file
filename="C:\Users\pilvi\Documents\UNIVERSITY\ESD6\ESD6-Project\Beamforming\antena1ro30035x5_Patch_rectangular1_FarField.csv";  
data = readmatrix(filename);
% The CSV file should contain Theta (deg), Phi (deg), and Directivity(Total) (dB)
theta_data = data(:,1);  % Extract Theta values
phi_data = data(:,2);  % Extract Phi values
directivity_total_dB = data(:,9); % Extract directivity in dB

% Remove invalid data (NaN or Inf)
valid_indices = isfinite(theta_data) & isfinite(phi_data) & isfinite(directivity_total_dB);
theta_data = theta_data(valid_indices);
phi_data = phi_data(valid_indices);
directivity_total_dB = directivity_total_dB(valid_indices);

% Convert directivity from dB to linear scale
directivity_total = db2mag(directivity_total_dB);

% Define range of plotting angle
theta = 0:1:359;  % Cover full azimuth range

% Define constants
N = 4; % Number of antenna elements
c = 3e8; % Speed of light (m/s)
f = 5.8e9; % Frequency (Hz)
lambda = c / f; % Wavelength (m)
d = lambda / 2; % Element spacing (half wavelength)
k = 2 * pi / lambda; % Wavenumber

% Phase shift for beamforming (in degrees)
phase_shift_deg = input('Enter phase shift (in degrees) for beamforming: ');
phase_shift_rad = deg2rad(phase_shift_deg);

%numerator1=d*sin(phase_shift_deg);
%denominator1=lambda;

% betaSamlet=numerator1/denominator1*(180/pi)
% angleShift=mod(betaSamlet,360)


% Calculate Array Factor using the normalized formula
beta = phase_shift_rad;
psi = k * d * cosd(theta) + beta;
numerator = sin(N * psi / 2);
denominator = sin(psi / 2);
array_factor = (1 / N) * (numerator ./ denominator);
array_factor_magnitude = abs(array_factor);
array_factor_dB = 20 * log10(array_factor_magnitude);  

% Combine with Radiation Pattern
%total_pattern_dB = directivity_total + array_factor_dB;
%total_pattern_dB = array_factor_dB;

% Ensure theta_data is unique by averaging duplicate values
[theta_unique, ia, ic] = unique(theta_data); % Get unique theta values
directivity_unique = accumarray(ic, directivity_total, [], @mean); % Average duplicates

% Interpolate using the cleaned dataset
directivity_interpolated = interp1(theta_unique, directivity_unique, theta, 'linear', 'extrap');

% Compute Total Radiation Pattern: E_total = E_element * AF
total_pattern = directivity_interpolated .* array_factor_magnitude;
total_pattern_dB = mag2db(total_pattern);

% Plot in Polar Coordinates
figure;
polarplot(deg2rad(theta), db2mag(total_pattern_dB), 'LineWidth', 1.5);
title(['4-Element Linear Array Radiation Pattern with Phase Shift = ', num2str(phase_shift_deg), '°']);
rlim([0 1]);

% Uncomment below for Cartesian Plot
figure;
plot(theta, total_pattern_dB, 'LineWidth', 1.5);
xlabel('Theta (degrees)');
ylabel('Radiation Pattern (dB)');
title('Radiation Pattern in Cartesian Coordinates');
grid on;

% Plot arrayFactor 
% figure;
% polarplot(deg2rad(theta), db2mag(total_pattern_dB), 'LineWidth', 1.5);
% title(['4-Element Linear Array Radiation Pattern with Phase Shift = ', num2str(phase_shift_deg), '°']);
% rlim([0 1]);

% Additional Plot (Cartesian)
% figure;
% plot(theta, total_pattern_dB, 'b-', 'LineWidth', 1.5);
% xlabel('Theta (degrees)');
% ylabel('Radiation Pattern (dB)');
% grid on;
% title(['Radiation Pattern with Phase Shift = ', num2str(phase_shift_deg), '°']);

% 3D Plot of Raw Data
% figure;
% [ThetaGrid, PhiGrid] = meshgrid(unique(theta), unique(phi));
% DirectivityGrid = griddata(theta, phi, directivity_total, ThetaGrid, PhiGrid);
% 
% [X, Y, Z] = sph2cart(deg2rad(PhiGrid), deg2rad(90 - ThetaGrid), db2mag(DirectivityGrid));
% surf(X, Y, Z, 'EdgeColor', 'none');
% colormap jet;
% colorbar;
% xlabel('X');
% ylabel('Y');
% zlabel('Magnitude');
% title('3D Radiation Pattern of Raw Data');
% axis equal;


