import math
import random
from pathlib import Path
import pygame as pg
from . import settings as S

# AK-47 animation frames (loaded lazily)
AK_FRAMES = []
AK_FRAMES_FLIPPED = []  # Pre-flipped frames for left-facing
AK_FRAMES_LOADED = False

# SMG animation frames (loaded lazily)
SMG_FRAMES = []
SMG_FRAMES_FLIPPED = []
SMG_FRAMES_LOADED = False

# Rocket launcher animation frames (loaded lazily)
ROCKET_FRAMES = []
ROCKET_FRAMES_FLIPPED = []
ROCKET_FRAMES_LOADED = False

# Shotgun animation frames (loaded lazily)
SHOTGUN_FRAMES = []
SHOTGUN_FRAMES_FLIPPED = []
SHOTGUN_FRAMES_LOADED = False

# Pistol animation frames (loaded lazily)
PISTOL_FRAMES = []
PISTOL_FRAMES_FLIPPED = []
PISTOL_FRAMES_LOADED = False

# Character animation frames
CHAR_IDLE_FRAMES = []
CHAR_IDLE_FRAMES_FLIPPED = []
CHAR_WALK_FRAMES = []
CHAR_WALK_FRAMES_FLIPPED = []
CHAR_JUMP_START_FRAMES = []
CHAR_JUMP_START_FRAMES_FLIPPED = []
CHAR_JUMP_END_FRAMES = []
CHAR_JUMP_END_FRAMES_FLIPPED = []
CHAR_FRAMES_LOADED = False

def load_ak_frames():
    """Load AK-47 animation frames - called after pygame is initialized"""
    global AK_FRAMES, AK_FRAMES_FLIPPED, AK_FRAMES_LOADED
    if AK_FRAMES_LOADED:
        return
    try:
        ak_folder = Path(__file__).parent / 'Weapons' / 'AK_Animation'
        ak_files = sorted(ak_folder.glob('*.png'))
        for ak_file in ak_files:
            img = pg.image.load(str(ak_file)).convert_alpha()
            # Scale to a good size for the game - bigger weapon
            scale_factor = 0.24  # Bigger scale for visibility
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

def load_smg_frames():
    """Load SMG animation frames - called after pygame is initialized"""
    global SMG_FRAMES, SMG_FRAMES_FLIPPED, SMG_FRAMES_LOADED
    if SMG_FRAMES_LOADED:
        return
    try:
        smg_folder = Path(__file__).parent / 'Weapons' / 'SMG'
        smg_files = sorted(smg_folder.glob('*.png'))
        for smg_file in smg_files:
            img = pg.image.load(str(smg_file)).convert_alpha()
            # Scale to a good size for the game - bigger weapon
            scale_factor = 1.5  # Much bigger for visibility
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            SMG_FRAMES.append(scaled)
            # Pre-flip for left-facing direction
            SMG_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        if SMG_FRAMES:
            print(f"Loaded {len(SMG_FRAMES)} SMG animation frames")
        SMG_FRAMES_LOADED = True
    except Exception as e:
        print(f"Could not load SMG sprites: {e}")
        SMG_FRAMES_LOADED = True

def load_rocket_frames():
    """Load Rocket launcher animation frames - called after pygame is initialized"""
    global ROCKET_FRAMES, ROCKET_FRAMES_FLIPPED, ROCKET_FRAMES_LOADED
    if ROCKET_FRAMES_LOADED:
        return
    try:
        rocket_folder = Path(__file__).parent / 'Weapons' / 'Rocket'
        rocket_files = sorted(rocket_folder.glob('*.png'))
        for rocket_file in rocket_files:
            img = pg.image.load(str(rocket_file)).convert_alpha()
            # Scale to a good size for the game - bigger weapon
            scale_factor = 2.0  # Good size for rocket launcher
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ROCKET_FRAMES.append(scaled)
            # Pre-flip for left-facing direction
            ROCKET_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        if ROCKET_FRAMES:
            print(f"Loaded {len(ROCKET_FRAMES)} Rocket animation frames")
        ROCKET_FRAMES_LOADED = True
    except Exception as e:
        print(f"Could not load Rocket sprites: {e}")
        ROCKET_FRAMES_LOADED = True

def load_shotgun_frames():
    """Load Shotgun animation frames - called after pygame is initialized"""
    global SHOTGUN_FRAMES, SHOTGUN_FRAMES_FLIPPED, SHOTGUN_FRAMES_LOADED
    if SHOTGUN_FRAMES_LOADED:
        return
    try:
        shotgun_folder = Path(__file__).parent / 'Weapons' / 'Shotgun'
        shotgun_files = sorted(shotgun_folder.glob('*.png'))
        for shotgun_file in shotgun_files:
            img = pg.image.load(str(shotgun_file)).convert_alpha()
            # Scale to a good size for the game
            scale_factor = 2.0  # Good size for shotgun
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            SHOTGUN_FRAMES.append(scaled)
            # Pre-flip for left-facing direction
            SHOTGUN_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        if SHOTGUN_FRAMES:
            print(f"Loaded {len(SHOTGUN_FRAMES)} Shotgun animation frames")
        SHOTGUN_FRAMES_LOADED = True
    except Exception as e:
        print(f"Could not load Shotgun sprites: {e}")
        SHOTGUN_FRAMES_LOADED = True

def load_pistol_frames():
    """Load Pistol animation frames - called after pygame is initialized"""
    global PISTOL_FRAMES, PISTOL_FRAMES_FLIPPED, PISTOL_FRAMES_LOADED
    if PISTOL_FRAMES_LOADED:
        return
    try:
        pistol_folder = Path(__file__).parent / 'Weapons' / 'Pistol'
        pistol_files = sorted(pistol_folder.glob('*.png'))
        for pistol_file in pistol_files:
            img = pg.image.load(str(pistol_file)).convert_alpha()
            # Scale to a good size for the game
            scale_factor = 2.0  # Good size for pistol
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            PISTOL_FRAMES.append(scaled)
            # Pre-flip for left-facing direction
            PISTOL_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        if PISTOL_FRAMES:
            print(f"Loaded {len(PISTOL_FRAMES)} Pistol animation frames")
        PISTOL_FRAMES_LOADED = True
    except Exception as e:
        print(f"Could not load Pistol sprites: {e}")
        PISTOL_FRAMES_LOADED = True

def load_character_frames():
    """Load character animation frames - called after pygame is initialized"""
    global CHAR_IDLE_FRAMES, CHAR_IDLE_FRAMES_FLIPPED
    global CHAR_WALK_FRAMES, CHAR_WALK_FRAMES_FLIPPED
    global CHAR_JUMP_START_FRAMES, CHAR_JUMP_START_FRAMES_FLIPPED
    global CHAR_JUMP_END_FRAMES, CHAR_JUMP_END_FRAMES_FLIPPED
    global CHAR_FRAMES_LOADED
    
    if CHAR_FRAMES_LOADED:
        return
    
    try:
        char_folder = Path(__file__).parent / 'Char1'
        target_height = 124  # Target height in pixels to match collision box
        
        # Load Idle frames
        idle_folder = char_folder / 'Idle'
        idle_files = sorted(idle_folder.glob('idle_*.png'))
        for f in idle_files:
            img = pg.image.load(str(f)).convert_alpha()
            # Scale to target height, maintaining aspect ratio
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            CHAR_IDLE_FRAMES.append(scaled)
            CHAR_IDLE_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(CHAR_IDLE_FRAMES)} idle frames")
        
        # Load Walk frames
        walk_folder = char_folder / 'walk'
        walk_files = sorted(walk_folder.glob('walk_*.png'))
        for f in walk_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            CHAR_WALK_FRAMES.append(scaled)
            CHAR_WALK_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(CHAR_WALK_FRAMES)} walk frames")
        
        # Load Jump Start frames
        jump_folder = char_folder / 'jump'
        jump_start_files = sorted(jump_folder.glob('jumpStart_*.png'))
        for f in jump_start_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            CHAR_JUMP_START_FRAMES.append(scaled)
            CHAR_JUMP_START_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(CHAR_JUMP_START_FRAMES)} jump start frames")
        
        # Load Jump End frames
        jump_end_files = sorted(jump_folder.glob('jumpEnd_*.png'))
        for f in jump_end_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            CHAR_JUMP_END_FRAMES.append(scaled)
            CHAR_JUMP_END_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(CHAR_JUMP_END_FRAMES)} jump end frames")
        
        CHAR_FRAMES_LOADED = True
        
    except Exception as e:
        print(f"Could not load character sprites: {e}")
        CHAR_FRAMES_LOADED = True

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
        load_smg_frames()  # Load SMG sprites
        load_rocket_frames()  # Load Rocket sprites
        load_shotgun_frames()  # Load Shotgun sprites
        load_pistol_frames()  # Load Pistol sprites
        load_character_frames()  # Load character sprites
        self.pos.update(x, y)
        self.color = (120, 200, 255)
        
        # Character animation state
        self.anim_state = 'idle'  # idle, walk, jump_start, jump_end
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.idle_frame_duration = 0.12  # Time per idle frame
        self.walk_frame_duration = 0.08  # Time per walk frame
        self.jump_frame_duration = 0.1   # Time per jump frame
        
        # Keep collision box small and consistent - match sprite size
        self.size = pg.Vector2(20, 40)  # Smaller collision box
        
        # Set initial image from character sprites or fallback
        if CHAR_IDLE_FRAMES:
            self.image = CHAR_IDLE_FRAMES[0]
            self.sprite_size = pg.Vector2(self.image.get_width(), self.image.get_height())
        else:
            self.sprite_size = self.size.copy()
            self.image = pg.Surface(self.size, pg.SRCALPHA)
            self.draw_character_fallback()
        
        # Collision rect uses fixed size
        self.rect = pg.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
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
        self.aim_angle = 0.0  # Angle to mouse in degrees
        self.was_on_ground = True  # Track previous ground state for jump detection
        self.input_mode = 'mouse'  # Track last used input: 'mouse' or 'controller'
        self.last_mouse_pos = pg.Vector2(0, 0)  # Track mouse position to detect movement
        
        # Health system
        self.max_health = 4  # Will be set by difficulty
        self.health = self.max_health
    
    def set_health_from_difficulty(self, difficulty):
        """Set max health based on difficulty settings"""
        settings = S.DIFFICULTY_SETTINGS.get(difficulty, S.DIFFICULTY_SETTINGS[S.DIFF_NORMAL])
        self.max_health = settings.get('player_health', 4)
        self.health = self.max_health
    
    def take_damage(self, amount=1):
        """Take damage and return True if player died"""
        if self.invuln > 0:
            return False
        self.health -= amount
        self.invuln = 1.0  # Brief invulnerability after being hit
        if self.health <= 0:
            self.health = 0
            self.alive = False
            return True
        return False
    
    def heal(self, amount=1):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
    
    def draw_character_fallback(self):
        """Draw a fallback character sprite if images not loaded"""
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
    
    def update_animation(self, dt):
        """Update character animation based on state"""
        if not CHAR_FRAMES_LOADED:
            return
        
        # Determine animation state
        prev_state = self.anim_state
        
        if not self.on_ground:
            if self.vel.y < 0:
                self.anim_state = 'jump_start'
            else:
                self.anim_state = 'jump_end'
        elif abs(self.vel.x) > 10:
            self.anim_state = 'walk'
        else:
            self.anim_state = 'idle'
        
        # Reset frame if state changed
        if prev_state != self.anim_state:
            self.anim_frame = 0
            self.anim_timer = 0.0
        
        # Update animation timer
        self.anim_timer += dt
        
        # Get current frames list and frame duration
        if self.anim_state == 'idle' and CHAR_IDLE_FRAMES:
            frames = CHAR_IDLE_FRAMES
            frames_flipped = CHAR_IDLE_FRAMES_FLIPPED
            frame_duration = self.idle_frame_duration
        elif self.anim_state == 'walk' and CHAR_WALK_FRAMES:
            frames = CHAR_WALK_FRAMES
            frames_flipped = CHAR_WALK_FRAMES_FLIPPED
            frame_duration = self.walk_frame_duration
        elif self.anim_state == 'jump_start' and CHAR_JUMP_START_FRAMES:
            frames = CHAR_JUMP_START_FRAMES
            frames_flipped = CHAR_JUMP_START_FRAMES_FLIPPED
            frame_duration = self.jump_frame_duration
        elif self.anim_state == 'jump_end' and CHAR_JUMP_END_FRAMES:
            frames = CHAR_JUMP_END_FRAMES
            frames_flipped = CHAR_JUMP_END_FRAMES_FLIPPED
            frame_duration = self.jump_frame_duration
        else:
            return
        
        # Advance frame
        if self.anim_timer >= frame_duration:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % len(frames)
        
        # Clamp frame index
        self.anim_frame = min(self.anim_frame, len(frames) - 1)
        
        # Set current image based on facing direction
        if self.facing > 0:
            self.image = frames[self.anim_frame]
        else:
            self.image = frames_flipped[self.anim_frame]

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

    def update(self, dt, platforms, bullets, joystick=None):
        keys = pg.key.get_pressed()
        dx = 0
        
        # Keyboard input
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            dx -= 1
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            dx += 1
        
        # Controller input
        controller_shoot = False
        
        if joystick:
            # Left stick horizontal (axis 0) for movement
            axis_x = joystick.get_axis(0)
            deadzone = 0.2
            if abs(axis_x) > deadzone:
                dx = axis_x  # Use analog value for smooth movement
            
            # D-pad (hat) for movement
            if joystick.get_numhats() > 0:
                hat = joystick.get_hat(0)
                if hat[0] != 0:
                    dx = hat[0]
            
            # Right stick for aiming (axis 2 = X, axis 3 = Y on most controllers)
            # This mimics mouse behavior - the stick direction IS the aim direction
            if joystick.get_numaxes() >= 4:
                aim_x = joystick.get_axis(2) if joystick.get_numaxes() > 2 else 0
                aim_y = joystick.get_axis(3) if joystick.get_numaxes() > 3 else 0
                stick_magnitude = math.sqrt(aim_x * aim_x + aim_y * aim_y)
                
                if stick_magnitude > deadzone:
                    self.input_mode = 'controller'  # Switch to controller mode
                    # Calculate angle from stick position (like mouse position relative to player)
                    self.aim_angle = math.degrees(math.atan2(-aim_y, aim_x))
                    # Update facing based on aim direction
                    if aim_x > 0.1:
                        self.facing = 1
                    elif aim_x < -0.1:
                        self.facing = -1
            
            # R2/RT trigger for shooting (axis 5 on PS4, axis 4 on some controllers)
            # Or R1/RB button (button 5 on PS4)
            if joystick.get_numaxes() >= 6:
                r2_trigger = joystick.get_axis(5)
                if r2_trigger > -0.5:  # Trigger pressed (goes from -1 to 1)
                    controller_shoot = True
            if joystick.get_numbuttons() > 5:
                if joystick.get_button(5):  # R1/RB
                    controller_shoot = True
            
            # X/A button for jump (button 0 on PS4, button 0 on Xbox)
            if joystick.get_numbuttons() > 0:
                if joystick.get_button(0) and self.on_ground:
                    self.vel.y = S.JUMP_VELOCITY
        
        self.vel.x = dx * S.PLAYER_SPEED
        if dx != 0:
            self.facing = 1 if dx > 0 else -1
        if (keys[pg.K_SPACE] or keys[pg.K_w] or keys[pg.K_UP]) and self.on_ground:
            self.vel.y = S.JUMP_VELOCITY
        
        self.was_on_ground = self.on_ground
        self.on_ground = self.physics_step(dt, platforms)
        
        # Respawn if falling below screen
        if self.pos.y > S.HEIGHT - 50:  # Respawn if at or below bottom platform
            print(f"[RESPAWN] Player at Y={self.pos.y} - respawning to top!")
            self.respawn()
        
        # Update invulnerability timer
        if self.invuln > 0:
            self.invuln -= dt
        
        # Update character animation
        self.update_animation(dt)
        
        self.shoot_cooldown = max(0, self.shoot_cooldown - dt)
        
        # Update weapon firing animation
        if self.is_firing and self.weapon and hasattr(self.weapon, 'has_sprite') and self.weapon.has_sprite:
            # Get the appropriate frames for the current weapon
            weapon_frames = None
            if hasattr(self.weapon, 'sprite_type'):
                if self.weapon.sprite_type == 'smg' and SMG_FRAMES:
                    weapon_frames = SMG_FRAMES
                elif self.weapon.sprite_type == 'ak47' and AK_FRAMES:
                    weapon_frames = AK_FRAMES
                elif self.weapon.sprite_type == 'rocket' and ROCKET_FRAMES:
                    weapon_frames = ROCKET_FRAMES
                elif self.weapon.sprite_type == 'shotgun' and SHOTGUN_FRAMES:
                    weapon_frames = SHOTGUN_FRAMES
                elif self.weapon.sprite_type == 'pistol' and PISTOL_FRAMES:
                    weapon_frames = PISTOL_FRAMES
            elif AK_FRAMES:
                weapon_frames = AK_FRAMES
            
            if weapon_frames:
                self.firing_timer += dt
                self.weapon_anim_timer += dt
                
                # Cycle through frames during firing
                if self.weapon_anim_timer >= self.weapon_frame_duration:
                    self.weapon_anim_timer = 0
                    self.weapon_anim_frame = (self.weapon_anim_frame + 1) % len(weapon_frames)
                
                # End firing animation after duration
                if self.firing_timer >= self.firing_anim_duration:
                    self.is_firing = False
                    self.weapon_anim_frame = 0
                    self.firing_timer = 0.0
        
        # Update muzzle flash
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= dt
        
        # Update aim angle based on mouse position (only if mouse moved)
        mouse_pos = pg.Vector2(pg.mouse.get_pos())
        mouse_moved = (mouse_pos - self.last_mouse_pos).length_squared() > 4  # Detect if mouse moved
        
        if mouse_moved:
            self.input_mode = 'mouse'  # Switch to mouse mode
            self.last_mouse_pos = mouse_pos.copy()
        
        # Only update aim from mouse if in mouse mode
        if self.input_mode == 'mouse':
            player_center = pg.Vector2(self.rect.centerx, self.rect.centery)
            aim_dir = mouse_pos - player_center
            if aim_dir.length_squared() > 0:
                self.aim_angle = math.degrees(math.atan2(-aim_dir.y, aim_dir.x))  # Negative y because pygame y is inverted
                # Update facing based on mouse position
                if aim_dir.x > 0:
                    self.facing = 1
                elif aim_dir.x < 0:
                    self.facing = -1
        
        if self.weapon and (keys[pg.K_j] or keys[pg.K_f] or pg.mouse.get_pressed()[0] or controller_shoot):
            if self.shoot_cooldown <= 0:
                ox = 14 * self.facing
                oy = -6
                origin = pg.Vector2(self.rect.centerx + ox, self.rect.centery + oy)
                
                # Use aim angle for direction (works for both mouse and controller)
                angle_rad = math.radians(self.aim_angle)
                direction = pg.Vector2(math.cos(angle_rad), -math.sin(angle_rad))
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
        
        # Calculate sprite draw position - align feet with bottom of collision box
        sprite_w = self.image.get_width()
        sprite_h = self.image.get_height()
        
        # Center horizontally, push sprite down so feet touch the ground
        draw_x = self.rect.centerx - sprite_w // 2 + ox
        draw_y = self.rect.bottom - sprite_h + 12 + oy  # +12 to push down onto platform
        
        # Draw player character
        surf.blit(self.image, (draw_x, draw_y))
        
        # Draw weapon if equipped and has sprite
        if self.weapon and hasattr(self.weapon, 'has_sprite') and self.weapon.has_sprite:
            # Determine which weapon frames to use
            weapon_frames = None
            if hasattr(self.weapon, 'sprite_type'):
                if self.weapon.sprite_type == 'smg' and SMG_FRAMES:
                    weapon_frames = SMG_FRAMES
                elif self.weapon.sprite_type == 'ak47' and AK_FRAMES:
                    weapon_frames = AK_FRAMES
                elif self.weapon.sprite_type == 'rocket' and ROCKET_FRAMES:
                    weapon_frames = ROCKET_FRAMES
                elif self.weapon.sprite_type == 'shotgun' and SHOTGUN_FRAMES:
                    weapon_frames = SHOTGUN_FRAMES
                elif self.weapon.sprite_type == 'pistol' and PISTOL_FRAMES:
                    weapon_frames = PISTOL_FRAMES
            elif AK_FRAMES:  # Fallback for AK-47
                weapon_frames = AK_FRAMES
            
            if weapon_frames:
                # Get the base frame (cycle through for animation)
                frame_idx = self.weapon_anim_frame % len(weapon_frames)
                base_img = weapon_frames[frame_idx]
                
                # Calculate rotation angle
                if self.facing > 0:
                    # Facing right - use normal image, rotate by aim angle
                    rotated_img = pg.transform.rotate(base_img, self.aim_angle)
                else:
                    # Facing left - flip vertically (not horizontally) and use negative angle
                    flipped_img = pg.transform.flip(base_img, False, True)
                    rotated_img = pg.transform.rotate(flipped_img, self.aim_angle)
                
                # Get the rotated image rect, centered on player's hand position
                weapon_center_x = self.rect.centerx + (12 * self.facing) + ox
                weapon_center_y = draw_y + sprite_h // 2 + 30  # Positioned lower at player's hands
                rotated_rect = rotated_img.get_rect(center=(weapon_center_x, weapon_center_y))
                
                surf.blit(rotated_img, rotated_rect)
                
                # Draw muzzle flash when firing
                if self.muzzle_flash_timer > 0:
                    flash_size = random.randint(6, 12) if self.weapon.sprite_type == 'smg' else random.randint(8, 14)
                    if hasattr(self.weapon, 'sprite_type') and self.weapon.sprite_type == 'rocket':
                        flash_size = random.randint(12, 18)  # Bigger flash for rocket
                    
                    # Calculate muzzle position based on weapon length and aim angle
                    weapon_length = base_img.get_width() // 2 + 10
                    angle_rad = math.radians(self.aim_angle)
                    
                    # Muzzle flash always follows the aim direction
                    flash_x = weapon_center_x + int(math.cos(angle_rad) * weapon_length)
                    flash_y = weapon_center_y - int(math.sin(angle_rad) * weapon_length)
                    
                    # Draw layered muzzle flash - different colors for each weapon
                    if hasattr(self.weapon, 'sprite_type') and self.weapon.sprite_type == 'smg':
                        pg.draw.circle(surf, (255, 240, 150), (flash_x, flash_y), flash_size)
                        pg.draw.circle(surf, (255, 180, 50), (flash_x, flash_y), flash_size - 2)
                        pg.draw.circle(surf, (255, 255, 200), (flash_x, flash_y), flash_size - 4)
                    elif hasattr(self.weapon, 'sprite_type') and self.weapon.sprite_type == 'rocket':
                        # Orange/red flash for rocket launcher
                        pg.draw.circle(surf, (255, 150, 50), (flash_x, flash_y), flash_size)
                        pg.draw.circle(surf, (255, 100, 30), (flash_x, flash_y), flash_size - 4)
                        pg.draw.circle(surf, (255, 200, 100), (flash_x, flash_y), flash_size - 8)
                    else:
                        pg.draw.circle(surf, (255, 255, 200), (flash_x, flash_y), flash_size)
                        pg.draw.circle(surf, (255, 200, 50), (flash_x, flash_y), flash_size - 3)
                        pg.draw.circle(surf, (255, 255, 255), (flash_x, flash_y), flash_size - 6)
