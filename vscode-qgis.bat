@echo off
REM --- Launch VS Code with QGIS environment ---

REM Define paths
set "QGIS_ENV=C:\OSGeo4W\OSGeo4W.bat"
set "VSCODE_EXE=C:\Users\m_nee\AppData\Local\Programs\Microsoft VS Code\Code.exe"

REM Change to the directory where this .bat file is located
cd /d "%~dp0"

REM Launch VS Code in a separate clean shell to avoid environment interference
start "" "%VSCODE_EXE%" .

REM Now set up the QGIS environment in this shell (for completeness, if you use it interactively)
call "%QGIS_ENV%"
