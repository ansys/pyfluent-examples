echo off
set LOCALHOST=%COMPUTERNAME%
set KILL_CMD="C:\PROGRA~1\ANSYSI~1\v231\fluent/ntbin/win64/winkill.exe"

"C:\PROGRA~1\ANSYSI~1\v231\fluent\ntbin\win64\tell.exe" MILAKWELLS2 58731 CLEANUP_EXITING
if /i "%LOCALHOST%"=="MILAKWELLS2" (%KILL_CMD% 36152) 
if /i "%LOCALHOST%"=="MILAKWELLS2" (%KILL_CMD% 34604) 
if /i "%LOCALHOST%"=="MILAKWELLS2" (%KILL_CMD% 6304)
del "C:\Users\akwells\Documents\GitHub\pyfluent-examples\cleanup-fluent-MILAKWELLS2-34604.bat"
