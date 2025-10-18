#!/usr/bin/env python3
"""
Simple localhost launcher for the 3D Space Combat Game
This script makes it easy to start the server and client for local testing
"""

import subprocess
import sys
import os
import time
import threading

def print_banner():
    """Print the game banner"""
    print("=" * 60)
    print("    3D SPACE COMBAT - LOCALHOST LAUNCHER")
    print("=" * 60)
    print()

def show_menu():
    """Show the main menu"""
    print("Choose an option:")
    print("1. Start Server (Host Game)")
    print("2. Start Client (Join Game)")
    print("3. Start Both (Server + Client)")
    print("4. Test Connection")
    print("5. Exit")
    print()

def start_server():
    """Start the game server"""
    print("Starting Game Server...")
    print("Server will be accessible at: localhost:5555")
    print("Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Start server with proper arguments
        subprocess.run([sys.executable, "launch_server.py", "--host", "localhost", "--port", "5555"])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

def start_client():
    """Start the game client"""
    print("Starting Game Client...")
    print("When prompted, enter: localhost")
    print("Press Ctrl+C to stop the client")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "launch_client.py"])
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Error starting client: {e}")

def start_both():
    """Start both server and client"""
    print("Starting both Server and Client...")
    print("This will open two windows:")
    print("1. Server window (leave this running)")
    print("2. Client window (use this to play)")
    print("-" * 40)
    
    try:
        # Start server in background
        print("Starting server...")
        server_process = subprocess.Popen([sys.executable, "launch_server.py", "--host", "localhost", "--port", "5555"])
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("Starting client...")
        print("In the client window, enter: localhost")
        print("Press Enter here to continue...")
        input()
        
        # Start client
        client_process = subprocess.Popen([sys.executable, "launch_client.py"])
        
        print("Both server and client are running!")
        print("Close this window to stop both processes.")
        print("Press Enter to stop...")
        input()
        
        # Clean up
        server_process.terminate()
        client_process.terminate()
        server_process.wait()
        client_process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping both server and client...")
        try:
            server_process.terminate()
            client_process.terminate()
        except:
            pass
    except Exception as e:
        print(f"Error: {e}")

def test_connection():
    """Test the connection"""
    print("Testing localhost connection...")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, "test_localhost.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Connection test PASSED!")
            print("Localhost is working correctly.")
        else:
            print("Connection test FAILED!")
            print("Output:", result.stdout)
            print("Error:", result.stderr)
            
    except Exception as e:
        print(f"Error running test: {e}")
    
    print("\nPress Enter to continue...")
    input()

def main():
    """Main function"""
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    while True:
        print_banner()
        show_menu()
        
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                start_server()
            elif choice == "2":
                start_client()
            elif choice == "3":
                start_both()
            elif choice == "4":
                test_connection()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
