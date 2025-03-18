clc; clear; close all;

% Given parameters
B = 10e6; % Bandwidth in Hz
Pt = 5; % Transmit power in W
G_dBi = 6.8; % Gain in dBi
G = 10^(G_dBi/10); % Convert dBi to linear scale
k = 1.38e-23; % Boltzmann constant
T0 = 290; % Standard temperature in Kelvin
F_dB = 6.5; % Noise figure in dB
F = 10^(F_dB/10); % Convert dB to linear scale

% Define variable ranges
lambda = [3e8/5.8e9, 3e8/10e9, 3e8/32e9, 3e8/70e9]; % Convert GHz to meters
sigma_vals = [3.47e-6, 1.38e-4, 2.17e-3, 0.011, 0.035];
SNRo_vals = logspace(-2, 2, 100); % SNR0 range in linear scale
SNRo_dB = 10 * log10(SNRo_vals);  % Convert SNR0 to dB

% Plot for each sigma
for s_idx = 1:length(sigma_vals)
    sigma = sigma_vals(s_idx);
    figure;
    hold on;
    
    % Loop through each lambda
    for l_idx = 1:length(lambda)
        lam = lambda(l_idx);
        
        % Calculate Rmax for each SNRo
        Rmax = ((Pt * G^2 * lam^2 * sigma) ./ ((4 * pi)^3 * k * T0 * B * SNRo_vals * F)).^(1/4);
        
        % Plot each lambda case
        plot(Rmax, SNRo_dB, 'LineWidth', 2, 'DisplayName', sprintf('\\lambda = %.1f GHz', 3e8/lam * 1e-9));
    end
    
    % Formatting the plot
    set(gca, 'XScale', 'log'); % Log scale for Rmax
    xlabel('R_{max} [m]');
    ylabel('SNR_0 [dB]');
    title(sprintf('\\sigma = %.2e', sigma));
    legend('show', 'Location', 'Best');
    grid on;
end
