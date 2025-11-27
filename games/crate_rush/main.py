import math
import random
import json
from pathlib import Path
import pygame as pg
from . import settings as S
from .level import Level
from .player import Player
from .enemies import Enemy, Spawner, load_enemy1_frames, load_enemy2_frames
from .weapons import WEAPON_POOL
from .crate import Crate
from . import ui
from .particles import Burst
from .multiplayer import MultiplayerManager, get_local_ip

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Crate Rush")
        self.screen = pg.display.set_mode((S.WIDTH, S.HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20, bold=True)
        self.big_font = pg.font.SysFont("consolas", 60, bold=True)
        self.mid_font = pg.font.SysFont("consolas", 32, bold=True)
        
        # Pre-load all enemy sprites before game starts
        load_enemy1_frames()
        load_enemy2_frames()
        
        self.level = Level()
        self.save_path = Path(__file__).with_name('save.json')
        self.highscore = self.load_highscore()
        self.state = S.STATE_TITLE
        self.game_difficulty = S.DIFF_NORMAL  # Default difficulty
        self.selected_difficulty = S.DIFF_NORMAL  # Currently highlighted difficulty
        self.menu_selection = S.MENU_OFFLINE  # Main menu selection
        self.mp_menu_selection = S.MP_HOST  # Multiplayer menu selection
        self.shake = 0.0
        self.time = 0.0
        self.bg_offset = 0.0
        self.bg_change_timer = 0.0
        self.bg_change_interval = 10.0  # Change background every 10 seconds
        self.xp_level = 0
        
        # Multiplayer
        self.multiplayer = MultiplayerManager()
        self.player_name = "Player"
        self.join_ip = ""
        self.join_port = "5555"
        self.connection_mode = S.CONN_LAN  # LAN or PUBLIC
        self.input_active = False  # For text input
        self.input_field = "ip"  # 'ip' or 'port'
        self.input_text = ""
        self.input_mode = ""  # 'name' or 'ip'
        self.mp_error_message = ""
        self.mp_error_timer = 0
        self.selected_map = 0  # Index of selected map for host
        self.current_map_id = "classic"  # Current map being played
        
        self.reset_run(full=True)
        self.load_backgrounds()

    def reset_run(self, full=False, map_id=None):
        # Load map if specified
        if map_id:
            self.current_map_id = map_id
            self.level.load_map(map_id)
        
        self.all = pg.sprite.Group()
        self.platforms = self.level.platforms
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()  # Enemy bullets that can hit player
        self.crates = pg.sprite.Group()
        self.player = Player(S.WIDTH // 2 - 100, 60)
        self.all.add(self.player)
        self.difficulty = 0
        self.spawn_timer = S.ENEMY_SPAWN_START
        self.spawners = [Spawner(p) for p in self.level.spawners]
        self.crate_timer = 0
        self.crates_collected = 0 if full else self.crates_collected
        self.xp_level = 0 if full else self.xp_level
        self.player.give_weapon(random.choice(WEAPON_POOL)())
        self.particles = pg.sprite.Group()

    def spawn_enemy(self):
        sp = random.choice(self.spawners)
        e = sp.spawn(self.difficulty, self.game_difficulty)
        self.enemies.add(e)
        self.all.add(e)

    def spawn_crate(self):
        pos = self.level.random_crate_spot()
        c = Crate(pos)
        self.crates.add(c)
        self.all.add(c)

    def load_backgrounds(self):
        """Load all background images from the backgrounds folder"""
        self.bg_images = []
        self.bg_surfaces = []
        self.bg_widths = []
        self.current_bg_index = 0
        
        try:
            bg_folder = Path(__file__).with_name('backgrounds')
            if not bg_folder.exists():
                print(f"Backgrounds folder not found at: {bg_folder}")
                self.bg_surface = None
                return
            
            # Get all image files from backgrounds folder
            image_files = list(bg_folder.glob('*.jpg')) + list(bg_folder.glob('*.png'))
            
            if not image_files:
                print("No background images found in backgrounds folder")
                self.bg_surface = None
                return
            
            print(f"Found {len(image_files)} background images")
            
            # Load and process each background
            for bg_path in sorted(image_files):
                try:
                    img = pg.image.load(str(bg_path)).convert()
                    print(f"Loaded: {bg_path.name} ({img.get_width()}x{img.get_height()})")
                    
                    # Scale to cover screen while maintaining aspect ratio
                    img_ratio = img.get_width() / img.get_height()
                    screen_ratio = S.WIDTH / S.HEIGHT
                    if img_ratio > screen_ratio:
                        new_h = S.HEIGHT
                        new_w = int(new_h * img_ratio)
                    else:
                        new_w = S.WIDTH
                        new_h = int(new_w / img_ratio)
                    
                    scaled_img = pg.transform.smoothscale(img, (new_w, new_h))
                    self.bg_images.append(scaled_img)
                    self.bg_widths.append(new_w)
                    
                    # Apply opacity if needed
                    if S.BG_OPACITY < 255:
                        surface = scaled_img.copy()
                        surface.set_alpha(S.BG_OPACITY)
                        self.bg_surfaces.append(surface)
                    else:
                        self.bg_surfaces.append(scaled_img)
                except Exception as e:
                    print(f"Error loading {bg_path.name}: {e}")
            
            if self.bg_surfaces:
                self.bg_surface = self.bg_surfaces[0]
                self.bg_width = self.bg_widths[0]
                print(f"Successfully loaded {len(self.bg_surfaces)} backgrounds")
            else:
                self.bg_surface = None
                
        except Exception as e:
            print(f"Background loading error: {e}")
            self.bg_surface = None
    
    def cycle_background(self):
        """Switch to the next background image"""
        if not self.bg_surfaces:
            return
        
        self.current_bg_index = (self.current_bg_index + 1) % len(self.bg_surfaces)
        self.bg_surface = self.bg_surfaces[self.current_bg_index]
        self.bg_width = self.bg_widths[self.current_bg_index]
        self.bg_offset = 0  # Reset offset for new background

    def bullet_enemy_collisions(self):
        for b in list(self.bullets):
            hits = [e for e in self.enemies if e.rect.colliderect(b.rect)]
            if hits:
                for e in hits:
                    dead = e.damage(b.damage)
                    if dead:
                        e.kill()
                        self.shake = min(S.SHAKE_MAX, self.shake + 6)
                        Burst(self.particles, e.rect.center, (240,120,130), count=10, speed=260)
                b.kill()

    def enemy_player_collisions(self):
        # Don't check collision if player is invulnerable
        if self.player.invuln > 0:
            return
        if any(e.rect.colliderect(self.player.rect) for e in self.enemies):
            self.on_game_over()
    
    def enemy_bullet_player_collisions(self):
        """Check if enemy bullets hit the player"""
        # Don't check if player is invulnerable
        if self.player.invuln > 0:
            return
        for b in list(self.enemy_bullets):
            if b.rect.colliderect(self.player.rect):
                b.kill()
                self.shake = min(S.SHAKE_MAX, self.shake + 8)
                Burst(self.particles, self.player.rect.center, (255, 100, 100), count=12, speed=200)
                self.on_game_over()
                return

    def on_game_over(self):
        self.highscore = max(self.highscore, self.crates_collected)
        self.save_highscore()
        self.state = S.STATE_GAMEOVER
        self.shake = max(self.shake, 10)

    def update(self, dt):
        self.time += dt
        
        # Update error message timer
        if self.mp_error_timer > 0:
            self.mp_error_timer -= dt
        
        # Check for game start if in lobby (client waiting for host)
        if self.state == S.STATE_MULTIPLAYER_LOBBY:
            started, map_id = self.multiplayer.check_game_started()
            if started:
                self.reset_run(full=True, map_id=map_id)
                self.state = S.STATE_MULTIPLAYER_RUNNING
                return
        
        # Cycle backgrounds during gameplay
        if self.state in (S.STATE_RUNNING, S.STATE_MULTIPLAYER_RUNNING) and self.bg_surfaces:
            self.bg_change_timer += dt
            if self.bg_change_timer >= self.bg_change_interval:
                self.cycle_background()
                self.bg_change_timer = 0.0
        
        if self.state == S.STATE_MULTIPLAYER_RUNNING:
            # Multiplayer game update
            self._update_multiplayer_game(dt)
            return
        
        if self.state not in (S.STATE_RUNNING,):
            # Update minimal animations only
            for p in list(self.particles):
                p.update(dt)
            self.shake = max(0.0, self.shake - S.SHAKE_DECAY * dt)
            return

        self.player.update(dt, self.platforms, self.bullets)
        for e in list(self.enemies):
            e.update(dt, self.platforms, self.player, self.enemy_bullets)
        for b in list(self.bullets):
            b.update(dt, self.platforms)
        for b in list(self.enemy_bullets):
            b.update(dt, self.platforms)
        for p in list(self.particles):
            p.update(dt)
        self.bullet_enemy_collisions()
        self.enemy_player_collisions()
        self.enemy_bullet_player_collisions()
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.difficulty += 1
            self.spawn_timer = max(S.ENEMY_SPAWN_MIN, S.ENEMY_SPAWN_START - self.difficulty * S.ENEMY_SPAWN_ACCEL)
        self.crate_timer -= dt
        if len(self.crates) == 0 and self.crate_timer <= 0:
            self.spawn_crate()
        for c in list(self.crates):
            if c.rect.colliderect(self.player.rect):
                c.apply(self.player)
                c.kill()
                self.crates_collected += 1
                
                # Check for XP gift every 5 crates
                if self.crates_collected % 5 == 0:
                    self.xp_level += 1
                    self.shake = min(S.SHAKE_MAX, self.shake + 15)  # Big shake for gift
                    # Big golden burst for XP gift
                    Burst(self.particles, self.player.rect.center, (255,215,0), count=30, speed=350)
                    print(f"[XP GIFT] Level {self.xp_level}! Collected {self.crates_collected} crates!")
                else:
                    self.shake = min(S.SHAKE_MAX, self.shake + 8)
                    Burst(self.particles, self.player.rect.center, (240,210,120), count=14, speed=280)
                
                self.crate_timer = S.CRATE_RESPAWN_DELAY
        self.shake = max(0.0, self.shake - S.SHAKE_DECAY * dt)
        # Parallax scroll effect
        if self.bg_surface:
            self.bg_offset += S.BG_PARALLAX_SPEED * dt * 60
            if self.bg_offset >= self.bg_width:
                self.bg_offset = 0

    def draw_hud(self):
        pulse = 1.0 + 0.08 * math.sin(self.time * 4)
        ui.draw_panel(self.screen, pg.Rect(8, 8, 400, 100), glow=True)
        score_col = (255, 220, 100) if self.crates_collected > 0 else S.FG_COLOR
        ui.text(self.screen, self.mid_font, f"Crates: {self.crates_collected}", score_col, (24, 20), glow=(self.crates_collected > 0))
        
        # Show XP level with gift indicator
        xp_progress = self.crates_collected % 5
        xp_text = f"XP Level: {self.xp_level} ({xp_progress}/5)"
        xp_col = (255, 215, 0) if xp_progress == 0 and self.crates_collected > 0 else (100, 200, 255)
        ui.text(self.screen, self.font, xp_text, xp_col, (24, 54), glow=(xp_progress >= 3))
        
        ui.text(self.screen, self.font, f"Best: {self.highscore}", S.FG_COLOR, (24, 78))
        name = self.player.weapon.name if self.player.weapon else 'None'
        badge = pg.Rect(220, 20, 130, 36)
        ui.draw_panel(self.screen, badge, bg=(40,70,150), border=(100,160,255), glow=True)
        ui.text(self.screen, self.font, name, (255,255,255), (badge.centerx, badge.centery-2), center=True, glow=True)
        ui.text(self.screen, self.font, "Move: A/D or Arrows  Jump: Space  Shoot: J/F/Mouse  Pause: P", S.TIP_COLOR, (12, S.HEIGHT - 24))

    def draw_title(self):
        ui.gradient_bg(self.screen)
        # Draw background on title with slow scroll
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        pulse = 1.0 + 0.12 * math.sin(self.time * 3)
        title = "CRATE RUSH"
        for off in [(-3,3),(3,3),(-3,-3),(3,-3)]:
            ui.text(self.screen, self.big_font, title, (80,50,20), (S.WIDTH//2+off[0], 120+off[1]), center=True, shadow=False)
        ui.text(self.screen, self.big_font, title, S.TITLE_COLOR, (S.WIDTH//2, 120), center=True, shadow=True, glow=True)
        ui.text(self.screen, self.font, "Collect crates to swap weapons. One hit = game over!", S.TIP_COLOR, (S.WIDTH//2, 190), center=True)
        panel = pg.Rect(S.WIDTH//2 - 240, 230, 480, 180)
        ui.draw_panel(self.screen, panel, glow=True)
        start_pulse = int(120 + 135 * abs(math.sin(self.time * 3)))
        start_col = (start_pulse, 255, start_pulse)
        ui.text(self.screen, self.mid_font, "Press Enter to Start", start_col, (S.WIDTH//2, 270), center=True, glow=True)
        # Show current difficulty
        diff_settings = S.DIFFICULTY_SETTINGS[self.game_difficulty]
        ui.text(self.screen, self.font, f"Difficulty: {diff_settings['name']}", diff_settings['color'], (S.WIDTH//2, 320), center=True, glow=True)
        ui.text(self.screen, self.font, "Press D to change difficulty", S.TIP_COLOR, (S.WIDTH//2, 355), center=True)
        ui.text(self.screen, self.font, "Controls: A/D, Space, J/F/Mouse, P to Pause", S.TIP_COLOR, (S.WIDTH//2, 390), center=True)
        pg.display.flip()
    
    def draw_difficulty_select(self):
        """Draw difficulty selection screen"""
        ui.gradient_bg(self.screen)
        # Draw background
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Title
        ui.text(self.screen, self.big_font, "SELECT DIFFICULTY", S.TITLE_COLOR, (S.WIDTH//2, 80), center=True, shadow=True, glow=True)
        
        # Difficulty options
        difficulties = [
            (S.DIFF_EASY, "EASY", "Enemies miss a lot, shoot slowly"),
            (S.DIFF_NORMAL, "NORMAL", "Balanced challenge"),
            (S.DIFF_HARD, "HARD", "Accurate enemies, fast shooting"),
            (S.DIFF_SUPERHARD, "SUPER HARD", "Near-perfect aim, relentless fire"),
        ]
        
        start_y = 150
        for i, (diff_id, name, desc) in enumerate(difficulties):
            y_pos = start_y + i * 90
            settings = S.DIFFICULTY_SETTINGS[diff_id]
            
            # Highlight selected
            is_selected = (diff_id == self.selected_difficulty)
            
            # Draw panel for each option
            panel_width = 500
            panel = pg.Rect(S.WIDTH//2 - panel_width//2, y_pos - 10, panel_width, 75)
            
            if is_selected:
                # Pulsing glow for selected
                pulse = abs(math.sin(self.time * 4))
                glow_color = tuple(int(c * (0.7 + 0.3 * pulse)) for c in settings['color'])
                ui.draw_panel(self.screen, panel, bg=(40, 50, 80), border=glow_color, glow=True)
                # Arrow indicator
                arrow_x = panel.left - 30
                ui.text(self.screen, self.mid_font, ">", settings['color'], (arrow_x, y_pos + 20), center=True, glow=True)
            else:
                ui.draw_panel(self.screen, panel, bg=(25, 30, 45), border=(60, 70, 90), glow=False)
            
            # Difficulty name
            name_color = settings['color'] if is_selected else (150, 150, 150)
            ui.text(self.screen, self.mid_font, name, name_color, (S.WIDTH//2, y_pos + 12), center=True, glow=is_selected)
            
            # Description
            desc_color = S.TIP_COLOR if is_selected else (100, 100, 120)
            ui.text(self.screen, self.font, desc, desc_color, (S.WIDTH//2, y_pos + 45), center=True)
        
        # Instructions
        ui.text(self.screen, self.font, "Up/Down or W/S to select  |  Enter to confirm  |  Esc to go back", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT - 40), center=True)
        pg.display.flip()

    def draw_main_menu(self):
        """Draw main menu with Offline/Online selection"""
        ui.gradient_bg(self.screen)
        # Draw background
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Title
        for off in [(-3,3),(3,3),(-3,-3),(3,-3)]:
            ui.text(self.screen, self.big_font, "CRATE RUSH", (80,50,20), (S.WIDTH//2+off[0], 100+off[1]), center=True, shadow=False)
        ui.text(self.screen, self.big_font, "CRATE RUSH", S.TITLE_COLOR, (S.WIDTH//2, 100), center=True, shadow=True, glow=True)
        
        ui.text(self.screen, self.mid_font, "SELECT GAME MODE", (200, 220, 255), (S.WIDTH//2, 180), center=True, glow=True)
        
        # Menu options
        menu_options = [
            (S.MENU_OFFLINE, "OFFLINE MODE", "Play solo against AI enemies", (100, 255, 100)),
            (S.MENU_ONLINE, "ONLINE MULTIPLAYER", "Play with friends online", (100, 180, 255)),
        ]
        
        start_y = 260
        for i, (option_id, name, desc, color) in enumerate(menu_options):
            y_pos = start_y + i * 110
            is_selected = (option_id == self.menu_selection)
            
            # Draw panel for each option
            panel_width = 450
            panel = pg.Rect(S.WIDTH//2 - panel_width//2, y_pos - 15, panel_width, 85)
            
            if is_selected:
                # Pulsing glow for selected
                pulse = abs(math.sin(self.time * 4))
                glow_color = tuple(int(c * (0.7 + 0.3 * pulse)) for c in color)
                ui.draw_panel(self.screen, panel, bg=(40, 50, 80), border=glow_color, glow=True)
                # Arrow indicator
                arrow_x = panel.left - 30
                ui.text(self.screen, self.mid_font, ">", color, (arrow_x, y_pos + 25), center=True, glow=True)
            else:
                ui.draw_panel(self.screen, panel, bg=(25, 30, 45), border=(60, 70, 90), glow=False)
            
            # Option name
            name_color = color if is_selected else (120, 120, 120)
            ui.text(self.screen, self.mid_font, name, name_color, (S.WIDTH//2, y_pos + 15), center=True, glow=is_selected)
            
            # Description
            desc_color = S.TIP_COLOR if is_selected else (100, 100, 120)
            ui.text(self.screen, self.font, desc, desc_color, (S.WIDTH//2, y_pos + 50), center=True)
        
        # Current difficulty display
        diff_settings = S.DIFFICULTY_SETTINGS[self.game_difficulty]
        ui.text(self.screen, self.font, f"Difficulty: {diff_settings['name']}", diff_settings['color'], (S.WIDTH//2, S.HEIGHT - 80), center=True, glow=True)
        
        # Instructions
        ui.text(self.screen, self.font, "Up/Down to select  |  Enter to confirm  |  D for difficulty  |  Esc to go back", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT - 40), center=True)
        pg.display.flip()

    def draw_multiplayer_soon(self):
        """Draw coming soon message for multiplayer"""
        ui.gradient_bg(self.screen)
        # Draw background
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Big panel in center
        panel = pg.Rect(S.WIDTH//2 - 300, S.HEIGHT//2 - 120, 600, 240)
        ui.draw_panel(self.screen, panel, bg=(30, 40, 60), border=(100, 180, 255), glow=True)
        
        # Coming soon text with pulsing effect
        pulse = abs(math.sin(self.time * 2))
        title_color = (int(100 + 155 * pulse), int(180 + 75 * pulse), 255)
        ui.text(self.screen, self.big_font, "COMING SOON!", title_color, (S.WIDTH//2, S.HEIGHT//2 - 40), center=True, glow=True)
        
        ui.text(self.screen, self.mid_font, "Online Multiplayer", (200, 220, 255), (S.WIDTH//2, S.HEIGHT//2 + 20), center=True)
        ui.text(self.screen, self.font, "This feature is currently under development.", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT//2 + 60), center=True)
        ui.text(self.screen, self.font, "Stay tuned for updates!", (255, 200, 100), (S.WIDTH//2, S.HEIGHT//2 + 90), center=True)
        
        # Instructions
        ui.text(self.screen, self.font, "Press Enter or Esc to go back", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT - 40), center=True)
        pg.display.flip()
    
    def draw_multiplayer_menu(self):
        """Draw multiplayer menu (Host/Join selection)"""
        ui.gradient_bg(self.screen)
        # Draw background
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Title
        ui.text(self.screen, self.big_font, "MULTIPLAYER", S.TITLE_COLOR, (S.WIDTH//2, 80), center=True, shadow=True, glow=True)
        
        # Player name display
        ui.text(self.screen, self.font, f"Player Name: {self.player_name}", (200, 220, 255), (S.WIDTH//2, 130), center=True)
        ui.text(self.screen, self.font, "Press N to change name", S.TIP_COLOR, (S.WIDTH//2, 155), center=True)
        
        # Menu options
        menu_options = [
            (S.MP_HOST, "HOST GAME", "Create a game lobby for others to join", (100, 255, 100)),
            (S.MP_JOIN, "JOIN GAME", "Connect to an existing game", (100, 180, 255)),
        ]
        
        start_y = 200
        for i, (option_id, name, desc, color) in enumerate(menu_options):
            y_pos = start_y + i * 110
            is_selected = (option_id == self.mp_menu_selection)
            
            panel_width = 450
            panel = pg.Rect(S.WIDTH//2 - panel_width//2, y_pos - 15, panel_width, 85)
            
            if is_selected:
                pulse = abs(math.sin(self.time * 4))
                glow_color = tuple(int(c * (0.7 + 0.3 * pulse)) for c in color)
                ui.draw_panel(self.screen, panel, bg=(40, 50, 80), border=glow_color, glow=True)
                arrow_x = panel.left - 30
                ui.text(self.screen, self.mid_font, ">", color, (arrow_x, y_pos + 25), center=True, glow=True)
            else:
                ui.draw_panel(self.screen, panel, bg=(25, 30, 45), border=(60, 70, 90), glow=False)
            
            name_color = color if is_selected else (120, 120, 120)
            ui.text(self.screen, self.mid_font, name, name_color, (S.WIDTH//2, y_pos + 15), center=True, glow=is_selected)
            
            desc_color = S.TIP_COLOR if is_selected else (100, 100, 120)
            ui.text(self.screen, self.font, desc, desc_color, (S.WIDTH//2, y_pos + 50), center=True)
        
        # Show local IP
        local_ip = get_local_ip()
        ui.text(self.screen, self.font, f"Your IP: {local_ip}", (180, 180, 200), (S.WIDTH//2, S.HEIGHT - 80), center=True)
        
        # Instructions
        ui.text(self.screen, self.font, "Up/Down to select  |  Enter to confirm  |  Esc to go back", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT - 40), center=True)
        pg.display.flip()
    
    def draw_multiplayer_host(self):
        """Draw hosting lobby screen with map selection"""
        from .level import Level
        
        ui.gradient_bg(self.screen)
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Title
        ui.text(self.screen, self.big_font, "HOSTING GAME", (100, 255, 100), (S.WIDTH//2, 40), center=True, shadow=True, glow=True)
        
        # Left side - Connection info
        info_panel = pg.Rect(30, 80, 320, 120)
        ui.draw_panel(self.screen, info_panel, bg=(30, 50, 40), border=(100, 200, 100), glow=False)
        
        local_ip = get_local_ip()
        ui.text(self.screen, self.font, "LAN:", (100, 200, 100), (190, 95), center=True)
        ui.text(self.screen, self.font, f"{local_ip}:{S.DEFAULT_PORT}", (150, 255, 150), (190, 120), center=True)
        ui.text(self.screen, self.font, "PUBLIC: Use tunnel address", (255, 180, 100), (190, 150), center=True)
        ui.text(self.screen, self.font, "(playit.gg/ngrok)", (200, 150, 80), (190, 175), center=True)
        
        # Right side - Map selection
        map_panel = pg.Rect(610, 80, 320, 120)
        ui.draw_panel(self.screen, map_panel, bg=(40, 35, 50), border=(180, 120, 200), glow=False)
        
        ui.text(self.screen, self.font, "MAP (Left/Right to change)", (180, 140, 220), (770, 95), center=True)
        
        maps = Level.get_map_list()
        current_map = maps[self.selected_map]
        map_id, map_name, map_desc = current_map
        
        # Map name with arrows
        arrow_color = (180, 140, 220)
        ui.text(self.screen, self.font, "<", arrow_color, (660, 125), center=True)
        ui.text(self.screen, self.mid_font, map_name, (220, 180, 255), (770, 125), center=True, glow=True)
        ui.text(self.screen, self.font, ">", arrow_color, (880, 125), center=True)
        
        # Map description
        ui.text(self.screen, self.font, map_desc, (150, 150, 170), (770, 155), center=True)
        
        # Map counter
        ui.text(self.screen, self.font, f"{self.selected_map + 1}/{len(maps)}", (120, 120, 140), (770, 180), center=True)
        
        # Players panel (center)
        players_panel = pg.Rect(S.WIDTH//2 - 200, 215, 400, 150)
        ui.draw_panel(self.screen, players_panel, bg=(25, 30, 45), border=(80, 120, 180), glow=False)
        
        ui.text(self.screen, self.mid_font, "PLAYERS IN LOBBY", (200, 220, 255), (S.WIDTH//2, 235), center=True)
        
        player_list = self.multiplayer.get_player_list()
        player_count = len(player_list)
        
        y_offset = 270
        for i, name in enumerate(player_list[:4]):  # Show max 4 players
            color = (100, 255, 100) if i == 0 else (200, 200, 200)
            prefix = "(You) " if i == 0 else ""
            ui.text(self.screen, self.font, f"{prefix}{name}", color, (S.WIDTH//2, y_offset + i * 22), center=True)
        
        ui.text(self.screen, self.font, f"Players: {player_count}", (180, 180, 200), (S.WIDTH//2, 380), center=True)
        
        # Error message
        if self.mp_error_timer > 0 and self.mp_error_message:
            ui.text(self.screen, self.font, self.mp_error_message, (255, 100, 100), (S.WIDTH//2, 405), center=True)
        
        # Start button hint
        pulse = abs(math.sin(self.time * 3))
        start_color = (int(100 + 155 * pulse), 255, int(100 + 155 * pulse))
        ui.text(self.screen, self.mid_font, "Press SPACE to Start Game", start_color, (S.WIDTH//2, S.HEIGHT - 80), center=True, glow=True)
        ui.text(self.screen, self.font, "Left/Right: Map  |  N: Name  |  Esc: Cancel", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT - 40), center=True)
        
        # Draw name input overlay if active
        if self.input_mode == 'name':
            self.draw_name_input()
        
        pg.display.flip()
    
    def draw_multiplayer_join(self):
        """Draw join game screen with IP input and connection mode selection"""
        ui.gradient_bg(self.screen)
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Title
        ui.text(self.screen, self.big_font, "JOIN GAME", (100, 180, 255), (S.WIDTH//2, 60), center=True, shadow=True, glow=True)
        
        # Connection mode selection
        mode_panel = pg.Rect(S.WIDTH//2 - 250, 110, 500, 60)
        ui.draw_panel(self.screen, mode_panel, bg=(25, 30, 45), border=(80, 120, 180), glow=False)
        
        ui.text(self.screen, self.font, "Connection Mode (Press TAB to switch):", S.TIP_COLOR, (S.WIDTH//2, 125), center=True)
        
        # LAN option
        lan_color = (100, 255, 100) if self.connection_mode == S.CONN_LAN else (100, 100, 120)
        lan_text = "[ LAN ]" if self.connection_mode == S.CONN_LAN else "  LAN  "
        ui.text(self.screen, self.mid_font, lan_text, lan_color, (S.WIDTH//2 - 80, 150), center=True, glow=(self.connection_mode == S.CONN_LAN))
        
        # Public option
        pub_color = (255, 180, 100) if self.connection_mode == S.CONN_PUBLIC else (100, 100, 120)
        pub_text = "[ PUBLIC ]" if self.connection_mode == S.CONN_PUBLIC else "  PUBLIC  "
        ui.text(self.screen, self.mid_font, pub_text, pub_color, (S.WIDTH//2 + 80, 150), center=True, glow=(self.connection_mode == S.CONN_PUBLIC))
        
        # IP input panel
        input_panel = pg.Rect(S.WIDTH//2 - 250, 185, 500, 140)
        border_color = (100, 200, 255) if self.input_active else (80, 120, 180)
        ui.draw_panel(self.screen, input_panel, bg=(25, 30, 45), border=border_color, glow=self.input_active)
        
        if self.connection_mode == S.CONN_LAN:
            # LAN mode - just IP input
            ui.text(self.screen, self.font, "Enter Host IP Address:", S.TIP_COLOR, (S.WIDTH//2, 205), center=True)
            
            # IP input box
            ip_box = pg.Rect(S.WIDTH//2 - 150, 230, 300, 40)
            ip_border = (100, 255, 100) if self.input_active else (80, 120, 180)
            pg.draw.rect(self.screen, (40, 45, 60), ip_box, border_radius=8)
            pg.draw.rect(self.screen, ip_border, ip_box, width=2, border_radius=8)
            
            # Display IP with cursor
            display_ip = self.join_ip
            if self.input_active and int(self.time * 2) % 2 == 0:
                display_ip += "|"
            ui.text(self.screen, self.mid_font, display_ip, (255, 255, 255), (S.WIDTH//2, 250), center=True)
            
            # Example
            ui.text(self.screen, self.font, "Example: 192.168.1.100", (120, 120, 140), (S.WIDTH//2, 295), center=True)
        else:
            # Public mode - IP/hostname + port input
            ui.text(self.screen, self.font, "Enter ngrok/Public Address:", S.TIP_COLOR, (S.WIDTH//2 - 70, 205), center=True)
            ui.text(self.screen, self.font, "Port:", S.TIP_COLOR, (S.WIDTH//2 + 175, 205), center=True)
            
            # Address input box
            addr_box = pg.Rect(S.WIDTH//2 - 230, 230, 280, 40)
            addr_border = (255, 180, 100) if (self.input_active and self.input_field == 'ip') else (80, 120, 180)
            pg.draw.rect(self.screen, (40, 45, 60), addr_box, border_radius=8)
            pg.draw.rect(self.screen, addr_border, addr_box, width=2, border_radius=8)
            
            # Display address with cursor
            display_addr = self.join_ip
            if self.input_active and self.input_field == 'ip' and int(self.time * 2) % 2 == 0:
                display_addr += "|"
            ui.text(self.screen, self.font, display_addr, (255, 255, 255), (addr_box.centerx, 250), center=True)
            
            # Port input box
            port_box = pg.Rect(S.WIDTH//2 + 100, 230, 100, 40)
            port_border = (255, 180, 100) if (self.input_active and self.input_field == 'port') else (80, 120, 180)
            pg.draw.rect(self.screen, (40, 45, 60), port_box, border_radius=8)
            pg.draw.rect(self.screen, port_border, port_box, width=2, border_radius=8)
            
            # Display port with cursor
            display_port = self.join_port
            if self.input_active and self.input_field == 'port' and int(self.time * 2) % 2 == 0:
                display_port += "|"
            ui.text(self.screen, self.mid_font, display_port, (255, 255, 255), (port_box.centerx, 250), center=True)
            
            # Example
            ui.text(self.screen, self.font, "Example: 0.tcp.ngrok.io  Port: 12345", (120, 120, 140), (S.WIDTH//2, 295), center=True)
        
        # Error message
        if self.mp_error_timer > 0 and self.mp_error_message:
            ui.text(self.screen, self.font, self.mp_error_message, (255, 100, 100), (S.WIDTH//2, 340), center=True)
        
        # Instructions
        if self.connection_mode == S.CONN_PUBLIC:
            ui.text(self.screen, self.font, "Ctrl+V: Paste  |  TAB: Switch field/mode  |  Enter: Connect  |  Esc: Back", S.TIP_COLOR, (S.WIDTH//2, 380), center=True)
        else:
            ui.text(self.screen, self.font, "Ctrl+V: Paste  |  TAB: Switch mode  |  Enter: Connect  |  Esc: Back", S.TIP_COLOR, (S.WIDTH//2, 380), center=True)
        
        # Mode description
        if self.connection_mode == S.CONN_LAN:
            ui.text(self.screen, self.font, "LAN Mode: Connect to a host on your local network", (100, 200, 100), (S.WIDTH//2, S.HEIGHT - 40), center=True)
        else:
            ui.text(self.screen, self.font, "PUBLIC Mode: Connect via ngrok or port forwarding", (255, 180, 100), (S.WIDTH//2, S.HEIGHT - 40), center=True)
        
        pg.display.flip()
    
    def draw_multiplayer_lobby(self):
        """Draw lobby waiting screen (for clients)"""
        ui.gradient_bg(self.screen)
        if self.bg_surface:
            offset = int(self.time * 20) % self.bg_width
            x1 = -offset
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Title
        pulse = abs(math.sin(self.time * 2))
        title_color = (int(100 + 80 * pulse), int(180 + 40 * pulse), 255)
        ui.text(self.screen, self.big_font, "WAITING IN LOBBY", title_color, (S.WIDTH//2, 80), center=True, shadow=True, glow=True)
        
        # Connection status
        ui.text(self.screen, self.font, f"Connected to: {self.join_ip}", (150, 200, 150), (S.WIDTH//2, 130), center=True)
        
        # Players panel
        players_panel = pg.Rect(S.WIDTH//2 - 200, 170, 400, 200)
        ui.draw_panel(self.screen, players_panel, bg=(25, 30, 45), border=(80, 120, 180), glow=False)
        
        ui.text(self.screen, self.mid_font, "PLAYERS", (200, 220, 255), (S.WIDTH//2, 195), center=True)
        
        player_list = self.multiplayer.get_player_list()
        y_offset = 235
        for i, name in enumerate(player_list[:6]):
            color = (100, 255, 100) if name == self.player_name else (200, 200, 200)
            prefix = "(You) " if name == self.player_name else ""
            ui.text(self.screen, self.font, f"{prefix}{name}", color, (S.WIDTH//2, y_offset + i * 25), center=True)
        
        # Waiting animation
        dots = "." * (int(self.time * 2) % 4)
        ui.text(self.screen, self.mid_font, f"Waiting for host to start{dots}", S.TIP_COLOR, (S.WIDTH//2, 400), center=True)
        
        # Instructions
        ui.text(self.screen, self.font, "N to change name  |  Esc to disconnect", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT - 40), center=True)
        
        # Draw name input overlay if active
        if self.input_mode == 'name':
            self.draw_name_input()
        
        pg.display.flip()
    
    def draw_name_input(self):
        """Draw name input overlay"""
        # Darken background
        s = pg.Surface((S.WIDTH, S.HEIGHT), pg.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))
        
        # Input panel
        panel = pg.Rect(S.WIDTH//2 - 200, S.HEIGHT//2 - 60, 400, 120)
        ui.draw_panel(self.screen, panel, bg=(30, 35, 50), border=(100, 180, 255), glow=True)
        
        ui.text(self.screen, self.mid_font, "Enter Your Name", (200, 220, 255), (S.WIDTH//2, S.HEIGHT//2 - 35), center=True)
        
        # Input box
        input_box = pg.Rect(S.WIDTH//2 - 120, S.HEIGHT//2, 240, 35)
        pg.draw.rect(self.screen, (40, 45, 60), input_box, border_radius=6)
        pg.draw.rect(self.screen, (100, 180, 255), input_box, width=2, border_radius=6)
        
        display_text = self.input_text
        if int(self.time * 2) % 2 == 0:
            display_text += "|"
        ui.text(self.screen, self.font, display_text, (255, 255, 255), (S.WIDTH//2, S.HEIGHT//2 + 17), center=True)
        
        ui.text(self.screen, self.font, "Enter to confirm  |  Esc to cancel", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT//2 + 50), center=True)
    
    def _update_multiplayer_game(self, dt):
        """Update multiplayer game state"""
        # Track bullet count before update to detect new bullets
        bullet_count_before = len(self.bullets)
        
        # Update player
        self.player.update(dt, self.platforms, self.bullets)
        
        # Check if player spawned new bullets and send to network
        if len(self.bullets) > bullet_count_before:
            # New bullets were added - send them to other players
            for bullet in list(self.bullets)[-(len(self.bullets) - bullet_count_before):]:
                # Only send bullets we created locally (not remote bullets)
                if not getattr(bullet, 'is_remote', False):
                    self.multiplayer.send_bullet_spawn(
                        bullet.pos.x, bullet.pos.y,
                        bullet.vel.x, bullet.vel.y,
                        getattr(bullet, 'color', (255, 220, 80)),
                        getattr(bullet, 'damage', 1),
                        getattr(bullet, 'radius', 4)
                    )
        
        # Update multiplayer state
        self.multiplayer.update(dt, self.player, self.player.weapon)
        
        # Spawn remote bullets
        self._spawn_remote_bullets()
        
        # Update bullets
        for b in list(self.bullets):
            b.update(dt, self.platforms)
        
        # Check bullet collisions with remote players
        self._check_multiplayer_bullet_hits()
        
        # Update particles
        for p in list(self.particles):
            p.update(dt)
        
        # Respawn check
        if self.player.pos.y > 450:
            self.player.respawn()
        
        # Shake decay
        self.shake = max(0.0, self.shake - S.SHAKE_DECAY * dt)
        
        # Parallax scroll
        if self.bg_surface:
            self.bg_offset += S.BG_PARALLAX_SPEED * dt * 60
            if self.bg_offset >= self.bg_width:
                self.bg_offset = 0
    
    def _check_multiplayer_bullet_hits(self):
        """Check if local player's bullets hit remote players"""
        for b in list(self.bullets):
            for player_id, remote in list(self.multiplayer.remote_players.items()):
                # Create a slightly larger hitbox for remote players
                hitbox = pg.Rect(remote.rect.x - 10, remote.rect.y - 20, 
                                remote.rect.width + 20, remote.rect.height + 40)
                if hitbox.colliderect(b.rect):
                    # Hit detected!
                    damage = getattr(b, 'damage', 1)
                    remote.health -= damage * 10  # 10 damage per hit
                    
                    # Visual feedback
                    self.shake = min(S.SHAKE_MAX, self.shake + 4)
                    Burst(self.particles, b.rect.center, (255, 100, 100), count=8, speed=200)
                    
                    # Send hit to server
                    self.multiplayer.send_player_hit(player_id, damage * 10)
                    
                    b.kill()
                    
                    # Check if player died
                    if remote.health <= 0:
                        remote.health = 0
                        self.multiplayer.send_player_kill(player_id)
                        Burst(self.particles, remote.rect.center, (255, 50, 50), count=20, speed=300)
                    break
        
        # Check if we got hit by remote bullets
        self.multiplayer.check_incoming_hits(self.player, self.particles, self)
    
    def _spawn_remote_bullets(self):
        """Spawn bullets from remote players"""
        from .weapons import Bullet
        
        for bullet_data in self.multiplayer.get_pending_bullets():
            # Don't spawn our own bullets (we already have them)
            if self.multiplayer.client and bullet_data.get("owner_id") == self.multiplayer.client.player_id:
                continue
            
            pos = (bullet_data["pos_x"], bullet_data["pos_y"])
            vel = (bullet_data["vel_x"], bullet_data["vel_y"])
            color = tuple(bullet_data.get("color", (255, 220, 80)))
            damage = bullet_data.get("damage", 1)
            radius = bullet_data.get("radius", 4)
            
            # Create the bullet
            bullet = Bullet(pos, vel, radius=radius, color=color, damage=damage)
            # Mark it as remote so we don't send it back
            bullet.is_remote = True
            self.bullets.add(bullet)
    
    def draw_multiplayer_game(self):
        """Draw multiplayer game state"""
        # Fill with dark base
        self.screen.fill((12, 14, 20))
        
        # Calculate shake offset
        ox = int(random.uniform(-self.shake, self.shake))
        oy = int(random.uniform(-self.shake, self.shake))
        
        # Draw background
        if self.bg_surface:
            x1 = -int(self.bg_offset) + ox
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2 + oy
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        
        # Draw platforms
        for p in self.platforms:
            self.screen.blit(p.image, p.rect.move(ox, oy))
        
        # Draw remote players
        self.multiplayer.draw_remote_players(self.screen, offset=(ox, oy))
        
        # Draw bullets
        for spr in self.bullets:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        
        # Draw particles
        for spr in self.particles:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        
        # Draw local player
        self.player.draw(self.screen, offset=(ox, oy))
        
        # Draw local player name above head
        name_font = pg.font.SysFont("consolas", 14, bold=True)
        name_surf = name_font.render(self.player_name, True, (100, 255, 100))
        name_x = self.player.rect.centerx - name_surf.get_width() // 2 + ox
        name_y = self.player.rect.top - 25 + oy
        name_shadow = name_font.render(self.player_name, True, (0, 0, 0))
        self.screen.blit(name_shadow, (name_x + 1, name_y + 1))
        self.screen.blit(name_surf, (name_x, name_y))
        
        # Draw multiplayer HUD
        self.draw_multiplayer_hud()
        
        if self.state == S.STATE_PAUSED:
            self.draw_pause()
        
        pg.display.flip()
    
    def draw_multiplayer_hud(self):
        """Draw HUD for multiplayer mode"""
        # Left panel - player info
        ui.draw_panel(self.screen, pg.Rect(8, 8, 200, 100), glow=True)
        
        ui.text(self.screen, self.font, f"Player: {self.player_name}", (100, 255, 100), (20, 16))
        
        weapon_name = self.player.weapon.name if self.player.weapon else 'None'
        ui.text(self.screen, self.font, f"Weapon: {weapon_name}", (200, 200, 255), (20, 40))
        
        player_count = self.multiplayer.get_player_count()
        ui.text(self.screen, self.font, f"Players: {player_count}", S.TIP_COLOR, (20, 64))
        
        # Health bar
        health = self.multiplayer.local_health
        health_bar_x = 20
        health_bar_y = 85
        bar_width = 170
        bar_height = 10
        
        # Background
        pg.draw.rect(self.screen, (60, 60, 60), (health_bar_x, health_bar_y, bar_width, bar_height))
        # Health fill
        health_fill = int(bar_width * (health / 100))
        health_color = (100, 255, 100) if health > 50 else (255, 200, 50) if health > 25 else (255, 80, 80)
        pg.draw.rect(self.screen, health_color, (health_bar_x, health_bar_y, health_fill, bar_height))
        # Border
        pg.draw.rect(self.screen, (100, 100, 100), (health_bar_x, health_bar_y, bar_width, bar_height), 1)
        
        # Controls hint
        ui.text(self.screen, self.font, "Move: A/D  Jump: Space  Shoot: Mouse/J  Pause: P", S.TIP_COLOR, (12, S.HEIGHT - 24))

    def draw_pause(self):
        s = pg.Surface((S.WIDTH, S.HEIGHT), pg.SRCALPHA)
        s.fill((0,0,0,160))
        self.screen.blit(s, (0,0))
        panel = pg.Rect(S.WIDTH//2 - 200, S.HEIGHT//2 - 80, 400, 140)
        ui.draw_panel(self.screen, panel, glow=True)
        ui.text(self.screen, self.big_font, "Paused", (150,220,255), (S.WIDTH//2, S.HEIGHT//2 - 20), center=True, glow=True)
        ui.text(self.screen, self.font, "Press P or Esc to resume", S.TIP_COLOR, (S.WIDTH//2, S.HEIGHT//2 + 30), center=True)

    def draw_gameover(self):
        s = pg.Surface((S.WIDTH, S.HEIGHT), pg.SRCALPHA)
        s.fill((0,0,0,170))
        self.screen.blit(s, (0,0))
        panel = pg.Rect(S.WIDTH//2 - 260, 120, 520, 220)
        ui.draw_panel(self.screen, panel, glow=True)
        ui.text(self.screen, self.big_font, "Game Over", S.DANGER, (S.WIDTH//2, 160), center=True, glow=True)
        score_col = S.SCORE_GLOW if self.crates_collected == self.highscore and self.crates_collected > 0 else S.FG_COLOR
        ui.text(self.screen, self.mid_font, f"Crates: {self.crates_collected}", score_col, (S.WIDTH//2, 220), center=True, glow=(self.crates_collected == self.highscore))
        ui.text(self.screen, self.font, f"Best: {self.highscore}", S.FG_COLOR, (S.WIDTH//2, 260), center=True)
        ui.text(self.screen, self.font, "R to retry  |  Enter to Title", S.TIP_COLOR, (S.WIDTH//2, 305), center=True)

    def draw_world(self):
        # Draw parallax background if loaded
        if self.bg_surface:
            x1 = -int(self.bg_offset)
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        for p in self.platforms:
            self.screen.blit(p.image, p.rect)
        for spr in self.enemies:
            spr.draw(self.screen)
        for spr in self.crates:
            self.screen.blit(spr.image, spr.rect)
        for spr in self.bullets:
            self.screen.blit(spr.image, spr.rect)
        for spr in self.enemy_bullets:
            self.screen.blit(spr.image, spr.rect)
        for spr in self.particles:
            self.screen.blit(spr.image, spr.rect)
        self.player.draw(self.screen)

    def draw(self):
        if self.state == S.STATE_TITLE:
            self.draw_title()
            return
        if self.state == S.STATE_MENU:
            self.draw_main_menu()
            return
        if self.state == S.STATE_MULTIPLAYER_SOON:
            self.draw_multiplayer_soon()
            return
        if self.state == S.STATE_MULTIPLAYER_MENU:
            self.draw_multiplayer_menu()
            if self.input_mode == 'name':
                self.draw_name_input()
            pg.display.flip()
            return
        if self.state == S.STATE_MULTIPLAYER_HOST:
            self.draw_multiplayer_host()
            return
        if self.state == S.STATE_MULTIPLAYER_JOIN:
            self.draw_multiplayer_join()
            return
        if self.state == S.STATE_MULTIPLAYER_LOBBY:
            self.draw_multiplayer_lobby()
            return
        if self.state == S.STATE_MULTIPLAYER_RUNNING:
            self.draw_multiplayer_game()
            return
        if self.state == S.STATE_DIFFICULTY:
            self.draw_difficulty_select()
            return
        # Fill with dark base
        self.screen.fill((12, 14, 20))
        # Calculate shake offset
        ox = int(random.uniform(-self.shake, self.shake))
        oy = int(random.uniform(-self.shake, self.shake))
        # Draw background with parallax and shake
        if self.bg_surface:
            x1 = -int(self.bg_offset) + ox
            x2 = x1 + self.bg_width
            y = (S.HEIGHT - self.bg_surface.get_height()) // 2 + oy
            self.screen.blit(self.bg_surface, (x1, y))
            if x1 + self.bg_width < S.WIDTH:
                self.screen.blit(self.bg_surface, (x2, y))
        # Draw game elements with shake offset
        for p in self.platforms:
            self.screen.blit(p.image, p.rect.move(ox, oy))
        for spr in self.enemies:
            spr.draw(self.screen, offset=(ox, oy))
        for spr in self.crates:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        for spr in self.bullets:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        for spr in self.enemy_bullets:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        for spr in self.particles:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        # Draw player with shake (using player.draw to include weapon)
        self.player.draw(self.screen, offset=(ox, oy))
        # Draw HUD (no shake)
        self.draw_hud()
        if self.state == S.STATE_PAUSED:
            self.draw_pause()
        elif self.state == S.STATE_GAMEOVER:
            self.draw_gameover()
        pg.display.flip()

    def load_highscore(self):
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                return int(json.load(f).get('highscore', 0))
        except Exception:
            return 0

    def save_highscore(self):
        try:
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump({'highscore': int(self.highscore)}, f)
        except Exception:
            pass

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(S.FPS) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.multiplayer.disconnect()
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    # Handle click for text input activation
                    if self.state == S.STATE_MULTIPLAYER_JOIN:
                        if self.connection_mode == S.CONN_LAN:
                            # LAN mode - only IP input box
                            ip_box = pg.Rect(S.WIDTH//2 - 150, 230, 300, 40)
                            if ip_box.collidepoint(event.pos):
                                self.input_active = True
                                self.input_field = 'ip'
                            else:
                                self.input_active = False
                        else:
                            # Public mode - IP and port input boxes
                            addr_box = pg.Rect(S.WIDTH//2 - 230, 230, 280, 40)
                            port_box = pg.Rect(S.WIDTH//2 + 100, 230, 100, 40)
                            if addr_box.collidepoint(event.pos):
                                self.input_active = True
                                self.input_field = 'ip'
                            elif port_box.collidepoint(event.pos):
                                self.input_active = True
                                self.input_field = 'port'
                            else:
                                self.input_active = False
                elif event.type == pg.KEYDOWN:
                    # Handle text input for name or IP
                    if self.input_mode == 'name':
                        if event.key == pg.K_RETURN:
                            if self.input_text.strip():
                                self.player_name = self.input_text.strip()[:S.MAX_PLAYER_NAME_LENGTH]
                                self.multiplayer.player_name = self.player_name
                                # Update name on server if connected
                                if self.multiplayer.client and self.multiplayer.connected:
                                    self.multiplayer.client.send_lobby_name(self.player_name)
                            self.input_mode = ""
                            self.input_text = ""
                        elif event.key == pg.K_ESCAPE:
                            self.input_mode = ""
                            self.input_text = ""
                        elif event.key == pg.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif len(self.input_text) < S.MAX_PLAYER_NAME_LENGTH:
                            if event.unicode.isprintable() and event.unicode:
                                self.input_text += event.unicode
                        continue
                    
                    if self.state == S.STATE_MULTIPLAYER_JOIN:
                        # TAB switches connection mode (when not typing) or switches field (in public mode)
                        if event.key == pg.K_TAB:
                            if self.input_active and self.connection_mode == S.CONN_PUBLIC:
                                # Switch between ip and port fields
                                self.input_field = 'port' if self.input_field == 'ip' else 'ip'
                            else:
                                # Switch connection mode
                                self.connection_mode = S.CONN_PUBLIC if self.connection_mode == S.CONN_LAN else S.CONN_LAN
                            continue
                        
                        if self.input_active:
                            if event.key == pg.K_RETURN:
                                self._try_join_game()
                            elif event.key == pg.K_BACKSPACE:
                                if self.input_field == 'ip':
                                    self.join_ip = self.join_ip[:-1]
                                else:
                                    self.join_port = self.join_port[:-1]
                            elif event.key == pg.K_ESCAPE:
                                self.input_active = False
                                self.state = S.STATE_MULTIPLAYER_MENU
                            elif event.key == pg.K_v and (event.mod & pg.KMOD_CTRL):
                                # Ctrl+V - Paste from clipboard
                                try:
                                    import pyperclip
                                    clipboard = pyperclip.paste()
                                except:
                                    # Fallback for Windows
                                    try:
                                        import subprocess
                                        clipboard = subprocess.check_output(['powershell', '-command', 'Get-Clipboard'], text=True).strip()
                                    except:
                                        clipboard = ""
                                
                                if clipboard:
                                    # Check if pasted text contains address:port format
                                    if ':' in clipboard and self.input_field == 'ip':
                                        parts = clipboard.rsplit(':', 1)  # Split from right to handle IPv6
                                        self.join_ip = parts[0].strip()[:50]
                                        if parts[1].strip().isdigit():
                                            self.join_port = parts[1].strip()[:5]
                                    elif self.input_field == 'ip':
                                        self.join_ip = clipboard.strip()[:50]
                                    elif self.input_field == 'port':
                                        # Only paste digits for port
                                        port_text = ''.join(c for c in clipboard if c.isdigit())[:5]
                                        if port_text:
                                            self.join_port = port_text
                            else:
                                # Add character to appropriate field
                                if self.input_field == 'ip':
                                    if len(self.join_ip) < 50:  # Allow longer for hostnames like ngrok
                                        if event.unicode.isprintable() and event.unicode:
                                            self.join_ip += event.unicode
                                else:  # port
                                    if len(self.join_port) < 5:  # Max port is 65535
                                        if event.unicode.isdigit():
                                            self.join_port += event.unicode
                            continue
                        elif event.key == pg.K_ESCAPE:
                            self.state = S.STATE_MULTIPLAYER_MENU
                            continue
                    
                    if self.state == S.STATE_TITLE:
                        if event.key in (pg.K_RETURN, pg.K_SPACE):
                            # Go to main menu instead of starting game directly
                            self.state = S.STATE_MENU
                        elif event.key == pg.K_d:
                            # Open difficulty selection
                            self.selected_difficulty = self.game_difficulty
                            self.state = S.STATE_DIFFICULTY
                    elif self.state == S.STATE_MENU:
                        if event.key in (pg.K_UP, pg.K_w):
                            self.menu_selection = S.MENU_OFFLINE
                        elif event.key in (pg.K_DOWN, pg.K_s):
                            self.menu_selection = S.MENU_ONLINE
                        elif event.key == pg.K_RETURN:
                            if self.menu_selection == S.MENU_OFFLINE:
                                self.reset_run(full=True)
                                self.state = S.STATE_RUNNING
                            else:
                                # Go to multiplayer menu
                                self.state = S.STATE_MULTIPLAYER_MENU
                        elif event.key == pg.K_d:
                            # Open difficulty selection from menu
                            self.selected_difficulty = self.game_difficulty
                            self.state = S.STATE_DIFFICULTY
                        elif event.key == pg.K_ESCAPE:
                            self.state = S.STATE_TITLE
                    elif self.state == S.STATE_MULTIPLAYER_MENU:
                        if event.key in (pg.K_UP, pg.K_w):
                            self.mp_menu_selection = S.MP_HOST
                        elif event.key in (pg.K_DOWN, pg.K_s):
                            self.mp_menu_selection = S.MP_JOIN
                        elif event.key == pg.K_n:
                            # Open name input
                            self.input_mode = 'name'
                            self.input_text = self.player_name
                        elif event.key == pg.K_RETURN:
                            if self.mp_menu_selection == S.MP_HOST:
                                self._try_host_game()
                            else:
                                self.state = S.STATE_MULTIPLAYER_JOIN
                                self.input_active = True
                        elif event.key == pg.K_ESCAPE:
                            self.state = S.STATE_MENU
                    elif self.state == S.STATE_MULTIPLAYER_HOST:
                        from .level import Level, MAP_LIST
                        if event.key == pg.K_SPACE:
                            # Start the game with selected map and notify all clients
                            map_id = MAP_LIST[self.selected_map]
                            self.multiplayer.start_game(map_id)
                            self.reset_run(full=True, map_id=map_id)
                            self.state = S.STATE_MULTIPLAYER_RUNNING
                        elif event.key in (pg.K_LEFT, pg.K_a):
                            # Previous map
                            self.selected_map = (self.selected_map - 1) % len(MAP_LIST)
                        elif event.key in (pg.K_RIGHT, pg.K_d):
                            # Next map
                            self.selected_map = (self.selected_map + 1) % len(MAP_LIST)
                        elif event.key == pg.K_n:
                            # Change name
                            self.input_mode = 'name'
                            self.input_text = self.player_name
                        elif event.key == pg.K_ESCAPE:
                            self.multiplayer.disconnect()
                            self.state = S.STATE_MULTIPLAYER_MENU
                    elif self.state == S.STATE_MULTIPLAYER_LOBBY:
                        if event.key == pg.K_n:
                            # Change name
                            self.input_mode = 'name'
                            self.input_text = self.player_name
                        elif event.key == pg.K_ESCAPE:
                            self.multiplayer.disconnect()
                            self.state = S.STATE_MULTIPLAYER_MENU
                    elif self.state == S.STATE_MULTIPLAYER_RUNNING:
                        if event.key in (pg.K_p, pg.K_ESCAPE):
                            self.state = S.STATE_PAUSED
                    elif self.state == S.STATE_MULTIPLAYER_SOON:
                        if event.key in (pg.K_RETURN, pg.K_ESCAPE):
                            self.state = S.STATE_MENU
                    elif self.state == S.STATE_DIFFICULTY:
                        if event.key in (pg.K_UP, pg.K_w):
                            self.selected_difficulty = max(0, self.selected_difficulty - 1)
                        elif event.key in (pg.K_DOWN, pg.K_s):
                            self.selected_difficulty = min(3, self.selected_difficulty + 1)
                        elif event.key == pg.K_RETURN:
                            self.game_difficulty = self.selected_difficulty
                            self.state = S.STATE_MENU  # Go back to menu after selecting difficulty
                        elif event.key == pg.K_ESCAPE:
                            self.state = S.STATE_MENU  # Go back to menu
                    elif self.state == S.STATE_RUNNING:
                        if event.key in (pg.K_p, pg.K_ESCAPE):
                            self.state = S.STATE_PAUSED
                    elif self.state == S.STATE_PAUSED:
                        if event.key in (pg.K_p, pg.K_ESCAPE):
                            if self.multiplayer.connected:
                                self.state = S.STATE_MULTIPLAYER_RUNNING
                            else:
                                self.state = S.STATE_RUNNING
                    elif self.state == S.STATE_GAMEOVER:
                        if event.key == pg.K_r:
                            self.reset_run(full=True)
                            self.state = S.STATE_RUNNING
                        elif event.key in (pg.K_RETURN, pg.K_ESCAPE):
                            self.reset_run(full=True)
                            self.state = S.STATE_TITLE
            self.update(dt)
            self.draw()
        pg.quit()
    
    def _try_host_game(self):
        """Try to host a game"""
        success, ip, error = self.multiplayer.host_game(self.player_name)
        if success:
            self.state = S.STATE_MULTIPLAYER_HOST
        else:
            self.mp_error_message = error or "Failed to host game"
            self.mp_error_timer = 3.0
    
    def _try_join_game(self):
        """Try to join a game"""
        if not self.join_ip.strip():
            self.mp_error_message = "Please enter an IP address"
            self.mp_error_timer = 3.0
            return
        
        ip = self.join_ip.strip()
        
        if self.connection_mode == S.CONN_LAN:
            # LAN mode - use default port unless specified with ':'
            port = S.DEFAULT_PORT
            if ':' in ip:
                parts = ip.split(':')
                ip = parts[0]
                try:
                    port = int(parts[1])
                except ValueError:
                    self.mp_error_message = "Invalid port number"
                    self.mp_error_timer = 3.0
                    return
        else:
            # Public mode - use the separate port field
            if not self.join_port.strip():
                self.mp_error_message = "Please enter a port number"
                self.mp_error_timer = 3.0
                return
            try:
                port = int(self.join_port.strip())
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                self.mp_error_message = "Invalid port (1-65535)"
                self.mp_error_timer = 3.0
                return
        
        success, error = self.multiplayer.join_game(ip, self.player_name, port)
        if success:
            self.input_active = False
            self.state = S.STATE_MULTIPLAYER_LOBBY
        else:
            self.mp_error_message = error or "Failed to connect"
            self.mp_error_timer = 3.0

if __name__ == "__main__":
    Game().run()
