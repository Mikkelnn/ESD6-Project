% ------------------------------------------
% Beamforming Simulation with Co-Pol and Cross-Pol from Measured Patterns
% ------------------------------------------

clear; clc;

%% Configuration
freq_target = 5.8e9;                    % Target frequency [Hz]
c = 3e8;
lambda = c / freq_target;
d = lambda / 2;                         % Element spacing [m]

N = 4;                                  % Number of transmitter elements
positions = [0:d:(N-1)*d; 0 0 0 0; 0 0 0 0]; % Linear array along X-axis

phases_deg = [0 0 0 0];
phases_rad = deg2rad(phases_deg);

calibration_offset_dB = 0;

files = {'ant1.txt', 'ant2.txt', 'ant3.txt', 'ant4.txt'};

E_theta_total = [];
E_phi_total = [];

for i = 1:N
    data = readmatrix(files{i}, 'NumHeaderLines', 1);
    data_5800 = data(data(:,3) == freq_target, :);

    az = data_5800(:,1);
    el = data_5800(:,2);
    phi = az; theta = el;

    if i == 1
        phi_unique = unique(phi);
        theta_unique = unique(theta);
        [Phi, Theta] = meshgrid(phi_unique, theta_unique);
        E_theta_total = zeros(size(Phi));
        E_phi_total = zeros(size(Phi));
    end

    EH_re = data_5800(:,4); EH_im = data_5800(:,5);
    EV_re = data_5800(:,6); EV_im = data_5800(:,7);

    E_theta = EH_re + 1i * EH_im;
    E_phi   = EV_re + 1i * EV_im;

    E_theta_matrix = reshape(E_theta, length(theta_unique), length(phi_unique));
    E_phi_matrix   = reshape(E_phi,   length(theta_unique), length(phi_unique));

    k = 2 * pi / lambda;
    r = positions(:,i);
    phase_shift = exp(1i * (k * (r(1)*sin(Theta).*cos(Phi) + ...
                                 r(2)*sin(Theta).*sin(Phi) + ...
                                 r(3)*cos(Theta)) + phases_rad(i)));

    E_theta_total = E_theta_total + E_theta_matrix .* phase_shift;
    E_phi_total   = E_phi_total   + E_phi_matrix   .* phase_shift;
end

%% Magnitudes  (with -6.02 dB correction applied to co-pol, cross-pol, and combined)
gain_corr_lin = 10^(-10*log10(N)/20);  % ≈ 0.5012

E_co = abs(E_theta_total) * gain_corr_lin;
E_xp = abs(E_phi_total) * gain_corr_lin;
E_combined_raw = sqrt(E_co.^2 + E_xp.^2);
E_combined = E_combined_raw;

% --- Corrected maximum gain ---
[max_val, ~] = max(E_combined(:));
max_gain_dB = 20*log10(max_val) + calibration_offset_dB;

fprintf('Array-corrected max gain: %.2f dB\n', max_gain_dB);
fprintf('--- Radiation Metrics ---\n');
fprintf('Max E-field amplitude (combined): %.3f\n', max_val);
fprintf('Calibrated Gain Estimate (combined): %.2f dB\n', max_gain_dB);



%% Polar Cuts (φ = 0°, φ = 90°, θ = 90°)     <<< REPLACE YOUR BLOCK WITH THIS

threshold_dB   = -30;
corr_lin       = 10^(-10*log10(N)/20);   % ≈ 0.5012  (−6.02 dB)

% --- helper function to convert a field slice to corrected dB with floor ---
to_dB = @(x) max( 20*log10( abs(x) * corr_lin ), threshold_dB );

% -------- φ = 0°  (θ sweep) --------
cut_phi_0            = 0;
[~, idx_phi_0]       = min(abs(rad2deg(phi_unique) - cut_phi_0));
cut_theta_co_0_dB    = to_dB(E_co(:, idx_phi_0));
cut_theta_xp_0_dB    = to_dB(E_xp(:, idx_phi_0));
cut_theta_comb_0_dB  = to_dB(E_combined(:, idx_phi_0));

% -------- φ = 90°  (θ sweep) --------
cut_phi_90           = 90;
[~, idx_phi_90]      = min(abs(rad2deg(phi_unique) - cut_phi_90));
cut_theta_co_90_dB   = to_dB(E_co(:, idx_phi_90));
cut_theta_xp_90_dB   = to_dB(E_xp(:, idx_phi_90));
cut_theta_comb_90_dB = to_dB(E_combined(:, idx_phi_90));

% -------- θ = 90°  (φ sweep) --------
cut_theta_90         = 90;
[~, idx_theta_90]    = min(abs(rad2deg(theta_unique) - cut_theta_90));
cut_phi_co_0_dB      = to_dB(E_co(idx_theta_90, :));
cut_phi_xp_0_dB      = to_dB(E_xp(idx_theta_90, :));
cut_phi_comb_0_dB    = to_dB(E_combined(idx_theta_90, :));

% --- r-axis upper limit ---
all_dB = [cut_theta_co_0_dB; cut_theta_xp_0_dB; cut_theta_comb_0_dB; ...
          cut_theta_co_90_dB; cut_theta_xp_90_dB; cut_theta_comb_90_dB; ...
          cut_phi_co_0_dB'; cut_phi_xp_0_dB'; cut_phi_comb_0_dB'];
rlim_upper = ceil(max(all_dB)/5)*5;

%% Polar plots
figure('Units','normalized','Position',[0.05 0.1 0.9 0.7]);

subplot(1,3,1);
polarplot(deg2rad(rad2deg(theta_unique)), cut_theta_co_0_dB, 'b', ...
          deg2rad(rad2deg(theta_unique)), cut_theta_xp_0_dB, 'r--', ...
          deg2rad(rad2deg(theta_unique)), cut_theta_comb_0_dB, 'k:');
title('\phi = 0°', 'FontSize', 12);
legend('Co-pol', 'Cross-pol', 'Combined', 'Location', 'southoutside');
rlim([threshold_dB rlim_upper]);

subplot(1,3,2);
polarplot(deg2rad(rad2deg(theta_unique)), cut_theta_co_90_dB, 'b', ...
          deg2rad(rad2deg(theta_unique)), cut_theta_xp_90_dB, 'r--', ...
          deg2rad(rad2deg(theta_unique)), cut_theta_comb_90_dB, 'k:');
title('\phi = 90°', 'FontSize', 12);
legend('Co-pol', 'Cross-pol', 'Combined', 'Location', 'southoutside');
rlim([threshold_dB rlim_upper]);

subplot(1,3,3);
polarplot(deg2rad(rad2deg(phi_unique)), cut_phi_co_0_dB, 'b', ...
          deg2rad(rad2deg(phi_unique)), cut_phi_xp_0_dB, 'r--', ...
          deg2rad(rad2deg(phi_unique)), cut_phi_comb_0_dB, 'k:');
title('\theta = 90°', 'FontSize', 12);
legend('Co-pol', 'Cross-pol', 'Combined', 'Location', 'southoutside');
rlim([threshold_dB rlim_upper]);

% === Refined 3D Visualization (turbo colormap, –6 dB correction) ===
interp_factor = 3;                                    % angular density
theta_fine = linspace(min(theta_unique), max(theta_unique), ...
                      length(theta_unique)*interp_factor);
phi_fine   = linspace(min(phi_unique),   max(phi_unique),   ...
                      length(phi_unique)*interp_factor);
[Phi_fine, Theta_fine] = meshgrid(phi_fine, theta_fine);

% --- Interpolate the pattern for smoothing ---
E_combined_fine = interp2(phi_unique, theta_unique, E_combined, ...
                          phi_fine, theta_fine', 'spline');

% --- Convert to dB and apply -6 dB offset ---
E_comb_dB_fine = 20*log10(abs(E_combined_fine));
E_comb_dB_fine = max(E_comb_dB_fine, -50);           % threshold floor

% --- Cartesian coordinates for scatter3 ---
[X_fine, Y_fine, Z_fine] = sph2cart(Phi_fine, pi/2 - Theta_fine, ...
                                    abs(E_combined_fine));

% gain peak
[max_gain_comb_dB, idx_max] = max(E_comb_dB_fine(:));
[row_max, col_max] = ind2sub(size(E_comb_dB_fine), idx_max);
theta_max = theta_fine(row_max);
phi_max   = phi_fine(col_max);

% --- 3D plot ---
figure('Name','3D Combined Pattern (turbo, -6 dB)','Color','w');
scatter3(X_fine(:), Y_fine(:), Z_fine(:), 12, E_comb_dB_fine(:), 'filled');
colormap(turbo);                                     % red = maximum
caxis([max(E_comb_dB_fine(:))-40, max(E_comb_dB_fine(:))]); % 40 dB dynamic range
colorbar;
axis equal;
view(45,30);
xlabel('X'); ylabel('Y'); zlabel('Z');
title('3D Radiation Pattern - Combined (Interpolated, -6 dB applied)', ...
      'FontSize', 14);

text(0, 0, max(abs(E_combined_fine(:))), ...
     sprintf('Max Gain: %.2f dB', max_gain_comb_dB), ...
     'HorizontalAlignment','center','VerticalAlignment','bottom', ...
     'FontSize',12,'FontWeight','bold','BackgroundColor','white');

%fprintf('\n--- 3D Radiation Peak (with -6 dB correction) ---\n');
%fprintf('Max Gain: %.2f dB\n', max_gain_comb_dB);
%fprintf('At θ = %.2f°, φ = %.2f°\n', rad2deg(theta_max), rad2deg(phi_max));
