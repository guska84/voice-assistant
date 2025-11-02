@echo off
setlocal enabledelayedexpansion

echo ============================================
echo Voice Assistant Installer
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed!
    echo.
    echo Please choose an option:
    echo 1. Download and install Python automatically
    echo 2. Exit and install Python manually from python.org
    echo.
    set /p choice="Enter your choice (1 or 2): "
    
    if "!choice!"=="1" (
        call :install_python
    ) else (
        echo.
        echo Please install Python 3.8 or higher from https://www.python.org/downloads/
        echo Make sure to check "Add Python to PATH" during installation
        pause
        exit /b 1
    )
) else (
    echo Python is already installed
    python --version
)

echo.
echo ============================================
echo Installing Dependencies...
echo ============================================
echo.

:: Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: Install core dependencies
echo.
echo Installing core packages...
python -m pip install SpeechRecognition pyttsx3 requests

:: Install PyAudio (can be tricky on Windows)
echo.
echo Installing PyAudio...
python -m pip install pyaudio
if %errorlevel% neq 0 (
    echo.
    echo PyAudio installation failed. Trying alternative method...
    python -m pip install pipwin
    pipwin install pyaudio
    if %errorlevel% neq 0 (
        echo.
        echo WARNING: PyAudio installation failed.
        echo The voice assistant will still work, but microphone input may not function.
        echo You may need to install PyAudio manually.
        echo.
    )
)

:: Install optional dependencies
echo.
echo Installing optional packages for better audio support...
python -m pip install pydub
if %errorlevel% neq 0 (
    echo pydub installation failed - continuing without it
)

echo.
echo ============================================
echo Creating Launcher...
echo ============================================
echo.

:: Create launcher script
(
echo @echo off
echo cd /d "%%~dp0"
echo python voice-assistant.py
echo if %%errorlevel%% neq 0 ^(
echo     echo.
echo     echo Error running Voice Assistant!
echo     echo Press any key to exit...
echo     pause ^>nul
echo ^)
) > launch.bat

echo Launcher created: launch.bat

:: Create desktop shortcut (optional)
echo.
set /p create_shortcut="Create desktop shortcut? (y/n): "
if /i "!create_shortcut!"=="y" (
    call :create_shortcut
)

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo You can now run the Voice Assistant by:
echo   - Double-clicking launch.bat
echo   - Or running: python voice-assistant.py
echo.
if /i "!create_shortcut!"=="y" (
    echo A desktop shortcut has also been created.
    echo.
)
echo Press any key to exit...
pause >nul
exit /b 0

:install_python
echo.
echo Downloading Python installer...
echo.

:: Download Python installer
set PYTHON_VERSION=3.11.7
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set INSTALLER=python_installer.exe

powershell -Command "& {Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER%'}"

if not exist %INSTALLER% (
    echo Failed to download Python installer
    echo Please install Python manually from python.org
    pause
    exit /b 1
)

echo.
echo Installing Python...
echo Please wait, this may take a few minutes...
echo.

:: Install Python silently with PATH
%INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Wait for installation
timeout /t 10 /nobreak >nul

:: Clean up
del %INSTALLER%

:: Refresh environment variables
call refreshenv.cmd >nul 2>&1

:: Verify installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python installation may have failed.
    echo Please restart your computer and run this installer again.
    echo If the problem persists, install Python manually from python.org
    pause
    exit /b 1
)

echo Python installed successfully!
goto :eof

:create_shortcut
echo Creating desktop shortcut...

set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Voice Assistant.lnk

:: Use PowerShell to create shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%SCRIPT_DIR%launch.bat'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'Voice Assistant'; $Shortcut.Save()"

if exist "%SHORTCUT_PATH%" (
    echo Desktop shortcut created successfully!
) else (
    echo Failed to create desktop shortcut
)
goto :eof
