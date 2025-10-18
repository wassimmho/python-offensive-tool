# 🚀 Quick Reference Guide

## Running the Game

### Option 1: Automated Test (Windows)
```bash
test_game.bat
```
This will automatically:
1. Test connection
2. Start server
3. Wait 3 seconds
4. Start client

### Option 2: Manual Start
```bash
# Terminal 1 - Start Server
python server.py

# Terminal 2 - Start Client (after server is running)
python client.py
```

### Option 3: Connection Test First
```bash
# Test connection before running game
python test_connection.py

# If test passes, start server and client
python server.py    # Terminal 1
python client.py    # Terminal 2
```

## What You Should See

### ✅ Server Console (Successful Start)
```
============================================================
🎮 3D MULTIPLAYER SHOOTER - SERVER
============================================================
🎮 GAME SERVER STARTED
============================================================
✅ Server listening on 0.0.0.0:5555
🌐 Public IP: [your IP]
...
✅ Game loop started
🔄 Accepting connections...
```

### ✅ Client Console (Successful Connection)
```
============================================================
🎮 3D MULTIPLAYER SHOOTER - CLIENT
============================================================
🔌 CONNECTING TO SERVER
...
✅ Successfully connected to server localhost:5555
🔄 Network loop started
📥 Received message type: init
============================================================
🎮 INITIALIZED AS PLAYER 0
   Position: (x, y)
   Health: 100
   Ammo: 30
============================================================
🎮 GAME LOOP STARTED
```

### ✅ Client Window (Visual Confirmation)
You should see:
- **Dark blue/gray background** (not black)
- **Red square** in center (test rectangle)
- **"3D Game Active"** text at top
- **Health/Ammo/Score** in top-left corner
- **Debug info** in bottom-left (green text):
  - Player ID
  - Position
  - Angle
  - Player count
  - FPS counter
- **Connection status** in top-right

## Debug Indicators

### Server Indicators
| Emoji | Meaning |
|-------|---------|
| 🎮 | Game event |
| ✅ | Success |
| ❌ | Error/Failure |
| 📥 | Data received |
| 📤 | Data sent |
| 🔄 | Process running |
| ⚠️ | Warning |
| 🏃 | Player movement |
| 🔫 | Shooting action |

### Client Indicators
| Emoji | Meaning |
|-------|---------|
| 🎮 | Game event |
| ✅ | Success |
| ❌ | Error/Failure |
| 📥 | Data received |
| 📤 | Data sent |
| 🔌 | Connection event |
| 📡 | Network operation |
| ⌨️ | Keyboard input |
| 🖱️ | Mouse input |
| 🎬 | Frame update |

## Common Issues Quick Fix

### Issue: Blank/Black Screen
**Quick Check:**
1. Is red square visible? → If NO, check console for errors
2. Is "3D Game Active" visible? → If NO, game not initialized
3. Is FPS counter visible? → If NO, rendering issue

**Quick Fix:**
1. Close client
2. Verify server shows "NEW PLAYER CONNECTION"
3. Restart client
4. Look for "INITIALIZED AS PLAYER X" message

### Issue: Connection Refused
**Quick Fix:**
1. Make sure server is running FIRST
2. Check server console shows "Accepting connections..."
3. Try: `python test_connection.py`
4. If test fails, check port 5555 availability

### Issue: Nothing Happens
**Quick Check Console:**
- Server: Should show "Game loop running" every second
- Client: Should show frame updates

**Quick Fix:**
1. Close both server and client
2. Wait 5 seconds
3. Start server, wait for "Accepting connections..."
4. Start client

### Issue: Can't Move
**Quick Check:**
1. Press W/A/S/D keys → Look for "⌨️ Key pressed" in console
2. Check Health > 0
3. Check player is marked "Alive"

**Quick Fix:**
1. Check if you're looking at movement in debug info
2. Position values should change when moving
3. If not, check server console for "Player X moved to..."

## Performance Check

### Expected Performance
- **Server**: Game loop running at ~60 FPS
- **Client**: FPS counter shows 50-60 FPS
- **Network**: Messages every frame (60/second)

### If Performance is Poor
1. Check CPU usage (should be moderate)
2. Close other applications
3. Reduce number of players
4. Check network latency

## Controls Reminder

| Action | Keys/Mouse |
|--------|------------|
| Move Forward | W |
| Move Backward | S |
| Strafe Left | A |
| Strafe Right | D |
| Rotate Player Left | Q |
| Rotate Player Right | E |
| Rotate Camera Left | Left Arrow |
| Rotate Camera Right | Right Arrow |
| Shoot | Left Mouse Click |
| Exit | ESC |

## Debug Info Legend (On-Screen)

Bottom-left corner shows:
- **Player ID**: Your player number (0-7)
- **Pos**: Your position (x, y) in world
- **Angle**: Your rotation angle (0-360)
- **Players**: Number of players in game
- **FPS**: Frames per second (performance)

## When to Report Issues

Save the following information:
1. **Console Output**: Copy from both server and client
2. **Last Message**: What was the last thing printed?
3. **Visual State**: What do you see in the window?
4. **Steps**: What did you do before the issue?
5. **Test Result**: Output from `test_connection.py`

## Tips for Best Experience

1. **Always start server first**, wait for "Accepting connections"
2. **Check console regularly** for error messages
3. **Use test_connection.py** before running full game
4. **Keep terminals visible** to monitor status
5. **Close cleanly** with ESC or Ctrl+C
6. **Wait 5 seconds** between restarts

## File Reference

| File | Purpose |
|------|---------|
| `server.py` | Game server (run first) |
| `client.py` | Game client |
| `test_connection.py` | Connection test tool |
| `test_game.bat` | Auto-start script (Windows) |
| `DEBUG.md` | Detailed debugging guide |
| `CHANGES.md` | List of modifications |
| `QUICK_REFERENCE.md` | This file |

## Need More Help?

1. Read `DEBUG.md` for detailed troubleshooting
2. Read `CHANGES.md` to understand what was added
3. Check `README.md` for general game information
4. Run `test_connection.py` to verify connectivity

---

**Remember**: Server must be running before client connects!
