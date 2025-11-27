# 🎮 Crate Rush - Quick Start Guide

## ✅ Installation Complete!

Your game now has **FULL MULTIPLAYER** support!

## 🚀 How to Start Playing

### Single Player Mode (Offline)
```bash
cd C:\Users\hp\OneDrive\Documents\python-offensive-tool\games
.\crate_rush\.venv\Scripts\python.exe -m crate_rush.main
```

### Multiplayer Mode

#### 1️⃣ Start the Server (One Person Hosts)
```bash
cd C:\Users\hp\OneDrive\Documents\python-offensive-tool\games\crate_rush
.\.venv\Scripts\python.exe start_server.py
```

**The server is now running on: `192.168.100.5:5051`**

#### 2️⃣ Join the Game (Multiple Players Can Join)

Open a NEW terminal for each player:

```bash
cd C:\Users\hp\OneDrive\Documents\python-offensive-tool\games\crate_rush
.\.venv\Scripts\python.exe join_game.py
```

When prompted:
- **Enter your name**: Type any name you want
- **Server IP**: Type `192.168.100.5` (or just press Enter for localhost if testing on same PC)

## 🎯 What's New in Multiplayer?

✅ **Real-time Online Play** - Play with friends over LAN or internet
✅ **Multiple Players** - Unlimited players can join
✅ **Shared Game World** - Everyone sees the same enemies, crates, and bullets
✅ **Live Synchronization** - All actions sync in real-time
✅ **Player Names** - See who's playing with you
✅ **Scoreboard** - Compete for the highest score
✅ **No Fall Death** - Respawn system so you don't lose progress

## 🎨 Game Features

✅ **Rotating Backgrounds** - 4 beautiful backgrounds cycle every 10 seconds
✅ **Character Sprites** - Real character art instead of squares
✅ **AK-47 Weapon** - Animated pixel art weapon with 3 firing frames
✅ **Better Crates** - 3D wooden crate designs
✅ **Enemy Sprites** - Detailed enemy characters with red glowing eyes

## 🎮 Controls

- **Move**: A/D or Arrow Keys
- **Jump**: Space Bar
- **Shoot**: J, F, or Mouse Click
- **Pause**: P (single player only)
- **Quit**: ESC

## 📡 Network Info

- **Server IP**: 192.168.100.5
- **Port**: 5051
- **Protocol**: TCP/IP with JSON
- **Update Rate**: 60 FPS

## 🔥 Testing Multiplayer on Same PC

You can test multiplayer by yourself:

1. Start the server (keep it running)
2. Open 2-3 new PowerShell windows
3. Run `join_game.py` in each
4. Use `127.0.0.1` as server IP
5. Give each player a different name

Watch them all play together in real-time!

## 📝 Tips

- The server must stay running for multiplayer to work
- Share the server IP with friends on your network
- Each player needs their own game client running
- Players can join/leave anytime
- Server automatically manages all game logic

---

**Enjoy your fully multiplayer Crate Rush game! 🎉**
