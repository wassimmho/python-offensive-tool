@echo off
title 3D Space Combat Game
echo ================================================
echo    3D Space Combat - Multiplayer Game
echo ================================================
echo.
echo Choose an option:
echo 1. Start Server (Host Game)
echo 2. Start Client (Join Game)
echo 3. Test Connection (Troubleshoot)
echo 4. Install Dependencies
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting Game Server...
    python launch_server.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Game Client...
    python launch_client.py
) else if "%choice%"=="3" (
    echo.
    echo Starting Connection Tester...
    python test_connection_gui.py
) else if "%choice%"=="4" (
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo Dependencies installed! Press any key to continue...
    pause >nul
    goto :start
) else if "%choice%"=="5" (
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    goto :start
)

:start
cls
goto :eof
