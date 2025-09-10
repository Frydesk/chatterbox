@echo off
echo ========================================
echo   Chatterbox TTS Troubleshooting Tool
echo ========================================
echo.

echo Checking system requirements...

REM Check Python version
echo 1. Checking Python version...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    goto :end
)

REM Check if virtual environment exists
echo.
echo 2. Checking virtual environment...
if exist ".venv\Scripts\activate.bat" (
    echo Virtual environment exists
) else (
    echo Virtual environment not found
    echo Run setup.bat or setup_pip.bat first
    goto :end
)

REM Check if uv is available
echo.
echo 3. Checking uv installation...
where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo uv is installed
    set USE_UV=1
) else (
    echo uv is not installed, will use pip
    set USE_UV=0
)

REM Activate virtual environment
echo.
echo 4. Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check installed packages
echo.
echo 5. Checking installed packages...
python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"

REM Try to import chatterbox
echo.
echo 6. Testing Chatterbox imports...
python -c "from chatterbox.mtl_tts import ChatterboxMultilingualTTS; print('Chatterbox import successful')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Chatterbox import failed
    echo Try reinstalling: pip install -e .
    goto :end
)

REM Check if models are downloaded
echo.
echo 7. Checking model availability...
python -c "
import os
from pathlib import Path
import torch
from huggingface_hub import snapshot_download

try:
    # Check if models are cached
    cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
    if cache_dir.exists():
        print(f'HF cache directory exists: {cache_dir}')
        # List some files to see if models are there
        for item in cache_dir.iterdir():
            if 'ResembleAI' in str(item):
                print(f'Found ResembleAI cache: {item.name}')
                break
    else:
        print('HF cache directory not found')
    
    print('Model check completed')
except Exception as e:
    print(f'Model check error: {e}')
"

echo.
echo 8. Testing WebSocket server import...
python -c "import websocket_server; print('WebSocket server import successful')"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WebSocket server import failed
    echo Check if all dependencies are installed
    goto :end
)

echo.
echo ========================================
echo   Troubleshooting Complete
echo ========================================
echo.
echo If all checks passed, you should be able to:
echo 1. Start the server: start.bat
echo 2. Test the service: test.bat
echo.
echo If you encountered errors:
echo 1. Try setup_pip.bat instead of setup.bat
echo 2. Check your Python version (3.10+ required)
echo 3. Ensure you have enough disk space for models
echo 4. Check your internet connection for model downloads
echo.

:end
pause
