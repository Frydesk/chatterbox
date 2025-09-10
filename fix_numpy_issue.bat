@echo off
echo Fixing numpy/distutils issue...

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing setuptools and wheel...
pip install --upgrade setuptools wheel

echo Installing numpy with specific version...
pip install "numpy>=1.24.0,<1.26.0" --force-reinstall

echo Installing other dependencies...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

echo Installing remaining dependencies...
pip install -e .

echo.
echo Fix applied! Try running the setup again or start the server.
pause
