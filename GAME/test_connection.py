#!/usr/bin/env python3
"""
Simple connection test script
Tests if client can connect to server
"""

import socket
import json
import time
import sys

def test_connection(host='localhost', port=5555):
    """Test connection to server"""
    print("=" * 60)
    print("CONNECTION TEST")
    print("=" * 60)
    print(f"Testing connection to {host}:{port}")
    
    try:
        # Create socket
        print("1. Creating socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        # Connect
        print("2. Connecting to server...")
        sock.connect((host, port))
        print("Connected successfully!")
        
        # Send join message first
        print("3. Sending join message...")
        join_msg = {
            'type': 'join',
            'name': 'TestPlayer'
        }
        data = json.dumps(join_msg) + '\n'
        sock.send(data.encode())
        print("Join message sent!")
        
        # Wait for init message
        print("4. Waiting for initialization message...")
        sock.settimeout(5)
        data = sock.recv(4096).decode()
        
        if data:
            print("Received data from server!")
            # Handle newline-delimited messages
            messages = data.strip().split('\n')
            for msg_str in messages:
                if msg_str.strip():
                    try:
                        message = json.loads(msg_str)
                        print(f"Message type: {message.get('type')}")
                        if message.get('type') == 'init':
                            print(f"Player ID: {message.get('player_id')}")
                            print(f"Game state players: {len(message.get('game_state', {}).get('players', {}))}")
                        break
                    except json.JSONDecodeError:
                        continue
        else:
            print("No data received")
        
        # Send a test message
        print("5. Sending test message...")
        test_msg = {
            'type': 'player_update',
            'x': 10,
            'y': 0,
            'z': 10,
            'angle': 1.57
        }
        # Use newline delimiter
        data = json.dumps(test_msg) + '\n'
        sock.send(data.encode())
        print("Message sent!")
        
        # Wait a bit for game state
        time.sleep(1)
        print("6. Checking for game state updates...")
        sock.settimeout(2)
        try:
            data = sock.recv(4096).decode()
            if data:
                # Handle multiple newline-delimited messages
                messages = data.strip().split('\n')
                print(f"Received {len(messages)} message(s)")
                for msg_str in messages[:3]:  # Show first 3
                    if msg_str.strip():
                        try:
                            message = json.loads(msg_str)
                            print(f"   - Type: {message.get('type')}")
                        except json.JSONDecodeError:
                            continue
        except socket.timeout:
            print("No update received (timeout)")
        
        # Close
        print("7. Closing connection...")
        sock.close()
        print("Connection closed")
        
        print("=" * 60)
        print("CONNECTION TEST PASSED")
        print("=" * 60)
        return True
        
    except socket.timeout:
        print("Connection timeout")
        print("=" * 60)
        return False
    except ConnectionRefusedError:
        print("Connection refused - Is the server running?")
        print("=" * 60)
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False

if __name__ == "__main__":
    host = "localhost"
    if len(sys.argv) > 1:
        host = sys.argv[1]
    
    success = test_connection(host)
    sys.exit(0 if success else 1)