@echo off
echo ============================================================
echo 3D Multiplayer Shooter - Debug Test
echo ============================================================
echo.
echo This script will:
echo 1. Test connection
echo 2. Start server
echo 3. Wait 3 seconds
echo 4. Start client
echo.
echo Press any key to continue...
pause > nul
echo.

echo ============================================================
echo Step 1: Testing Connection
echo ============================================================
python test_connection.py
if errorlevel 1 (
    echo.
    echo WARNING: Connection test failed!
    echo Starting server anyway...
    echo.
    timeout /t 3 > nul
)

echo ============================================================
echo Step 2: Starting Server
echo ============================================================
start "Game Server" cmd /k python server.py

echo ============================================================
echo Step 3: Waiting for server to initialize...
echo ============================================================
timeout /t 3

echo ============================================================
echo Step 4: Starting Client
echo ============================================================
start "Game Client" cmd /k python client.py

echo.
echo ============================================================
echo Both server and client windows should now be open!
echo Check the console windows for debug output.
echo.
echo Server window: Look for "NEW PLAYER CONNECTION"
echo Client window: Look for "INITIALIZED AS PLAYER"
echo.
echo Press any key to exit this window...
echo ============================================================
pause > nul
