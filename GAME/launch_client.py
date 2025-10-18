#!/usr/bin/env python3
"""
Launch script for the 3D Space Combat Game Client
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_client import GameClient

def main():
    print("🎮 3D Space Combat Game Client Launcher")
    print("=" * 50)
    
    client = GameClient()
    client.run()

if __name__ == "__main__":
    main()
