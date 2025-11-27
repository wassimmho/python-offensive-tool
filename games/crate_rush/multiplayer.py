"""
Crate Rush - Multiplayer Mode
Online multiplayer version of the game
"""
import math
import random
import json
from pathlib import Path
import pygame as pg
from . import settings as S
from .level import Level
from .player import Player, load_ak_frames
from .enemies import Enemy
from .weapons import WEAPON_POOL
from .crate import Crate
from . import ui
from .particles import Burst
from .network_client import NetworkClient

class NetworkedPlayer(pg.sprite.Sprite):
    """Represents another player in the network"""
    def __init__(self, player_id, name, x, y):
        super().__init__()
        self.player_id = player_id
        self.name = name
        self.pos = pg.Vector2(x, y)
        self.facing = 1
        self.size = pg.Vector2(28, 36)
        
        # Create character sprite (same as local player)
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.draw_character()
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos
    
    def draw_character(self):
        """Draw character sprite (copy from Player class)"""
        self.image.fill((0, 0, 0, 0))
        w, h = int(self.size.x), int(self.size.y)
        
        # Body - different color to distinguish from local player
        body_rect = pg.Rect(w//4, h//3, w//2, h//2)
        pg.draw.rect(self.image, (255, 180, 100), body_rect, border_radius=4)
        pg.draw.rect(self.image, (235, 160, 80), body_rect, width=2, border_radius=4)
        
        # Head
        head_size = w // 2.5
        head_center = (w // 2, h // 5)
        pg.draw.circle(self.image, (255, 220, 180), head_center, int(head_size))
        pg.draw.circle(self.image, (200, 160, 130), head_center, int(head_size), width=2)
        
        # Eyes
        eye_y = h // 6
        pg.draw.circle(self.image, (50, 50, 80), (w//2 - 4, eye_y), 2)
        pg.draw.circle(self.image, (50, 50, 80), (w//2 + 4, eye_y), 2)
        
        # Legs
        leg_top = h // 3 + h // 2
        leg_width = 5
        pg.draw.rect(self.image, (180, 100, 60), (w//3 - 2, leg_top, leg_width, h - leg_top), border_radius=2)
        pg.draw.rect(self.image, (180, 100, 60), (w - w//3 - 3, leg_top, leg_width, h - leg_top), border_radius=2)
        
        # Arms
        arm_y = h // 3 + 5
        arm_height = h // 3
        pg.draw.rect(self.image, (255, 220, 180), (2, arm_y, 4, arm_height), border_radius=2)
        pg.draw.rect(self.image, (255, 220, 180), (w - 6, arm_y, 4, arm_height), border_radius=2)
    
    def update_from_state(self, state):
        """Update player from network state"""
        self.pos.x = state['x']
        self.pos.y = state['y']
        self.facing = state['facing']
        self.rect.topleft = self.pos
    
    def draw(self, surf):
        """Draw the networked player"""
        surf.blit(self.image, self.rect)
        # Draw name tag
        font = pg.font.SysFont("consolas", 14, bold=True)
        name_surf = font.render(self.name, True, (255, 255, 255))
        name_x = self.rect.centerx - name_surf.get_width() // 2
        name_y = self.rect.top - 18
        surf.blit(name_surf, (name_x, name_y))

class MultiplayerGame:
    def __init__(self, server_ip, player_name):
        pg.init()
        pg.display.set_caption("Crate Rush - Multiplayer")
        self.screen = pg.display.set_mode((S.WIDTH, S.HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20, bold=True)
        self.big_font = pg.font.SysFont("consolas", 60, bold=True)
        self.mid_font = pg.font.SysFont("consolas", 32, bold=True)
        
        self.level = Level()
        self.network = NetworkClient(server_ip)
        self.player_name = player_name
        
        # Connect to server
        if not self.network.connect(player_name):
            print("[ERROR] Failed to connect to server!")
            self.running = False
            return
        
        print(f"[CONNECTED] Player ID: {self.network.player_id}")
        
        # Local player
        self.player = Player(S.WIDTH // 2 - 100, 60)
        self.player.give_weapon(random.choice(WEAPON_POOL)())
        
        # Other players
        self.other_players = {}
        
        # Game entities (managed by server)
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.crates = pg.sprite.Group()
        self.particles = pg.sprite.Group()
        
        self.running = True
        self.shake = 0.0
        self.time = 0.0
        
        # Track bullet cooldown locally
        self.shoot_cooldown = 0
        
    def update(self, dt):
        self.time += dt
        
        # Update local player
        keys = pg.key.get_pressed()
        dx = 0
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            dx -= 1
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            dx += 1
        
        self.player.vel.x = dx * S.PLAYER_SPEED
        if dx != 0:
            self.player.facing = 1 if dx > 0 else -1
        
        if (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) and self.player.on_ground:
            self.player.vel.y = S.JUMP_VELOCITY
        
        self.player.on_ground = self.player.physics_step(dt, self.level.platforms)
        
        # Respawn if falling
        if self.player.pos.y > S.HAZARD_HEIGHT + 100:
            self.player.respawn()
        
        self.player.rect.topleft = self.player.pos
        
        # Send player position to server
        self.network.send_player_move(
            self.player.pos.x, self.player.pos.y,
            self.player.vel.x, self.player.vel.y,
            self.player.facing
        )
        
        # Handle shooting
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        if self.player.weapon and (keys[pg.K_j] or keys[pg.K_f] or pg.mouse.get_pressed()[0]):
            if self.shoot_cooldown <= 0:
                ox = 14 * self.player.facing
                oy = -6
                origin = pg.Vector2(self.player.rect.centerx + ox, self.player.rect.centery + oy)
                aim = pg.Vector2(pg.mouse.get_pos())
                direction = (aim - origin)
                if direction.length_squared() == 0:
                    direction = pg.Vector2(self.player.facing, 0)
                else:
                    direction = direction.normalize()
                
                vel = direction * 900  # Bullet speed
                self.shoot_cooldown = self.player.weapon.cooldown
                
                # Send shoot command to server
                self.network.send_shoot(origin.x, origin.y, vel.x, vel.y, damage=1)
        
        # Get game state from server
        game_state = self.network.get_game_state()
        
        # Update other players
        server_players = game_state.get('players', {})
        current_player_ids = set(self.other_players.keys())
        server_player_ids = set(int(pid) for pid in server_players.keys())
        
        # Remove disconnected players
        for pid in current_player_ids - server_player_ids:
            if pid != self.network.player_id and pid in self.other_players:
                del self.other_players[pid]
        
        # Add/update players
        for pid_str, pdata in server_players.items():
            pid = int(pid_str)
            if pid != self.network.player_id:
                if pid not in self.other_players:
                    self.other_players[pid] = NetworkedPlayer(
                        pid, pdata['name'], pdata['x'], pdata['y']
                    )
                else:
                    self.other_players[pid].update_from_state(pdata)
        
        # Update particles
        for p in list(self.particles):
            p.update(dt)
        
        # Check crate collection
        server_crates = game_state.get('crates', {})
        for crate_id_str, crate_data in server_crates.items():
            crate_id = int(crate_id_str)
            crate_pos = pg.Vector2(crate_data['x'], crate_data['y'])
            if self.player.rect.collidepoint(crate_pos.x, crate_pos.y):
                # Collect crate
                weapon = random.choice(WEAPON_POOL)()
                self.player.give_weapon(weapon)
                self.network.send_collect_crate(crate_id, weapon.name)
                self.shake = min(16, self.shake + 8)
                Burst(self.particles, self.player.rect.center, (240, 210, 120), count=14, speed=280)
        
        self.shake = max(0.0, self.shake - 14.0 * dt)
    
    def draw(self):
        self.screen.fill((12, 14, 20))
        
        # Calculate shake offset
        ox = int(random.uniform(-self.shake, self.shake))
        oy = int(random.uniform(-self.shake, self.shake))
        
        # Draw platforms
        for p in self.level.platforms:
            self.screen.blit(p.image, p.rect.move(ox, oy))
        
        # Get game state
        game_state = self.network.get_game_state()
        
        # Draw enemies from server
        for enemy_data in game_state.get('enemies', {}).values():
            rect = pg.Rect(enemy_data['x'], enemy_data['y'], 28, 36)
            # Draw simple enemy representation
            pg.draw.rect(self.screen, (220, 110, 120), rect.move(ox, oy), border_radius=4)
        
        # Draw crates from server
        for crate_data in game_state.get('crates', {}).values():
            rect = pg.Rect(crate_data['x'] - 11, crate_data['y'] - 11, 22, 22)
            pg.draw.rect(self.screen, (200, 150, 80), rect.move(ox, oy), border_radius=2)
        
        # Draw bullets from server
        for bullet_data in game_state.get('bullets', {}).values():
            pos = (int(bullet_data['x']) + ox, int(bullet_data['y']) + oy)
            pg.draw.circle(self.screen, (250, 230, 90), pos, 4)
        
        # Draw other players
        for other_player in self.other_players.values():
            pr = other_player.rect.move(ox, oy)
            self.screen.blit(other_player.image, pr)
            # Draw name
            font = pg.font.SysFont("consolas", 14, bold=True)
            name_surf = font.render(other_player.name, True, (255, 255, 255))
            name_x = pr.centerx - name_surf.get_width() // 2
            name_y = pr.top - 18
            self.screen.blit(name_surf, (name_x, name_y))
        
        # Draw local player
        pr = self.player.rect.move(ox, oy)
        self.screen.blit(self.player.image, pr)
        
        # Draw particles
        for spr in self.particles:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        
        # Draw HUD
        self.draw_hud(game_state)
        
        pg.display.flip()
    
    def draw_hud(self, game_state):
        """Draw HUD with multiplayer info"""
        ui.draw_panel(self.screen, pg.Rect(8, 8, 360, 84), glow=True)
        
        # Get player's score from server
        my_score = 0
        server_players = game_state.get('players', {})
        if str(self.network.player_id) in server_players:
            my_score = server_players[str(self.network.player_id)]['score']
        
        ui.text(self.screen, self.mid_font, f"Crates: {my_score}", (255, 220, 100), (24, 20), glow=True)
        ui.text(self.screen, self.font, f"Players: {len(server_players)}", S.FG_COLOR, (24, 54))
        
        weapon_name = self.player.weapon.name if self.player.weapon else 'None'
        badge = pg.Rect(220, 20, 130, 36)
        ui.draw_panel(self.screen, badge, bg=(40, 70, 150), border=(100, 160, 255), glow=True)
        ui.text(self.screen, self.font, weapon_name, (255, 255, 255), (badge.centerx, badge.centery - 2), center=True, glow=True)
        
        ui.text(self.screen, self.font, f"ID: {self.network.player_id} | {self.player_name}", S.TIP_COLOR, (12, S.HEIGHT - 24))
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(S.FPS) / 1000.0
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.running = False
            
            if self.network.connected:
                self.update(dt)
                self.draw()
            else:
                print("[DISCONNECTED] Lost connection to server")
                self.running = False
        
        self.network.disconnect()
        pg.quit()

def start_multiplayer(server_ip="127.0.0.1", player_name="Player"):
    """Start multiplayer game"""
    game = MultiplayerGame(server_ip, player_name)
    if game.running:
        game.run()
