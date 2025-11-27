# Crate Rush - Multiplayer Mode

## 🎮 How to Play Online Multiplayer

### Option 1: Play on Local Network (LAN)

#### Step 1: Start the Server
One person needs to host the game server:

```bash
cd games/crate_rush
python start_server.py
```

The server will display its IP address. Share this IP with other players!

#### Step 2: Join the Game
Other players can join by running:

```bash
cd games/crate_rush
python join_game.py
```

When prompted:
- Enter your player name
- Enter the server's IP address

### Option 2: Play on the Same Computer (localhost)

1. Start the server:
```bash
python start_server.py
```

2. In another terminal, start clients:
```bash
python join_game.py
```

When asked for server IP, just press Enter (uses 127.0.0.1 by default)

You can open multiple terminals to test with multiple players!

## 🎯 Game Features

### Multiplayer Features:
- **Multiple Players**: See and play with other players in real-time
- **Shared World**: All players share the same enemies, crates, and bullets
- **Real-time Sync**: Player movements, shooting, and collections sync instantly
- **Scoreboard**: Track your score and compete with others
- **Player Names**: See who you're playing with

### Controls (Same as Single Player):
- **Move**: A/D or Arrow Keys
- **Jump**: Space
- **Shoot**: J/F or Mouse Click
- **Quit**: ESC

## 🔧 Technical Details

- **Server Port**: 5051
- **Protocol**: TCP/IP with JSON messages
- **Update Rate**: ~60 times per second
- **Players**: Unlimited (tested with multiple clients)

## 🐛 Troubleshooting

**Can't connect to server?**
- Make sure the server is running first
- Check firewall settings (port 5051 must be open)
- Verify the IP address is correct
- For LAN play, both computers must be on the same network

**Server won't start?**
- Port 5051 might be in use
- Try restarting your computer
- Check if another instance is already running

**Lag or disconnections?**
- Check network connection
- Server needs stable internet
- Reduce network load (close other apps)

## 🎮 Single Player Mode

To play single player (offline), just run:
```bash
python -m crate_rush.main
```

## 📝 Server Commands

While the server is running:
- **Ctrl+C**: Stop the server gracefully
- Server automatically manages all game state
- Check console for player connections/disconnections

Enjoy playing Crate Rush with your friends! 🚀
