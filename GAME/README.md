# 🚀 3D Space Combat - Multiplayer Game

A beautiful 3D multiplayer space combat game built with Python and Pygame, featuring real-time multiplayer networking, 3D graphics, and engaging gameplay.

## ✨ Features

- **3D Graphics**: Custom 3D rendering engine using Pygame
- **Multiplayer**: Real-time multiplayer with up to 8 players
- **Public IP Support**: Play with friends over the internet
- **Beautiful UI**: Modern space-themed interface
- **Game Mechanics**:
  - Ship combat and movement
  - Asteroid field navigation
  - Power-up collection (health, ammo, shield, speed)
  - Projectile shooting
  - Score system
- **Particle Effects**: Explosions and visual effects
- **Responsive Controls**: WASD movement, mouse look, click to shoot

## 🎮 How to Play

### Controls
- **WASD**: Move your ship
- **Mouse**: Look around (rotation)
- **Left Click**: Shoot projectiles
- **Escape**: Return to menu

### Gameplay
- Navigate through the asteroid field
- Shoot asteroids to earn points
- Collect power-ups to enhance your ship
- Avoid other players' projectiles
- Compete for the highest score!

## 🚀 Quick Start

### Option 1: Use the Launcher (Windows)
```bash
# Double-click start_game.bat or run:
start_game.bat
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Server (Host)**
   ```bash
   python launch_server.py
   ```

3. **Start Client (Join)**
   ```bash
   python launch_client.py
   ```

## 🌐 Multiplayer Setup

### Hosting a Game (Server)
1. Run the server: `python launch_server.py`
2. The server will bind to `0.0.0.0:5555` by default
3. Share your **public IP address** with other players
4. Make sure port 5555 is open in your firewall

### Joining a Game (Client)
1. Run the client: `python launch_client.py`
2. Click "Connect to Server"
3. Enter the host's **public IP address**
4. Enter your player name
5. Start playing!

### Finding Your Public IP
- Visit [whatismyip.com](https://whatismyip.com)
- Or use command line: `curl ifconfig.me` (Linux/Mac) or `nslookup myip.opendns.com` (Windows)

## 🔧 Advanced Configuration

### Server Options
```bash
# Custom host and port
python launch_server.py --host 192.168.1.100 --port 7777

# Default (accessible from anywhere)
python launch_server.py --host 0.0.0.0 --port 5555
```

### Network Requirements
- **Port**: 5555 (default, configurable)
- **Protocol**: TCP
- **Bandwidth**: Low (text-based messages)
- **Firewall**: Allow incoming connections on game port

## 🎨 Game Features

### 3D Graphics Engine
- Custom 3D-to-2D projection
- Perspective rendering
- Distance-based scaling
- Smooth camera movement

### Visual Effects
- Animated starfield background
- Particle explosion system
- Rotating asteroids and power-ups
- Dynamic lighting effects

### Game World
- **Asteroids**: 20 rotating obstacles to navigate and destroy
- **Power-ups**: 4 types scattered across the map
  - 🔴 Health: Restore 25 HP
  - 🟡 Ammo: Add 25 bullets
  - 🔵 Shield: Add 50 shield points
  - 🟢 Speed: Increase movement speed
- **Projectiles**: Fast-moving bullets with collision detection

## 🛠️ Technical Details

### Architecture
- **Server**: Python socket server with threading
- **Client**: Pygame-based 3D game engine
- **Networking**: JSON-based message protocol
- **Physics**: Custom collision detection
- **Rendering**: Software-based 3D graphics

### Performance
- **Frame Rate**: 60 FPS target
- **Network**: ~20 updates per second
- **Memory**: Low footprint (~50MB)
- **CPU**: Optimized for smooth gameplay

## 🐛 Troubleshooting

### Common Issues

**Can't connect to server**
- Check if server is running
- Verify IP address and port
- Check firewall settings
- Ensure port forwarding is configured

**Game runs slowly**
- Close other applications
- Update graphics drivers
- Reduce window size if needed

**Connection drops**
- Check internet stability
- Verify server is still running
- Restart client if needed

### Network Protocol Fixed ✅

**Previous Issue**: `invalid literal for int() with base 10: '{"ty'` error
**Solution**: Implemented newline-delimited JSON protocol for reliable message transmission

The networking now uses:
- Newline (`\n`) delimited messages for reliable parsing
- Message buffering to handle TCP stream fragmentation
- Robust error handling for malformed messages

### Network Debugging
```bash
# Test server connection
python test_connection.py [server_ip]

# Check if port is open
telnet [server_ip] 5555
```

## 📁 Project Structure

```
GAME/
├── game_server.py      # Main server implementation
├── game_client.py      # Main client implementation
├── launch_server.py    # Server launcher script
├── launch_client.py    # Client launcher script
├── start_game.bat      # Windows batch launcher
├── requirements.txt    # Python dependencies
├── test_connection.py  # Network testing utility
└── README.md          # This file
```

## 🎯 Future Enhancements

- [ ] Sound effects and music
- [ ] More ship types and customization
- [ ] Team-based gameplay
- [ ] Power-up crafting system
- [ ] Leaderboards and statistics
- [ ] Spectator mode
- [ ] Replay system

## 🤝 Contributing

Feel free to contribute to this project! Areas for improvement:
- Enhanced graphics and effects
- Better networking optimization
- Additional game modes
- Mobile platform support

## 📄 License

This project is open source and available under the MIT License.

---

**Enjoy your space combat adventure!** 🚀✨
