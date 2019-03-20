%============================
% @Author: Jing Xie
% @Email: xjasura@gmail.com
% @Date: 2019-3-20
% @Func: Parse and plot the data recorded by the group_recorder in GridLAB-D
%============================

clc
clear all
close all

format short g

%% Params
lds_volts_csv_fns = {'loads_volts_A.csv','loads_volts_B.csv','loads_volts_C.csv'};
nominal_vol = 2401; %Unit: V

%% Parse the voltages (Phase A, B, and C) of all loads, together with timestamps
for cur_ite = 1:numel(lds_volts_csv_fns)
    %==Parse voltages & timestamps
    cur_csv_filename = lds_volts_csv_fns{cur_ite};
    [cur_lds_volts_mat, time_raw_data] = parse_loads_voltages(cur_csv_filename, nominal_vol);
    
    %==Parse timestamp
    timestamp_sec_ary = parse_timestamp(time_raw_data);

    %==Plot
    figure()
    plot(timestamp_sec_ary, cur_lds_volts_mat)
    title(strrep(lds_volts_csv_fns{cur_ite}, '_', '-'))
end
