% === Load and filter antenna measurement data ===
data = readmatrix('antFULL.txt');
frequency = 5.8e9;
data_filtered = data(data(:, 3) == frequency, :);

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
E_total_dB_calibrated = E_total_dB + 1.4516 + 5.65;

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

% === 2D Cut: φ = 90° (pi/2 rad), varying θ ===
phi_90_indices = abs(phi - pi/2) < 1e-3;
theta_phi_90 = theta(phi_90_indices);
gain_phi_90 = gain(phi_90_indices);

[max_gain_phi_90, idx_max_phi_90] = max(gain_phi_90);
theta_max_gain_phi_90 = theta_phi_90(idx_max_phi_90);
fprintf('Max gain for φ = 90°: %.2f dB at θ = %.2f°\n', ...
    max_gain_phi_90, rad2deg(theta_max_gain_phi_90));

figure;
polarplot(theta_phi_90, gain_phi_90, 'b-');
title('2D Cut for φ = 90° (Variation in θ)');
rlim([-5 15]);
grid on;

% === 2D Cut: θ = 0° (0 rad), varying φ ===
theta_0_indices = abs(theta) < 1e-3;
phi_theta_0 = phi(theta_0_indices);
gain_theta_0 = gain(theta_0_indices);

[max_gain_theta_0, idx_max_theta_0] = max(gain_theta_0);
phi_max_gain_theta_0 = phi_theta_0(idx_max_theta_0);
fprintf('Max gain for θ = 0°: %.2f dB at φ = %.2f°\n', ...
    max_gain_theta_0, rad2deg(phi_max_gain_theta_0));

figure;
polarplot(phi_theta_0, gain_theta_0, 'r-');
title('2D Cut for θ = 0° (Variation in φ)');
rlim([-5 15]);
grid on;

