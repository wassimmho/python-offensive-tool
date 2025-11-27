import math
import random
from pathlib import Path
import pygame as pg
from . import settings as S

# AK-47 animation frames (loaded lazily)
AK_FRAMES = []
AK_FRAMES_FLIPPED = []  # Pre-flipped frames for left-facing
AK_FRAMES_LOADED = False

def load_ak_frames():
    """Load AK-47 animation frames - called after pygame is initialized"""
    global AK_FRAMES, AK_FRAMES_FLIPPED, AK_FRAMES_LOADED
    if AK_FRAMES_LOADED:
        return
    try:
        ak_folder = Path(__file__).parent / 'AK_Animation'
        ak_files = sorted(ak_folder.glob('*.png'))
        for ak_file in ak_files:
            img = pg.image.load(str(ak_file)).convert_alpha()
            # Scale to a good size for the game (adjust as needed based on your images)
            scale_factor = 0.15  # Smaller scale for better fit
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            AK_FRAMES.append(scaled)
            # Pre-flip for left-facing direction
            AK_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
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
        self.weapon_frame_duration = 0.06  # How long each frame shows during firing
        self.is_firing = False  # Track if currently in firing animation
        self.firing_anim_duration = 0.18  # Total time to play full firing animation
        self.firing_timer = 0.0
        self.muzzle_flash_timer = 0.0  # For muzzle flash effect
    
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
        
        # Update weapon firing animation
        if self.is_firing and AK_FRAMES:
            self.firing_timer += dt
            self.weapon_anim_timer += dt
            
            # Cycle through frames during firing
            if self.weapon_anim_timer >= self.weapon_frame_duration:
                self.weapon_anim_timer = 0
                self.weapon_anim_frame = (self.weapon_anim_frame + 1) % len(AK_FRAMES)
            
            # End firing animation after duration
            if self.firing_timer >= self.firing_anim_duration:
                self.is_firing = False
                self.weapon_anim_frame = 0
                self.firing_timer = 0.0
        
        # Update muzzle flash
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= dt
        
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
                
                # Trigger firing animation for AK-47
                if hasattr(self.weapon, 'has_sprite') and self.weapon.has_sprite:
                    self.is_firing = True
                    self.firing_timer = 0.0
                    self.weapon_anim_timer = 0.0
                    self.weapon_anim_frame = 1  # Start from first firing frame
                    self.muzzle_flash_timer = 0.08  # Show muzzle flash briefly
        self.rect.topleft = self.pos

    def draw(self, surf, offset=(0, 0)):
        ox, oy = offset
        # Draw player character with offset
        surf.blit(self.image, self.rect.move(ox, oy))
        
        # Draw AK-47 weapon if equipped
        if self.weapon and hasattr(self.weapon, 'has_sprite') and self.weapon.has_sprite and AK_FRAMES:
            # Use pre-flipped frames for better performance
            if self.facing > 0:
                weapon_img = AK_FRAMES[self.weapon_anim_frame]
            else:
                weapon_img = AK_FRAMES_FLIPPED[self.weapon_anim_frame]
            
            # Position weapon at player's hands
            weapon_w = weapon_img.get_width()
            weapon_h = weapon_img.get_height()
            
            # Offset to place weapon in hand position
            if self.facing > 0:
                # Facing right - weapon extends to the right
                weapon_x = self.rect.centerx + 2 + ox
                weapon_y = self.rect.centery - weapon_h // 2 + 4 + oy
            else:
                # Facing left - weapon extends to the left
                weapon_x = self.rect.centerx - weapon_w - 2 + ox
                weapon_y = self.rect.centery - weapon_h // 2 + 4 + oy
            
            surf.blit(weapon_img, (weapon_x, weapon_y))
            
            # Draw muzzle flash when firing
            if self.muzzle_flash_timer > 0:
                flash_size = random.randint(8, 14)
                if self.facing > 0:
                    flash_x = weapon_x + weapon_w + 2
                else:
                    flash_x = weapon_x - 4
                flash_y = weapon_y + weapon_h // 2 - 2
                
                # Draw layered muzzle flash
                pg.draw.circle(surf, (255, 255, 200), (flash_x, flash_y), flash_size)
                pg.draw.circle(surf, (255, 200, 50), (flash_x, flash_y), flash_size - 3)
                pg.draw.circle(surf, (255, 255, 255), (flash_x, flash_y), flash_size - 6)
