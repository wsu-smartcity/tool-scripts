function [ timestamp_sec_ary ] = parse_timestamp( time_raw_data )
%PARSE_TIMESTAMP Summary of this function goes here
%   Detailed explanation goes here

    SHORT_TIMESTAMP_LEN = 23;
    LONG_TIMESTAMP_FORMAT_STR = 'yyyy-mm-dd HH:MM:SS.FFF';
    SHORT_TIMESTAMP_FORMAT_STR = 'yyyy-mm-dd HH:MM:SS';
    DAT_TO_SEC = 1*24*60*60;
    
    time_str_len_ary=cellfun(@length, time_raw_data);
    
    time_raw_data_len_mask = time_str_len_ary > SHORT_TIMESTAMP_LEN;
    timestamp_sec_ary = zeros(size(time_raw_data));

    if (any(time_raw_data_len_mask))
        timestamp_sec_ary(time_raw_data_len_mask) = datenum(time_raw_data(time_raw_data_len_mask), LONG_TIMESTAMP_FORMAT_STR);
    end

    if (any(~time_raw_data_len_mask))
        timestamp_sec_ary(~time_raw_data_len_mask) = datenum(time_raw_data(~time_raw_data_len_mask), SHORT_TIMESTAMP_FORMAT_STR);
    end

    timestamp_sec_ary = (timestamp_sec_ary - timestamp_sec_ary(1))*DAT_TO_SEC; % convert from "day" to "sec"

end

