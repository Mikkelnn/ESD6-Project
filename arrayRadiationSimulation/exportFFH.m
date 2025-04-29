function exportFFH(filename, outname, target_freq)
    % Constante física
    eta = 377;  % Impedancia del vacío

    % Lee datos del archivo
    %data = readtable(filename);
data = readtable(filename, 'VariableNamingRule', 'preserve');

    % Filtra por frecuencia deseada
    idx = data.Frequency == target_freq;
    theta = rad2deg(data.Elevation(idx));
    phi   = rad2deg(data.Azimuth(idx));  % Suponemos azimut constante o ignorado

    % Componentes del campo eléctrico
    Re_EH = data.("EH. Real part")(idx);
    Im_EH = data.("EH. Imaginary part")(idx);
    Re_EV = data.("EV. Real part")(idx);
    Im_EV = data.("EV. Imaginary part")(idx);

    % Calcula H a partir de E (cruzado con r̂)
    % H_theta = -E_phi / eta = -EH / eta
    % H_phi   =  E_theta / eta =  EV / eta

    Re_Htheta = -Re_EH / eta;
    Im_Htheta = -Im_EH / eta;
    Re_Hphi   =  Re_EV / eta;
    Im_Hphi   =  Im_EV / eta;

    % Escribe archivo .ffh
    fid = fopen(outname, 'w');
    fprintf(fid, '$START\n');
    fprintf(fid, '$LABEL Campo H generado desde E - %s\n', filename);
    fprintf(fid, '$FREQUENCY %.0f\n', target_freq);
    fprintf(fid, '$RADIUS 1\n');
    fprintf(fid, '$COORDINATES SPHERICAL\n');
    fprintf(fid, '$FIELDS H\n');
    fprintf(fid, '$UNITS DEGREE\n');
    fprintf(fid, '$DATA\n');
    fprintf(fid, 'Theta Phi Re(Htheta) Im(Htheta) Re(Hphi) Im(Hphi)\n');

    for i = 1:length(theta)
        fprintf(fid, '%.2f %.2f %.6e %.6e %.6e %.6e\n', ...
            theta(i), phi(i), Re_Htheta(i), Im_Htheta(i), Re_Hphi(i), Im_Hphi(i));
    end

    fprintf(fid, '$END\n');
    fclose(fid);
    fprintf('Archivo .ffh exportado a: %s\n', outname);
end
