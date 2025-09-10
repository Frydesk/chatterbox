@echo off
echo Starting Chatterbox TTS WebSocket Server...

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if server file exists
if not exist "websocket_server.py" (
    echo websocket_server.py not found!
    pause
    exit /b 1
)

echo Starting WebSocket server on ws://localhost:8000
echo Press Ctrl+C to stop the server
echo.

REM Start the server
python websocket_server.py --host localhost --port 8000

pause
