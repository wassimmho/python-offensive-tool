import math
from pathlib import Path
import pygame as pg
from . import settings as S

# AK-47 animation frames (loaded lazily)
AK_FRAMES = []
AK_FRAMES_LOADED = False

def load_ak_frames():
    """Load AK-47 animation frames - called after pygame is initialized"""
    global AK_FRAMES, AK_FRAMES_LOADED
    if AK_FRAMES_LOADED:
        return
    try:
        ak_folder = Path(__file__).parent / 'AK_Animation'
        ak_files = sorted(ak_folder.glob('*.png'))
        for ak_file in ak_files:
            img = pg.image.load(str(ak_file)).convert_alpha()
            # Scale down to appropriate size for the game
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * 0.3), int(img.get_height() * 0.3)))
            AK_FRAMES.append(scaled)
        if AK_FRAMES:
            print(f"Loaded {len(AK_FRAMES)} AK-47 animation frames")
        AK_FRAMES_LOADED = True
    except Exception as e:
        print(f"Could not load AK-47 sprites: {e}")
        AK_FRAMES_LOADED = True

class PhysicsSprite(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pg.Vector2(0, 0)
        self.vel = pg.Vector2(0, 0)
        self.size = pg.Vector2(28, 36)
        self.rect = pg.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)

    def physics_step(self, dt, platforms):
        self.vel.y += S.GRAVITY * dt
        self.pos.x += self.vel.x * dt
        self.rect.topleft = self.pos
        for p in platforms:
            if self.rect.colliderect(p.rect) and self.vel.x != 0:
                if self.vel.x > 0:
                    self.rect.right = p.rect.left
                else:
                    self.rect.left = p.rect.right
                self.pos.x = self.rect.x
                self.vel.x = 0
        self.pos.y += self.vel.y * dt
        self.rect.topleft = self.pos
        on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect) and self.vel.y != 0:
                if self.vel.y > 0:
                    self.rect.bottom = p.rect.top
                    on_ground = True
                else:
                    self.rect.top = p.rect.bottom
                self.pos.y = self.rect.y
                self.vel.y = 0
        return on_ground

class Player(PhysicsSprite):
    def __init__(self, x, y):
        super().__init__()
        load_ak_frames()  # Load weapon sprites if not already loaded
        self.pos.update(x, y)
        self.color = (120, 200, 255)
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.draw_character()
        self.rect.topleft = self.pos
        self.on_ground = False
        self.facing = 1
        self.shoot_cooldown = 0
        self.alive = True
        self.invuln = 0
        self.weapon = None
        self.weapon_anim_frame = 0
        self.weapon_anim_timer = 0.0
        self.weapon_frame_duration = 0.05  # How long each frame shows
        self.weapon_frame_duration = 0.05  # How long each frame shows
    
    def draw_character(self):
        """Draw a proper character sprite"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        w, h = int(self.size.x), int(self.size.y)
        
        # Body (torso)
        body_rect = pg.Rect(w//4, h//3, w//2, h//2)
        pg.draw.rect(self.image, (100, 180, 255), body_rect, border_radius=4)
        pg.draw.rect(self.image, (80, 160, 235), body_rect, width=2, border_radius=4)
        
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
        pg.draw.rect(self.image, (60, 100, 180), (w//3 - 2, leg_top, leg_width, h - leg_top), border_radius=2)
        pg.draw.rect(self.image, (60, 100, 180), (w - w//3 - 3, leg_top, leg_width, h - leg_top), border_radius=2)
        
        # Arms
        arm_y = h // 3 + 5
        arm_height = h // 3
        pg.draw.rect(self.image, (255, 220, 180), (2, arm_y, 4, arm_height), border_radius=2)
        pg.draw.rect(self.image, (255, 220, 180), (w - 6, arm_y, 4, arm_height), border_radius=2)

    def give_weapon(self, weapon):
        self.weapon = weapon
    
    def respawn(self):
        """Respawn player at a safe location"""
        self.pos.x = S.WIDTH // 2 - 100
        self.pos.y = 60
        self.vel.x = 0
        self.vel.y = 0
        self.rect.topleft = self.pos
        self.invuln = 2.0  # 2 seconds of invulnerability after respawn

    def update(self, dt, platforms, bullets):
        keys = pg.key.get_pressed()
        dx = 0
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            dx -= 1
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            dx += 1
        self.vel.x = dx * S.PLAYER_SPEED
        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        if (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) and self.on_ground:
            self.vel.y = S.JUMP_VELOCITY
        self.on_ground = self.physics_step(dt, platforms)
        
        # Respawn if on bottom platform or falling too far
        if self.pos.y > 450:  # Respawn if at or below bottom platform
            print(f"[RESPAWN] Player at Y={self.pos.y} - respawning to top!")
            self.respawn()
        
        # Update invulnerability timer
        if self.invuln > 0:
            self.invuln -= dt
        
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        
        # Update weapon animation
        if self.shoot_cooldown > 0 and AK_FRAMES:
            self.weapon_anim_timer += dt
            if self.weapon_anim_timer >= self.weapon_frame_duration:
                self.weapon_anim_timer = 0
                self.weapon_anim_frame = (self.weapon_anim_frame + 1) % len(AK_FRAMES)
        else:
            self.weapon_anim_frame = 0
            self.weapon_anim_timer = 0
        
        if self.weapon and (keys[pg.K_j] or keys[pg.K_f] or pg.mouse.get_pressed()[0]):
            if self.shoot_cooldown <= 0:
                ox = 14 * self.facing
                oy = -6
                origin = pg.Vector2(self.rect.centerx + ox, self.rect.centery + oy)
                aim = pg.Vector2(pg.mouse.get_pos())
                direction = (aim - origin)
                if direction.length_squared() == 0:
                    direction = pg.Vector2(self.facing, 0)
                else:
                    direction = direction.normalize()
                self.shoot_cooldown = self.weapon.cooldown
                self.weapon.shoot(origin, direction, bullets)
        self.rect.topleft = self.pos

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        
        # Draw weapon if equipped and has sprite
        if self.weapon and hasattr(self.weapon, 'has_sprite') and self.weapon.has_sprite and AK_FRAMES:
            weapon_img = AK_FRAMES[self.weapon_anim_frame]
            
            # Flip weapon based on facing direction
            if self.facing < 0:
                weapon_img = pg.transform.flip(weapon_img, True, False)
            
            # Position weapon in front of player (in hand position)
            weapon_offset_x = 8 * self.facing
            weapon_offset_y = 2
            
            # Calculate weapon position
            if self.facing > 0:
                weapon_pos = (self.rect.right + weapon_offset_x - weapon_img.get_width(), 
                             self.rect.centery + weapon_offset_y - weapon_img.get_height() // 2)
            else:
                weapon_pos = (self.rect.left + weapon_offset_x, 
                             self.rect.centery + weapon_offset_y - weapon_img.get_height() // 2)
            
            surf.blit(weapon_img, weapon_pos)
