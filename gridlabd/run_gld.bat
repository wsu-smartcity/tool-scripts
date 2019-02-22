@echo off

:: Config Params
set gld_bin_path=D:\GridLAB-D\bin
set mgw_bin_path=C:\msys32\mingw64\bin

set gld_lib_glpath=D:\GridLAB-D\lib\gridlabd
set gld_share_glpath=D:\GridLAB-D\share\gridlabd

:: Start [Note that setx does changes permanently]
if exist %gld_bin_path% (
	SET PATH=%PATH%;%gld_bin_path%;
) else (
	echo PATH %gld_bin_path% does not exist!
	pause
)

if exist %mgw_bin_path% (
	SET PATH=%PATH%;%mgw_bin_path%;
) else (
	echo PATH %mgw_bin_path% does not exist!
	pause
)

SET GLPATH=%gld_lib_glpath%;%gld_share_glpath%

:: Run and Open the CMD Window
start cmd