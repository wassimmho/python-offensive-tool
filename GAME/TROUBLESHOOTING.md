# 🔧 Troubleshooting Guide - 3D Space Combat Game

## 🚨 Common Connection Issues & Solutions

### Issue: "Can't connect to server" or "Connection error"

#### **Step 1: Use the Connection Tester**
1. Run: `python test_connection_gui.py`
2. Or use the launcher: `start_game.bat` → Option 3
3. Enter the server IP and port
4. Click "Test Connection"
5. The tester will show exactly what's wrong

#### **Step 2: Check Server Status**
Make sure the server is running:
```bash
# Start server first
python launch_server.py
# Or
python game_server.py --host 0.0.0.0 --port 5555
```

#### **Step 3: Verify IP Address**
- **Local testing**: Use `127.0.0.1` or `localhost`
- **Same network**: Use local IP like `192.168.1.100`
- **Internet**: Use public IP address

### 🔍 Detailed Error Messages

#### **"Connection timeout - Server not responding"**
**Causes:**
- Server is not running
- Wrong IP address
- Firewall blocking connection
- Network connectivity issues

**Solutions:**
1. Make sure server is started first
2. Check IP address is correct
3. Disable Windows Firewall temporarily to test
4. Check internet connection

#### **"Connection refused - No server running"**
**Causes:**
- No server at that address
- Wrong port number
- Server crashed

**Solutions:**
1. Start the server: `python launch_server.py`
2. Check port number (default: 5555)
3. Restart server if it crashed

#### **"DNS/Network error"**
**Causes:**
- Invalid IP address format
- Internet connectivity issues
- Hostname not found

**Solutions:**
1. Check IP format: `192.168.1.100` (not `192.168.1.100:5555`)
2. Test internet connection
3. Try IP address instead of hostname

### 🌐 Network Setup Guide

#### **For Local Network (Same WiFi)**
1. **Host (Server):**
   ```bash
   python game_server.py --host 0.0.0.0 --port 5555
   ```
   - Share your local IP (e.g., `192.168.1.100`)

2. **Players (Clients):**
   - Enter host's local IP: `192.168.1.100`
   - Port: `5555`

#### **For Internet Play**
1. **Host (Server):**
   ```bash
   python game_server.py --host 0.0.0.0 --port 5555
   ```
   - Find your public IP: visit [whatismyip.com](https://whatismyip.com)
   - Share your public IP with players
   - **Important**: Open port 5555 in router firewall

2. **Players (Clients):**
   - Enter host's public IP
   - Port: `5555`

#### **Firewall Configuration**

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python or the game executable
4. Allow both Private and Public networks

**Router Port Forwarding:**
1. Access router admin panel (usually 192.168.1.1)
2. Find "Port Forwarding" or "Virtual Server"
3. Add rule:
   - External Port: 5555
   - Internal Port: 5555
   - Internal IP: Your computer's local IP
   - Protocol: TCP

### 🧪 Testing Steps

#### **Step 1: Test Locally**
```bash
# Terminal 1 - Start server
python game_server.py --host 127.0.0.1 --port 5555

# Terminal 2 - Test connection
python test_connection.py 127.0.0.1 5555
```

#### **Step 2: Test Network**
```bash
# Use connection tester GUI
python test_connection_gui.py
```

#### **Step 3: Test with Game Client**
```bash
# Start client and try connecting
python launch_client.py
```

### 📱 Finding Your IP Address

#### **Local IP (for same network):**
```bash
# Windows
ipconfig

# Look for: IPv4 Address: 192.168.x.x
```

#### **Public IP (for internet):**
- Visit: [whatismyip.com](https://whatismyip.com)
- Or: [ipify.org](https://api.ipify.org)

### 🛠️ Advanced Troubleshooting

#### **Check if Port is Open**
```bash
# Windows - Check if port is listening
netstat -an | findstr :5555

# Should show: TCP 0.0.0.0:5555 LISTENING
```

#### **Test with Telnet**
```bash
# Windows
telnet [server-ip] 5555

# If connection works, you'll see a blank screen
# Press Ctrl+C to exit
```

#### **Check Server Logs**
When starting server, look for:
```
Starting 3D Space Combat Game Server on 0.0.0.0:5555
Server ready for connections...
```

#### **Check Client Logs**
In the game client console, look for:
```
Successfully connected to [ip]:5555
Connected as player [id]
```

### 🆘 Still Having Issues?

#### **Quick Fixes to Try:**
1. **Restart everything**: Close all game windows, restart server
2. **Try different port**: Use `--port 7777` instead of 5555
3. **Check antivirus**: Temporarily disable to test
4. **Use localhost**: Try `127.0.0.1` first to test locally
5. **Update Python**: Make sure you have Python 3.7+

#### **Common Mistakes:**
- ❌ Forgetting to start server first
- ❌ Using wrong IP format (should be `192.168.1.100`, not `192.168.1.100:5555`)
- ❌ Not opening firewall ports
- ❌ Using wrong port number
- ❌ Server and client on different networks

#### **Get Help:**
If nothing works, run the connection tester and share the results:
```bash
python test_connection_gui.py
```

The tester will show exactly what's wrong and help diagnose the issue.

---

## ✅ Success Indicators

When everything is working, you should see:

**Server:**
```
Starting 3D Space Combat Game Server on 0.0.0.0:5555
Server ready for connections...
New connection from ('192.168.1.100', 12345)
Player PlayerName (abc123) joined the game
```

**Client:**
```
Successfully connected to 192.168.1.100:5555
Connected as player abc123
```

**Game:**
- You can move with WASD
- You can shoot with mouse click
- You see other players
- You see asteroids and power-ups

Happy gaming! 🚀
