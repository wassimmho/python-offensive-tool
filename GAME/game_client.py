#!/usr/bin/env python3
"""
3D Multiplayer Space Combat Game Client
Beautiful 3D graphics with pygame, multiplayer networking, and modern UI
"""

import pygame
import socket
import json
import threading
import time
import math
import numpy as np
from typing import Dict, List, Tuple, Optional
import sys
import os
import subprocess

# Import server for hosting functionality
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from game_server import GameServer
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False

# Initialize Pygame
pygame.init()

class Colors:
    """Color palette for the game"""
    # Space theme colors
    DEEP_SPACE = (5, 5, 15)
    DARK_BLUE = (20, 30, 60)
    NEON_BLUE = (0, 150, 255)
    NEON_GREEN = (0, 255, 150)
    NEON_PURPLE = (150, 0, 255)
    NEON_RED = (255, 50, 50)
    NEON_YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    
    # UI colors
    UI_BACKGROUND = (10, 15, 25)
    UI_BORDER = (50, 100, 150)
    UI_ACCENT = (100, 200, 255)

class Vector3:
    """3D Vector class for 3D math operations"""
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector3(self.x/length, self.y/length, self.z/length)
        return Vector3(0, 0, 0)

class Camera:
    """3D Camera for perspective projection"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = Vector3(0, 0, 0)
        self.rotation_x = 0
        self.rotation_y = 0
        self.fov = 60
        self.near = 0.1
        self.far = 2000
        
    def project_3d_to_2d(self, point3d):
        """Project 3D point to 2D screen coordinates"""
        # Translate relative to camera
        x = point3d.x - self.position.x
        y = point3d.y - self.position.y
        z = point3d.z - self.position.z
        
        # Apply rotation
        cos_x, sin_x = math.cos(self.rotation_x), math.sin(self.rotation_x)
        cos_y, sin_y = math.cos(self.rotation_y), math.sin(self.rotation_y)
        
        # Rotate around Y axis
        new_x = x * cos_y + z * sin_y
        new_z = -x * sin_y + z * cos_y
        
        # Rotate around X axis
        new_y = y * cos_x - new_z * sin_x
        new_z = y * sin_x + new_z * cos_x
        
        # Perspective projection
        if new_z > 0:
            f = self.fov
            screen_x = (new_x * f / new_z) * self.width / 2 + self.width / 2
            screen_y = (-new_y * f / new_z) * self.height / 2 + self.height / 2
            return (int(screen_x), int(screen_y), new_z)
        
        return None

class ParticleSystem:
    """Particle system for visual effects"""
    def __init__(self):
        self.particles = []
    
    def add_explosion(self, x, y, z, color, count=20):
        """Add explosion particles"""
        for _ in range(count):
            particle = {
                'x': x, 'y': y, 'z': z,
                'vx': (random.random() - 0.5) * 50,
                'vy': (random.random() - 0.5) * 50,
                'vz': (random.random() - 0.5) * 50,
                'life': 1.0,
                'color': color,
                'size': random.uniform(2, 8)
            }
            self.particles.append(particle)
    
    def update(self, dt):
        """Update all particles"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['z'] += particle['vz'] * dt
            particle['life'] -= dt * 2
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def render(self, screen, camera):
        """Render all particles"""
        for particle in self.particles:
            pos = camera.project_3d_to_2d(Vector3(particle['x'], particle['y'], particle['z']))
            if pos:
                size = max(1, int(particle['size'] * particle['life']))
                alpha = int(255 * particle['life'])
                color = (*particle['color'][:3], alpha)
                pygame.draw.circle(screen, color, (pos[0], pos[1]), size)

class GameClient:
    """Main game client class"""
    
    def _set_game_icon(self):
        """Create and set a custom game icon"""
        # Create a 64x64 icon surface for better quality
        icon_size = 64
        icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
        
        # Fill with transparent background
        icon.fill((0, 0, 0, 0))
        
        center_x, center_y = icon_size // 2, icon_size // 2
        
        # Draw a gradient background (dark space)
        for y in range(icon_size):
            alpha = int(50 * (1 - abs(y - center_y) / center_y))
            pygame.draw.line(icon, (10, 15, 25, alpha), (0, y), (icon_size, y))
        
        # Add some stars
        star_positions = [(8, 12), (45, 18), (22, 45), (55, 35), (12, 50)]
        for x, y in star_positions:
            pygame.draw.circle(icon, (200, 220, 255, 180), (x, y), 1)
            # Add sparkle effect
            pygame.draw.circle(icon, (255, 255, 255, 100), (x, y), 2)
        
        # Main spaceship body - sleek design
        ship_color = (0, 180, 255)  # Bright blue
        ship_shadow = (0, 100, 150)
        
        # Ship hull (elongated triangle)
        hull_points = [
            (center_x, center_y - 25),      # Nose
            (center_x - 12, center_y + 8),  # Left wing
            (center_x + 12, center_y + 8)   # Right wing
        ]
        
        # Draw ship shadow first
        shadow_points = [(x+1, y+1) for x, y in hull_points]
        pygame.draw.polygon(icon, ship_shadow, shadow_points)
        
        # Draw main ship hull
        pygame.draw.polygon(icon, ship_color, hull_points)
        
        # Ship details - cockpit
        cockpit_color = (0, 255, 200)  # Bright cyan
        pygame.draw.ellipse(icon, cockpit_color, (center_x - 4, center_y - 18, 8, 12))
        pygame.draw.ellipse(icon, (255, 255, 255, 150), (center_x - 3, center_y - 16, 6, 8))
        
        # Engine nacelles (side thrusters)
        engine_color = (255, 100, 50)  # Orange
        pygame.draw.ellipse(icon, engine_color, (center_x - 15, center_y - 2, 6, 16))
        pygame.draw.ellipse(icon, engine_color, (center_x + 9, center_y - 2, 6, 16))
        
        # Engine glow effects
        pygame.draw.ellipse(icon, (255, 200, 100, 150), (center_x - 14, center_y + 10, 4, 8))
        pygame.draw.ellipse(icon, (255, 200, 100, 150), (center_x + 10, center_y + 10, 4, 8))
        
        # Main engine (rear thruster)
        pygame.draw.ellipse(icon, (255, 150, 50), (center_x - 3, center_y + 10, 6, 12))
        pygame.draw.ellipse(icon, (255, 220, 100, 200), (center_x - 2, center_y + 12, 4, 6))
        
        # Wing details
        wing_color = (100, 200, 255)
        pygame.draw.polygon(icon, wing_color, [
            (center_x - 12, center_y + 8),
            (center_x - 18, center_y + 12),
            (center_x - 8, center_y + 12)
        ])
        pygame.draw.polygon(icon, wing_color, [
            (center_x + 12, center_y + 8),
            (center_x + 18, center_y + 12),
            (center_x + 8, center_y + 12)
        ])
        
        # Weapon systems (small turrets)
        turret_color = (255, 50, 50)
        pygame.draw.circle(icon, turret_color, (center_x - 8, center_y), 2)
        pygame.draw.circle(icon, turret_color, (center_x + 8, center_y), 2)
        
        # Energy shield effect (subtle glow around ship)
        shield_color = (100, 200, 255, 50)
        pygame.draw.ellipse(icon, shield_color, (center_x - 20, center_y - 30, 40, 50), 2)
        
        # Add some particle effects
        particle_color = (255, 200, 100, 120)
        pygame.draw.circle(icon, particle_color, (center_x - 20, center_y + 15), 2)
        pygame.draw.circle(icon, particle_color, (center_x + 20, center_y + 18), 1)
        pygame.draw.circle(icon, particle_color, (center_x - 25, center_y + 12), 1)
        
        # Set the icon
        pygame.display.set_icon(icon)
    
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("3D Space Combat - Multiplayer")
        
        # Set custom game icon
        self._set_game_icon()
        
        # Game state
        self.player_id = None
        self.game_state = {}
        self.player_data = {}
        self.connected = False
        self.socket = None
        
        # 3D rendering
        self.camera = Camera(self.screen_width, self.screen_height)
        self.particles = ParticleSystem()
        
        # UI
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Game state
        self.running = True
        self.in_menu = True
        self.server_ip = ""
        self.player_name = ""
        
        # Input
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_captured = False
        
        # Menu state
        self.menu_option = 0
        self.menu_options = ["Connect to Server", "Host Server", "Settings", "Exit"]
        
        # Server hosting
        self.server_thread = None
        self.server = None
        self.server_process = None
        
    def connect_to_server(self, host, port=5555):
        """Connect to game server"""
        try:
            # Add timeout for connection
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout
            
            # Try to connect
            self.socket.connect((host, port))
            self.connected = True
            
            # Remove timeout after connection
            self.socket.settimeout(None)
            
            # Start networking thread
            network_thread = threading.Thread(target=self._network_loop, daemon=True)
            network_thread.start()
            
            # Send join message
            join_msg = {
                'type': 'join',
                'name': self.player_name or f'Player_{int(time.time())}'
            }
            self._send_message(join_msg)
            
            print(f"Successfully connected to {host}:{port}")
            return True
            
        except socket.timeout:
            print(f"Connection timeout - Server {host}:{port} not responding")
            return False
        except ConnectionRefusedError:
            print(f"Connection refused - No server running at {host}:{port}")
            return False
        except socket.gaierror as e:
            print(f"DNS/Network error: {e}")
            return False
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def _network_loop(self):
        """Handle network communication"""
        buffer = ""
        
        while self.connected:
            try:
                # Receive data
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                buffer += data
                
                # Process complete messages
                while '\n' in buffer:
                    message_str, buffer = buffer.split('\n', 1)
                    if not message_str.strip():
                        continue
                        
                    try:
                        message = json.loads(message_str)
                        self._handle_server_message(message)
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
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
            self.in_menu = False
            # Capture mouse for gameplay
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(True)
            self.mouse_captured = True
            print(f"Connected as player {self.player_id}")
            
        elif message['type'] == 'game_state':
            self.game_state = message['game_state']
            
        elif message['type'] == 'player_join':
            print(f"{message['player_name']} joined the game")
            
        elif message['type'] == 'player_leave':
            print(f"Player {message['player_id']} left the game")
    
    def _send_message(self, message):
        """Send message to server"""
        if self.socket and self.connected:
            try:
                data = json.dumps(message) + '\n'  # Add newline delimiter
                self.socket.send(data.encode())
            except:
                self.connected = False
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(60) / 1000.0  # Delta time in seconds
            
            # Handle events
            self._handle_events()
            
            # Update game
            self._update(dt)
            
            # Render
            self._render()
            
            pygame.display.flip()
        
        # Clean up server process
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=2)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
        
        pygame.quit()
    
    def _handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                
                if event.key == pygame.K_ESCAPE:
                    if not self.in_menu:
                        self.in_menu = True
                        # Release mouse when going to menu
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                        self.mouse_captured = False
                    else:
                        self.running = False
                        
                elif self.in_menu:
                    self._handle_menu_input(event.key)
                    
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
                
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.in_menu:
                    self._handle_menu_click(event.pos)
    
    def _handle_menu_input(self, key):
        """Handle menu navigation"""
        if key == pygame.K_UP:
            self.menu_option = (self.menu_option - 1) % len(self.menu_options)
        elif key == pygame.K_DOWN:
            self.menu_option = (self.menu_option + 1) % len(self.menu_options)
        elif key == pygame.K_RETURN:
            self._select_menu_option()
    
    def _handle_menu_click(self, pos):
        """Handle menu clicks"""
        # Simple menu click detection
        if 400 <= pos[0] <= 800 and 300 <= pos[1] <= 500:
            option = (pos[1] - 300) // 50
            if 0 <= option < len(self.menu_options):
                self.menu_option = option
                self._select_menu_option()
    
    def _select_menu_option(self):
        """Select current menu option"""
        if self.menu_option == 0:  # Connect to Server
            self._show_connection_dialog()
        elif self.menu_option == 1:  # Host Server
            self._show_host_dialog()
        elif self.menu_option == 2:  # Settings
            self._show_settings_dialog()
        elif self.menu_option == 3:  # Exit
            self.running = False
    
    def _show_connection_dialog(self):
        """Show connection dialog"""
        # Simple input dialog
        font = pygame.font.Font(None, 36)
        input_text = ""
        input_active = True
        error_message = ""
        connecting = False
        
        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if input_text.strip() and not connecting:
                            self.server_ip = input_text.strip()
                            connecting = True
                            error_message = "Connecting..."
                            
                            # Try to connect in a separate thread to avoid blocking
                            import threading
                            def connect_thread():
                                nonlocal connecting, error_message, input_active
                                try:
                                    if self.connect_to_server(self.server_ip):
                                        input_active = False
                                    else:
                                        connecting = False
                                        error_message = "Failed to connect - Server not responding"
                                except Exception as e:
                                    connecting = False
                                    error_message = f"Connection error: {str(e)}"
                            
                            thread = threading.Thread(target=connect_thread, daemon=True)
                            thread.start()
                            
                    elif event.key == pygame.K_ESCAPE:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                        
                elif event.type == pygame.QUIT:
                    self.running = False
                    input_active = False
            
            # Render dialog
            self.screen.fill(Colors.UI_BACKGROUND)
            
            title = self.font_large.render("Connect to Server", True, Colors.WHITE)
            self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 150))
            
            prompt = font.render("Enter server IP:", True, Colors.WHITE)
            self.screen.blit(prompt, (self.screen_width//2 - prompt.get_width()//2, 250))
            
            input_surface = font.render(input_text, True, Colors.NEON_BLUE)
            self.screen.blit(input_surface, (self.screen_width//2 - input_surface.get_width()//2, 300))
            
            if not connecting:
                cursor = font.render("_", True, Colors.WHITE)
                self.screen.blit(cursor, (self.screen_width//2 + input_surface.get_width()//2 + 5, 300))
            
            # Show error or status message
            if error_message:
                if "Failed" in error_message or "error" in error_message:
                    error_surface = font.render(error_message, True, Colors.NEON_RED)
                else:
                    error_surface = font.render(error_message, True, Colors.NEON_YELLOW)
                self.screen.blit(error_surface, (self.screen_width//2 - error_surface.get_width()//2, 350))
            
            hint = self.font_small.render("Press Enter to connect, Escape to cancel", True, Colors.GRAY)
            self.screen.blit(hint, (self.screen_width//2 - hint.get_width()//2, 420))
            
            # Show common IP examples
            examples = self.font_small.render("Examples: 192.168.1.100, 127.0.0.1, your-friends-ip.com", True, Colors.GRAY)
            self.screen.blit(examples, (self.screen_width//2 - examples.get_width()//2, 450))
            
            pygame.display.flip()
    
    def _show_host_dialog(self):
        """Show host server dialog"""
        if not SERVER_AVAILABLE:
            message = self.font_medium.render("Server module not available!", True, Colors.NEON_RED)
            self.screen.blit(message, (self.screen_width//2 - message.get_width()//2, 400))
            pygame.display.flip()
            time.sleep(2)
            return
            
        # Start server as subprocess
        try:
            self.server_process = subprocess.Popen([
                sys.executable, 'game_server.py', '--host', 'localhost', '--port', '5555'
            ], cwd=os.path.dirname(os.path.abspath(__file__)))
        except Exception as e:
            message = self.font_medium.render("Failed to start server!", True, Colors.NEON_RED)
            self.screen.blit(message, (self.screen_width//2 - message.get_width()//2, 400))
            pygame.display.flip()
            time.sleep(2)
            return
        
        # Wait a moment for server to start
        time.sleep(1)
        
        # Connect to localhost
        self.server_ip = "127.0.0.1"
        
        # Try connecting multiple times
        for attempt in range(5):
            if self.connect_to_server(self.server_ip):
                return
            time.sleep(0.5)
        
        # Failed to connect after retries
        message = self.font_medium.render("Failed to start local server!", True, Colors.NEON_RED)
        self.screen.blit(message, (self.screen_width//2 - message.get_width()//2, 400))
        pygame.display.flip()
        time.sleep(2)
        
        # Kill the server process if it failed
        try:
            self.server_process.terminate()
        except:
            pass
    
    def _show_settings_dialog(self):
        """Show settings dialog"""
        # For now, just show a message
        message = self.font_medium.render("Settings feature coming soon!", True, Colors.NEON_YELLOW)
        self.screen.blit(message, (self.screen_width//2 - message.get_width()//2, 400))
        pygame.display.flip()
        time.sleep(2)
    
    def _update(self, dt):
        """Update game logic"""
        if not self.in_menu and self.connected:
            self._update_player_input()
            self._update_camera()
            self.particles.update(dt)
    
    def _update_player_input(self):
        """Update player input and send to server"""
        if not self.player_id or self.player_id not in self.game_state.get('players', {}):
            return
            
        player = self.game_state['players'][self.player_id]
        moved = False
        
        # Movement
        speed = player.get('speed', 5)
        angle = player.get('angle', 0)
        
        if pygame.K_w in self.keys_pressed:
            player['x'] += math.cos(angle) * speed
            player['z'] += math.sin(angle) * speed
            moved = True
        if pygame.K_s in self.keys_pressed:
            player['x'] -= math.cos(angle) * speed
            player['z'] -= math.sin(angle) * speed
            moved = True
        if pygame.K_a in self.keys_pressed:
            player['x'] += math.cos(angle - math.pi/2) * speed
            player['z'] += math.sin(angle - math.pi/2) * speed
            moved = True
        if pygame.K_d in self.keys_pressed:
            player['x'] += math.cos(angle + math.pi/2) * speed
            player['z'] += math.sin(angle + math.pi/2) * speed
            moved = True
        
        # Rotation - get relative mouse movement
        if self.mouse_captured:
            mouse_rel = pygame.mouse.get_rel()
            if abs(mouse_rel[0]) > 0:
                player['angle'] += mouse_rel[0] * 0.005  # Slower rotation
                moved = True
        
        # Shooting
        if pygame.mouse.get_pressed()[0] and self.mouse_captured:  # Left mouse button
            self._send_message({'type': 'shoot'})
        
        # Send update if moved
        if moved:
            self._send_message({
                'type': 'player_update',
                'x': player['x'],
                'y': player['y'],
                'z': player['z'],
                'angle': player['angle']
            })
    
    def _update_camera(self):
        """Update camera position"""
        if self.player_id and self.player_id in self.game_state.get('players', {}):
            player = self.game_state['players'][self.player_id]
            
            # Follow player with slight offset
            self.camera.position.x = player['x'] - 50
            self.camera.position.y = player['y'] + 30
            self.camera.position.z = player['z'] - 50
            
            # Camera rotation based on player angle
            self.camera.rotation_y = player['angle']
    
    def _render(self):
        """Render the game"""
        if self.in_menu:
            self._render_menu()
        else:
            self._render_game()
    
    def _render_menu(self):
        """Render main menu with beautiful effects"""
        # Animated background with gradient
        for y in range(self.screen_height):
            # Create gradient from deep space to dark blue
            ratio = y / self.screen_height
            r = int(5 + (20 - 5) * ratio)
            g = int(5 + (30 - 5) * ratio)
            b = int(15 + (60 - 15) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Enhanced animated starfield
        current_time = pygame.time.get_ticks()
        for i in range(150):
            x = (i * 37 + current_time // 50) % self.screen_width
            y = (i * 73) % self.screen_height
            brightness = (i * 13 + current_time // 10) % 255
            size = 1 + (i % 3)
            color = (brightness, brightness, min(255, brightness + 50))
            pygame.draw.circle(self.screen, color, (x, y), size)
        
        # Glowing title background
        title_y = 80
        title_bg_rect = pygame.Rect(self.screen_width//2 - 350, title_y - 20, 700, 120)
        # Glow effect
        for i in range(5):
            alpha = 30 - i * 5
            glow_rect = title_bg_rect.inflate(i * 4, i * 4)
            pygame.draw.rect(self.screen, (0, 100, 200, alpha), glow_rect, border_radius=15)
        
        # Main title with shadow
        title_font = pygame.font.Font(None, 72)
        title_text = "3D SPACE COMBAT"
        # Shadow
        title_shadow = title_font.render(title_text, True, (0, 0, 0))
        self.screen.blit(title_shadow, (self.screen_width//2 - title_shadow.get_width()//2 + 3, title_y + 3))
        # Main title with glow
        title = title_font.render(title_text, True, Colors.NEON_BLUE)
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, title_y))
        
        # Subtitle with animation
        subtitle_font = pygame.font.Font(None, 36)
        pulse = abs(math.sin(current_time / 500))
        subtitle_color = (0, int(150 + 105 * pulse), int(100 + 55 * pulse))
        subtitle = subtitle_font.render("⚔️ Multiplayer Edition ⚔️", True, subtitle_color)
        self.screen.blit(subtitle, (self.screen_width//2 - subtitle.get_width()//2, 160))
        
        # Decorative line
        line_y = 220
        pygame.draw.line(self.screen, Colors.NEON_BLUE, 
                        (self.screen_width//2 - 300, line_y), 
                        (self.screen_width//2 + 300, line_y), 2)
        
        # Menu options with beautiful boxes
        menu_start_y = 280
        for i, option in enumerate(self.menu_options):
            y = menu_start_y + i * 70
            
            # Menu box
            box_width = 400
            box_height = 55
            box_x = self.screen_width//2 - box_width//2
            box_rect = pygame.Rect(box_x, y, box_width, box_height)
            
            if i == self.menu_option:
                # Selected item - glowing box
                for j in range(3):
                    glow_rect = box_rect.inflate(j * 6, j * 6)
                    pygame.draw.rect(self.screen, (0, 150 + j * 20, 255, 50), glow_rect, border_radius=10)
                pygame.draw.rect(self.screen, (0, 100, 200), box_rect, border_radius=10)
                pygame.draw.rect(self.screen, Colors.NEON_BLUE, box_rect, 3, border_radius=10)
                text_color = Colors.WHITE
                
                # Animated selection indicator
                indicator_offset = int(10 * abs(math.sin(current_time / 200)))
                pygame.draw.polygon(self.screen, Colors.NEON_YELLOW, [
                    (box_x - 25 - indicator_offset, y + box_height//2),
                    (box_x - 10 - indicator_offset, y + box_height//2 - 8),
                    (box_x - 10 - indicator_offset, y + box_height//2 + 8)
                ])
            else:
                # Unselected item - subtle box
                pygame.draw.rect(self.screen, (20, 30, 50, 150), box_rect, border_radius=10)
                pygame.draw.rect(self.screen, (50, 80, 120), box_rect, 2, border_radius=10)
                text_color = Colors.LIGHT_GRAY
            
            # Option text
            text = self.font_medium.render(option, True, text_color)
            text_x = self.screen_width//2 - text.get_width()//2
            text_y = y + (box_height - text.get_height())//2
            self.screen.blit(text, (text_x, text_y))
        
        # Instructions at bottom
        instructions = [
            "Use ↑↓ Arrow Keys or Mouse to navigate",
            "Press ENTER or Click to select",
            "ESC to exit"
        ]
        inst_y = self.screen_height - 100
        for instruction in instructions:
            inst_text = self.font_small.render(instruction, True, Colors.GRAY)
            self.screen.blit(inst_text, (self.screen_width//2 - inst_text.get_width()//2, inst_y))
            inst_y += 25
        
        # Version/Credits
        version_text = self.font_small.render("v1.0 | Press H for Help", True, (80, 80, 120))
        self.screen.blit(version_text, (20, self.screen_height - 30))
    
    def _render_game(self):
        """Render the 3D game world"""
        # Background
        self.screen.fill(Colors.DEEP_SPACE)
        
        # Stars
        self._render_starfield()
        
        # Render 3D objects
        self._render_asteroids()
        self._render_players()
        self._render_projectiles()
        self._render_powerups()
        
        # Render particles
        self.particles.render(self.screen, self.camera)
        
        # Render UI
        self._render_game_ui()
    
    def _render_starfield(self):
        """Render animated starfield background"""
        for i in range(100):
            x = (i * 37) % self.screen_width
            y = (i * 73) % self.screen_height
            brightness = (i * 13) % 255
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (x, y), 1)
    
    def _render_asteroids(self):
        """Render 3D HUMAN ENEMIES with advanced graphics"""
        current_time = pygame.time.get_ticks()
        
        for asteroid in self.game_state.get('asteroids', []):
            pos = self.camera.project_3d_to_2d(Vector3(asteroid['x'], asteroid['y'], asteroid['z']))
            if pos:
                size = int(asteroid['size'] / (pos[2] + 1))  # Distance-based scaling
                size = max(8, min(60, size))
                
                # DRAW HUMAN ENEMY
                enemy_height = size * 2
                enemy_width = size
                
                # Shadow beneath enemy
                shadow_width = enemy_width * 1.2
                shadow_ellipse = pygame.Rect(pos[0] - shadow_width // 2, pos[1] + enemy_height // 2 - 5, 
                                             shadow_width, 10)
                pygame.draw.ellipse(self.screen, (20, 20, 30, 150), shadow_ellipse)
                
                # Body position
                body_x = pos[0]
                body_y = pos[1]
                
                # Animated walk cycle
                walk_cycle = abs(math.sin(current_time / 200 + asteroid['rotation']))
                
                # === LEGS ===
                leg_width = size // 5
                leg_height = enemy_height // 3
                leg_color = (60, 60, 80)
                leg_highlight = (80, 80, 120)
                
                # Left leg (animated)
                left_leg_offset = int(5 * walk_cycle)
                left_leg = pygame.Rect(body_x - enemy_width // 4 - leg_width // 2 + left_leg_offset, 
                                      body_y + enemy_height // 3, leg_width, leg_height)
                pygame.draw.rect(self.screen, leg_color, left_leg, border_radius=3)
                pygame.draw.rect(self.screen, leg_highlight, left_leg, 1, border_radius=3)
                
                # Right leg (animated opposite)
                right_leg_offset = int(5 * (1 - walk_cycle))
                right_leg = pygame.Rect(body_x + enemy_width // 4 - leg_width // 2 + right_leg_offset, 
                                       body_y + enemy_height // 3, leg_width, leg_height)
                pygame.draw.rect(self.screen, leg_color, right_leg, border_radius=3)
                pygame.draw.rect(self.screen, leg_highlight, right_leg, 1, border_radius=3)
                
                # === BODY/TORSO ===
                torso_width = enemy_width
                torso_height = enemy_height // 2
                
                # Body glow (hostile red aura)
                for i in range(3):
                    glow_rect = pygame.Rect(body_x - torso_width // 2 - i * 2, 
                                           body_y - torso_height // 2 - i * 2,
                                           torso_width + i * 4, torso_height + i * 4)
                    pygame.draw.rect(self.screen, (255, 0, 0, 30 - i * 8), glow_rect, border_radius=5)
                
                # Main body
                body_rect = pygame.Rect(body_x - torso_width // 2, body_y - torso_height // 2, 
                                       torso_width, torso_height)
                # Body gradient effect
                for y in range(int(torso_height)):
                    ratio = y / torso_height
                    r = int(100 + 50 * ratio)
                    g = int(20 + 20 * ratio)
                    b = int(20 + 30 * ratio)
                    pygame.draw.line(self.screen, (r, g, b), 
                                   (body_rect.left, body_rect.top + y),
                                   (body_rect.right, body_rect.top + y))
                
                pygame.draw.rect(self.screen, (180, 40, 40), body_rect, 2, border_radius=5)
                
                # Armor plates
                plate_color = (100, 30, 30)
                pygame.draw.circle(self.screen, plate_color, (body_x, body_y), size // 4)
                pygame.draw.circle(self.screen, (150, 50, 50), (body_x, body_y), size // 4, 1)
                
                # === ARMS (with weapons) ===
                arm_width = size // 6
                arm_height = enemy_height // 3
                arm_color = (80, 40, 40)
                
                # Left arm
                left_arm_x = body_x - torso_width // 2 - arm_width // 2
                left_arm = pygame.Rect(left_arm_x, body_y - arm_height // 2, arm_width, arm_height)
                pygame.draw.rect(self.screen, arm_color, left_arm, border_radius=3)
                
                # Weapon in left hand (gun)
                weapon_size = size // 3
                weapon_rect = pygame.Rect(left_arm_x - weapon_size, body_y - 2, weapon_size, 4)
                pygame.draw.rect(self.screen, (150, 150, 150), weapon_rect)
                pygame.draw.circle(self.screen, (200, 100, 0), (weapon_rect.left, body_y), 3)
                
                # Right arm
                right_arm_x = body_x + torso_width // 2 - arm_width // 2
                right_arm = pygame.Rect(right_arm_x, body_y - arm_height // 2, arm_width, arm_height)
                pygame.draw.rect(self.screen, arm_color, right_arm, border_radius=3)
                
                # === HEAD ===
                head_size = size // 2
                head_y = body_y - torso_height // 2 - head_size // 2
                
                # Head shadow/glow
                pygame.draw.circle(self.screen, (50, 20, 20), (body_x + 2, head_y + 2), head_size // 2)
                
                # Main head (helmet)
                pygame.draw.circle(self.screen, (120, 60, 60), (body_x, head_y), head_size // 2)
                pygame.draw.circle(self.screen, (180, 80, 80), (body_x, head_y), head_size // 2, 2)
                
                # Visor (glowing red eyes)
                visor_width = head_size // 2
                visor_height = head_size // 4
                visor_pulse = abs(math.sin(current_time / 300))
                
                # Left eye
                left_eye_x = body_x - head_size // 5
                eye_color = (255, int(50 + 100 * visor_pulse), 0)
                pygame.draw.ellipse(self.screen, eye_color, 
                                   (left_eye_x - 3, head_y - 2, 6, visor_height))
                pygame.draw.ellipse(self.screen, (255, 200, 100), 
                                   (left_eye_x - 2, head_y - 1, 4, visor_height - 2))
                
                # Right eye
                right_eye_x = body_x + head_size // 5
                pygame.draw.ellipse(self.screen, eye_color, 
                                   (right_eye_x - 3, head_y - 2, 6, visor_height))
                pygame.draw.ellipse(self.screen, (255, 200, 100), 
                                   (right_eye_x - 2, head_y - 1, 4, visor_height - 2))
                
                # Helmet antenna
                antenna_color = (200, 100, 50)
                pygame.draw.line(self.screen, antenna_color, 
                               (body_x, head_y - head_size // 2),
                               (body_x, head_y - head_size // 2 - 5), 2)
                pygame.draw.circle(self.screen, Colors.NEON_RED, 
                                 (body_x, head_y - head_size // 2 - 5), 2)
                
                # Health bar above enemy
                health_bar_width = enemy_width
                health_bar_height = 4
                health_bar_y = body_y - enemy_height // 2 - 15
                
                # Health bar background
                pygame.draw.rect(self.screen, (40, 40, 40), 
                               (body_x - health_bar_width // 2, health_bar_y, 
                                health_bar_width, health_bar_height))
                
                # Health fill (assume enemies have health property)
                health_percent = asteroid.get('health', 100) / 100
                health_fill = int(health_bar_width * health_percent)
                if health_fill > 0:
                    health_color = (255, int(200 * health_percent), 0)
                    pygame.draw.rect(self.screen, health_color,
                                   (body_x - health_bar_width // 2, health_bar_y,
                                    health_fill, health_bar_height))
                
                pygame.draw.rect(self.screen, Colors.NEON_RED, 
                               (body_x - health_bar_width // 2, health_bar_y,
                                health_bar_width, health_bar_height), 1)
                
                # Enemy label
                enemy_label = self.font_small.render("⚠️ HOSTILE", True, Colors.NEON_RED)
                label_x = body_x - enemy_label.get_width() // 2
                label_y = health_bar_y - 15
                
                # Label background
                label_bg = pygame.Surface((enemy_label.get_width() + 6, enemy_label.get_height() + 2), 
                                         pygame.SRCALPHA)
                pygame.draw.rect(label_bg, (100, 20, 20, 180), 
                               (0, 0, enemy_label.get_width() + 6, enemy_label.get_height() + 2), 
                               border_radius=3)
                self.screen.blit(label_bg, (label_x - 3, label_y - 1))
                self.screen.blit(enemy_label, (label_x, label_y))
    
    def _render_players(self):
        """Render 3D player ships with beautiful effects"""
        current_time = pygame.time.get_ticks()
        
        for player_id, player in self.game_state.get('players', {}).items():
            pos = self.camera.project_3d_to_2d(Vector3(player['x'], player['y'], player['z']))
            if pos:
                size = 20
                is_local = player_id == self.player_id
                
                # Colors
                if is_local:
                    ship_color = Colors.NEON_GREEN
                    glow_color = (0, 255, 150)
                else:
                    ship_color = Colors.NEON_BLUE
                    glow_color = (0, 150, 255)
                
                # Ship shadow
                shadow_points = []
                for i in range(3):
                    angle = player['angle'] + i * 2 * math.pi / 3
                    x = pos[0] + (size + 2) * math.cos(angle) + 2
                    y = pos[1] + (size + 2) * math.sin(angle) + 2
                    shadow_points.append((x, y))
                pygame.draw.polygon(self.screen, (20, 20, 30), shadow_points)
                
                # Glow effect around ship
                for glow_layer in range(3, 0, -1):
                    glow_points = []
                    for i in range(3):
                        angle = player['angle'] + i * 2 * math.pi / 3
                        x = pos[0] + (size + glow_layer * 3) * math.cos(angle)
                        y = pos[1] + (size + glow_layer * 3) * math.sin(angle)
                        glow_points.append((x, y))
                    alpha = 30 // glow_layer
                    glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    pygame.draw.polygon(glow_surf, (*glow_color, alpha), 
                                      [(p[0] - pos[0] + size * 2, p[1] - pos[1] + size * 2) for p in glow_points])
                    self.screen.blit(glow_surf, (pos[0] - size * 2, pos[1] - size * 2))
                
                # Main ship body
                points = []
                for i in range(3):
                    angle = player['angle'] + i * 2 * math.pi / 3
                    x = pos[0] + size * math.cos(angle)
                    y = pos[1] + size * math.sin(angle)
                    points.append((x, y))
                
                pygame.draw.polygon(self.screen, ship_color, points)
                pygame.draw.polygon(self.screen, Colors.WHITE, points, 2)
                
                # Engine glow at rear
                rear_angle = player['angle'] + math.pi
                engine_pulse = abs(math.sin(current_time / 100))
                engine_size = 5 + int(3 * engine_pulse)
                engine_x = pos[0] + (size - 5) * math.cos(rear_angle)
                engine_y = pos[1] + (size - 5) * math.sin(rear_angle)
                
                # Engine glow layers
                for layer in range(3):
                    e_size = engine_size + layer * 2
                    e_alpha = 150 - layer * 40
                    pygame.draw.circle(self.screen, (255, 150, 50, e_alpha), 
                                     (int(engine_x), int(engine_y)), e_size)
                pygame.draw.circle(self.screen, (255, 200, 100), 
                                 (int(engine_x), int(engine_y)), engine_size - 2)
                
                # Cockpit detail
                cockpit_x = pos[0] + 10 * math.cos(player['angle'])
                cockpit_y = pos[1] + 10 * math.sin(player['angle'])
                pygame.draw.circle(self.screen, (100, 200, 255), (int(cockpit_x), int(cockpit_y)), 4)
                pygame.draw.circle(self.screen, Colors.WHITE, (int(cockpit_x), int(cockpit_y)), 2)
                
                # Player name with background
                if player_id != self.player_id:
                    name = player['name']
                    name_text = self.font_small.render(name, True, Colors.WHITE)
                    name_bg_rect = pygame.Rect(pos[0] - name_text.get_width()//2 - 5, 
                                               pos[1] - 40, 
                                               name_text.get_width() + 10, 
                                               name_text.get_height() + 4)
                    # Semi-transparent background
                    name_bg = pygame.Surface((name_bg_rect.width, name_bg_rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(name_bg, (10, 15, 30, 180), (0, 0, name_bg_rect.width, name_bg_rect.height), border_radius=5)
                    self.screen.blit(name_bg, name_bg_rect)
                    self.screen.blit(name_text, (name_bg_rect.x + 5, name_bg_rect.y + 2))
                
                # Shield indicator if active
                if player.get('shield', 0) > 0:
                    shield_pulse = abs(math.sin(current_time / 200))
                    shield_radius = size + 8 + int(2 * shield_pulse)
                    shield_color = (100, 200, 255, int(80 + 50 * shield_pulse))
                    pygame.draw.circle(self.screen, shield_color, pos[:2], shield_radius, 2)
    
    def _render_projectiles(self):
        """Render 3D projectiles with trails"""
        for projectile in self.game_state.get('projectiles', []):
            pos = self.camera.project_3d_to_2d(Vector3(projectile['x'], projectile['y'], projectile['z']))
            if pos:
                is_mine = projectile['player_id'] == self.player_id
                
                if is_mine:
                    core_color = Colors.NEON_YELLOW
                    glow_color = (255, 200, 0)
                else:
                    core_color = Colors.NEON_RED
                    glow_color = (255, 100, 50)
                
                # Glow effect
                for i in range(3, 0, -1):
                    glow_size = 3 + i * 2
                    alpha = 80 // i
                    pygame.draw.circle(self.screen, (*glow_color, alpha), (pos[0], pos[1]), glow_size)
                
                # Core projectile
                pygame.draw.circle(self.screen, core_color, (pos[0], pos[1]), 4)
                pygame.draw.circle(self.screen, Colors.WHITE, (pos[0], pos[1]), 2)
                
                # Trail effect
                angle = math.atan2(projectile.get('vy', 0), projectile.get('vx', 0))
                for i in range(3):
                    trail_dist = (i + 1) * 8
                    trail_x = pos[0] - trail_dist * math.cos(angle)
                    trail_y = pos[1] - trail_dist * math.sin(angle)
                    trail_size = 3 - i
                    trail_alpha = 100 - i * 30
                    pygame.draw.circle(self.screen, (*glow_color, trail_alpha), 
                                     (int(trail_x), int(trail_y)), trail_size)
    
    def _render_powerups(self):
        """Render 3D powerups with glowing effects"""
        current_time = pygame.time.get_ticks()
        
        for powerup in self.game_state.get('powerups', []):
            if powerup['active']:
                pos = self.camera.project_3d_to_2d(Vector3(powerup['x'], powerup['y'], powerup['z']))
                if pos:
                    size = 15
                    pulse = abs(math.sin(current_time / 300))
                    animated_size = size + int(3 * pulse)
                    
                    # Color and icon mapping
                    color_map = {
                        'health': (Colors.NEON_RED, '❤️'),
                        'ammo': (Colors.NEON_YELLOW, '🔫'),
                        'shield': (Colors.NEON_BLUE, '🛡️'),
                        'speed': (Colors.NEON_GREEN, '⚡')
                    }
                    color, icon = color_map.get(powerup['type'], (Colors.WHITE, '⭐'))
                    
                    # Outer glow rings
                    for ring in range(3, 0, -1):
                        ring_size = animated_size + ring * 5
                        ring_alpha = 50 - ring * 10
                        pygame.draw.circle(self.screen, (*color, ring_alpha), pos[:2], ring_size, 2)
                    
                    # Rotating square
                    points = []
                    for i in range(4):
                        angle = i * math.pi / 2 + powerup['rotation']
                        x = pos[0] + animated_size * math.cos(angle)
                        y = pos[1] + animated_size * math.sin(angle)
                        points.append((x, y))
                    
                    # Shadow
                    shadow_points = [(x + 2, y + 2) for x, y in points]
                    pygame.draw.polygon(self.screen, (20, 20, 30), shadow_points)
                    
                    # Main shape with gradient
                    pygame.draw.polygon(self.screen, color, points)
                    pygame.draw.polygon(self.screen, Colors.WHITE, points, 2)
                    
                    # Inner detail - smaller rotated square
                    inner_points = []
                    for i in range(4):
                        angle = i * math.pi / 2 - powerup['rotation']
                        x = pos[0] + (animated_size * 0.5) * math.cos(angle)
                        y = pos[1] + (animated_size * 0.5) * math.sin(angle)
                        inner_points.append((x, y))
                    pygame.draw.polygon(self.screen, Colors.WHITE, inner_points)
                    
                    # Type label below
                    type_text = self.font_small.render(icon, True, color)
                    self.screen.blit(type_text, (pos[0] - type_text.get_width()//2, pos[1] + size + 5))
    
    def _render_game_ui(self):
        """Render ULTRA HIGH-QUALITY game UI overlay"""
        if not self.player_id or self.player_id not in self.game_state.get('players', {}):
            return
            
        player = self.game_state['players'][self.player_id]
        current_time = pygame.time.get_ticks()
        
        # === ULTRA PROFESSIONAL TOP HUD BAR ===
        # Full-width top bar with animated gradient
        hud_height = 110
        scan_line = (current_time // 20) % hud_height
        
        for y in range(hud_height):
            alpha = int(230 - (y / hud_height) * 230)
            # Add scan line effect
            if abs(y - scan_line) < 2:
                alpha = min(255, alpha + 50)
            pygame.draw.line(self.screen, (5, 10, 20, alpha), (0, y), (self.screen_width, y))
        
        # Animated hexagon pattern overlay
        hex_size = 30
        for x in range(0, self.screen_width, hex_size):
            for y in range(0, hud_height, hex_size):
                offset_x = (y // hex_size) % 2 * (hex_size // 2)
                hex_alpha = int(20 * abs(math.sin((current_time / 1000) + x / 100)))
                pygame.draw.circle(self.screen, (0, 100, 150, hex_alpha), 
                                 (x + offset_x, y), hex_size // 4, 1)
        
        # Decorative top border with animated glow
        for i in range(4):
            glow_intensity = abs(math.sin(current_time / 500 + i * 0.2))
            alpha = int((120 - i * 25) * glow_intensity)
            pygame.draw.line(self.screen, (0, 150 - i * 30, 255, alpha), 
                           (0, hud_height + i), (self.screen_width, hud_height + i), 2)
        
        # Corner accents
        corner_size = 40
        corner_color = (0, 200, 255, 150)
        # Top-left corner
        pygame.draw.line(self.screen, corner_color, (0, 0), (corner_size, 0), 3)
        pygame.draw.line(self.screen, corner_color, (0, 0), (0, corner_size), 3)
        # Top-right corner
        pygame.draw.line(self.screen, corner_color, 
                        (self.screen_width - corner_size, 0), (self.screen_width, 0), 3)
        pygame.draw.line(self.screen, corner_color, 
                        (self.screen_width, 0), (self.screen_width, corner_size), 3)
        
        # === LEFT SIDE - PLAYER STATUS ===
        status_x = 30
        status_y = 15
        
        # Player avatar circle with animated border
        avatar_size = 70
        avatar_center = (status_x + avatar_size // 2, status_y + avatar_size // 2)
        
        # Animated spinning border
        for layer in range(3):
            offset = (current_time / 500 + layer * 0.5) % (2 * math.pi)
            for i in range(8):
                angle = i * math.pi / 4 + offset
                start_angle = angle - 0.3
                end_angle = angle + 0.3
                arc_points = []
                for a in [start_angle, (start_angle + end_angle) / 2, end_angle]:
                    x = avatar_center[0] + (avatar_size // 2 + layer * 3) * math.cos(a)
                    y = avatar_center[1] + (avatar_size // 2 + layer * 3) * math.sin(a)
                    arc_points.append((int(x), int(y)))
                if len(arc_points) >= 2:
                    pygame.draw.lines(self.screen, (0, 255 - layer * 50, 255), False, arc_points, 3)
        
        # Avatar background
        pygame.draw.circle(self.screen, (20, 30, 50), avatar_center, avatar_size // 2)
        pygame.draw.circle(self.screen, Colors.NEON_BLUE, avatar_center, avatar_size // 2, 3)
        
        # Player icon/initial
        player_initial = self.font_large.render(player.get('name', 'P')[0].upper(), True, Colors.WHITE)
        self.screen.blit(player_initial, 
                        (avatar_center[0] - player_initial.get_width() // 2,
                         avatar_center[1] - player_initial.get_height() // 2))
        
        # === HEALTH BAR - Modern horizontal design ===
        health_x = status_x + avatar_size + 25
        health_y = status_y + 10
        health_width = 350
        health_height = 22
        
        # Health label
        health_label = self.font_small.render("HEALTH", True, (180, 180, 200))
        self.screen.blit(health_label, (health_x, health_y - 18))
        
        # Health bar container with depth
        pygame.draw.rect(self.screen, (15, 20, 35), 
                        (health_x - 2, health_y - 2, health_width + 4, health_height + 4), 
                        border_radius=12)
        pygame.draw.rect(self.screen, (25, 35, 55), 
                        (health_x, health_y, health_width, health_height), 
                        border_radius=10)
        
        # Health fill with smooth gradient
        health_percent = player['health'] / 100
        health_fill_width = int(health_percent * health_width)
        
        if health_fill_width > 0:
            # Create health gradient surface
            health_surf = pygame.Surface((health_fill_width, health_height), pygame.SRCALPHA)
            for i in range(health_fill_width):
                ratio = i / health_width
                # Color transitions: Green -> Yellow -> Red
                if health_percent > 0.6:
                    r = int(50 + 205 * (1 - health_percent) * 2.5)
                    g = int(255 - 100 * ratio)
                    b = 20
                elif health_percent > 0.3:
                    r = 255
                    g = int(200 - 150 * (0.6 - health_percent) * 3.3)
                    b = 0
                else:
                    r = 255
                    g = int(50 - 50 * health_percent / 0.3)
                    b = int(20 - 20 * health_percent / 0.3)
                
                # Add shine effect
                shine = int(30 * abs(math.sin(i / 20)))
                pygame.draw.line(health_surf, (min(255, r + shine), min(255, g + shine), b), 
                               (i, 0), (i, health_height))
            
            self.screen.blit(health_surf, (health_x, health_y))
        
        # Health bar shine overlay
        shine_height = health_height // 3
        shine_surf = pygame.Surface((health_fill_width, shine_height), pygame.SRCALPHA)
        pygame.draw.rect(shine_surf, (255, 255, 255, 40), (0, 0, health_fill_width, shine_height))
        self.screen.blit(shine_surf, (health_x, health_y + 2))
        
        # Health border glow
        if health_percent < 0.3:
            pulse = abs(math.sin(current_time / 200))
            pygame.draw.rect(self.screen, (255, 0, 0, int(100 * pulse)), 
                           (health_x - 3, health_y - 3, health_width + 6, health_height + 6), 
                           3, border_radius=12)
        
        pygame.draw.rect(self.screen, (100, 150, 200), 
                        (health_x, health_y, health_width, health_height), 
                        2, border_radius=10)
        
        # Health percentage text
        health_text = self.font_medium.render(f"{int(player['health'])}%", True, Colors.WHITE)
        text_shadow = self.font_medium.render(f"{int(player['health'])}%", True, (0, 0, 0))
        self.screen.blit(text_shadow, (health_x + health_width + 12, health_y - 2))
        self.screen.blit(health_text, (health_x + health_width + 10, health_y - 4))
        
        # === SHIELD BAR ===
        shield_y = health_y + 32
        
        # Shield label
        shield_label = self.font_small.render("SHIELD", True, (150, 200, 255))
        self.screen.blit(shield_label, (health_x, shield_y - 18))
        
        # Shield bar
        pygame.draw.rect(self.screen, (15, 20, 35), 
                        (health_x - 2, shield_y - 2, health_width + 4, health_height + 4), 
                        border_radius=12)
        pygame.draw.rect(self.screen, (25, 35, 55), 
                        (health_x, shield_y, health_width, health_height), 
                        border_radius=10)
        
        shield_percent = player['shield'] / 100
        shield_fill_width = int(shield_percent * health_width)
        
        if shield_fill_width > 0:
            # Animated shield gradient
            shield_surf = pygame.Surface((shield_fill_width, health_height), pygame.SRCALPHA)
            for i in range(shield_fill_width):
                ratio = i / health_width
                wave = abs(math.sin((i / 20) + (current_time / 300)))
                b = int(150 + 105 * ratio + 50 * wave)
                pygame.draw.line(shield_surf, (0, int(150 + 50 * wave), min(255, b)), 
                               (i, 0), (i, health_height))
            
            self.screen.blit(shield_surf, (health_x, shield_y))
            
            # Shield shine
            shine_surf = pygame.Surface((shield_fill_width, health_height // 3), pygame.SRCALPHA)
            pygame.draw.rect(shine_surf, (200, 220, 255, 60), (0, 0, shield_fill_width, health_height // 3))
            self.screen.blit(shine_surf, (health_x, shield_y + 2))
        
        pygame.draw.rect(self.screen, (100, 200, 255), 
                        (health_x, shield_y, health_width, health_height), 
                        2, border_radius=10)
        
        shield_text = self.font_medium.render(f"{int(player['shield'])}%", True, (150, 220, 255))
        text_shadow = self.font_medium.render(f"{int(player['shield'])}%", True, (0, 0, 0))
        self.screen.blit(text_shadow, (health_x + health_width + 12, shield_y - 2))
        self.screen.blit(shield_text, (health_x + health_width + 10, shield_y - 4))
        
        # === RIGHT SIDE - AMMO & SCORE ===
        right_x = self.screen_width - 320
        
        # Ammo display with magazine visual
        ammo_y = status_y + 5
        ammo_box_width = 140
        ammo_box_height = 45
        
        # Ammo container
        ammo_surf = pygame.Surface((ammo_box_width, ammo_box_height), pygame.SRCALPHA)
        pygame.draw.rect(ammo_surf, (20, 25, 40, 230), (0, 0, ammo_box_width, ammo_box_height), border_radius=10)
        
        ammo_color = Colors.NEON_YELLOW if player['ammo'] > 10 else Colors.NEON_RED
        if player['ammo'] <= 10:
            pulse = abs(math.sin(current_time / 150))
            pygame.draw.rect(ammo_surf, (255, 0, 0, int(50 * pulse)), 
                           (0, 0, ammo_box_width, ammo_box_height), 3, border_radius=10)
        else:
            pygame.draw.rect(ammo_surf, (100, 150, 200, 150), 
                           (0, 0, ammo_box_width, ammo_box_height), 2, border_radius=10)
        
        self.screen.blit(ammo_surf, (right_x, ammo_y))
        
        # Ammo icon and text
        ammo_icon = self.font_medium.render("🔫", True, ammo_color)
        self.screen.blit(ammo_icon, (right_x + 10, ammo_y + 8))
        
        ammo_label = self.font_small.render("AMMO", True, (150, 150, 170))
        self.screen.blit(ammo_label, (right_x + 45, ammo_y + 5))
        
        ammo_count = self.font_large.render(str(player['ammo']), True, Colors.WHITE)
        self.screen.blit(ammo_count, (right_x + 45, ammo_y + 18))
        
        # Score display with glowing effect
        score_y = ammo_y + ammo_box_height + 10
        score_box_width = 140
        score_box_height = 45
        
        # Score container with glow
        score_surf = pygame.Surface((score_box_width + 10, score_box_height + 10), pygame.SRCALPHA)
        
        # Glowing border animation
        glow_pulse = abs(math.sin(current_time / 400))
        for i in range(3):
            glow_alpha = int((50 - i * 15) * glow_pulse)
            pygame.draw.rect(score_surf, (255, 200, 0, glow_alpha), 
                           (i, i, score_box_width + 10 - i * 2, score_box_height + 10 - i * 2), 
                           border_radius=12)
        
        pygame.draw.rect(score_surf, (20, 25, 40, 240), 
                        (5, 5, score_box_width, score_box_height), border_radius=10)
        pygame.draw.rect(score_surf, (255, 200, 0, 200), 
                        (5, 5, score_box_width, score_box_height), 2, border_radius=10)
        
        self.screen.blit(score_surf, (right_x - 5, score_y - 5))
        
        # Score icon and text
        score_icon = self.font_medium.render("⭐", True, Colors.NEON_YELLOW)
        self.screen.blit(score_icon, (right_x + 10, score_y + 8))
        
        score_label = self.font_small.render("SCORE", True, (255, 220, 100))
        self.screen.blit(score_label, (right_x + 45, score_y + 5))
        
        score_count = self.font_large.render(str(player['score']), True, Colors.WHITE)
        score_shadow = self.font_large.render(str(player['score']), True, (0, 0, 0))
        self.screen.blit(score_shadow, (right_x + 46, score_y + 19))
        self.screen.blit(score_count, (right_x + 45, score_y + 18))
        
        # === THREAT LEVEL & STATISTICS ===
        # Threat level indicator (left side below HUD)
        threat_x = 30
        threat_y = hud_height + 20
        threat_width = 200
        threat_height = 60
        
        # Threat panel background
        threat_surf = pygame.Surface((threat_width, threat_height), pygame.SRCALPHA)
        pygame.draw.rect(threat_surf, (30, 10, 10, 220), (0, 0, threat_width, threat_height), border_radius=10)
        
        # Animated warning border
        warning_pulse = abs(math.sin(current_time / 300))
        border_alpha = int(150 + 105 * warning_pulse)
        pygame.draw.rect(threat_surf, (255, 50, 50, border_alpha), 
                        (0, 0, threat_width, threat_height), 3, border_radius=10)
        self.screen.blit(threat_surf, (threat_x, threat_y))
        
        # Threat level calculation
        enemy_count = len(self.game_state.get('asteroids', []))
        threat_level = min(5, enemy_count // 4 + 1)
        threat_names = ["LOW", "MODERATE", "HIGH", "CRITICAL", "EXTREME"]
        threat_colors = [Colors.NEON_GREEN, Colors.NEON_YELLOW, (255, 150, 0), Colors.NEON_RED, (200, 0, 200)]
        
        threat_color = threat_colors[threat_level - 1]
        threat_name = threat_names[threat_level - 1]
        
        # Threat label
        threat_title = self.font_small.render("⚠️ THREAT LEVEL", True, (200, 200, 200))
        self.screen.blit(threat_title, (threat_x + 10, threat_y + 5))
        
        # Threat level bars
        for i in range(5):
            bar_x = threat_x + 10 + i * 35
            bar_y = threat_y + 28
            bar_width = 30
            bar_height = 20
            
            if i < threat_level:
                # Active bar with glow
                pygame.draw.rect(self.screen, (50, 20, 20), 
                               (bar_x, bar_y, bar_width, bar_height), border_radius=3)
                pygame.draw.rect(self.screen, threat_color, 
                               (bar_x + 2, bar_y + 2, bar_width - 4, bar_height - 4), border_radius=2)
                # Glow effect
                if warning_pulse > 0.5:
                    pygame.draw.rect(self.screen, (*threat_color[:3], int(100 * warning_pulse)), 
                                   (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 
                                   border_radius=4)
            else:
                # Inactive bar
                pygame.draw.rect(self.screen, (40, 40, 40), 
                               (bar_x, bar_y, bar_width, bar_height), border_radius=3)
                pygame.draw.rect(self.screen, (60, 60, 60), 
                               (bar_x, bar_y, bar_width, bar_height), 1, border_radius=3)
        
        # Threat name
        threat_text = self.font_small.render(threat_name, True, threat_color)
        self.screen.blit(threat_text, (threat_x + 10, threat_y + 48))
        
        # Enemy counter
        enemy_count_text = self.font_small.render(f"👤 {enemy_count} Hostiles", True, Colors.NEON_RED)
        self.screen.blit(enemy_count_text, (threat_x + 95, threat_y + 48))
        
        # === MINI-MAP CORNER (Top Right) ===
        minimap_size = 180
        minimap_x = self.screen_width - minimap_size - 20
        minimap_y = hud_height + 20
        
        # Mini-map background
        minimap_surf = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        pygame.draw.rect(minimap_surf, (10, 15, 25, 200), (0, 0, minimap_size, minimap_size), border_radius=15)
        pygame.draw.rect(minimap_surf, (0, 150, 255, 150), (0, 0, minimap_size, minimap_size), 3, border_radius=15)
        
        # Grid lines
        for i in range(5):
            line_pos = i * minimap_size // 4
            pygame.draw.line(minimap_surf, (50, 70, 100, 100), (line_pos, 0), (line_pos, minimap_size))
            pygame.draw.line(minimap_surf, (50, 70, 100, 100), (0, line_pos), (minimap_size, line_pos))
        
        self.screen.blit(minimap_surf, (minimap_x, minimap_y))
        
        # Mini-map title
        minimap_title = self.font_small.render("RADAR", True, (100, 200, 255))
        self.screen.blit(minimap_title, (minimap_x + minimap_size // 2 - minimap_title.get_width() // 2, 
                                         minimap_y - 20))
        
        # Draw objects on minimap
        map_center_x = minimap_x + minimap_size // 2
        map_center_y = minimap_y + minimap_size // 2
        map_scale = 0.5
        
        # Draw asteroids
        for asteroid in self.game_state.get('asteroids', [])[:20]:  # Limit for performance
            rel_x = (asteroid['x'] - player['x']) * map_scale
            rel_z = (asteroid['z'] - player['z']) * map_scale
            map_x = map_center_x + int(rel_x)
            map_y = map_center_y + int(rel_z)
            if minimap_x < map_x < minimap_x + minimap_size and minimap_y < map_y < minimap_y + minimap_size:
                pygame.draw.circle(self.screen, (150, 150, 150), (map_x, map_y), 3)
        
        # Draw other players
        for pid, p in self.game_state.get('players', {}).items():
            if pid != self.player_id:
                rel_x = (p['x'] - player['x']) * map_scale
                rel_z = (p['z'] - player['z']) * map_scale
                map_x = map_center_x + int(rel_x)
                map_y = map_center_y + int(rel_z)
                if minimap_x < map_x < minimap_x + minimap_size and minimap_y < map_y < minimap_y + minimap_size:
                    pygame.draw.circle(self.screen, Colors.NEON_RED, (map_x, map_y), 4)
                    pygame.draw.circle(self.screen, Colors.WHITE, (map_x, map_y), 4, 1)
        
        # Draw player at center (pulsing)
        player_pulse = 6 + int(2 * abs(math.sin(current_time / 200)))
        pygame.draw.circle(self.screen, Colors.NEON_GREEN, (map_center_x, map_center_y), player_pulse)
        pygame.draw.circle(self.screen, Colors.WHITE, (map_center_x, map_center_y), player_pulse, 2)
        
        # Player direction indicator
        dir_length = 15
        dir_x = map_center_x + int(dir_length * math.cos(player['angle']))
        dir_y = map_center_y + int(dir_length * math.sin(player['angle']))
        pygame.draw.line(self.screen, Colors.WHITE, (map_center_x, map_center_y), (dir_x, dir_y), 2)
        
        # === ULTRA PROFESSIONAL CROSSHAIR ===
        center_x, center_y = self.screen_width // 2, self.screen_height // 2
        
        # Dynamic crosshair based on aim/state
        pulse = abs(math.sin(current_time / 250))
        crosshair_color = (int(100 + 155 * pulse), 255, int(100 + 155 * pulse))
        
        # Outer targeting ring
        ring_size = 25 + int(5 * pulse)
        for i in range(3):
            alpha = 150 - i * 40
            pygame.draw.circle(self.screen, (*crosshair_color[:2], alpha), 
                             (center_x, center_y), ring_size + i, 1)
        
        # Dynamic corner brackets
        bracket_size = 20
        bracket_offset = 12
        bracket_thickness = 3
        
        # Top-left bracket
        pygame.draw.line(self.screen, crosshair_color, 
                        (center_x - bracket_offset, center_y - bracket_offset),
                        (center_x - bracket_offset - bracket_size, center_y - bracket_offset), 
                        bracket_thickness)
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x - bracket_offset, center_y - bracket_offset),
                        (center_x - bracket_offset, center_y - bracket_offset - bracket_size), 
                        bracket_thickness)
        
        # Top-right
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x + bracket_offset, center_y - bracket_offset),
                        (center_x + bracket_offset + bracket_size, center_y - bracket_offset), 
                        bracket_thickness)
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x + bracket_offset, center_y - bracket_offset),
                        (center_x + bracket_offset, center_y - bracket_offset - bracket_size), 
                        bracket_thickness)
        
        # Bottom-left
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x - bracket_offset, center_y + bracket_offset),
                        (center_x - bracket_offset - bracket_size, center_y + bracket_offset), 
                        bracket_thickness)
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x - bracket_offset, center_y + bracket_offset),
                        (center_x - bracket_offset, center_y + bracket_offset + bracket_size), 
                        bracket_thickness)
        
        # Bottom-right
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x + bracket_offset, center_y + bracket_offset),
                        (center_x + bracket_offset + bracket_size, center_y + bracket_offset), 
                        bracket_thickness)
        pygame.draw.line(self.screen, crosshair_color,
                        (center_x + bracket_offset, center_y + bracket_offset),
                        (center_x + bracket_offset, center_y + bracket_offset + bracket_size), 
                        bracket_thickness)
        
        # Center dot with glow
        for i in range(3, 0, -1):
            pygame.draw.circle(self.screen, (255, 100, 100, 50 * i), (center_x, center_y), i * 2)
        pygame.draw.circle(self.screen, Colors.NEON_RED, (center_x, center_y), 3)
        pygame.draw.circle(self.screen, Colors.WHITE, (center_x, center_y), 1)
        
        # === BOTTOM STATUS BAR ===
        bottom_y = self.screen_height - 50
        bottom_height = 50
        
        # Gradient background
        for y in range(bottom_height):
            alpha = int((y / bottom_height) * 220)
            pygame.draw.line(self.screen, (5, 10, 20, alpha), 
                           (0, bottom_y + bottom_height - y), 
                           (self.screen_width, bottom_y + bottom_height - y))
        
        # Top border glow
        for i in range(3):
            pygame.draw.line(self.screen, (0, 150 - i * 30, 255, 100 - i * 30), 
                           (0, bottom_y - i), (self.screen_width, bottom_y - i), 2)
        
        # Controls hint with icons
        controls_y = bottom_y + 15
        control_items = [
            ("WASD", "Move", Colors.NEON_BLUE),
            ("MOUSE", "Aim", Colors.NEON_GREEN),
            ("CLICK", "Shoot", Colors.NEON_RED),
            ("ESC", "Menu", Colors.NEON_YELLOW)
        ]
        
        total_width = sum([self.font_small.render(f"{k}: {v}", True, Colors.WHITE).get_width() 
                          for k, v, _ in control_items]) + 60
        start_x = (self.screen_width - total_width) // 2
        
        for key, action, color in control_items:
            # Key box
            key_text = self.font_small.render(key, True, color)
            action_text = self.font_small.render(action, True, Colors.LIGHT_GRAY)
            
            # Key background
            key_bg = pygame.Surface((key_text.get_width() + 10, 22), pygame.SRCALPHA)
            pygame.draw.rect(key_bg, (30, 40, 60, 200), (0, 0, key_text.get_width() + 10, 22), border_radius=5)
            pygame.draw.rect(key_bg, color, (0, 0, key_text.get_width() + 10, 22), 1, border_radius=5)
            
            self.screen.blit(key_bg, (start_x, controls_y))
            self.screen.blit(key_text, (start_x + 5, controls_y + 3))
            self.screen.blit(action_text, (start_x + key_text.get_width() + 15, controls_y + 3))
            
            start_x += key_text.get_width() + action_text.get_width() + 35
        
        # FPS and ping indicators
        fps_text = self.font_small.render(f"FPS: 60", True, Colors.NEON_GREEN)
        self.screen.blit(fps_text, (self.screen_width - 100, controls_y + 3))
        
        # Kills indicator (if available)
        kills = sum(1 for ast in self.game_state.get('asteroids', []) if not ast.get('active', True))
        kills_text = self.font_small.render(f"💥 Kills: {kills}", True, Colors.NEON_YELLOW)
        self.screen.blit(kills_text, (30, controls_y + 3))

if __name__ == "__main__":
    import random
    
    # Add random import for particle system
    random = __import__('random')
    
    client = GameClient()
    client.run()
