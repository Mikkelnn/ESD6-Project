% Given constants
f_0 = 5.6e9; % Design frequency (mid-point of Bluetooth range), in Hz
c = 3e8; % Speed of light, m/s
epsilon_r = 3; % Dielectric constant for PP
h = 1.6e-3; % Substrate thickness, in meters
Z_0 = 50; % Desired impedance, in ohms
lambda=c/f_0;

% Step 1: Calculate the width W of the patch
W = (c / (2 * f_0)) * sqrt(2 / (epsilon_r + 1));


% Step 2: Calculate the effective dielectric constant (epsilon_eff)
epsilon_eff = (epsilon_r + 1) / 2 + (epsilon_r - 1) / 2* (1 + 12 * h / W)^(-0.5);

% Step 3: Calculate the effective length L_eff
L_eff = c / (2 * f_0 * sqrt(epsilon_eff));


% Step 4: Calculate the length extension (Delta L)
delta_L = h * 0.412 * ((epsilon_eff + 0.3) * (W / h + 0.264)) / ((epsilon_eff - 0.258) * (W / h + 0.8));

% Step 5: Calculate the actual length L
L = L_eff - 2 * delta_L;

Z_edge = 90*((epsilon_r^2)/(epsilon_r-1))*L/W;% Impedance at edge, in ohms

% Step 6: Calculate the position for 50 Ohm impedance
x = (L / pi) * acos(sqrt(Z_0 / Z_edge));

% Step 7: Calculate the width of the stripline
nepa_0 = 120*pi;
W_strip = (nepa_0*h)/(Z_0*sqrt(epsilon_r));

% Display the results
fprintf('Patch width (W): %.2f mm\n', W * 1e3);
fprintf('Effective dielectric constant (epsilon_eff): %.2f\n', epsilon_eff);
fprintf('Patch length (L): %.2f mm\n', L * 1e3);
fprintf('Position for 50 Ohm impedance (x): %.2f mm\n', x * 1e3);
fprintf('Width of the stripline: %.2f mm\n', W_strip * 1e3);

% Microstrip width calculation for 50 Ohms - iterative method
W_0 = 1e-3; % Initial guess for W_0 (in meters)
tolerance = 1e-6; % Tolerance for the solution
Z_0_target = 50; % Target impedance

for iteration = 1:1000
    Z_0_calc = (60 / sqrt(epsilon_eff)) * log((8 * h / W_0) + (W_0 / (4 * h)));
    if abs(Z_0_calc - Z_0_target) < tolerance
        break;
    end
    W_0 = W_0 - 1e-5 * (Z_0_calc - Z_0_target); % Adjust W_0 based on the error
end

fprintf('Microstrip width for 50 Ohms (W_0): %.2f mm\n', W_0 * 1e3);

% Define dielectric substrate
substrate = dielectric('Name', 'PP', 'EpsilonR', epsilon_r, 'Thickness', h);

% Define inset-fed patch antenna
patch = patchMicrostripInsetfed(...
    'Length', L, ...
    'Width', W, ...
    'Substrate', substrate, ...
    'GroundPlaneLength', 1.5 * L, ...
    'GroundPlaneWidth', 1.5 * W, ...

    'FeedOffset', [-x, 0]); % Inset feed location for 50Ω matching

% Plot the 3D radiation pattern
figure;
pattern(patch, f_0);
title('3D Radiation Pattern of the Inset-Fed Patch Antenna');

% Display impedance over a frequency range
figure;
impedance(patch, linspace(0.8*f_0, 1.2*f_0, 101)); % Sweep from 80% to 120% of f_0
title('Impedance of the Inset-Fed Patch Antenna');