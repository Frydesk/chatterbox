@echo off
echo Advanced Testing for Chatterbox TTS WebSocket Service...

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
echo Running comprehensive tests...
echo Make sure the server is running (start.bat) before running this test.
echo.

echo 1. Testing server info...
python test_client.py --test info

echo.
echo 2. Testing server ping...
python test_client.py --test ping

echo.
echo 3. Testing basic Spanish TTS...
python test_client.py --test basic --text "Hola, este es un test del sistema de síntesis de voz Chatterbox en español." --language es --output test_spanish_basic.wav

echo.
echo 4. Testing English TTS...
python test_client.py --test basic --text "Hello, this is a test of the Chatterbox text-to-speech system in English." --language en --output test_english.wav

echo.
echo 5. Testing French TTS...
python test_client.py --test basic --text "Bonjour, ceci est un test du système de synthèse vocale Chatterbox en français." --language fr --output test_french.wav

echo.
echo 6. Testing with different parameters...
python test_client.py --test basic --text "Este es un test con parámetros diferentes de exageración y temperatura." --language es --output test_spanish_params.wav

echo.
echo All tests completed! Check the generated .wav files for results.
echo.

pause
