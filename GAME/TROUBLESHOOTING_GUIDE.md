# Troubleshooting Guide - "I Can't Play the Game"

## Quick Diagnostic

First, run this to check if everything is working:
```bash
python diagnose_game.py
```

## Common Issues and Solutions

### Issue 1: "Game opens but I can't move"

**Symptoms:**
- Game window opens
- You see the space background
- Pressing WASD does nothing

**Solutions:**
1. **Make sure the game window is focused** (click on it)
2. **Check if you're connected:**
   - Look for "PLAYER X - CONNECTED" message
   - If you see "NOT CONNECTED", reconnect to server
3. **Try the minimal test:**
   ```bash
   python test_minimal_game.py
   ```

### Issue 2: "Game crashes when I try to connect"

**Symptoms:**
- Game window closes immediately
- Error messages in console

**Solutions:**
1. **Make sure server is running first:**
   ```bash
   python launch_server.py
   ```
2. **Wait for "Server ready for connections..." message**
3. **Then start the client:**
   ```bash
   python launch_client.py
   ```

### Issue 3: "I can't see my ship"

**Symptoms:**
- Game is connected
- You can move (position changes in debug info)
- But you don't see your ship on screen

**Solutions:**
1. **Move your mouse around** - the ship might be off-screen
2. **Try pressing W** to move forward
3. **Look for a green triangle** - that's your ship

### Issue 4: "Connection dialog doesn't work"

**Symptoms:**
- Game opens but stuck on connection screen
- Can't type or press Enter

**Solutions:**
1. **Make sure the game window is focused**
2. **Type exactly:** `localhost` (no spaces, lowercase)
3. **Press Enter** (not clicking)
4. **If that doesn't work, try:** `127.0.0.1`

### Issue 5: "Game is too slow/laggy"

**Symptoms:**
- Game runs but feels choppy
- Input is delayed

**Solutions:**
1. **Close other applications**
2. **Check if you have enough RAM**
3. **Make sure no antivirus is scanning**

## Step-by-Step Fix Process

### Step 1: Check Server
```bash
python launch_server.py
```
**Expected output:**
```
Starting 3D Space Combat Game Server on localhost:5555
Server ready for connections...
```

### Step 2: Test Connection
```bash
python test_connection.py localhost
```
**Expected output:**
```
CONNECTION TEST PASSED
```

### Step 3: Start Client
```bash
python launch_client.py
```

### Step 4: Connect
- Type: `localhost`
- Press: Enter

### Step 5: Test Movement
- Press: W (should move forward)
- Move: Mouse (should rotate ship)

## Alternative: Use the Simple Launcher

If manual steps don't work, try the automated launcher:

```bash
python start_localhost.py
```

Choose option **3** (Start Both Server + Client)

## Still Having Issues?

### Run Full Diagnostic
```bash
python diagnose_game.py
```

### Check These Files Exist
- `game_server.py`
- `game_client.py` 
- `launch_server.py`
- `launch_client.py`

### Check Python Version
```bash
python --version
```
Should be Python 3.7 or higher.

### Check Dependencies
```bash
python -c "import pygame, numpy; print('OK')"
```

## Getting Help

If nothing works, provide this information:

1. **Operating System:** Windows/Mac/Linux
2. **Python Version:** `python --version`
3. **Error Messages:** Copy any red text from console
4. **What You See:** Describe what appears on screen
5. **What You Did:** Step-by-step what you tried

## Emergency Fix: Reset Everything

If all else fails:

1. **Close all game windows**
2. **Wait 10 seconds**
3. **Run diagnostic:**
   ```bash
   python diagnose_game.py
   ```
4. **If diagnostic passes, try minimal test:**
   ```bash
   python test_minimal_game.py
   ```
5. **If minimal test works, the full game should work too**

## Success Indicators

You know it's working when you see:
- ✅ Green "PLAYER X - CONNECTED" message
- ✅ Your position changes when pressing WASD
- ✅ Green triangle (your ship) moves around
- ✅ Gray asteroids in the background
- ✅ Health/ammo bars in top-left corner
