# 🎮 How to Play - 3D Space Combat Game

## 🚀 Quick Start Guide

### **Step 1: Start the Game**
```bash
# Double-click this file or run in terminal:
start_game.bat
```

### **Step 2: Choose Your Role**

#### **Option 1: Host a Game (Server)**
1. Choose `1. Start Server (Host Game)`
2. Server will start on `0.0.0.0:5555`
3. **Share your IP address** with other players:
   - Local network: `192.168.1.100` (check with `ipconfig`)
   - Internet: Visit [whatismyip.com](https://whatismyip.com)

#### **Option 2: Join a Game (Client)**
1. Choose `2. Start Client (Join Game)`
2. Click "Connect to Server"
3. Enter the server IP address
4. Press Enter to connect

#### **Option 3: Test Connection**
1. Choose `3. Test Connection (Troubleshoot)`
2. Enter server IP and port
3. Click "Test Connection" to diagnose issues

### **Step 3: Play the Game!**

#### **Controls:**
- **WASD** - Move your ship
- **Mouse** - Look around (rotation)
- **Left Click** - Shoot projectiles
- **Escape** - Return to menu

#### **Gameplay:**
- Navigate through asteroid fields
- Shoot asteroids to earn points
- Collect power-ups (health, ammo, shield, speed)
- Avoid other players' projectiles
- Compete for the highest score!

## 🔧 If You Can't Connect

### **Use the Connection Tester:**
1. Run: `python test_connection_gui.py`
2. Enter server IP and port
3. Click "Test Connection"
4. Follow the error messages to fix the issue

### **Common Solutions:**

#### **"Connection timeout"**
- Server is not running
- Wrong IP address
- Firewall blocking connection

**Fix:** Start server first, check IP, disable firewall temporarily

#### **"Connection refused"**
- No server at that address
- Wrong port number

**Fix:** Make sure server is running, use port 5555

#### **"DNS/Network error"**
- Invalid IP format
- No internet connection

**Fix:** Check IP format, test internet connection

## 🌐 Multiplayer Setup

### **Local Network (Same WiFi):**
1. **Host:** Start server, share local IP (192.168.x.x)
2. **Players:** Enter host's local IP

### **Internet Play:**
1. **Host:** Start server, share public IP, open port 5555 in router
2. **Players:** Enter host's public IP

### **Finding Your IP:**
```bash
# Local IP (for same network)
ipconfig

# Public IP (for internet)
# Visit: whatismyip.com
```

## 🎯 Game Features

- **3D Graphics:** Beautiful space environment with particle effects
- **Real-time Multiplayer:** Up to 8 players simultaneously
- **Power-ups:** Health, ammo, shield, and speed boosts
- **Scoring System:** Destroy asteroids and compete for high scores
- **Smooth Controls:** WASD movement with mouse look

## 🆘 Still Need Help?

1. **Read the troubleshooting guide:** `TROUBLESHOOTING.md`
2. **Use the connection tester:** `python test_connection_gui.py`
3. **Test locally first:** Use `127.0.0.1` to test on your own computer

## 🎉 Enjoy Your Space Combat Adventure!

The game features beautiful 3D graphics, smooth multiplayer networking, and engaging gameplay. Have fun exploring the asteroid fields and competing with your friends!
