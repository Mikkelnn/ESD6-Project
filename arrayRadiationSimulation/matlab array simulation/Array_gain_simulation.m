% === Load and filter antenna measurement data ===
data = readmatrix('antFULL.txt');
frequency = 5.8e9;
data_filtered = data(data(:, 3) == frequency, :);
splitter_loss = 3.56;

% === Extract spherical coordinates and field components ===
phi = data_filtered(:, 1);      % Azimuth
theta = data_filtered(:, 2);    % Elevation
E_theta_real = data_filtered(:, 5);
E_theta_imag = data_filtered(:, 6);
E_phi_real = data_filtered(:, 7);
E_phi_imag = data_filtered(:, 8);

% === Compute field magnitudes ===
E_theta_mag = sqrt(E_theta_real.^2 + E_theta_imag.^2);
E_phi_mag = sqrt(E_phi_real.^2 + E_phi_imag.^2);
E_total_mag = sqrt(E_theta_mag.^2 + E_phi_mag.^2);

% === Convert to dB and apply calibration ===
E_total_dB = 20 * log10(E_total_mag);
E_total_dB_calibrated = E_total_dB + splitter_loss;

% === Filter values above a threshold ===
threshold_dB = -5;
valid_indices = E_total_dB_calibrated > threshold_dB;
phi = phi(valid_indices);
theta = theta(valid_indices);
gain = E_total_dB_calibrated(valid_indices);

% === 3D Radiation Pattern ===
[X, Y, Z] = sph2cart(phi, pi/2 - theta, gain);
[max_gain_dB_3D, idx_max_3D] = max(gain);

figure;
scatter3(X, Y, Z, 20, gain, 'filled');
title('3D Radiation Pattern');
xlabel('X'); ylabel('Y'); zlabel('Z');
colormap(jet);
colorbar;
caxis([0 15]);
axis equal;
view(3);
text(0, 0, max(gain), sprintf('Max Gain: %.2f dB', max_gain_dB_3D), ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', ...
    'FontSize', 12, 'FontWeight', 'bold', 'BackgroundColor', 'white');

fprintf('Maximum calibrated gain (3D): %.2f dB\n', max_gain_dB_3D);
fprintf('At θ = %.2f°, φ = %.2f°\n', rad2deg(theta(idx_max_3D)), rad2deg(phi(idx_max_3D)));


