#!/usr/bin/env python3
"""
Test script for the 3D Space Combat Game
Tests both server and client functionality
"""

import subprocess
import time
import threading
import sys
import os

def test_server_startup():
    """Test if server starts without errors"""
    print("Testing server startup...")
    
    try:
        # Start server in background
        server_process = subprocess.Popen([
            sys.executable, 'game_server.py', '--host', '127.0.0.1', '--port', '5556'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Check if server is still running
        if server_process.poll() is None:
            print("Server started successfully")
            server_process.terminate()
            server_process.wait()
            return True
        else:
            stdout, stderr = server_process.communicate()
            print(f"Server failed to start: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"Error testing server: {e}")
        return False

def test_client_import():
    """Test if client imports without errors"""
    print("Testing client import...")
    
    try:
        # Try to import the client
        import game_client
        print("Client imports successfully")
        return True
    except Exception as e:
        print(f"Client import failed: {e}")
        return False

def test_dependencies():
    """Test if all dependencies are available"""
    print("Testing dependencies...")
    
    dependencies = ['pygame', 'numpy']
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"{dep} available")
        except ImportError:
            print(f"{dep} not available")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("3D Space Combat Game - Test Suite")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_client_import,
        test_server_startup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Test failed with exception: {e}")
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! Game is ready to play!")
        print()
        print("To start playing:")
        print("   1. Run: python launch_server.py")
        print("   2. Run: python launch_client.py")
        print("   3. Or use: start_game.bat")
    else:
        print("Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
