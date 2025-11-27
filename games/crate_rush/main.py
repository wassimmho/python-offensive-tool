import math
import random
import json
from pathlib import Path
import pygame as pg
from . import settings as S
from .level import Level
from .player import Player
from .enemies import Enemy, Spawner
from .weapons import WEAPON_POOL
from .crate import Crate
from . import ui
from .particles import Burst

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption("Crate Rush")
        self.screen = pg.display.set_mode((S.WIDTH, S.HEIGHT))
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("consolas", 20, bold=True)
        self.big_font = pg.font.SysFont("consolas", 60, bold=True)
        self.mid_font = pg.font.SysFont("consolas", 32, bold=True)
        self.level = Level()
        self.save_path = Path(__file__).with_name('save.json')
        self.highscore = self.load_highscore()
        self.state = S.STATE_TITLE
        self.shake = 0.0
        self.time = 0.0
        self.bg_offset = 0.0
        self.bg_change_timer = 0.0
        self.bg_change_interval = 10.0  # Change background every 10 seconds
        self.xp_level = 0
        self.reset_run(full=True)
        self.load_backgrounds()

    def reset_run(self, full=False):
        self.all = pg.sprite.Group()
        self.platforms = self.level.platforms
        self.enemies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
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
        e = sp.spawn(self.difficulty)
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

    def on_game_over(self):
        self.highscore = max(self.highscore, self.crates_collected)
        self.save_highscore()
        self.state = S.STATE_GAMEOVER
        self.shake = max(self.shake, 10)

    def update(self, dt):
        self.time += dt
        
        # Cycle backgrounds during gameplay
        if self.state == S.STATE_RUNNING and self.bg_surfaces:
            self.bg_change_timer += dt
            if self.bg_change_timer >= self.bg_change_interval:
                self.cycle_background()
                self.bg_change_timer = 0.0
        
        if self.state != S.STATE_RUNNING:
            # Update minimal animations only
            for p in list(self.particles):
                p.update(dt)
            self.shake = max(0.0, self.shake - S.SHAKE_DECAY * dt)
            return

        self.player.update(dt, self.platforms, self.bullets)
        for e in list(self.enemies):
            e.update(dt, self.platforms)
        for b in list(self.bullets):
            b.update(dt, self.platforms)
        for p in list(self.particles):
            p.update(dt)
        self.bullet_enemy_collisions()
        self.enemy_player_collisions()
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
        panel = pg.Rect(S.WIDTH//2 - 240, 230, 480, 160)
        ui.draw_panel(self.screen, panel, glow=True)
        start_pulse = int(120 + 135 * abs(math.sin(self.time * 3)))
        start_col = (start_pulse, 255, start_pulse)
        ui.text(self.screen, self.mid_font, "Press Enter to Start", start_col, (S.WIDTH//2, 280), center=True, glow=True)
        ui.text(self.screen, self.font, "Controls: A/D, Space, J/F/Mouse, P to Pause", S.TIP_COLOR, (S.WIDTH//2, 330), center=True)
        pg.display.flip()

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
            self.screen.blit(spr.image, spr.rect)
        for spr in self.crates:
            self.screen.blit(spr.image, spr.rect)
        for spr in self.bullets:
            self.screen.blit(spr.image, spr.rect)
        for spr in self.particles:
            self.screen.blit(spr.image, spr.rect)
        self.player.draw(self.screen)

    def draw(self):
        if self.state == S.STATE_TITLE:
            self.draw_title()
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
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        for spr in self.crates:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        for spr in self.bullets:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        for spr in self.particles:
            self.screen.blit(spr.image, spr.rect.move(ox, oy))
        # Draw player with shake
        pr = self.player.rect.move(ox, oy)
        self.screen.blit(self.player.image, pr)
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
                    running = False
                elif event.type == pg.KEYDOWN:
                    if self.state == S.STATE_TITLE:
                        if event.key in (pg.K_RETURN, pg.K_SPACE):
                            self.reset_run(full=True)
                            self.state = S.STATE_RUNNING
                    elif self.state == S.STATE_RUNNING:
                        if event.key in (pg.K_p, pg.K_ESCAPE):
                            self.state = S.STATE_PAUSED
                    elif self.state == S.STATE_PAUSED:
                        if event.key in (pg.K_p, pg.K_ESCAPE):
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

if __name__ == "__main__":
    Game().run()
