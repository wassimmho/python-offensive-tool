#!/usr/bin/env python3
"""
3D Multiplayer Space Combat Game Server
Handles multiple players, game state synchronization, and networking
"""

import socket
import threading
import json
import time
import math
import random
from typing import Dict, List, Tuple
import uuid

class GameServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        
        # Game state
        self.players: Dict[str, Dict] = {}
        self.asteroids: List[Dict] = []
        self.projectiles: List[Dict] = []
        self.powerups: List[Dict] = {}
        self.game_started = False
        self.max_players = 8
        
        # Networking
        self.connections: Dict[str, socket.socket] = {}
        self.lock = threading.Lock()
        
        # Initialize game world
        self._initialize_world()
        
    def _initialize_world(self):
        """Initialize the game world with asteroids and powerups"""
        # Create asteroids
        for i in range(20):
            asteroid = {
                'id': str(uuid.uuid4()),
                'x': random.uniform(-1000, 1000),
                'y': random.uniform(-1000, 1000),
                'z': random.uniform(-1000, 1000),
                'size': random.uniform(20, 80),
                'rotation': random.uniform(0, 2 * math.pi),
                'rotation_speed': random.uniform(-0.1, 0.1),
                'health': 100
            }
            self.asteroids.append(asteroid)
            
        # Create powerups
        for i in range(10):
            powerup = {
                'id': str(uuid.uuid4()),
                'x': random.uniform(-800, 800),
                'y': random.uniform(-800, 800),
                'z': random.uniform(-800, 800),
                'type': random.choice(['health', 'ammo', 'shield', 'speed']),
                'active': True,
                'rotation': 0
            }
            self.powerups[powerup['id']] = powerup
    
    def start(self):
        """Start the game server"""
        print(f"Starting 3D Space Combat Game Server on {self.host}:{self.port}")
        print(f"Server ready for connections...")
        
        self.socket.listen()
        
        # Start game loop in separate thread
        game_thread = threading.Thread(target=self._game_loop, daemon=True)
        game_thread.start()
        
        while True:
            try:
                conn, addr = self.socket.accept()
                print(f"New connection from {addr}")
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(conn, addr), 
                    daemon=True
                )
                client_thread.start()
                
            except Exception as e:
                print(f"Error accepting connection: {e}")
    
    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]):
        """Handle individual client connection"""
        player_id = None
        buffer = ""
        
        try:
            while True:
                # Receive data
                data = conn.recv(4096).decode('utf-8')
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
                        
                        with self.lock:
                            if message['type'] == 'join':
                                player_id = self._handle_join(conn, addr, message)
                            elif message['type'] == 'player_update':
                                self._handle_player_update(player_id, message)
                            elif message['type'] == 'shoot':
                                self._handle_shoot(player_id, message)
                            elif message['type'] == 'disconnect':
                                break
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
        finally:
            if player_id:
                self._remove_player(player_id)
            conn.close()
    
    def _handle_join(self, conn: socket.socket, addr: Tuple[str, int], message: Dict) -> str:
        """Handle player joining the game"""
        if len(self.players) >= self.max_players:
            conn.send(json.dumps({'type': 'error', 'message': 'Server full'}).encode())
            return None
            
        player_id = str(uuid.uuid4())
        player_name = message.get('name', f'Player_{len(self.players) + 1}')
        
        # Create player
        player = {
            'id': player_id,
            'name': player_name,
            'x': random.uniform(-200, 200),
            'y': random.uniform(-200, 200),
            'z': random.uniform(-200, 200),
            'angle': 0,
            'health': 100,
            'ammo': 50,
            'shield': 100,
            'speed': 5,
            'score': 0,
            'last_update': time.time(),
            'addr': addr
        }
        
        self.players[player_id] = player
        self.connections[player_id] = conn
        
        # Send initialization message
        init_message = {
            'type': 'init',
            'player_id': player_id,
            'game_state': self._get_game_state()
        }
        
        conn.send((json.dumps(init_message) + '\n').encode())
        
        print(f"Player {player_name} ({player_id}) joined the game")
        
        # Notify other players
        self._broadcast_player_join(player_id, player_name)
        
        return player_id
    
    def _handle_player_update(self, player_id: str, message: Dict):
        """Handle player position/movement updates"""
        if player_id not in self.players:
            return
            
        player = self.players[player_id]
        player['x'] = message.get('x', player['x'])
        player['y'] = message.get('y', player['y'])
        player['z'] = message.get('z', player['z'])
        player['angle'] = message.get('angle', player['angle'])
        player['last_update'] = time.time()
    
    def _handle_shoot(self, player_id: str, message: Dict):
        """Handle projectile shooting"""
        if player_id not in self.players:
            return
            
        player = self.players[player_id]
        
        if player['ammo'] <= 0:
            return
            
        player['ammo'] -= 1
        
        # Create projectile
        projectile = {
            'id': str(uuid.uuid4()),
            'player_id': player_id,
            'x': player['x'],
            'y': player['y'],
            'z': player['z'],
            'angle': player['angle'],
            'speed': 15,
            'life': 3.0,  # 3 seconds
            'damage': 25
        }
        
        self.projectiles.append(projectile)
    
    def _remove_player(self, player_id: str):
        """Remove player from game"""
        if player_id in self.players:
            player_name = self.players[player_id]['name']
            del self.players[player_id]
            
        if player_id in self.connections:
            del self.connections[player_id]
            
        print(f"Player {player_name} left the game")
        
        # Notify other players
        self._broadcast_player_leave(player_id)
    
    def _broadcast_player_join(self, player_id: str, player_name: str):
        """Broadcast player join to all other players"""
        message = {
            'type': 'player_join',
            'player_id': player_id,
            'player_name': player_name
        }
        self._broadcast(message, exclude=player_id)
    
    def _broadcast_player_leave(self, player_id: str):
        """Broadcast player leave to all other players"""
        message = {
            'type': 'player_leave',
            'player_id': player_id
        }
        self._broadcast(message, exclude=player_id)
    
    def _broadcast(self, message: Dict, exclude: str = None):
        """Broadcast message to all connected players"""
        data = json.dumps(message) + '\n'  # Add newline delimiter
        
        for pid, conn in list(self.connections.items()):
            if pid != exclude:
                try:
                    conn.send(data.encode())
                except:
                    # Connection failed, remove player
                    if pid in self.players:
                        self._remove_player(pid)
    
    def _get_game_state(self) -> Dict:
        """Get current game state"""
        return {
            'players': {pid: {k: v for k, v in p.items() if k != 'addr'} 
                       for pid, p in self.players.items()},
            'asteroids': self.asteroids,
            'projectiles': self.projectiles,
            'powerups': list(self.powerups.values())
        }
    
    def _game_loop(self):
        """Main game loop - runs at 60 FPS"""
        last_time = time.time()
        
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            with self.lock:
                self._update_game_state(dt)
                
                # Broadcast game state every frame
                if self.players:
                    game_state = self._get_game_state()
                    self._broadcast({
                        'type': 'game_state',
                        'game_state': game_state
                    })
            
            # Cap at 60 FPS
            time.sleep(max(0, 1/60 - dt))
    
    def _update_game_state(self, dt: float):
        """Update game physics and logic"""
        # Update projectiles
        self._update_projectiles(dt)
        
        # Update asteroids
        self._update_asteroids(dt)
        
        # Update powerups
        self._update_powerups(dt)
        
        # Check collisions
        self._check_collisions()
        
        # Clean up old projectiles
        self.projectiles = [p for p in self.projectiles if p['life'] > 0]
    
    def _update_projectiles(self, dt: float):
        """Update projectile positions"""
        for projectile in self.projectiles:
            projectile['life'] -= dt
            
            # Move projectile
            dx = math.cos(projectile['angle']) * projectile['speed'] * dt
            dz = math.sin(projectile['angle']) * projectile['speed'] * dt
            
            projectile['x'] += dx
            projectile['z'] += dz
    
    def _update_asteroids(self, dt: float):
        """Update asteroid rotations"""
        for asteroid in self.asteroids:
            asteroid['rotation'] += asteroid['rotation_speed'] * dt
    
    def _update_powerups(self, dt: float):
        """Update powerup rotations"""
        for powerup in self.powerups.values():
            powerup['rotation'] += dt * 2  # Rotate slowly
    
    def _check_collisions(self):
        """Check for collisions between game objects"""
        # Projectile vs Asteroid collisions
        for projectile in self.projectiles[:]:
            for asteroid in self.asteroids:
                if self._distance_3d(projectile, asteroid) < asteroid['size']:
                    # Hit asteroid
                    asteroid['health'] -= projectile['damage']
                    projectile['life'] = 0  # Remove projectile
                    
                    if asteroid['health'] <= 0:
                        # Destroy asteroid, award points
                        self._destroy_asteroid(asteroid, projectile['player_id'])
                    break
        
        # Player vs Powerup collisions
        for player in self.players.values():
            for powerup in list(self.powerups.values()):
                if (powerup['active'] and 
                    self._distance_3d(player, powerup) < 30):
                    self._collect_powerup(player, powerup)
    
    def _distance_3d(self, obj1: Dict, obj2: Dict) -> float:
        """Calculate 3D distance between two objects"""
        dx = obj1['x'] - obj2['x']
        dy = obj1['y'] - obj2['y']
        dz = obj1['z'] - obj2['z']
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _destroy_asteroid(self, asteroid: Dict, player_id: str):
        """Handle asteroid destruction"""
        if player_id in self.players:
            self.players[player_id]['score'] += 100
            
        # Remove asteroid
        if asteroid in self.asteroids:
            self.asteroids.remove(asteroid)
            
        # Spawn new asteroid somewhere else
        new_asteroid = {
            'id': str(uuid.uuid4()),
            'x': random.uniform(-1000, 1000),
            'y': random.uniform(-1000, 1000),
            'z': random.uniform(-1000, 1000),
            'size': random.uniform(20, 80),
            'rotation': random.uniform(0, 2 * math.pi),
            'rotation_speed': random.uniform(-0.1, 0.1),
            'health': 100
        }
        self.asteroids.append(new_asteroid)
    
    def _collect_powerup(self, player: Dict, powerup: Dict):
        """Handle powerup collection"""
        powerup['active'] = False
        
        if powerup['type'] == 'health':
            player['health'] = min(100, player['health'] + 25)
        elif powerup['type'] == 'ammo':
            player['ammo'] = min(100, player['ammo'] + 25)
        elif powerup['type'] == 'shield':
            player['shield'] = min(100, player['shield'] + 50)
        elif powerup['type'] == 'speed':
            player['speed'] = min(10, player['speed'] + 1)
        
        # Remove powerup and spawn new one
        del self.powerups[powerup['id']]
        
        new_powerup = {
            'id': str(uuid.uuid4()),
            'x': random.uniform(-800, 800),
            'y': random.uniform(-800, 800),
            'z': random.uniform(-800, 800),
            'type': random.choice(['health', 'ammo', 'shield', 'speed']),
            'active': True,
            'rotation': 0
        }
        self.powerups[new_powerup['id']] = new_powerup

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='3D Space Combat Game Server')
    parser.add_argument('--host', default='0.0.0.0', help='Server host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5555, help='Server port (default: 5555)')
    
    args = parser.parse_args()
    
    server = GameServer(args.host, args.port)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
