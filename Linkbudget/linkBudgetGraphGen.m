clc; clear; close all;

% Given parameters
Pt = 5;             % Transmitted power (W)
G = 13;               % Antenna gain (linear)
k = 1.38e-23;         % Boltzmann's constant (J/K)
T0 = 290;             % Standard temperature (K)
B = 10e6;              % Bandwidth (Hz)
SNR0 = 10e5;            % Required SNR (linear)

% Debris sizes (L) in meters
L_values = [1, 2.5, 5, 7.5, 10] * 1e-2; % Convert cm to meters

% Wavelengths for given frequencies
freq_values = [5.8e9, 10e9, 32e9, 70e9]; % Frequencies in Hz
lambda_values = 3e8 ./ freq_values; % Convert to meters

% Logarithmic range of noise figure F
F = logspace(-15, -5, 100); % 100 points from 10^-15 to 10^-5

% Colors for different lambda values
colors = lines(length(lambda_values));

% Generate plots for each debris size L
for idx = 1:length(L_values)
    L = L_values(idx);
    
    figure; hold on; grid on;
    title(sprintf('R_{max} vs Noise Figure (L = %.1f cm)', L*100));
    xlabel('Noise Figure F (log scale)');
    ylabel('R_{max} (m)');
    set(gca, 'XScale', 'log'); % Set x-axis to log scale
    
    for j = 1:length(lambda_values)
        lambda = lambda_values(j);
        
        % Compute sigma using the given formula
        sigma = (12 * pi * L^4) / lambda^2;
        
        % Compute R_max using the given formula
        R_max = ((Pt * G^2 * lambda^2 * sigma) ./ ((4 * pi)^3 * k * T0 * B * SNR0 .* F)).^(1/4);
        
        % Plot results
        plot(F, R_max, 'Color', colors(j, :), 'LineWidth', 2, ...
            'DisplayName', sprintf('\\lambda = %.1f GHz', freq_values(j)/1e9));
    end
    
    legend('show', 'Location', 'best');
end
