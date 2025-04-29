function exportFFE(filename, outname, target_freq)
    % Lee datos del archivo
    data = readtable(filename);

    % Filtra por frecuencia
    idx = data.Frequency == target_freq;
    theta = rad2deg(data.Elevation(idx));
    phi   = rad2deg(data.Azimuth(idx));  % Suponemos que es constante (0)
    
    % Componentes del campo eléctrico
    Re_EH = data.("EH. Real part")(idx);
    Im_EH = data.("EH. Imaginary part")(idx);
    Re_EV = data.("EV. Real part")(idx);
    Im_EV = data.("EV. Imaginary part")(idx);

    % Construir archivo .ffe
    fid = fopen(outname, 'w');
    fprintf(fid, '$START\n');
    fprintf(fid, '$LABEL Exported from MATLAB - %s\n', filename);
    fprintf(fid, '$FREQUENCY %.0f\n', target_freq);
    fprintf(fid, '$RADIUS 1\n');
    fprintf(fid, '$COORDINATES SPHERICAL\n');
    fprintf(fid, '$FIELDS E\n');  % Solo campo eléctrico
    fprintf(fid, '$UNITS DEGREE\n');
    fprintf(fid, '$DATA\n');
    fprintf(fid, 'Theta Phi Re(Etheta) Im(Etheta) Re(Ephi) Im(Ephi)\n');

    for i = 1:length(theta)
        fprintf(fid, '%.2f %.2f %.6e %.6e %.6e %.6e\n', ...
            theta(i), phi(i), Re_EV(i), Im_EV(i), Re_EH(i), Im_EH(i));
    end

    fprintf(fid, '$END\n');
    fclose(fid);
    fprintf('Archivo exportado a: %s\n', outname);
end
