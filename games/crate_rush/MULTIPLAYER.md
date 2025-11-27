# Crate Rush - Multiplayer Mode

## Overview

Crate Rush now supports LAN multiplayer! Play with your friends on the same local network.

## Features

- **Host a Game**: Create a lobby that others can join
- **Join a Game**: Connect to a friend's game using their IP address
- **Real-time Gameplay**: See other players move, shoot, and play in real-time
- **Player Names**: Each player's name is displayed above their head
- **Same Sprites**: All players use the same character and weapon sprites

## How to Play

### Hosting a Game

1. From the main menu, select **ONLINE MULTIPLAYER**
2. Press **N** to set your player name (optional)
3. Select **HOST GAME** and press Enter
4. Share your IP address (displayed on screen) with friends
5. Wait for players to join
6. Press **SPACE** to start the game

### Joining a Game

1. From the main menu, select **ONLINE MULTIPLAYER**
2. Press **N** to set your player name (optional)
3. Select **JOIN GAME** and press Enter
4. Enter the host's IP address
5. Press Enter to connect
6. Wait for the host to start the game

## Technical Details

### Network Architecture

- Uses TCP sockets for reliable communication
- Server-client architecture with one host acting as both server and client
- State updates sent at 30 Hz for smooth gameplay
- Position interpolation for smooth remote player movement

### Port Configuration

- Default port: **5555**
- Can specify custom port when joining: `192.168.1.100:5556`

### Current Limitations (Private IP)

The game currently works on **Local Area Network (LAN)** only:
- All players must be on the same local network
- Uses private IP addresses (e.g., 192.168.x.x)

### Future: Public IP Support

To enable internet play in the future:
1. The host needs to set up **port forwarding** on their router (port 5555)
2. Share the **public IP** instead of private IP
3. Or use a VPN service like Hamachi to create a virtual LAN

## Controls (Multiplayer)

| Action | Key |
|--------|-----|
| Move Left | A / Left Arrow |
| Move Right | D / Right Arrow |
| Jump | Space / W / Up Arrow |
| Shoot | J / F / Left Mouse |
| Pause | P / Escape |

## Troubleshooting

### Can't Connect to Host

1. Make sure both players are on the same network
2. Check if the host's firewall allows connections on port 5555
3. Verify the IP address is correct
4. Try using `127.0.0.1` if testing on the same machine

### Laggy Movement

- Check your network connection
- Reduce the number of players
- Close bandwidth-heavy applications

### Connection Lost

- The game will notify you if the connection is lost
- Try reconnecting or host a new game

## Files

- `network.py` - Network client/server implementation
- `multiplayer.py` - Multiplayer game logic and remote player rendering
- `settings.py` - Multiplayer state constants
