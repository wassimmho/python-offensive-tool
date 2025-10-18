# Localhost Setup Guide

## Quick Start

Your localhost is now working! Here's how to use it:

### Option 1: Simple Launcher (Recommended)
```bash
python start_localhost.py
```
Or double-click `start_localhost.bat` on Windows.

### Option 2: Manual Steps

1. **Start the Server:**
   ```bash
   python launch_server.py --host localhost --port 5555
   ```

2. **Start the Client:**
   ```bash
   python launch_client.py
   ```
   When prompted, enter: `localhost`

### Option 3: Test Connection First
```bash
python test_localhost.py
```

## Connection Details

- **Server IP:** `localhost` or `127.0.0.1`
- **Port:** `5555` (default)
- **Protocol:** TCP

## Troubleshooting

If you have connection issues:

1. **Check if server is running:**
   ```bash
   python test_connection.py localhost
   ```

2. **Make sure no firewall is blocking port 5555**

3. **Check if another application is using port 5555:**
   ```bash
   netstat -an | findstr :5555
   ```

## Game Controls

- **WASD:** Move
- **Mouse:** Look around
- **Left Click:** Shoot
- **Escape:** Menu

## Features

- ✅ 3D graphics with pygame
- ✅ Multiplayer networking
- ✅ Real-time game state synchronization
- ✅ Asteroid shooting
- ✅ Power-ups
- ✅ Score system

Enjoy your 3D Space Combat game!
