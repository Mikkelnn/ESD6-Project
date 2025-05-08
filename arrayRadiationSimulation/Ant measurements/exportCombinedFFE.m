function exportCombinedFFE(filename, outname, target_freq)
    % Read original data
    data = readtable(filename, 'VariableNamingRule', 'preserve');

    % Filter for selected frequency
    idx = data.Frequency == target_freq;

    % Convert angles to degrees and wrap between 0 and 360
    theta = mod(rad2deg(data.Elevation(idx)), 360);
    phi   = mod(rad2deg(data.Azimuth(idx)), 360);

    % Extract field components
    Re_Etheta = data.("ETheta. Real part")(idx);
    Im_Etheta = data.("ETheta. Imaginary part")(idx);
    Re_Ephi   = data.("EPhi. Real part")(idx);
    Im_Ephi   = data.("EPhi. Imaginary part")(idx);

    % Open output file with ASCII encoding
    fid = fopen(outname, 'w', 'n', 'US-ASCII');

    % File format 8 headers (strictly formatted)
    fprintf(fid, '##File Type: Far Field\r\n');
    fprintf(fid, '##File Format: 8\r\n');
    fprintf(fid, '##Source: %s\r\n', filename);
    fprintf(fid, '** File exported by MATLAB script\r\n\r\n');

    % Configuration header block
    fprintf(fid, '#Configuration Name: StandardConfiguration1\r\n');
    fprintf(fid, '#Request Name: FarField1\r\n');
    fprintf(fid, '#Frequency: %.6e\r\n', target_freq);
    fprintf(fid, '#Coordinate System: Spherical\r\n');
    fprintf(fid, '#Result Type: EField\r\n');
    fprintf(fid, '#Radius: 1.0\r\n');
    fprintf(fid, '#No. of Header Lines: 1\r\n');
    fprintf(fid, ['#    "Theta"    "Phi"    "Re(Etheta)"    "Im(Etheta)" ', ...
                  '"Re(Ephi)"    "Im(Ephi)"\r\n']);

    % Write the data rows
    for i = 1:length(theta)
        fprintf(fid, '%8.2f %8.2f %+e %+e %+e %+e\r\n', ...
            theta(i), phi(i), Re_Etheta(i), Im_Etheta(i), Re_Ephi(i), Im_Ephi(i));
    end

    fclose(fid);
    fprintf('✅ Archivo .ffe exportado: %s\n', outname);
end
