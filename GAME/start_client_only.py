#!/usr/bin/env python3
"""
Simple client starter - connects directly to localhost
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_client import GameClient

def main():
    print("Starting 3D Space Combat Client...")
    print("Connecting to local server (127.0.0.1:5555)")
    
    client = GameClient()
    
    # Auto-connect to localhost
    client.server_ip = "127.0.0.1"
    client.player_name = "Player"
    
    # Try to connect automatically
    if client.connect_to_server("127.0.0.1"):
        print("Connected successfully! Starting game...")
        client.in_menu = False  # Skip menu, go straight to game
    else:
        print("Could not connect. Starting in menu mode...")
    
    client.run()

if __name__ == "__main__":
    main()
