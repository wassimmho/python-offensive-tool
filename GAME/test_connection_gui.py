#!/usr/bin/env python3
"""
Simple GUI connection tester for the 3D Space Combat Game
Helps diagnose connection issues
"""

import tkinter as tk
from tkinter import messagebox, ttk
import socket
import json
import threading
import time

class ConnectionTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("3D Space Combat - Connection Tester")
        self.root.geometry("500x400")
        self.root.configure(bg='#0a0f19')
        
        # Variables
        self.host_var = tk.StringVar(value="127.0.0.1")
        self.port_var = tk.StringVar(value="5555")
        self.result_text = tk.Text(self.root, height=15, width=60, bg='#1a1f29', fg='white')
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="3D Space Combat - Connection Tester", 
                        font=('Arial', 16, 'bold'), fg='#00ffff', bg='#0a0f19')
        title.pack(pady=10)
        
        # Input frame
        input_frame = tk.Frame(self.root, bg='#0a0f19')
        input_frame.pack(pady=10)
        
        # Host input
        tk.Label(input_frame, text="Server IP:", fg='white', bg='#0a0f19').grid(row=0, column=0, padx=5)
        host_entry = tk.Entry(input_frame, textvariable=self.host_var, width=20)
        host_entry.grid(row=0, column=1, padx=5)
        
        # Port input
        tk.Label(input_frame, text="Port:", fg='white', bg='#0a0f19').grid(row=0, column=2, padx=5)
        port_entry = tk.Entry(input_frame, textvariable=self.port_var, width=10)
        port_entry.grid(row=0, column=3, padx=5)
        
        # Test button
        test_btn = tk.Button(self.root, text="Test Connection", 
                           command=self.test_connection, bg='#0066cc', fg='white',
                           font=('Arial', 12, 'bold'))
        test_btn.pack(pady=10)
        
        # Results
        tk.Label(self.root, text="Test Results:", fg='white', bg='#0a0f19', 
                font=('Arial', 12, 'bold')).pack(pady=(20,5))
        
        # Result text area
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.result_text.yview)
        
        # Common IP examples
        examples_frame = tk.Frame(self.root, bg='#0a0f19')
        examples_frame.pack(pady=10)
        
        tk.Label(examples_frame, text="Common IP Examples:", fg='#ffff00', bg='#0a0f19').pack()
        examples_text = "• 127.0.0.1 (localhost)\n• 192.168.1.100 (local network)\n• your-public-ip (internet)"
        tk.Label(examples_frame, text=examples_text, fg='#cccccc', bg='#0a0f19', 
                justify=tk.LEFT).pack()
        
    def log(self, message):
        """Add message to result text"""
        self.result_text.insert(tk.END, f"{message}\n")
        self.result_text.see(tk.END)
        self.root.update()
        
    def test_connection(self):
        """Test connection to server"""
        host = self.host_var.get().strip()
        port = self.port_var.get().strip()
        
        if not host or not port:
            messagebox.showerror("Error", "Please enter both IP and Port")
            return
            
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
            
        # Clear previous results
        self.result_text.delete(1.0, tk.END)
        
        # Run test in separate thread
        thread = threading.Thread(target=self._run_test, args=(host, port), daemon=True)
        thread.start()
        
    def _run_test(self, host, port):
        """Run the actual connection test"""
        self.log("=" * 50)
        self.log("CONNECTION TEST STARTED")
        self.log("=" * 50)
        self.log(f"Testing connection to {host}:{port}")
        self.log("")
        
        try:
            # Step 1: Create socket
            self.log("1. Creating socket...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            self.log("   ✓ Socket created")
            
            # Step 2: Try to connect
            self.log("2. Attempting connection...")
            start_time = time.time()
            sock.connect((host, port))
            connect_time = time.time() - start_time
            self.log(f"   ✓ Connected successfully! ({connect_time:.2f}s)")
            
            # Step 3: Send join message
            self.log("3. Sending join message...")
            join_msg = {
                'type': 'join',
                'name': 'ConnectionTester'
            }
            data = json.dumps(join_msg) + '\n'
            sock.send(data.encode())
            self.log("   ✓ Join message sent")
            
            # Step 4: Wait for response
            self.log("4. Waiting for server response...")
            sock.settimeout(5)
            response = sock.recv(4096).decode()
            
            if response:
                self.log("   ✓ Received response from server")
                
                # Parse response
                messages = response.strip().split('\n')
                for msg_str in messages:
                    if msg_str.strip():
                        try:
                            message = json.loads(msg_str)
                            msg_type = message.get('type', 'unknown')
                            self.log(f"   ✓ Message type: {msg_type}")
                            
                            if msg_type == 'init':
                                player_id = message.get('player_id', 'unknown')
                                self.log(f"   ✓ Player ID: {player_id}")
                                self.log("   ✓ Server is running the game correctly!")
                            elif msg_type == 'error':
                                error_msg = message.get('message', 'Unknown error')
                                self.log(f"   ⚠ Server error: {error_msg}")
                        except json.JSONDecodeError:
                            self.log(f"   ⚠ Could not parse message: {msg_str[:50]}...")
            else:
                self.log("   ⚠ No response from server")
            
            # Step 5: Send test message
            self.log("5. Testing message exchange...")
            test_msg = {
                'type': 'player_update',
                'x': 100,
                'y': 0,
                'z': 100,
                'angle': 1.57
            }
            data = json.dumps(test_msg) + '\n'
            sock.send(data.encode())
            self.log("   ✓ Test message sent")
            
            # Step 6: Check for updates
            self.log("6. Checking for game state updates...")
            sock.settimeout(2)
            try:
                update_data = sock.recv(4096).decode()
                if update_data:
                    update_messages = update_data.strip().split('\n')
                    self.log(f"   ✓ Received {len(update_messages)} update message(s)")
                    self.log("   ✓ Real-time communication working!")
                else:
                    self.log("   ⚠ No updates received (this might be normal)")
            except socket.timeout:
                self.log("   ⚠ No updates received (timeout - might be normal)")
            
            # Close connection
            sock.close()
            self.log("7. Connection closed")
            
            self.log("")
            self.log("=" * 50)
            self.log("✓ CONNECTION TEST PASSED!")
            self.log("=" * 50)
            self.log("The server is working correctly!")
            self.log("You should be able to connect with the game client.")
            
        except socket.timeout:
            self.log("")
            self.log("❌ CONNECTION TIMEOUT")
            self.log("The server is not responding. Possible causes:")
            self.log("• Server is not running")
            self.log("• Wrong IP address or port")
            self.log("• Firewall blocking the connection")
            self.log("• Network connectivity issues")
            
        except ConnectionRefusedError:
            self.log("")
            self.log("❌ CONNECTION REFUSED")
            self.log("No server is running at this address. Check:")
            self.log("• Is the server running?")
            self.log("• Is the IP address correct?")
            self.log("• Is the port correct? (default: 5555)")
            
        except socket.gaierror as e:
            self.log("")
            self.log("❌ NETWORK ERROR")
            self.log(f"DNS/Network error: {e}")
            self.log("Check:")
            self.log("• Is the IP address valid?")
            self.log("• Do you have internet connection?")
            self.log("• Is the hostname correct?")
            
        except Exception as e:
            self.log("")
            self.log("❌ UNEXPECTED ERROR")
            self.log(f"Error: {e}")
            self.log("This is an unexpected error. Please try again.")
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting Connection Tester...")
    tester = ConnectionTester()
    tester.run()
