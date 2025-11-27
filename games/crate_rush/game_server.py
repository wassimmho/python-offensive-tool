"""
Crate Rush Multiplayer Game Server
Manages game state for multiple connected players
"""
import socket
import threading
import json
import time
import random
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

HEADER = 64
PORT = 5051
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# Game constants
ENEMY_SPAWN_START = 2.2
ENEMY_SPAWN_MIN = 0.6
ENEMY_SPAWN_ACCEL = 0.015
CRATE_RESPAWN_DELAY = 0.6

@dataclass
class PlayerState:
    """Represents a player's state"""
    player_id: int
    name: str
    x: float
    y: float
    vel_x: float
    vel_y: float
    facing: int
    weapon: str
    score: int
    alive: bool

@dataclass
class EnemyState:
    """Represents an enemy's state"""
    enemy_id: int
    x: float
    y: float
    speed: float
    direction: int
    health: int

@dataclass
class BulletState:
    """Represents a bullet's state"""
    bullet_id: int
    player_id: int
    x: float
    y: float
    vel_x: float
    vel_y: float
    damage: int

@dataclass
class CrateState:
    """Represents a crate's state"""
    crate_id: int
    x: float
    y: float

class GameServer:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        
        self.players: Dict[int, PlayerState] = {}
        self.enemies: Dict[int, EnemyState] = {}
        self.bullets: Dict[int, BulletState] = {}
        self.crates: Dict[int, CrateState] = {}
        
        self.player_connections: Dict[int, socket.socket] = {}
        self.player_id_counter = 0
        self.enemy_id_counter = 0
        self.bullet_id_counter = 0
        self.crate_id_counter = 0
        
        self.difficulty = 0
        self.spawn_timer = ENEMY_SPAWN_START
        self.crate_timer = 0
        
        self.lock = threading.Lock()
        self.running = True
        self.game_time = 0
        
        # Spawn positions for enemies
        self.spawner_positions = [
            (50, 100), (910, 100), (50, 300), (910, 300)
        ]
        
        # Spawn positions for crates
        self.crate_spawn_positions = [
            (200, 200), (400, 300), (600, 200), (760, 300)
        ]
        
        print(f"[SERVER] Server initialized at {SERVER}:{PORT}")
    
    def send_message(self, conn, data):
        """Send a JSON message to a client"""
        try:
            message = json.dumps(data).encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            conn.send(send_length)
            conn.send(message)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False
    
    def receive_message(self, conn):
        """Receive a JSON message from a client"""
        try:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length.strip())
                msg = conn.recv(msg_length).decode(FORMAT)
                return json.loads(msg)
        except Exception as e:
            print(f"[ERROR] Failed to receive message: {e}")
            return None
    
    def handle_client(self, conn, addr):
        """Handle a connected client"""
        print(f"[NEW CONNECTION] {addr} connected.")
        
        # Receive player name
        player_data = self.receive_message(conn)
        if not player_data:
            conn.close()
            return
        
        with self.lock:
            player_id = self.player_id_counter
            self.player_id_counter += 1
            
            # Create new player
            player = PlayerState(
                player_id=player_id,
                name=player_data.get('name', f'Player{player_id}'),
                x=480, y=60,
                vel_x=0, vel_y=0,
                facing=1,
                weapon='Pistol',
                score=0,
                alive=True
            )
            
            self.players[player_id] = player
            self.player_connections[player_id] = conn
            
            # Send player their ID
            self.send_message(conn, {'type': 'player_id', 'player_id': player_id})
            print(f"[PLAYER JOINED] {player.name} (ID: {player_id})")
        
        # Handle client messages
        try:
            while self.running:
                data = self.receive_message(conn)
                if not data:
                    break
                
                self.handle_player_action(player_id, data)
        
        except Exception as e:
            print(f"[ERROR] Client {player_id} error: {e}")
        
        finally:
            with self.lock:
                if player_id in self.players:
                    print(f"[PLAYER LEFT] {self.players[player_id].name} (ID: {player_id})")
                    del self.players[player_id]
                if player_id in self.player_connections:
                    del self.player_connections[player_id]
            conn.close()
    
    def handle_player_action(self, player_id, data):
        """Handle player input"""
        with self.lock:
            if player_id not in self.players:
                return
            
            action_type = data.get('type')
            player = self.players[player_id]
            
            if action_type == 'move':
                player.x = data.get('x', player.x)
                player.y = data.get('y', player.y)
                player.vel_x = data.get('vel_x', player.vel_x)
                player.vel_y = data.get('vel_y', player.vel_y)
                player.facing = data.get('facing', player.facing)
            
            elif action_type == 'shoot':
                # Create bullet
                bullet_id = self.bullet_id_counter
                self.bullet_id_counter += 1
                
                bullet = BulletState(
                    bullet_id=bullet_id,
                    player_id=player_id,
                    x=data.get('x'),
                    y=data.get('y'),
                    vel_x=data.get('vel_x'),
                    vel_y=data.get('vel_y'),
                    damage=data.get('damage', 1)
                )
                self.bullets[bullet_id] = bullet
            
            elif action_type == 'collect_crate':
                crate_id = data.get('crate_id')
                if crate_id in self.crates:
                    del self.crates[crate_id]
                    player.score += 1
                    player.weapon = data.get('weapon', player.weapon)
    
    def game_loop(self):
        """Main game loop - updates game state"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            self.game_time += dt
            
            with self.lock:
                # Update bullets
                bullets_to_remove = []
                for bullet_id, bullet in list(self.bullets.items()):
                    bullet.x += bullet.vel_x * dt
                    bullet.y += bullet.vel_y * dt
                    
                    # Remove bullets out of bounds
                    if not (-50 <= bullet.x <= 1010 and -80 <= bullet.y <= 620):
                        bullets_to_remove.append(bullet_id)
                
                for bullet_id in bullets_to_remove:
                    if bullet_id in self.bullets:
                        del self.bullets[bullet_id]
                
                # Check bullet-enemy collisions
                for bullet_id, bullet in list(self.bullets.items()):
                    for enemy_id, enemy in list(self.enemies.items()):
                        # Simple collision check
                        if abs(bullet.x - enemy.x) < 20 and abs(bullet.y - enemy.y) < 20:
                            enemy.health -= bullet.damage
                            if bullet_id in self.bullets:
                                del self.bullets[bullet_id]
                            if enemy.health <= 0 and enemy_id in self.enemies:
                                del self.enemies[enemy_id]
                            break
                
                # Spawn enemies
                self.spawn_timer -= dt
                if self.spawn_timer <= 0:
                    self.spawn_enemy()
                    self.difficulty += 1
                    self.spawn_timer = max(ENEMY_SPAWN_MIN, ENEMY_SPAWN_START - self.difficulty * ENEMY_SPAWN_ACCEL)
                
                # Update enemies (simple movement)
                for enemy in self.enemies.values():
                    enemy.x += enemy.direction * enemy.speed * dt
                    if enemy.x < 50 or enemy.x > 910:
                        enemy.direction *= -1
                
                # Spawn crates
                self.crate_timer -= dt
                if len(self.crates) == 0 and self.crate_timer <= 0:
                    self.spawn_crate()
                    self.crate_timer = CRATE_RESPAWN_DELAY
            
            # Broadcast game state to all players
            self.broadcast_game_state()
            
            time.sleep(0.016)  # ~60 FPS
    
    def spawn_enemy(self):
        """Spawn a new enemy"""
        pos = random.choice(self.spawner_positions)
        enemy_id = self.enemy_id_counter
        self.enemy_id_counter += 1
        
        speed = 120 + self.difficulty * 18
        enemy = EnemyState(
            enemy_id=enemy_id,
            x=pos[0],
            y=pos[1],
            speed=speed,
            direction=random.choice([-1, 1]),
            health=2
        )
        self.enemies[enemy_id] = enemy
    
    def spawn_crate(self):
        """Spawn a new crate"""
        pos = random.choice(self.crate_spawn_positions)
        crate_id = self.crate_id_counter
        self.crate_id_counter += 1
        
        crate = CrateState(
            crate_id=crate_id,
            x=pos[0],
            y=pos[1]
        )
        self.crates[crate_id] = crate
    
    def broadcast_game_state(self):
        """Send game state to all connected players"""
        with self.lock:
            game_state = {
                'type': 'game_state',
                'players': {pid: asdict(player) for pid, player in self.players.items()},
                'enemies': {eid: asdict(enemy) for eid, enemy in self.enemies.items()},
                'bullets': {bid: asdict(bullet) for bid, bullet in self.bullets.items()},
                'crates': {cid: asdict(crate) for cid, crate in self.crates.items()},
            }
            
            disconnected = []
            for player_id, conn in self.player_connections.items():
                if not self.send_message(conn, game_state):
                    disconnected.append(player_id)
            
            # Clean up disconnected players
            for player_id in disconnected:
                if player_id in self.players:
                    del self.players[player_id]
                if player_id in self.player_connections:
                    del self.player_connections[player_id]
    
    def start(self):
        """Start the server"""
        self.server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
        
        # Start game loop in separate thread
        game_thread = threading.Thread(target=self.game_loop)
        game_thread.daemon = True
        game_thread.start()
        
        try:
            while self.running:
                conn, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Server shutting down...")
            self.running = False
            self.server.close()

if __name__ == "__main__":
    print("="*50)
    print("CRATE RUSH - MULTIPLAYER SERVER")
    print("="*50)
    server = GameServer()
    server.start()
