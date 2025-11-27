import math
import random
from pathlib import Path
import pygame as pg
from . import settings as S
from .player import (PhysicsSprite, AK_FRAMES, SMG_FRAMES, ROCKET_FRAMES, 
                     SHOTGUN_FRAMES, PISTOL_FRAMES, load_ak_frames, load_smg_frames,
                     load_rocket_frames, load_shotgun_frames, load_pistol_frames)
from .weapons import EnemyPistol, EnemySMG, EnemyShotgun, EnemyRocket, EnemyAK47

# Enemy1 animation frames (loaded lazily)
ENEMY1_IDLE_FRAMES = []
ENEMY1_IDLE_FRAMES_FLIPPED = []
ENEMY1_WALK_FRAMES = []
ENEMY1_WALK_FRAMES_FLIPPED = []
ENEMY1_FALL_FRAMES = []
ENEMY1_FALL_FRAMES_FLIPPED = []
ENEMY1_JUMP_START_FRAMES = []
ENEMY1_JUMP_START_FRAMES_FLIPPED = []
ENEMY1_JUMP_END_FRAMES = []
ENEMY1_JUMP_END_FRAMES_FLIPPED = []
ENEMY1_FRAMES_LOADED = False

# Enemy2 animation frames (loaded lazily)
ENEMY2_IDLE_FRAMES = []
ENEMY2_IDLE_FRAMES_FLIPPED = []
ENEMY2_WALK_FRAMES = []
ENEMY2_WALK_FRAMES_FLIPPED = []
ENEMY2_FALL_FRAMES = []
ENEMY2_FALL_FRAMES_FLIPPED = []
ENEMY2_JUMP_START_FRAMES = []
ENEMY2_JUMP_START_FRAMES_FLIPPED = []
ENEMY2_JUMP_END_FRAMES = []
ENEMY2_JUMP_END_FRAMES_FLIPPED = []
ENEMY2_FRAMES_LOADED = False

def load_enemy1_frames():
    """Load Enemy1 animation frames - called after pygame is initialized"""
    global ENEMY1_IDLE_FRAMES, ENEMY1_IDLE_FRAMES_FLIPPED
    global ENEMY1_WALK_FRAMES, ENEMY1_WALK_FRAMES_FLIPPED
    global ENEMY1_FALL_FRAMES, ENEMY1_FALL_FRAMES_FLIPPED
    global ENEMY1_JUMP_START_FRAMES, ENEMY1_JUMP_START_FRAMES_FLIPPED
    global ENEMY1_JUMP_END_FRAMES, ENEMY1_JUMP_END_FRAMES_FLIPPED
    global ENEMY1_FRAMES_LOADED
    
    if ENEMY1_FRAMES_LOADED:
        return
    
    try:
        enemy_folder = Path(__file__).parent / 'Enemy' / 'Enemy1'
        target_height = 140  # Target height for enemy sprites (bigger for visibility)
        
        # Load Idle frames
        idle_files = sorted(enemy_folder.glob('idle_*.png'))
        for f in idle_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY1_IDLE_FRAMES.append(scaled)
            ENEMY1_IDLE_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY1_IDLE_FRAMES)} enemy idle frames")
        
        # Load Walk frames
        walk_files = sorted(enemy_folder.glob('walk_*.png'))
        for f in walk_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY1_WALK_FRAMES.append(scaled)
            ENEMY1_WALK_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY1_WALK_FRAMES)} enemy walk frames")
        
        # Load Fall frames
        fall_files = sorted(enemy_folder.glob('fall_*.png'))
        for f in fall_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY1_FALL_FRAMES.append(scaled)
            ENEMY1_FALL_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY1_FALL_FRAMES)} enemy fall frames")
        
        # Load Jump Start frames
        jump_start_files = sorted(enemy_folder.glob('jumpStart_*.png'))
        for f in jump_start_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY1_JUMP_START_FRAMES.append(scaled)
            ENEMY1_JUMP_START_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY1_JUMP_START_FRAMES)} enemy jump start frames")
        
        # Load Jump End frames
        jump_end_files = sorted(enemy_folder.glob('jumpEnd_*.png'))
        for f in jump_end_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY1_JUMP_END_FRAMES.append(scaled)
            ENEMY1_JUMP_END_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY1_JUMP_END_FRAMES)} enemy jump end frames")
        
        ENEMY1_FRAMES_LOADED = True
        
    except Exception as e:
        print(f"Could not load Enemy1 sprites: {e}")
        ENEMY1_FRAMES_LOADED = True

def load_enemy2_frames():
    """Load Enemy2 animation frames - called after pygame is initialized"""
    global ENEMY2_IDLE_FRAMES, ENEMY2_IDLE_FRAMES_FLIPPED
    global ENEMY2_WALK_FRAMES, ENEMY2_WALK_FRAMES_FLIPPED
    global ENEMY2_FALL_FRAMES, ENEMY2_FALL_FRAMES_FLIPPED
    global ENEMY2_JUMP_START_FRAMES, ENEMY2_JUMP_START_FRAMES_FLIPPED
    global ENEMY2_JUMP_END_FRAMES, ENEMY2_JUMP_END_FRAMES_FLIPPED
    global ENEMY2_FRAMES_LOADED
    
    if ENEMY2_FRAMES_LOADED:
        return
    
    try:
        enemy_folder = Path(__file__).parent / 'Enemy' / 'Enemy2'
        target_height = 140  # Target height for enemy sprites (bigger for visibility)
        
        # Load Idle frames
        idle_files = sorted(enemy_folder.glob('idle_*.png'))
        for f in idle_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY2_IDLE_FRAMES.append(scaled)
            ENEMY2_IDLE_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY2_IDLE_FRAMES)} enemy2 idle frames")
        
        # Load Walk frames
        walk_files = sorted(enemy_folder.glob('walk_*.png'))
        for f in walk_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY2_WALK_FRAMES.append(scaled)
            ENEMY2_WALK_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY2_WALK_FRAMES)} enemy2 walk frames")
        
        # Load Fall frames
        fall_files = sorted(enemy_folder.glob('fall_*.png'))
        for f in fall_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY2_FALL_FRAMES.append(scaled)
            ENEMY2_FALL_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY2_FALL_FRAMES)} enemy2 fall frames")
        
        # Load Jump Start frames
        jump_start_files = sorted(enemy_folder.glob('jumpStart_*.png'))
        for f in jump_start_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY2_JUMP_START_FRAMES.append(scaled)
            ENEMY2_JUMP_START_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY2_JUMP_START_FRAMES)} enemy2 jump start frames")
        
        # Load Jump End frames
        jump_end_files = sorted(enemy_folder.glob('jumpEnd_*.png'))
        for f in jump_end_files:
            img = pg.image.load(str(f)).convert_alpha()
            scale_factor = target_height / img.get_height()
            scaled = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
            ENEMY2_JUMP_END_FRAMES.append(scaled)
            ENEMY2_JUMP_END_FRAMES_FLIPPED.append(pg.transform.flip(scaled, True, False))
        print(f"Loaded {len(ENEMY2_JUMP_END_FRAMES)} enemy2 jump end frames")
        
        ENEMY2_FRAMES_LOADED = True
        
    except Exception as e:
        print(f"Could not load Enemy2 sprites: {e}")
        ENEMY2_FRAMES_LOADED = True

class Enemy(PhysicsSprite):
    def __init__(self, x, y, speed=140, variant=None, game_difficulty=None):
        super().__init__()
        # Randomly choose variant if not specified
        self.variant = variant if variant is not None else random.choice([1, 2])
        
        # Get difficulty settings
        if game_difficulty is None:
            game_difficulty = S.DIFF_NORMAL
        self.game_difficulty = game_difficulty
        self.diff_settings = S.DIFFICULTY_SETTINGS[game_difficulty]
        
        # Load appropriate enemy sprites
        if self.variant == 1:
            load_enemy1_frames()
        else:
            load_enemy2_frames()
        
        self.pos.update(x, y)
        self.speed = speed * self.diff_settings['enemy_speed_mult']  # Apply difficulty speed multiplier
        self.size = pg.Vector2(24, 40)  # Collision box size
        
        # Animation state
        self.anim_state = 'idle'
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.idle_frame_duration = 0.12
        self.walk_frame_duration = 0.08
        self.fall_frame_duration = 0.1
        self.jump_frame_duration = 0.1
        
        # Set initial image based on variant
        idle_frames = ENEMY1_IDLE_FRAMES if self.variant == 1 else ENEMY2_IDLE_FRAMES
        if idle_frames:
            self.image = idle_frames[0]
            self.sprite_size = pg.Vector2(self.image.get_width(), self.image.get_height())
        else:
            self.sprite_size = self.size.copy()
            self.image = pg.Surface(self.size, pg.SRCALPHA)
            self.draw_enemy_fallback()
        
        self.rect = pg.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        self.rect.topleft = self.pos
        self.dir = random.choice([-1, 1])
        self.facing = self.dir
        self.health = 2
        self.on_ground = False
        
        # Weapon system with probability-based selection
        # Pistol: 40%, SMG: 25%, Shotgun: 15%, AK47: 15%, Rocket: 5%
        weapon_choices = [
            (EnemyPistol, 40),
            (EnemySMG, 25),
            (EnemyShotgun, 15),
            (EnemyAK47, 15),
            (EnemyRocket, 5)
        ]
        total_weight = sum(w[1] for w in weapon_choices)
        roll = random.randint(1, total_weight)
        cumulative = 0
        for weapon_class, weight in weapon_choices:
            cumulative += weight
            if roll <= cumulative:
                self.weapon = weapon_class()
                break
        
        self.shoot_cooldown = 0.0
        self.shoot_range = self.diff_settings['shoot_range']  # Distance based on difficulty
        self.can_see_player = False
        self.player_ref = None  # Will be set when update is called with player
        self.aim_angle = 0.0  # Angle to aim weapon
        self.muzzle_flash_timer = 0.0
        self.reaction_timer = self.diff_settings['reaction_delay']  # Delay before first shot
        
        # Advanced AI settings
        self.ai_state = 'patrol'  # 'patrol', 'chase', 'attack'
        self.jump_cooldown = 0.0
        self.chase_range = self.diff_settings['chase_range']  # Distance to start chasing
        self.attack_range = 300  # Distance to stop and focus on shooting
        self.jump_velocity = S.JUMP_VELOCITY * 0.9  # Slightly weaker jump than player
        self.jump_chance = self.diff_settings['jump_chance']  # Probability to jump when needed
        self.ai_aggression = self.diff_settings['ai_aggression']  # How aggressive the AI is
        self.stuck_timer = 0.0  # Timer to detect if stuck
        self.last_x = x  # Last x position to detect stuck
        self.ai_decision_timer = 0.0  # Timer for AI decision making
        self.target_platform = None  # Platform we're trying to reach
        
        # Map enemy weapon to sprite type for rendering
        self.weapon_sprite_type = self._get_weapon_sprite_type()
        self._load_weapon_frames()
    
    def _get_weapon_sprite_type(self):
        """Get the sprite type for the enemy's weapon"""
        if isinstance(self.weapon, EnemyPistol):
            return 'pistol'
        elif isinstance(self.weapon, EnemySMG):
            return 'smg'
        elif isinstance(self.weapon, EnemyShotgun):
            return 'shotgun'
        elif isinstance(self.weapon, EnemyRocket):
            return 'rocket'
        elif isinstance(self.weapon, EnemyAK47):
            return 'ak47'
        return None
    
    def _load_weapon_frames(self):
        """Load weapon sprite frames for this enemy's weapon"""
        if self.weapon_sprite_type == 'pistol':
            load_pistol_frames()
        elif self.weapon_sprite_type == 'smg':
            load_smg_frames()
        elif self.weapon_sprite_type == 'shotgun':
            load_shotgun_frames()
        elif self.weapon_sprite_type == 'rocket':
            load_rocket_frames()
        elif self.weapon_sprite_type == 'ak47':
            load_ak_frames()
    
    def draw_enemy_fallback(self):
        """Draw a proper enemy character sprite"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        w, h = int(self.size.x), int(self.size.y)
        
        # Body (torso) - more menacing colors
        body_rect = pg.Rect(w//4, h//3, w//2, h//2)
        pg.draw.rect(self.image, (220, 80, 90), body_rect, border_radius=4)
        pg.draw.rect(self.image, (180, 50, 60), body_rect, width=2, border_radius=4)
        
        # Head - skull-like
        head_size = w // 2.5
        head_center = (w // 2, h // 5)
        pg.draw.circle(self.image, (200, 200, 200), head_center, int(head_size))
        pg.draw.circle(self.image, (150, 150, 150), head_center, int(head_size), width=2)
        
        # Evil eyes (red)
        eye_y = h // 6
        pg.draw.circle(self.image, (255, 50, 50), (w//2 - 4, eye_y), 3)
        pg.draw.circle(self.image, (255, 50, 50), (w//2 + 4, eye_y), 3)
        pg.draw.circle(self.image, (150, 0, 0), (w//2 - 4, eye_y), 3, width=1)
        pg.draw.circle(self.image, (150, 0, 0), (w//2 + 4, eye_y), 3, width=1)
        
        # Legs
        leg_top = h // 3 + h // 2
        leg_width = 5
        pg.draw.rect(self.image, (150, 60, 70), (w//3 - 2, leg_top, leg_width, h - leg_top), border_radius=2)
        pg.draw.rect(self.image, (150, 60, 70), (w - w//3 - 3, leg_top, leg_width, h - leg_top), border_radius=2)
        
        # Arms (claws)
        arm_y = h // 3 + 5
        arm_height = h // 3
        pg.draw.rect(self.image, (180, 180, 180), (2, arm_y, 4, arm_height), border_radius=2)
        pg.draw.rect(self.image, (180, 180, 180), (w - 6, arm_y, 4, arm_height), border_radius=2)
        # Claw tips
        pg.draw.circle(self.image, (255, 50, 50), (4, arm_y + arm_height), 3)
        pg.draw.circle(self.image, (255, 50, 50), (w - 4, arm_y + arm_height), 3)

    def update_animation(self, dt):
        """Update enemy animation based on state"""
        # Check if frames are loaded based on variant
        if self.variant == 1 and not ENEMY1_FRAMES_LOADED:
            return
        if self.variant == 2 and not ENEMY2_FRAMES_LOADED:
            return
        
        # Get the appropriate frame lists based on variant
        if self.variant == 1:
            idle_frames = ENEMY1_IDLE_FRAMES
            idle_frames_flipped = ENEMY1_IDLE_FRAMES_FLIPPED
            walk_frames = ENEMY1_WALK_FRAMES
            walk_frames_flipped = ENEMY1_WALK_FRAMES_FLIPPED
            fall_frames = ENEMY1_FALL_FRAMES
            fall_frames_flipped = ENEMY1_FALL_FRAMES_FLIPPED
            jump_start_frames = ENEMY1_JUMP_START_FRAMES
            jump_start_frames_flipped = ENEMY1_JUMP_START_FRAMES_FLIPPED
            jump_end_frames = ENEMY1_JUMP_END_FRAMES
            jump_end_frames_flipped = ENEMY1_JUMP_END_FRAMES_FLIPPED
        else:
            idle_frames = ENEMY2_IDLE_FRAMES
            idle_frames_flipped = ENEMY2_IDLE_FRAMES_FLIPPED
            walk_frames = ENEMY2_WALK_FRAMES
            walk_frames_flipped = ENEMY2_WALK_FRAMES_FLIPPED
            fall_frames = ENEMY2_FALL_FRAMES
            fall_frames_flipped = ENEMY2_FALL_FRAMES_FLIPPED
            jump_start_frames = ENEMY2_JUMP_START_FRAMES
            jump_start_frames_flipped = ENEMY2_JUMP_START_FRAMES_FLIPPED
            jump_end_frames = ENEMY2_JUMP_END_FRAMES
            jump_end_frames_flipped = ENEMY2_JUMP_END_FRAMES_FLIPPED
        
        # Determine animation state
        prev_state = self.anim_state
        
        if not self.on_ground:
            if self.vel.y < 0 and jump_start_frames:
                self.anim_state = 'jump_start'
            elif self.vel.y > 50 and fall_frames:
                self.anim_state = 'fall'
            elif jump_end_frames:
                self.anim_state = 'jump_end'
        elif abs(self.vel.x) > 10 and walk_frames:
            self.anim_state = 'walk'
        elif idle_frames:
            self.anim_state = 'idle'
        
        # Reset frame if state changed
        if prev_state != self.anim_state:
            self.anim_frame = 0
            self.anim_timer = 0.0
        
        # Update animation timer
        self.anim_timer += dt
        
        # Get current frames list and frame duration
        frames = None
        frames_flipped = None
        frame_duration = 0.1
        
        if self.anim_state == 'idle' and idle_frames:
            frames = idle_frames
            frames_flipped = idle_frames_flipped
            frame_duration = self.idle_frame_duration
        elif self.anim_state == 'walk' and walk_frames:
            frames = walk_frames
            frames_flipped = walk_frames_flipped
            frame_duration = self.walk_frame_duration
        elif self.anim_state == 'fall' and fall_frames:
            frames = fall_frames
            frames_flipped = fall_frames_flipped
            frame_duration = self.fall_frame_duration
        elif self.anim_state == 'jump_start' and jump_start_frames:
            frames = jump_start_frames
            frames_flipped = jump_start_frames_flipped
            frame_duration = self.jump_frame_duration
        elif self.anim_state == 'jump_end' and jump_end_frames:
            frames = jump_end_frames
            frames_flipped = jump_end_frames_flipped
            frame_duration = self.jump_frame_duration
        
        if not frames:
            return
        
        # Advance frame
        if self.anim_timer >= frame_duration:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % len(frames)
        
        # Clamp frame index
        self.anim_frame = min(self.anim_frame, len(frames) - 1)
        
        # Set current image based on facing direction
        # Enemy faces right when dir is 1, left when dir is -1
        if self.dir > 0:
            self.image = frames[self.anim_frame]
        else:
            self.image = frames_flipped[self.anim_frame]

    def damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, dt, platforms, player=None, enemy_bullets=None):
        # Update timers
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        if self.reaction_timer > 0:
            self.reaction_timer -= dt
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= dt
        if self.jump_cooldown > 0:
            self.jump_cooldown -= dt
        
        self.ai_decision_timer += dt
        
        # Run advanced AI
        self.update_ai(dt, platforms, player)
        
        # Apply movement
        self.vel.x = self.dir * self.speed
        self.on_ground = self.physics_step(dt, platforms)
        
        # Update animation
        self.update_animation(dt)
        
        # Update aim angle toward player (even if not shooting)
        if player:
            my_center = pg.Vector2(self.rect.center)
            player_center = pg.Vector2(player.rect.center)
            direction = player_center - my_center
            if direction.length() > 0:
                self.aim_angle = math.degrees(math.atan2(-direction.y, direction.x))
        
        # Check if player is in range and shoot
        if player and enemy_bullets is not None:
            self.try_shoot_at_player(player, enemy_bullets)
        
        # Fall off screen check
        if self.pos.y > S.HAZARD_HEIGHT + 60:
            self.kill()
    
    def update_ai(self, dt, platforms, player):
        """Advanced AI behavior - chase, jump, and attack player"""
        
        # Detect if stuck (not moving horizontally)
        if abs(self.pos.x - self.last_x) < 1 and self.on_ground:
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0
        self.last_x = self.pos.x
        
        # If no player, just patrol
        if not player:
            self.ai_state = 'patrol'
            self.patrol_behavior(dt, platforms)
            return
        
        # Calculate distance to player
        my_center = pg.Vector2(self.rect.center)
        player_center = pg.Vector2(player.rect.center)
        direction = player_center - my_center
        distance = direction.length()
        
        # Determine AI state based on distance
        if distance < self.attack_range:
            self.ai_state = 'attack'
        elif distance < self.chase_range:
            self.ai_state = 'chase'
        else:
            self.ai_state = 'patrol'
        
        # Execute behavior based on state
        if self.ai_state == 'attack':
            self.attack_behavior(dt, platforms, player)
        elif self.ai_state == 'chase':
            self.chase_behavior(dt, platforms, player)
        else:
            self.patrol_behavior(dt, platforms)
    
    def patrol_behavior(self, dt, platforms):
        """Basic patrol - walk back and forth on platform"""
        if self.on_ground:
            # Check for edge or wall
            ahead = self.rect.move(self.dir * 10, 1)
            support = False
            for p in platforms:
                if p.rect.colliderect(ahead.move(0, 10)) and p.rect.top <= self.rect.bottom <= p.rect.bottom + 2:
                    support = True
                    break
            if not support:
                self.dir *= -1
            
            # Check for wall collision
            for p in platforms:
                if self.rect.colliderect(p.rect) and (self.rect.left <= p.rect.left or self.rect.right >= p.rect.right):
                    self.dir *= -1
                    break
            
            # If stuck, try jumping or reversing
            if self.stuck_timer > 0.5:
                self.dir *= -1
                self.stuck_timer = 0
    
    def chase_behavior(self, dt, platforms, player):
        """Chase the player - move toward them and jump if needed"""
        player_x = player.rect.centerx
        player_y = player.rect.centery
        my_x = self.rect.centerx
        my_y = self.rect.centery
        
        # Move toward player horizontally
        if player_x > my_x + 20:
            self.dir = 1
        elif player_x < my_x - 20:
            self.dir = -1
        
        # Update facing to match direction
        self.facing = self.dir
        
        if self.on_ground:
            # Check if we need to jump
            should_jump = False
            
            # Jump if player is above us
            if player_y < my_y - 50:
                # Check if there's a platform above we can reach
                for p in platforms:
                    if (p.rect.bottom < self.rect.top and 
                        p.rect.bottom > self.rect.top - 200 and
                        abs(p.rect.centerx - my_x) < 150):
                        should_jump = True
                        break
            
            # Jump if stuck
            if self.stuck_timer > 0.3:
                should_jump = True
                self.stuck_timer = 0
            
            # Jump over gaps when chasing
            ahead = self.rect.move(self.dir * 30, 1)
            has_ground_ahead = False
            for p in platforms:
                if p.rect.colliderect(ahead.move(0, 20)):
                    has_ground_ahead = True
                    break
            if not has_ground_ahead:
                # Check if there's a platform we can jump to
                jump_target = self.rect.move(self.dir * 80, -50)
                for p in platforms:
                    if p.rect.colliderect(jump_target.move(0, 60)):
                        should_jump = True
                        break
            
            # Jump over obstacles
            wall_ahead = False
            for p in platforms:
                if (self.rect.colliderect(p.rect.move(-self.dir * 5, 0)) and 
                    p.rect.top < self.rect.bottom - 10):
                    wall_ahead = True
                    break
            if wall_ahead:
                should_jump = True
            
            # Execute jump (with probability based on difficulty)
            if should_jump and self.jump_cooldown <= 0:
                if random.random() < self.jump_chance:
                    self.vel.y = self.jump_velocity
                    self.jump_cooldown = 0.4  # Cooldown between jumps
                else:
                    self.jump_cooldown = 0.3  # Small cooldown even if didn't jump
        
        # Edge detection while chasing - don't walk off unless jumping
        if self.on_ground and self.vel.y >= 0:
            ahead = self.rect.move(self.dir * 15, 1)
            has_support = False
            for p in platforms:
                if p.rect.colliderect(ahead.move(0, 15)):
                    has_support = True
                    break
            if not has_support:
                # Stop at edge, might need to jump
                if self.jump_cooldown <= 0 and random.random() < self.jump_chance:
                    # Try to jump across
                    self.vel.y = self.jump_velocity
                    self.jump_cooldown = 0.5
                else:
                    # Can't/won't jump, reverse direction
                    self.dir *= -1
    
    def attack_behavior(self, dt, platforms, player):
        """Attack mode - stay at medium range and focus on shooting"""
        player_x = player.rect.centerx
        player_y = player.rect.centery
        my_x = self.rect.centerx
        my_y = self.rect.centery
        
        horizontal_dist = abs(player_x - my_x)
        
        # Optimal distance varies by aggression (aggressive enemies get closer)
        optimal_distance = 180 - (self.ai_aggression * 60)  # 120-180 based on aggression
        
        if horizontal_dist < optimal_distance - 30:
            # Too close, back away (less aggressive enemies back away more)
            if random.random() < (1 - self.ai_aggression * 0.5):
                if player_x > my_x:
                    self.dir = -1
                else:
                    self.dir = 1
            else:
                self.dir = 0  # Aggressive enemies stand their ground
        elif horizontal_dist > optimal_distance + 50:
            # Too far, move closer
            if player_x > my_x:
                self.dir = 1
            else:
                self.dir = -1
        else:
            # Good distance, stop moving to aim better
            self.dir = 0
        
        # Always face the player
        if player_x > my_x:
            self.facing = 1
        else:
            self.facing = -1
        
        # Jump if player is significantly above (with probability)
        if self.on_ground and player_y < my_y - 80 and self.jump_cooldown <= 0:
            if random.random() < self.jump_chance:
                self.vel.y = self.jump_velocity
                self.jump_cooldown = 0.6
        
        # Edge detection - don't fall off while attacking
        if self.on_ground and self.dir != 0:
            ahead = self.rect.move(self.dir * 15, 1)
            has_support = False
            for p in platforms:
                if p.rect.colliderect(ahead.move(0, 15)):
                    has_support = True
                    break
            if not has_support:
                self.dir = 0  # Stop at edge
    
    def try_shoot_at_player(self, player, enemy_bullets):
        """Attempt to shoot at the player if in range and line of sight"""
        if not self.weapon or self.shoot_cooldown > 0:
            return
        
        # Reaction delay - enemy needs time to "notice" player
        if self.reaction_timer > 0:
            return
        
        # Calculate distance to player
        my_center = pg.Vector2(self.rect.center)
        player_center = pg.Vector2(player.rect.center)
        direction = player_center - my_center
        distance = direction.length()
        
        if distance > self.shoot_range or distance < 30:
            return
        
        # Shoot chance based on difficulty - not every opportunity results in a shot
        if random.random() > self.diff_settings['shoot_chance']:
            # Didn't decide to shoot this time, add small cooldown
            self.shoot_cooldown = 0.2
            return
        
        # Normalize direction
        if distance > 0:
            direction = direction.normalize()
        else:
            direction = pg.Vector2(self.dir, 0)
        
        # Update facing direction based on player position
        if direction.x > 0:
            self.facing = 1
        else:
            self.facing = -1
        
        # Calculate origin point (from enemy's weapon position)
        ox = 14 * self.facing
        oy = -6
        origin = pg.Vector2(self.rect.centerx + ox, self.rect.centery + oy)
        
        # Add inaccuracy based on difficulty (higher = more miss)
        inaccuracy = random.uniform(-self.diff_settings['inaccuracy'], self.diff_settings['inaccuracy'])
        angle = math.atan2(direction.y, direction.x) + inaccuracy
        direction = pg.Vector2(math.cos(angle), math.sin(angle))
        
        # Shoot!
        self.weapon.shoot(origin, direction, enemy_bullets)
        # Cooldown based on difficulty (higher multiplier = slower shooting)
        self.shoot_cooldown = self.weapon.cooldown * self.diff_settings['cooldown_mult']
        self.muzzle_flash_timer = 0.08  # Show muzzle flash briefly

    def draw(self, surf, offset=(0, 0)):
        """Draw the enemy with proper sprite positioning"""
        ox, oy = offset
        
        # Calculate sprite draw position - align feet with bottom of collision box
        sprite_w = self.image.get_width()
        sprite_h = self.image.get_height()
        
        # Center horizontally, push sprite down so feet touch the ground
        # The sprite has padding at the bottom, so we add offset to push it down
        draw_x = self.rect.centerx - sprite_w // 2 + ox
        draw_y = self.rect.bottom - sprite_h + 20 + oy  # +20 to push down onto platform
        
        surf.blit(self.image, (draw_x, draw_y))
        
        # Draw weapon sprite
        self._draw_weapon(surf, draw_x, draw_y, sprite_w, sprite_h, ox, oy)
    
    def _draw_weapon(self, surf, draw_x, draw_y, sprite_w, sprite_h, ox, oy):
        """Draw the enemy's weapon with proper positioning and rotation"""
        # Decrease muzzle flash timer
        # (Note: This should ideally be in update, but we do it here for simplicity)
        
        # Get the appropriate weapon frames
        weapon_frames = None
        if self.weapon_sprite_type == 'pistol' and PISTOL_FRAMES:
            weapon_frames = PISTOL_FRAMES
        elif self.weapon_sprite_type == 'smg' and SMG_FRAMES:
            weapon_frames = SMG_FRAMES
        elif self.weapon_sprite_type == 'shotgun' and SHOTGUN_FRAMES:
            weapon_frames = SHOTGUN_FRAMES
        elif self.weapon_sprite_type == 'rocket' and ROCKET_FRAMES:
            weapon_frames = ROCKET_FRAMES
        elif self.weapon_sprite_type == 'ak47' and AK_FRAMES:
            weapon_frames = AK_FRAMES
        
        if not weapon_frames:
            return
        
        # Use first frame (enemies don't have firing animation)
        base_img = weapon_frames[0]
        
        # Calculate rotation angle based on aim
        if self.facing > 0:
            # Facing right - use normal image
            rotated_img = pg.transform.rotate(base_img, self.aim_angle)
        else:
            # Facing left - flip vertically and use negative angle
            flipped_img = pg.transform.flip(base_img, False, True)
            rotated_img = pg.transform.rotate(flipped_img, self.aim_angle)
        
        # Position weapon at enemy's hand level
        weapon_center_x = self.rect.centerx + (12 * self.facing) + ox
        weapon_center_y = draw_y + sprite_h // 2 + 30  # At hands level
        rotated_rect = rotated_img.get_rect(center=(weapon_center_x, weapon_center_y))
        
        surf.blit(rotated_img, rotated_rect)
        
        # Draw muzzle flash when firing
        if self.muzzle_flash_timer > 0:
            flash_size = random.randint(6, 12)
            if self.weapon_sprite_type == 'rocket':
                flash_size = random.randint(10, 16)
            
            # Calculate muzzle position based on weapon and aim angle
            weapon_length = base_img.get_width() // 2 + 10
            angle_rad = math.radians(self.aim_angle)
            
            flash_x = weapon_center_x + int(math.cos(angle_rad) * weapon_length)
            flash_y = weapon_center_y - int(math.sin(angle_rad) * weapon_length)
            
            # Red/orange muzzle flash for enemies
            pg.draw.circle(surf, (255, 150, 80), (flash_x, flash_y), flash_size)
            pg.draw.circle(surf, (255, 100, 50), (flash_x, flash_y), flash_size - 3)
            pg.draw.circle(surf, (255, 200, 150), (flash_x, flash_y), flash_size - 6)

class Spawner:
    def __init__(self, pos):
        self.pos = pg.Vector2(pos)

    def spawn(self, difficulty, game_difficulty=None):
        speed = 120 + difficulty * 18
        return Enemy(self.pos.x, self.pos.y, speed, game_difficulty=game_difficulty)
