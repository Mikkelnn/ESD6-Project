% Given constants
f_0 = 5.8e9; % Design frequency (mid-point of Bluetooth range), in Hz
c = 3e8; % Speed of light, m/s
epsilon_r = 3; % Dielectric constant for PP
h = 1.524e-3; % Substrate thickness, in meters
Z_0 = 50; % Desired impedance, in ohms

% Step 1: Calculate the width W of the patch
W = (c / (2 * f_0)) * sqrt(2 / (epsilon_r + 1));

% Step 2: Calculate the effective dielectric constant (epsilon_eff)
epsilon_eff = (epsilon_r + 1)/2 + (epsilon_r - 1)/2 * (1 + 12 * h / W)^(-0.5);

% Step 3: Calculate the effective length L_eff
L_eff = c / (2 * f_0 * sqrt(epsilon_eff));

% Step 4: Calculate the length extension (Delta L)
delta_L = h * 0.412 * ((epsilon_eff + 0.3) * (W / h + 0.264)) / ((epsilon_eff - 0.258) * (W / h + 0.8));

% Step 5: Calculate the actual length L
L = L_eff - 2 * delta_L;

% Step 6: Calculate the impedance at the edge of the patch
Z_edge = 90*((epsilon_r^2)/(epsilon_r-1))*L/W;% Impedance at edge, in ohms
% Step 7: Calculate the position for 50 Ohm impedance
if Z_0 > Z_edge
    error('Z_0 is greater than Z_edge, impossible to find a valid feed position.');
end

x = (L / pi) * acos(sqrt(Z_0 / Z_edge)); % Position from the edge

% Display results
fprintf('Patch Width (W): %.3f mm\n', W * 1e3);
fprintf('Effective Dielectric Constant (epsilon_eff): %.3f\n', epsilon_eff);
fprintf('Patch Length (L): %.3f mm\n', L * 1e3);
fprintf('Impedance at Edge (Z_edge): %.2f Ohms\n', Z_edge);
fprintf('Optimal Feed Position (x): %.3f mm\n', x * 1e3);
