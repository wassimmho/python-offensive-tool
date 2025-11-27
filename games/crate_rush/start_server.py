"""
Crate Rush - Server Launcher
Easy launcher for the multiplayer game server
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crate_rush.game_server import GameServer

if __name__ == "__main__":
    print("="*60)
    print(" " * 15 + "CRATE RUSH")
    print(" " * 10 + "MULTIPLAYER GAME SERVER")
    print("="*60)
    print()
    print("Server will start on your local IP address")
    print("Share this IP with players who want to join!")
    print()
    print("Press Ctrl+C to stop the server")
    print("-"*60)
    print()
    
    server = GameServer()
    server.start()
