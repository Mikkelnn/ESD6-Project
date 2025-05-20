data = readmatrix('antFULL.txt');
frequency = 5.8e9;
data_filtered = data(data(:, 3) == frequency, :);
splitter_loss = 3.56;

phi = data_filtered(:, 1);      % Azimuth
theta = data_filtered(:, 2);    % Elevation
E_theta_real = data_filtered(:, 5);
E_theta_imag = data_filtered(:, 6);
E_phi_real = data_filtered(:, 7);
E_phi_imag = data_filtered(:, 8);

E_theta_dB = 20*log10(sqrt(E_theta_real.^2 + E_theta_imag.^2)) + splitter_loss;
E_phi_dB   = 20*log10(sqrt(E_phi_real.^2 + E_phi_imag.^2)) + splitter_loss;

% === Corte φ = 0° ===
tolerance = deg2rad(1);
phi0_idx = abs(phi - deg2rad(0)) < tolerance;
theta0 = rad2deg(theta(phi0_idx));
EH0 = E_theta_dB(phi0_idx);
EV0 = E_phi_dB(phi0_idx);
[theta0, i0] = sort(theta0); EH0 = EH0(i0); EV0 = EV0(i0);

figure;
plot_with_max_and_3dB(theta0, EH0, '0° 5800 MHz EH', 'r');
plot_with_max_and_3dB(theta0, EV0, '0° 5800 MHz EV', 'b');
title('[Gain] Elevation cut φ = 0°');
xlabel('Elevation (°)'); ylabel('Electric Field Magnitude (dB)');
grid on; legend('Location', 'best');

% === Corte φ = 90° ===
phi90_idx = abs(phi - deg2rad(90)) < tolerance;
theta90 = rad2deg(theta(phi90_idx));
EH90 = E_theta_dB(phi90_idx);
EV90 = E_phi_dB(phi90_idx);
[theta90, i90] = sort(theta90); EH90 = EH90(i90); EV90 = EV90(i90);

figure;
plot_with_max_and_3dB(theta90, EH90, '90° 5800 MHz EH', 'r');
plot_with_max_and_3dB(theta90, EV90, '90° 5800 MHz EV', 'b');
title('[Gain] Elevation cut φ = 90°');
xlabel('Elevation (°)'); ylabel('Electric Field Magnitude (dB)');
grid on; legend('Location', 'best');
