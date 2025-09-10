@echo off
echo ========================================
echo   Chatterbox TTS WebSocket API Setup
echo ========================================
echo.

echo This script will:
echo 1. Set up the environment
echo 2. Start the server
echo 3. Run basic tests
echo.

set /p choice="Do you want to proceed? (y/n): "
if /i "%choice%" neq "y" (
    echo Setup cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Setting up environment...
call setup.bat
if %ERRORLEVEL% neq 0 (
    echo Setup failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Starting server in background...
start "Chatterbox TTS Server" cmd /c "start.bat"

echo Waiting for server to start...
timeout /t 10 /nobreak >nul

echo.
echo Step 3: Running basic test...
call test.bat

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo The server is running in a separate window.
echo You can now:
echo 1. Open test_web_client.html in your browser
echo 2. Run test_advanced.bat for more tests
echo 3. Use the WebSocket API at ws://localhost:8000
echo.
echo Press any key to exit...
pause >nul
