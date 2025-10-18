#!/usr/bin/env python3
"""
Minimal game test - simplified version to test basic functionality
"""

import pygame
import socket
import json
import threading
import time
import math
import sys
import os

# Initialize pygame
pygame.init()

class MinimalGame:
    def __init__(self):
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Minimal Game Test")
        
        self.running = True
        self.connected = False
        self.player_id = None
        self.game_state = {}
        
        # Simple player data
        self.player = {
            'x': 0,
            'y': 0,
            'z': 0,
            'angle': 0,
            'speed': 5
        }
        
        # Input
        self.keys_pressed = set()
        
        # Font
        self.font = pygame.font.Font(None, 36)
        
    def connect_to_server(self, host='localhost', port=5555):
        """Try to connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((host, port))
            self.socket.settimeout(None)
            
            # Start network thread
            network_thread = threading.Thread(target=self._network_loop, daemon=True)
            network_thread.start()
            
            # Send join message
            join_msg = {
                'type': 'join',
                'name': 'TestPlayer'
            }
            self._send_message(join_msg)
            
            self.connected = True
            print(f"Connected to {host}:{port}")
            return True
            
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False
    
    def _network_loop(self):
        """Handle network communication"""
        buffer = ""
        
        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                
                # Process complete messages
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if message_str.strip():
                        try:
                            message = json.loads(message_str)
                            self._handle_server_message(message)
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                print(f"Network error: {e}")
                self.connected = False
                break
    
    def _handle_server_message(self, message):
        """Handle messages from server"""
        if message['type'] == 'init':
            self.player_id = message['player_id']
            self.game_state = message['game_state']
            print(f"Initialized as player {self.player_id}")
            
        elif message['type'] == 'game_state':
            self.game_state = message['game_state']
    
    def _send_message(self, message):
        """Send message to server"""
        if self.connected:
            try:
                data = json.dumps(message) + '\n'
                self.socket.send(data.encode())
            except:
                self.connected = False
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
    
    def update(self):
        """Update game logic"""
        if self.connected and self.player_id:
            # Handle movement
            moved = False
            
            if pygame.K_w in self.keys_pressed:
                self.player['x'] += math.cos(self.player['angle']) * self.player['speed']
                self.player['z'] += math.sin(self.player['angle']) * self.player['speed']
                moved = True
                
            if pygame.K_s in self.keys_pressed:
                self.player['x'] -= math.cos(self.player['angle']) * self.player['speed']
                self.player['z'] -= math.sin(self.player['angle']) * self.player['speed']
                moved = True
                
            if pygame.K_a in self.keys_pressed:
                self.player['x'] += math.cos(self.player['angle'] - math.pi/2) * self.player['speed']
                self.player['z'] += math.sin(self.player['angle'] - math.pi/2) * self.player['speed']
                moved = True
                
            if pygame.K_d in self.keys_pressed:
                self.player['x'] += math.cos(self.player['angle'] + math.pi/2) * self.player['speed']
                self.player['z'] += math.sin(self.player['angle'] + math.pi/2) * self.player['speed']
                moved = True
            
            # Send update if moved
            if moved:
                self._send_message({
                    'type': 'player_update',
                    'x': self.player['x'],
                    'y': self.player['y'],
                    'z': self.player['z'],
                    'angle': self.player['angle']
                })
    
    def render(self):
        """Render the game"""
        self.screen.fill((0, 0, 20))  # Dark blue background
        
        # Show status
        if not self.connected:
            text = self.font.render("NOT CONNECTED", True, (255, 0, 0))
        elif not self.player_id:
            text = self.font.render("CONNECTING...", True, (255, 255, 0))
        else:
            text = self.font.render(f"PLAYER {self.player_id} - CONNECTED", True, (0, 255, 0))
        
        self.screen.blit(text, (10, 10))
        
        # Show player position
        if self.player_id:
            pos_text = self.font.render(f"Position: {self.player['x']:.1f}, {self.player['z']:.1f}", True, (255, 255, 255))
            self.screen.blit(pos_text, (10, 50))
        
        # Show controls
        controls = [
            "WASD - Move",
            "ESC - Exit"
        ]
        
        for i, control in enumerate(controls):
            text = self.font.render(control, True, (200, 200, 200))
            self.screen.blit(text, (10, 100 + i * 30))
        
        # Show other players if any
        if self.game_state.get('players'):
            y_pos = 200
            for pid, player in self.game_state['players'].items():
                if pid != self.player_id:
                    text = self.font.render(f"Player {pid}: {player.get('name', 'Unknown')}", True, (100, 200, 255))
                    self.screen.blit(text, (10, y_pos))
                    y_pos += 25
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        print("Minimal Game Test")
        print("=" * 40)
        print("This is a simplified version to test basic functionality")
        print("Make sure the server is running first!")
        print()
        
        # Try to connect
        if not self.connect_to_server():
            print("Failed to connect to server. Make sure it's running.")
            print("Press Enter to continue anyway (offline mode)...")
            input()
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(60)
        
        if self.connected:
            self.socket.close()
        
        pygame.quit()

if __name__ == "__main__":
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    game = MinimalGame()
    game.run()
