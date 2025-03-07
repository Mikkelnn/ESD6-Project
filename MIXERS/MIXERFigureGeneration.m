% Define time vector
t = 0:0.0001:5; % Time from 0 to 0.1 seconds with step 0.001s

% Define signals
signal1 = 0.5 * sin(2 * pi * t);          % ½sin(2πt)
signal2 = 1 * sin(2 * pi * 100 * t);      % 2sin(2π100t)
mixed_signal = signal1 + signal2;         % Sum of both signals
shifted_signal = 0.5 * sin(2 * pi * t) + 1; % ½sin(2πt) + 3
MinShift = -0.5 * sin(2 * pi * t + pi) - 1;

% Plot signals
figure;
hold on;
plot(t, mixed_signal, 'b', 'LineWidth', 1.5); % Plot sum of signals in blue
plot(t, shifted_signal, 'r', 'LineWidth', 2); % Plot shifted signal in green dashed line
%plot(t, MinShift, 'g', 'LineWidth', 2);

% Labels and title
xlabel('Time (s)');
ylabel('Amplitude');
title('Mixed Signal and Shifted Signal');
legend('Mixed signal', 'Original signal');
grid on;
hold off;
