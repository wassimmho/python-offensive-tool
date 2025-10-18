#!/usr/bin/env python3
"""
EASY GAME LAUNCHER - Just run this file!
"""

import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("   🚀 3D SPACE COMBAT - QUICK START 🚀")
    print("=" * 50)
    print()
    print("📋 CONTROLS:")
    print("   W/A/S/D  - Move your spaceship")
    print("   Mouse    - Look around / Aim")
    print("   Click    - Shoot (destroy asteroids)")
    print("   ESC      - Pause / Menu")
    print()
    print("🎮 GAMEPLAY:")
    print("   • Destroy asteroids to earn points")
    print("   • Collect power-ups (colored squares)")
    print("   • Survive and get the highest score!")
    print()
    print("=" * 50)
    print()
    
    input("Press ENTER to start the game...")
    
    # Launch the game
    try:
        subprocess.run([sys.executable, 'game_client.py'], check=True)
    except KeyboardInterrupt:
        print("\n\nGame closed by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        input("Press ENTER to exit...")

if __name__ == "__main__":
    main()
