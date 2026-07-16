@echo off
cd /d "%~dp0"

echo Dang khoi dong CutCut...
echo Vui long doi giay lat, trinh duyet se tu dong mo.

:: Create a temporary VBS script to run python silently
echo Set WshShell = CreateObject("WScript.Shell") > run_silent.vbs
echo WshShell.Run "python app.py", 0, False >> run_silent.vbs

:: Run the script
cscript //nologo run_silent.vbs
del run_silent.vbs

:: Open browser
timeout /t 2 /nobreak >nul
start http://localhost:5000

exit
