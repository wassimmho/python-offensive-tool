"""
Multiplayer module for Crate Rush.
Handles remote player rendering and multiplayer game logic.
"""

import random
import pygame as pg
from pathlib import Path
from typing import Dict, Optional
from . import settings as S
from .network import PlayerState, GameClient, GameServer, Message, get_local_ip as network_get_local_ip
from .weapons import WEAPON_POOL
from .player import (
    CHAR_IDLE_FRAMES, CHAR_IDLE_FRAMES_FLIPPED,
    CHAR_WALK_FRAMES, CHAR_WALK_FRAMES_FLIPPED,
    CHAR_JUMP_START_FRAMES, CHAR_JUMP_START_FRAMES_FLIPPED,
    CHAR_JUMP_END_FRAMES, CHAR_JUMP_END_FRAMES_FLIPPED,
    AK_FRAMES, AK_FRAMES_FLIPPED,
    SMG_FRAMES, SMG_FRAMES_FLIPPED,
    ROCKET_FRAMES, ROCKET_FRAMES_FLIPPED,
    SHOTGUN_FRAMES, SHOTGUN_FRAMES_FLIPPED,
    PISTOL_FRAMES, PISTOL_FRAMES_FLIPPED,
    load_character_frames, load_ak_frames, load_smg_frames,
    load_rocket_frames, load_shotgun_frames, load_pistol_frames
)
import math

# Re-export get_local_ip for convenience
def get_local_ip():
    return network_get_local_ip()


class RemotePlayer(pg.sprite.Sprite):
    """
    Represents a remote player in the multiplayer game.
    Uses the same sprites as the local player.
    """
    
    def __init__(self, player_id: str, name: str):
        super().__init__()
        # Ensure sprites are loaded
        load_character_frames()
        load_ak_frames()
        load_smg_frames()
        load_rocket_frames()
        load_shotgun_frames()
        load_pistol_frames()
        
        self.player_id = player_id
        self.name = name
        self.pos = pg.Vector2(S.WIDTH // 2, 100)
        self.vel = pg.Vector2(0, 0)
        self.facing = 1
        self.weapon_name = "Pistol"
        self.is_firing = False
        self.aim_angle = 0.0
        self.anim_state = 'idle'
        self.anim_frame = 0
        self.health = 100
        
        # Interpolation for smooth movement
        self.target_pos = pg.Vector2(self.pos)
        self.interp_speed = 15.0
        
        # Size matching local player
        self.size = pg.Vector2(20, 40)
        
        # Set initial image
        if CHAR_IDLE_FRAMES:
            self.image = CHAR_IDLE_FRAMES[0]
            self.sprite_size = pg.Vector2(self.image.get_width(), self.image.get_height())
        else:
            self.sprite_size = self.size.copy()
            self.image = pg.Surface(self.size, pg.SRCALPHA)
            self.image.fill((150, 150, 255))
        
        self.rect = pg.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        
        # Font for name rendering
        self.name_font = pg.font.SysFont("consolas", 14, bold=True)
        
        # Generate a random color tint for this player (to distinguish players)
        self.color_tint = (
            random.randint(180, 255),
            random.randint(180, 255),
            random.randint(180, 255)
        )
    
    def update_from_state(self, state: PlayerState):
        """Update from network state"""
        self.target_pos.x = state.x
        self.target_pos.y = state.y
        self.vel.x = state.vel_x
        self.vel.y = state.vel_y
        self.facing = state.facing
        self.weapon_name = state.weapon_name
        self.is_firing = state.is_firing
        self.aim_angle = state.aim_angle
        self.anim_state = state.anim_state
        self.anim_frame = state.anim_frame
        self.health = state.health
        self.name = state.name
    
    def update(self, dt: float):
        """Update remote player with interpolation"""
        # Smooth interpolation to target position
        diff = self.target_pos - self.pos
        if diff.length() > 1:
            move = diff * min(1.0, self.interp_speed * dt)
            self.pos += move
        else:
            self.pos = self.target_pos.copy()
        
        self.rect.topleft = self.pos
        
        # Update animation frame
        self._update_animation()
    
    def _update_animation(self):
        """Update the current animation frame"""
        # Get appropriate frame list
        if self.anim_state == 'idle' and CHAR_IDLE_FRAMES:
            frames = CHAR_IDLE_FRAMES if self.facing > 0 else CHAR_IDLE_FRAMES_FLIPPED
        elif self.anim_state == 'walk' and CHAR_WALK_FRAMES:
            frames = CHAR_WALK_FRAMES if self.facing > 0 else CHAR_WALK_FRAMES_FLIPPED
        elif self.anim_state == 'jump_start' and CHAR_JUMP_START_FRAMES:
            frames = CHAR_JUMP_START_FRAMES if self.facing > 0 else CHAR_JUMP_START_FRAMES_FLIPPED
        elif self.anim_state == 'jump_end' and CHAR_JUMP_END_FRAMES:
            frames = CHAR_JUMP_END_FRAMES if self.facing > 0 else CHAR_JUMP_END_FRAMES_FLIPPED
        else:
            return
        
        # Clamp frame index
        frame_idx = min(self.anim_frame, len(frames) - 1)
        self.image = frames[frame_idx]
    
    def _get_weapon_frames(self):
        """Get the appropriate weapon frames based on weapon name"""
        weapon_name = self.weapon_name.lower()
        if 'smg' in weapon_name and SMG_FRAMES:
            return SMG_FRAMES, SMG_FRAMES_FLIPPED
        elif 'ak' in weapon_name and AK_FRAMES:
            return AK_FRAMES, AK_FRAMES_FLIPPED
        elif 'rocket' in weapon_name and ROCKET_FRAMES:
            return ROCKET_FRAMES, ROCKET_FRAMES_FLIPPED
        elif 'shotgun' in weapon_name and SHOTGUN_FRAMES:
            return SHOTGUN_FRAMES, SHOTGUN_FRAMES_FLIPPED
        elif 'pistol' in weapon_name and PISTOL_FRAMES:
            return PISTOL_FRAMES, PISTOL_FRAMES_FLIPPED
        return None, None
    
    def draw(self, surf: pg.Surface, offset=(0, 0)):
        """Draw the remote player with name above head"""
        ox, oy = offset
        
        # Calculate sprite draw position
        sprite_w = self.image.get_width()
        sprite_h = self.image.get_height()
        
        draw_x = self.rect.centerx - sprite_w // 2 + ox
        draw_y = self.rect.bottom - sprite_h + 12 + oy
        
        # Draw player sprite
        surf.blit(self.image, (draw_x, draw_y))
        
        # Draw weapon
        weapon_frames, weapon_frames_flipped = self._get_weapon_frames()
        if weapon_frames:
            frame_idx = 0  # Use first frame for remote players (simplified)
            base_img = weapon_frames[frame_idx]
            
            # Calculate rotation
            if self.facing > 0:
                rotated_img = pg.transform.rotate(base_img, self.aim_angle)
            else:
                flipped_img = pg.transform.flip(base_img, False, True)
                rotated_img = pg.transform.rotate(flipped_img, self.aim_angle)
            
            weapon_center_x = self.rect.centerx + (12 * self.facing) + ox
            weapon_center_y = draw_y + sprite_h // 2 + 30
            rotated_rect = rotated_img.get_rect(center=(weapon_center_x, weapon_center_y))
            
            surf.blit(rotated_img, rotated_rect)
        
        # Draw name above player
        name_surf = self.name_font.render(self.name, True, (255, 255, 255))
        name_shadow = self.name_font.render(self.name, True, (0, 0, 0))
        
        name_x = self.rect.centerx - name_surf.get_width() // 2 + ox
        name_y = draw_y - 20
        
        # Shadow
        surf.blit(name_shadow, (name_x + 1, name_y + 1))
        # Name
        surf.blit(name_surf, (name_x, name_y))
        
        # Draw health bar
        bar_width = 40
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2 + ox
        bar_y = draw_y - 10
        
        # Background
        pg.draw.rect(surf, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Health
        health_width = int(bar_width * (self.health / 100))
        health_color = (100, 255, 100) if self.health > 50 else (255, 200, 50) if self.health > 25 else (255, 80, 80)
        pg.draw.rect(surf, health_color, (bar_x, bar_y, health_width, bar_height))


class MultiplayerManager:
    """
    Manages multiplayer game state and network communication.
    """
    
    def __init__(self):
        self.client: Optional[GameClient] = None
        self.server: Optional[GameServer] = None
        self.is_host = False
        self.connected = False
        self.player_name = "Player"
        self.remote_players: Dict[str, RemotePlayer] = {}
        self.update_rate = 1/30  # 30 updates per second
        self.update_timer = 0
        self.pending_hits = []  # Hits received from network
        self.local_health = 100  # Local player health
        
    def host_game(self, name: str = "Player", port: int = 5555) -> tuple:
        """
        Host a new game server.
        Returns (success, ip_address, error_message)
        """
        self.player_name = name
        self.server = GameServer(port=port)
        
        if self.server.start():
            self.is_host = True
            # Also connect as a client to own server
            self.client = GameClient()
            ip = get_local_ip()
            if self.client.connect(ip, port, name):
                self.connected = True
                return True, ip, ""
            else:
                self.server.stop()
                return False, "", "Failed to connect to own server"
        else:
            return False, "", "Failed to start server"
    
    def join_game(self, host: str, name: str = "Player", port: int = 5555) -> tuple:
        """
        Join an existing game.
        Returns (success, error_message)
        """
        self.player_name = name
        self.client = GameClient()
        
        if self.client.connect(host, port, name):
            self.connected = True
            self.is_host = False
            return True, ""
        else:
            return False, "Failed to connect to server"
    
    def start_game(self):
        """Host starts the game - notify all clients"""
        if not self.is_host or not self.client:
            return
        msg = Message(Message.GAME_START, {"started": True})
        self.client.send(msg)
    
    def check_game_started(self) -> bool:
        """Check if we received a game start message"""
        if not self.client:
            return False
        messages = self.client.get_messages()
        for msg in messages:
            if msg.type == Message.GAME_START:
                return True
        return False
    
    def disconnect(self):
        """Disconnect from game"""
        if self.client:
            self.client.disconnect()
            self.client = None
        
        if self.server:
            self.server.stop()
            self.server = None
        
        self.connected = False
        self.is_host = False
        self.remote_players.clear()
    
    def update(self, dt: float, local_player, local_weapon):
        """Update multiplayer state"""
        if not self.connected or not self.client:
            return
        
        # Send local player state periodically
        self.update_timer += dt
        if self.update_timer >= self.update_rate:
            self.update_timer = 0
            self._send_player_state(local_player, local_weapon)
        
        # Process incoming messages
        messages = self.client.get_messages()
        for msg in messages:
            self._handle_message(msg)
        
        # Update remote player states from client
        remote_states = self.client.get_remote_players()
        for player_id, state in remote_states.items():
            if player_id not in self.remote_players:
                # New player joined
                self.remote_players[player_id] = RemotePlayer(player_id, state.name)
            self.remote_players[player_id].update_from_state(state)
        
        # Remove disconnected players
        connected_ids = set(remote_states.keys())
        for player_id in list(self.remote_players.keys()):
            if player_id not in connected_ids:
                del self.remote_players[player_id]
        
        # Update remote players
        for remote in self.remote_players.values():
            remote.update(dt)
    
    def _send_player_state(self, player, weapon):
        """Send local player state to server"""
        if not self.client:
            return
        
        weapon_name = weapon.name if weapon else "None"
        is_firing = getattr(player, 'is_firing', False)
        
        state = PlayerState(
            player_id=self.client.player_id,
            name=self.player_name,
            x=player.pos.x,
            y=player.pos.y,
            vel_x=player.vel.x,
            vel_y=player.vel.y,
            facing=player.facing,
            weapon_name=weapon_name,
            is_firing=is_firing,
            aim_angle=getattr(player, 'aim_angle', 0.0),
            anim_state=getattr(player, 'anim_state', 'idle'),
            anim_frame=getattr(player, 'anim_frame', 0),
            health=100
        )
        
        self.client.send_player_state(state)
    
    def _handle_message(self, msg: Message):
        """Handle incoming network messages"""
        if msg.type == Message.PLAYER_HIT:
            # Store hit info for processing
            self.pending_hits.append(msg.data)
        elif msg.type == Message.PLAYER_KILL:
            # Player was killed - they'll respawn
            pass
    
    def send_player_hit(self, target_player_id: str, damage: int):
        """Send a hit notification to the server"""
        if not self.client:
            return
        hit_data = {
            "target_id": target_player_id,
            "attacker_id": self.client.player_id,
            "damage": damage
        }
        msg = Message(Message.PLAYER_HIT, hit_data)
        self.client.send(msg)
    
    def send_player_kill(self, target_player_id: str):
        """Send a kill notification to the server"""
        if not self.client:
            return
        kill_data = {
            "target_id": target_player_id,
            "killer_id": self.client.player_id
        }
        msg = Message(Message.PLAYER_KILL, kill_data)
        self.client.send(msg)
    
    def check_incoming_hits(self, local_player, particles, game):
        """Check if we received any hits and apply damage"""
        from .particles import Burst
        
        for hit in self.pending_hits:
            target_id = hit.get("target_id", "")
            damage = hit.get("damage", 10)
            
            # Check if we are the target
            if self.client and target_id == self.client.player_id:
                # We got hit!
                self.local_health -= damage
                game.shake = min(15, game.shake + 6)
                Burst(particles, local_player.rect.center, (255, 100, 100), count=10, speed=220)
                
                if self.local_health <= 0:
                    # We died - respawn
                    self.local_health = 100
                    local_player.respawn()
                    Burst(particles, local_player.rect.center, (255, 50, 50), count=25, speed=350)
        
        self.pending_hits.clear()
    
    def draw_remote_players(self, surf: pg.Surface, offset=(0, 0)):
        """Draw all remote players"""
        for remote in self.remote_players.values():
            remote.draw(surf, offset)
    
    def get_player_count(self) -> int:
        """Get total player count (including self)"""
        if self.client:
            lobby = self.client.get_lobby_players()
            if lobby:
                return len(lobby)
        return len(self.remote_players) + (1 if self.connected else 0)
    
    def get_player_list(self) -> list:
        """Get list of all player names"""
        if self.client:
            lobby = self.client.get_lobby_players()
            if lobby:
                # Return names from lobby, putting self first
                names = []
                for p in lobby:
                    if p["id"] == self.client.player_id:
                        names.insert(0, p["name"])
                    else:
                        names.append(p["name"])
                return names
        
        # Fallback to old method
        names = [self.player_name] if self.connected else []
        for remote in self.remote_players.values():
            names.append(remote.name)
        return names


# Global multiplayer manager instance
multiplayer = MultiplayerManager()
