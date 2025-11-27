"""
Crate Rush - Multiplayer Client Launcher
Connect to a multiplayer game server
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crate_rush.multiplayer import start_multiplayer

if __name__ == "__main__":
    print("="*60)
    print(" " * 15 + "CRATE RUSH")
    print(" " * 10 + "MULTIPLAYER CLIENT")
    print("="*60)
    print()
    
    # Get player name
    player_name = input("Enter your player name: ").strip()
    if not player_name:
        player_name = "Player"
    
    # Get server IP
    print()
    print("Enter server IP address")
    print("(Press Enter for localhost/127.0.0.1)")
    server_ip = input("Server IP: ").strip()
    if not server_ip:
        server_ip = "127.0.0.1"
    
    print()
    print(f"Connecting to {server_ip}...")
    print("-"*60)
    
    start_multiplayer(server_ip, player_name)
