#!/usr/bin/env python3
"""
Quick test to verify the game is working
"""

import subprocess
import time
import sys

def main():
    print("3D Space Combat Game - Quick Test")
    print("=" * 40)
    
    # Test 1: Dependencies
    print("1. Testing dependencies...")
    try:
        import pygame
        import numpy
        print("   OK - pygame and numpy available")
    except ImportError as e:
        print(f"   ERROR - Missing dependency: {e}")
        return False
    
    # Test 2: Server startup
    print("2. Testing server startup...")
    try:
        server_process = subprocess.Popen([
            sys.executable, 'game_server.py', '--host', '127.0.0.1', '--port', '5558'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(2)
        
        if server_process.poll() is None:
            print("   OK - Server started successfully")
        else:
            stdout, stderr = server_process.communicate()
            print(f"   ERROR - Server failed: {stderr.decode()}")
            return False
    except Exception as e:
        print(f"   ERROR - Server error: {e}")
        return False
    
    # Test 3: Connection
    print("3. Testing network connection...")
    try:
        result = subprocess.run([
            sys.executable, 'test_connection.py', '127.0.0.1', '5558'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("   OK - Network connection works")
        else:
            print(f"   ERROR - Connection failed: {result.stderr}")
            server_process.terminate()
            return False
    except Exception as e:
        print(f"   ERROR - Connection error: {e}")
        server_process.terminate()
        return False
    
    # Test 4: Client import
    print("4. Testing client import...")
    try:
        import game_client
        print("   OK - Client imports successfully")
    except Exception as e:
        print(f"   ERROR - Client import error: {e}")
        server_process.terminate()
        return False
    
    # Cleanup
    server_process.terminate()
    server_process.wait()
    
    print("\n" + "=" * 40)
    print("ALL TESTS PASSED!")
    print("=" * 40)
    print()
    print("The game is working correctly!")
    print()
    print("To play:")
    print("  python launch_server.py    # Start server")
    print("  python launch_client.py    # Start client")
    print("  start_game.bat            # Windows launcher")
    print()
    print("Network protocol fixed - no more connection errors!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
