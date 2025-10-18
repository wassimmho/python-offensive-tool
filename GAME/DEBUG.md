# 🐛 Debugging Guide

## Enhanced Debugging Features

This version includes extensive debugging output to help identify issues:

### Server Debugging
- ✅ Connection events (new players joining)
- ✅ Player spawn information
- ✅ Message received/sent logging
- ✅ Player movement tracking
- ✅ Disconnect events
- ✅ Game loop status updates

### Client Debugging
- ✅ Connection status
- ✅ Initialization confirmation
- ✅ Game state updates
- ✅ Player input logging
- ✅ Render information
- ✅ On-screen debug info (FPS, position, etc.)

## Testing Steps

### 1. Test Connection
Run the connection test script first:
```bash
python test_connection.py
```

This will verify:
- Server is reachable
- Server accepts connections
- Init message is received
- Messages can be sent/received

### 2. Start Server
```bash
python server.py
```

Expected output:
```
============================================================
🎮 GAME SERVER STARTED
============================================================
✅ Server listening on 0.0.0.0:5555
🌐 Public IP: [your IP]
...
✅ Game loop started
```

### 3. Start Client
```bash
python client.py
```

Expected output:
```
============================================================
🔌 CONNECTING TO SERVER
...
✅ Successfully connected to server localhost:5555
============================================================
🎮 INITIALIZED AS PLAYER 0
...
```

## What to Look For

### Server Console
When a client connects, you should see:
```
📥 New connection request from ('127.0.0.1', xxxxx)
============================================================
🎮 NEW PLAYER CONNECTION
   Player ID: 0
   Address: ('127.0.0.1', xxxxx)
...
```

### Client Window
You should see:
- A red square in the center (test rectangle)
- "3D Game Active" text at top
- Green debug info at bottom left (position, FPS, etc.)
- UI with health/ammo at top left

## Common Issues

### Issue: Blank Screen
**Symptoms:** Window opens but shows only dark screen

**Possible Causes:**
1. Not connected to server
2. Not initialized (no player ID)
3. Rendering issue

**Check:**
- Console shows "Connected" and "Initialized as player X"
- Debug info appears on screen
- Test rectangle (red square) is visible

### Issue: Connection Failed
**Symptoms:** "Failed to connect to server"

**Solutions:**
1. Make sure server is running first
2. Check firewall settings
3. Verify port 5555 is available
4. Try localhost instead of IP address

### Issue: Server Not Accepting Connections
**Symptoms:** Server starts but clients can't connect

**Solutions:**
1. Check if port 5555 is already in use
2. Run as administrator (Windows)
3. Check firewall rules
4. Try different port in server.py

### Issue: Game Freezes
**Symptoms:** Window stops responding

**Check:**
1. Server console for errors
2. Network connectivity
3. Python process CPU usage

## Debug Output Examples

### Successful Connection (Server Side)
```
🔄 Accepting connections...
📥 New connection request from ('127.0.0.1', 54321)
✅ Accepting player (Current players: 0/8)
============================================================
🎮 NEW PLAYER CONNECTION
   Player ID: 0
   Address: ('127.0.0.1', 54321)
   Total players: 1
============================================================
✅ Player 0 spawned at (123, -45)
📤 Sending init message to Player 0
✅ Init message sent to Player 0
```

### Successful Connection (Client Side)
```
============================================================
🔌 CONNECTING TO SERVER
   Host: localhost
   Port: 5555
============================================================
📡 Creating socket...
📡 Attempting connection...
✅ Connection established!
🔄 Starting network thread...
✅ Network thread started
============================================================
🔄 Network loop started
📥 Received message type: init
============================================================
🎮 INITIALIZED AS PLAYER 0
   Position: (123, -45)
   Health: 100
   Ammo: 30
   Players in game: 1
============================================================
```

## Performance Notes

- Server runs at 60 FPS (one game loop iteration per frame)
- Client also targets 60 FPS
- Debug messages print every 60 frames (once per second)
- Movement updates only logged if position changes significantly

## Getting Help

If you're still having issues:

1. Run `test_connection.py` and save the output
2. Run server and client with output redirected:
   ```bash
   python server.py > server_log.txt 2>&1
   python client.py > client_log.txt 2>&1
   ```
3. Check both log files for errors
4. Look for the last successful operation before failure

## Reducing Debug Output

If the console output is too verbose, you can comment out or remove specific print statements in:
- `server.py` - Search for `print(f"📥` or similar emoji prefixes
- `client.py` - Same approach

Example - disable movement logging:
```python
# Comment this line in server.py process_client_message():
# print(f"🏃 Player {player_id} moved to ({new_x:.1f}, {new_y:.1f})")
```
