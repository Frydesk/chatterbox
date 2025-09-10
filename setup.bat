@echo off
setlocal enabledelayedexpansion
echo ========================================
echo   Chatterbox TTS WebSocket API Setup
echo   Python 3.11 + UV (Best Versions)
echo ========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo uv is not installed. Please install uv first:
    echo curl -LsSf https://astral.sh/uv/install.bat | cmd
    pause
    exit /b 1
)

REM Check if Python 3.11+ is available (try multiple paths)
set PYTHON_CMD=

echo Searching for Python 3.11+ installations...

REM Try Python 3.11 specifically
echo Trying py -3.11...
py -3.11 --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3.11
    goto :python_found
)

REM Try Microsoft Store Python with specific paths
echo Trying Microsoft Store Python paths...

REM Try different Microsoft Store Python paths
"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto :check_version
)

"%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe" --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe"
    goto :check_version
)

REM Try Python 3.11 in Microsoft Store Apps
"%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe" --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe"
    goto :python_found
)

REM Try python3.11.exe directly
"%LOCALAPPDATA%\Microsoft\WindowsApps\python3.11.exe" --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python3.11.exe"
    goto :python_found
)

REM Try Python 3.12 in Microsoft Store Apps
"%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe" --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe"
    goto :python_found
)

REM Try python3.12.exe directly
"%LOCALAPPDATA%\Microsoft\WindowsApps\python3.12.exe" --version >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python3.12.exe"
    goto :python_found
)

REM Try to find Python in Microsoft Store Apps directory
echo Searching Microsoft Store Apps directory...
for /d %%i in ("%LOCALAPPDATA%\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.*") do (
    echo Found Python directory: %%i
    "%%i\python.exe" --version >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        echo Testing version in: %%i
        "%%i\python.exe" --version | findstr "3.11" >nul
        if !ERRORLEVEL! EQU 0 (
            set PYTHON_CMD="%%i\python.exe"
            goto :python_found
        )
        "%%i\python.exe" --version | findstr "3.12" >nul
        if !ERRORLEVEL! EQU 0 (
            set PYTHON_CMD="%%i\python.exe"
            goto :python_found
        )
        "%%i\python.exe" --version | findstr "3.13" >nul
        if !ERRORLEVEL! EQU 0 (
            set PYTHON_CMD="%%i\python.exe"
            goto :python_found
        )
    )
)

goto :python_not_found

:check_version
%PYTHON_CMD% --version | findstr "3.11" >nul
if %ERRORLEVEL% EQU 0 goto :python_found
%PYTHON_CMD% --version | findstr "3.12" >nul
if %ERRORLEVEL% EQU 0 goto :python_found
%PYTHON_CMD% --version | findstr "3.13" >nul
if %ERRORLEVEL% EQU 0 goto :python_found

:python_not_found

echo Python 3.11+ is not found in any of the expected locations.
echo.
echo Debugging information:
echo Checking what Python installations are available...
echo.

REM Show what py command finds
echo Available Python versions via 'py' command:
py --list 2>nul
echo.

REM Show what's in Microsoft Store Apps directory
echo Checking Microsoft Store Apps directory:
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\" (
    dir "%LOCALAPPDATA%\Microsoft\WindowsApps\Python*" /b 2>nul
) else (
    echo Microsoft Store Apps directory not found
)
echo.

echo Please install Python 3.11 or higher:
echo 1. Microsoft Store: Search for "Python 3.11" or "Python 3.12"
echo 2. Or download from: https://www.python.org/downloads/
echo 3. Make sure to check "Add Python to PATH" during installation
echo.
echo Note: This project requires Python 3.11+ (you have Python 3.10.11)
echo.
pause
exit /b 1

:python_found
echo Found Python installation: %PYTHON_CMD%

REM Check Python version
echo Checking Python version...
%PYTHON_CMD% --version
%PYTHON_CMD% --version | findstr "3.11" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python 3.11+ is REQUIRED for this project.
    echo Current version does not meet requirements.
    echo.
    echo Please install Python 3.11 or higher:
    echo 1. Microsoft Store: Search for "Python 3.11" or "Python 3.12"
    echo 2. Or download from: https://www.python.org/downloads/
    echo 3. Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Creating virtual environment with found Python...
uv venv --python %PYTHON_CMD%

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing setuptools and wheel first...
uv pip install --upgrade pip setuptools wheel

echo Installing numpy using pre-built wheels (no compilation needed)...
uv pip install --only-binary=all numpy

echo Installing PyTorch...
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

echo Installing audio processing libraries...
uv pip install librosa

echo Installing ML libraries...
uv pip install transformers diffusers safetensors

echo Installing Chatterbox dependencies (with build isolation disabled)...
uv pip install s3tokenizer resemble-perth conformer --no-build-isolation
uv pip install pykakasi --no-build-isolation

echo Installing WebSocket dependencies...
uv pip install websockets uvicorn fastapi pydantic python-multipart aiofiles

echo Installing UI dependencies...
uv pip install gradio

echo Installing project in development mode...
uv pip install -e . --no-deps

echo.
echo Downloading models (this may take a while)...
python -c "from chatterbox.tts import ChatterboxTTS; from chatterbox.mtl_tts import ChatterboxMultilingualTTS; import torch; device = 'cuda' if torch.cuda.is_available() else 'cpu'; print(f'Downloading models for device: {device}'); ChatterboxTTS.from_pretrained(device); ChatterboxMultilingualTTS.from_pretrained(device); print('Models downloaded successfully!')"

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo You can now:
echo 1. Start the server: start.bat
echo 2. Test the service: test.bat
echo 3. Open test_web_client.html in your browser
echo.
echo Server will run on: ws://localhost:8000
echo.
pause
