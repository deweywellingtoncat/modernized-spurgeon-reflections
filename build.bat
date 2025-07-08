REM filepath: c:\Spurgeon\github_repo\build.bat
@echo off
echo Building Spurgeon Reflections GUI...
pyinstaller --onefile --windowed --noupx --name "SpurgeonReflections" --add-data "Spurgeon_Complete.txt;." spurgeon_gui.py
echo.
echo Build complete! Executable is in dist\SpurgeonReflections.exe
pause