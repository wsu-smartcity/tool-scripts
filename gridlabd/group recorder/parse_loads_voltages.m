function [ cur_lds_volts_mat, time_raw_data ] = parse_loads_voltages( csv_filename, nominal_vol )
%PARSE_VOLTAGES Summary of this function goes here
%   Detailed explanation goes here

    %--open csv file
    cur_fh = fopen(csv_filename, 'rt');
    
    %--volts
    lds_names = textscan(cur_fh, '%s', 1, 'HeaderLines', 9-1, 'Delimiter', '\n');
    lds_names_cell = strsplit(lds_names{:}{:}, ',');
    cur_format_str = ['%s', repmat(' %f', 1, numel(lds_names_cell)-1)];
    cur_raw_data = textscan(cur_fh, cur_format_str, 'Delimiter', ',');
    
    cur_lds_volts_mat = abs(cell2mat(cur_raw_data(2:end)))/nominal_vol;
    
    %--time
    time_raw_data = cur_raw_data{1};
    
    %--close csv file
    fclose(cur_fh);

end

