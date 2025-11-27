"""
Crate Rush Network Client
Handles connection to game server and state synchronization
"""
import socket
import json
import threading

HEADER = 64
FORMAT = 'utf-8'

class NetworkClient:
    def __init__(self, server_ip, port=5051):
        self.server_ip = server_ip
        self.port = port
        self.client = None
        self.player_id = None
        self.game_state = {
            'players': {},
            'enemies': {},
            'bullets': {},
            'crates': {}
        }
        self.connected = False
        self.lock = threading.Lock()
    
    def connect(self, player_name):
        """Connect to the game server"""
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.server_ip, self.port))
            
            # Send player name
            self.send_message({'name': player_name})
            
            # Receive player ID
            response = self.receive_message()
            if response and response.get('type') == 'player_id':
                self.player_id = response['player_id']
                self.connected = True
                
                # Start receiving thread
                receive_thread = threading.Thread(target=self.receive_loop)
                receive_thread.daemon = True
                receive_thread.start()
                
                return True
            return False
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            return False
    
    def send_message(self, data):
        """Send a JSON message to the server"""
        try:
            message = json.dumps(data).encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            self.connected = False
            return False
    
    def receive_message(self):
        """Receive a JSON message from the server"""
        try:
            msg_length = self.client.recv(HEADER).decode(FORMAT)
            if msg_length:
                msg_length = int(msg_length.strip())
                msg = self.client.recv(msg_length).decode(FORMAT)
                return json.loads(msg)
        except Exception as e:
            print(f"[ERROR] Failed to receive message: {e}")
            self.connected = False
            return None
    
    def receive_loop(self):
        """Continuously receive game state updates"""
        while self.connected:
            try:
                data = self.receive_message()
                if not data:
                    break
                
                if data.get('type') == 'game_state':
                    with self.lock:
                        self.game_state = data
            except Exception as e:
                print(f"[ERROR] Receive loop error: {e}")
                self.connected = False
                break
    
    def send_player_move(self, x, y, vel_x, vel_y, facing):
        """Send player movement data"""
        self.send_message({
            'type': 'move',
            'x': x,
            'y': y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'facing': facing
        })
    
    def send_shoot(self, x, y, vel_x, vel_y, damage=1):
        """Send bullet fire data"""
        self.send_message({
            'type': 'shoot',
            'x': x,
            'y': y,
            'vel_x': vel_x,
            'vel_y': vel_y,
            'damage': damage
        })
    
    def send_collect_crate(self, crate_id, weapon):
        """Send crate collection data"""
        self.send_message({
            'type': 'collect_crate',
            'crate_id': crate_id,
            'weapon': weapon
        })
    
    def get_game_state(self):
        """Get current game state (thread-safe)"""
        with self.lock:
            return self.game_state.copy()
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.client:
            self.client.close()
