function plot_with_max_and_3dB(theta_deg, gain_dB, label, color)
    % === Encontrar el pico ===
    [max_val, idx_max] = max(gain_dB);
    theta_max = theta_deg(idx_max);

    % === Calcular el nivel de -3 dB ===
    level_3dB = max_val - 3;

    % === Buscar puntos de corte a -3 dB ===
    % Parte izquierda
    idx_left = find(gain_dB(1:idx_max) <= level_3dB, 1, 'last');
    % Parte derecha
    idx_right = idx_max + find(gain_dB(idx_max:end) <= level_3dB, 1, 'first') - 1;

    % Graficar la curva
    plot(theta_deg, gain_dB, color, 'DisplayName', label, 'LineWidth', 1.5); hold on;
    plot(theta_max, max_val, 'o', 'Color', color, 'MarkerFaceColor', color, ...
        'DisplayName', sprintf('Max %.2f dB at %.1f°', max_val, theta_max));

    if ~isempty(idx_left)
        plot(theta_deg(idx_left), gain_dB(idx_left), 'x', 'Color', color, ...
            'DisplayName', sprintf('-3dB Left at %.1f°', theta_deg(idx_left)));
    end
    if ~isempty(idx_right)
        plot(theta_deg(idx_right), gain_dB(idx_right), 'x', 'Color', color, ...
            'DisplayName', sprintf('-3dB Right at %.1f°', theta_deg(idx_right)));
    end
end