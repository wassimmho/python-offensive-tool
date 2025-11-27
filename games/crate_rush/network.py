"""
Network module for Crate Rush multiplayer.
Handles client-server communication over TCP sockets.
Currently uses private IP, designed to be easily switched to public IP later.
"""

import socket
import json
import threading
import time
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any

# Network configuration
DEFAULT_PORT = 5555
BUFFER_SIZE = 4096
HEARTBEAT_INTERVAL = 0.5  # seconds
TIMEOUT = 5.0  # Connection timeout in seconds

@dataclass
class PlayerState:
    """State data for a player to be sent over network"""
    player_id: str
    name: str
    x: float
    y: float
    vel_x: float
    vel_y: float
    facing: int
    weapon_name: str
    is_firing: bool
    aim_angle: float
    anim_state: str
    anim_frame: int
    health: int = 100
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerState':
        return cls(**data)

@dataclass 
class BulletState:
    """State data for a bullet"""
    bullet_id: str
    x: float
    y: float
    vel_x: float
    vel_y: float
    owner_id: str
    damage: int
    radius: int
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BulletState':
        return cls(**data)

class Message:
    """Network message wrapper"""
    # Message types
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PLAYER_UPDATE = "player_update"
    BULLET_SPAWN = "bullet_spawn"
    PLAYER_HIT = "player_hit"
    PLAYER_KILL = "player_kill"
    CHAT = "chat"
    HEARTBEAT = "heartbeat"
    LOBBY_UPDATE = "lobby_update"
    GAME_START = "game_start"
    
    def __init__(self, msg_type: str, data: Any, sender_id: str = ""):
        self.type = msg_type
        self.data = data
        self.sender_id = sender_id
        self.timestamp = time.time()
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type,
            "data": self.data,
            "sender_id": self.sender_id,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        data = json.loads(json_str)
        msg = cls(data["type"], data["data"], data.get("sender_id", ""))
        msg.timestamp = data.get("timestamp", time.time())
        return msg


class GameServer:
    """
    Game server that handles multiple client connections.
    One lobby where all players join.
    """
    
    def __init__(self, host: str = "", port: int = DEFAULT_PORT):
        self.host = host or self.get_local_ip()
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.clients: Dict[str, socket.socket] = {}  # player_id -> socket
        self.player_states: Dict[str, PlayerState] = {}  # player_id -> state
        self.player_names: Dict[str, str] = {}  # player_id -> name
        self.running = False
        self.receive_queue = Queue()
        self.lock = threading.Lock()
        self.next_player_id = 1
        
    @staticmethod
    def get_local_ip() -> str:
        """Get local IP address for LAN play"""
        try:
            # Create a temporary socket to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def start(self) -> bool:
        """Start the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)  # Max 10 players in lobby
            self.socket.settimeout(1.0)  # Allow periodic checking
            self.running = True
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            print(f"[SERVER] Started on {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[SERVER] Failed to start: {e}")
            return False
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            self.socket.close()
        for client_socket in self.clients.values():
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()
        self.player_states.clear()
        print("[SERVER] Stopped")
    
    def _accept_connections(self):
        """Accept incoming connections in a separate thread"""
        while self.running:
            try:
                client_socket, address = self.socket.accept()
                client_socket.settimeout(TIMEOUT)
                
                # Assign player ID
                player_id = f"player_{self.next_player_id}"
                self.next_player_id += 1
                
                with self.lock:
                    self.clients[player_id] = client_socket
                
                # Send player their ID
                welcome_msg = Message(Message.CONNECT, {"player_id": player_id})
                self._send_to_client(client_socket, welcome_msg)
                
                # Start receive thread for this client
                recv_thread = threading.Thread(
                    target=self._receive_from_client, 
                    args=(player_id, client_socket),
                    daemon=True
                )
                recv_thread.start()
                
                print(f"[SERVER] Player {player_id} connected from {address}")
                
                # Broadcast lobby update to all clients after short delay
                # to allow new client to set up their name
                def send_lobby_update():
                    time.sleep(0.2)
                    self._broadcast_lobby_update()
                threading.Thread(target=send_lobby_update, daemon=True).start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Accept error: {e}")
    
    def _receive_from_client(self, player_id: str, client_socket: socket.socket):
        """Receive messages from a specific client"""
        buffer = ""
        while self.running:
            try:
                data = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = Message.from_json(line)
                            msg.sender_id = player_id
                            self._handle_message(msg)
                        except json.JSONDecodeError:
                            continue
                            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[SERVER] Receive error from {player_id}: {e}")
                break
        
        # Client disconnected
        self._handle_disconnect(player_id)
    
    def _handle_message(self, msg: Message):
        """Handle incoming message from client"""
        if msg.type == Message.PLAYER_UPDATE:
            # Update player state and broadcast to others
            state = PlayerState.from_dict(msg.data)
            with self.lock:
                self.player_states[msg.sender_id] = state
                self.player_names[msg.sender_id] = state.name
            
            # Broadcast to all other clients
            self.broadcast(msg, exclude=msg.sender_id)
            
            # Also broadcast lobby update when names change
            self._broadcast_lobby_update()
            
        elif msg.type == Message.LOBBY_UPDATE:
            # Client is sending their name for lobby
            name = msg.data.get("name", "Player")
            with self.lock:
                self.player_names[msg.sender_id] = name
            # Broadcast updated lobby to all
            self._broadcast_lobby_update()
            
        elif msg.type == Message.GAME_START:
            # Host is starting the game - broadcast to all
            self.broadcast(msg)
            
        elif msg.type == Message.BULLET_SPAWN:
            # Broadcast bullet to all clients
            self.broadcast(msg)
            
        elif msg.type == Message.PLAYER_HIT:
            # Broadcast hit to all clients (including sender so they see confirmation)
            self.broadcast(msg)
            
        elif msg.type == Message.PLAYER_KILL:
            # Broadcast kill to all clients
            self.broadcast(msg)
            
        elif msg.type == Message.CHAT:
            # Broadcast chat to all clients
            self.broadcast(msg)
            
        elif msg.type == Message.DISCONNECT:
            self._handle_disconnect(msg.sender_id)
    
    def _handle_disconnect(self, player_id: str):
        """Handle player disconnection"""
        with self.lock:
            if player_id in self.clients:
                try:
                    self.clients[player_id].close()
                except:
                    pass
                del self.clients[player_id]
            if player_id in self.player_states:
                del self.player_states[player_id]
            if player_id in self.player_names:
                del self.player_names[player_id]
        
        # Notify other players
        disconnect_msg = Message(Message.DISCONNECT, {"player_id": player_id})
        self.broadcast(disconnect_msg)
        print(f"[SERVER] Player {player_id} disconnected")
        
        # Broadcast updated lobby
        self._broadcast_lobby_update()
    
    def _broadcast_lobby_update(self):
        """Send lobby player list to all clients"""
        with self.lock:
            player_list = list(self.player_names.items())  # [(id, name), ...]
        
        lobby_data = {
            "players": [{"id": pid, "name": name} for pid, name in player_list],
            "count": len(player_list)
        }
        msg = Message(Message.LOBBY_UPDATE, lobby_data)
        self.broadcast(msg)
    
    def _send_to_client(self, client_socket: socket.socket, msg: Message) -> bool:
        """Send message to a specific client"""
        try:
            data = msg.to_json() + '\n'
            client_socket.sendall(data.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[SERVER] Send error: {e}")
            return False
    
    def broadcast(self, msg: Message, exclude: str = None):
        """Broadcast message to all clients except excluded one"""
        with self.lock:
            for player_id, client_socket in list(self.clients.items()):
                if player_id != exclude:
                    if not self._send_to_client(client_socket, msg):
                        # Client disconnected
                        self._handle_disconnect(player_id)
    
    def get_player_count(self) -> int:
        """Get number of connected players"""
        with self.lock:
            return len(self.clients)
    
    def get_player_list(self) -> List[str]:
        """Get list of player names"""
        with self.lock:
            return list(self.player_names.values())


class GameClient:
    """
    Game client that connects to a server.
    """
    
    def __init__(self):
        self.socket: Optional[socket.socket] = None
        self.player_id: str = ""
        self.player_name: str = ""
        self.connected = False
        self.running = False
        self.receive_queue = Queue()
        self.remote_players: Dict[str, PlayerState] = {}
        self.lobby_players: List[Dict] = []  # List of {"id": ..., "name": ...} for lobby
        self.lock = threading.Lock()
        self.last_heartbeat = 0
        
    def connect(self, host: str, port: int = DEFAULT_PORT, name: str = "Player") -> bool:
        """Connect to a game server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(TIMEOUT)
            self.socket.connect((host, port))
            self.player_name = name
            self.running = True
            
            # Wait for welcome message with player ID
            data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
            if data:
                msg = Message.from_json(data.strip())
                if msg.type == Message.CONNECT:
                    self.player_id = msg.data.get("player_id", "")
                    self.connected = True
                    
                    # Start receive thread
                    recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
                    recv_thread.start()
                    
                    # Send our name to server for lobby
                    self.send_lobby_name(name)
                    
                    print(f"[CLIENT] Connected as {self.player_id} ({name})")
                    return True
            
            return False
        except Exception as e:
            print(f"[CLIENT] Connection failed: {e}")
            return False
    
    def send_lobby_name(self, name: str):
        """Send player name to server for lobby display"""
        msg = Message(Message.LOBBY_UPDATE, {"name": name})
        self.send(msg)
    
    def disconnect(self):
        """Disconnect from server"""
        if self.connected:
            try:
                msg = Message(Message.DISCONNECT, {"player_id": self.player_id})
                self.send(msg)
            except:
                pass
        
        self.running = False
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("[CLIENT] Disconnected")
    
    def _receive_loop(self):
        """Receive messages from server in a loop"""
        buffer = ""
        while self.running and self.connected:
            try:
                data = self.socket.recv(BUFFER_SIZE).decode('utf-8')
                if not data:
                    break
                
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            msg = Message.from_json(line)
                            self._handle_message(msg)
                        except json.JSONDecodeError:
                            continue
                            
            except socket.timeout:
                continue
            except Exception as e:
                print(f"[CLIENT] Receive error: {e}")
                break
        
        self.connected = False
        print("[CLIENT] Connection lost")
    
    def _handle_message(self, msg: Message):
        """Handle incoming message from server"""
        if msg.type == Message.PLAYER_UPDATE:
            # Update remote player state
            state = PlayerState.from_dict(msg.data)
            if state.player_id != self.player_id:
                with self.lock:
                    self.remote_players[state.player_id] = state
                    
        elif msg.type == Message.LOBBY_UPDATE:
            # Update lobby player list
            with self.lock:
                self.lobby_players = msg.data.get("players", [])
                    
        elif msg.type == Message.GAME_START:
            # Host started the game - add to queue for main game to handle
            self.receive_queue.put(msg)
                    
        elif msg.type == Message.DISCONNECT:
            # Remove disconnected player
            player_id = msg.data.get("player_id", "")
            with self.lock:
                if player_id in self.remote_players:
                    del self.remote_players[player_id]
                    
        elif msg.type == Message.BULLET_SPAWN:
            # Add to queue for game to handle
            self.receive_queue.put(msg)
            
        elif msg.type == Message.PLAYER_HIT:
            self.receive_queue.put(msg)
            
        elif msg.type == Message.PLAYER_KILL:
            self.receive_queue.put(msg)
            
        elif msg.type == Message.CHAT:
            self.receive_queue.put(msg)
    
    def send(self, msg: Message) -> bool:
        """Send message to server"""
        if not self.connected:
            return False
        try:
            msg.sender_id = self.player_id
            data = msg.to_json() + '\n'
            self.socket.sendall(data.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[CLIENT] Send error: {e}")
            return False
    
    def send_player_state(self, state: PlayerState):
        """Send player state update to server"""
        msg = Message(Message.PLAYER_UPDATE, state.to_dict())
        self.send(msg)
    
    def send_bullet(self, bullet_data: dict):
        """Send bullet spawn to server"""
        msg = Message(Message.BULLET_SPAWN, bullet_data)
        self.send(msg)
    
    def get_remote_players(self) -> Dict[str, PlayerState]:
        """Get copy of remote player states"""
        with self.lock:
            return dict(self.remote_players)
    
    def get_lobby_players(self) -> List[Dict]:
        """Get list of players in lobby"""
        with self.lock:
            return list(self.lobby_players)
    
    def get_messages(self) -> List[Message]:
        """Get all pending messages from queue"""
        messages = []
        while True:
            try:
                msg = self.receive_queue.get_nowait()
                messages.append(msg)
            except Empty:
                break
        return messages


def get_local_ip() -> str:
    """Get local IP address for display"""
    return GameServer.get_local_ip()
