@echo off
echo Testing Chatterbox TTS WebSocket Service...

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if test client exists
if not exist "test_client.py" (
    echo test_client.py not found!
    pause
    exit /b 1
)

echo.
echo Running basic TTS test with Spanish text...
echo Make sure the server is running (start.bat) before running this test.
echo.

REM Run basic test
python test_client.py --test basic --text "Hola, este es un test del sistema de síntesis de voz Chatterbox en español." --language es --output test_spanish.wav

echo.
echo Test completed! Check test_spanish.wav for the generated audio.
echo.

pause
