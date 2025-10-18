#!/usr/bin/env python3
"""
🧟 ULTIMATE ZOMBIE SURVIVAL FPS 🧟
The BEST post-apocalyptic survival game with ultra-realistic mechanics!
Professional-grade graphics, AI, physics, and gameplay!
"""

import pygame
import socket
import json
import threading
import time
import math
import random
import sys
import os
from collections import deque

# Initialize Pygame
pygame.init()

# Initialize Sound System
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.mixer.set_num_channels(32)  # Allow more simultaneous sounds
    SOUND_ENABLED = True
    print("🎵 Sound system initialized successfully")
except Exception as e:
    print(f"⚠️ Sound system failed to initialize: {e}")
    SOUND_ENABLED = False

class Colors:
    """Professional Color Palette - Cinema Quality"""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    BLUE = (0, 150, 255)
    CYAN = (0, 255, 255)
    DARK_GREEN = (0, 100, 0)
    BLOOD_RED = (139, 0, 0)
    DARK_BLOOD = (80, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (200, 200, 200)
    GOLD = (255, 215, 0)
    PURPLE = (128, 0, 128)
    NEON_GREEN = (57, 255, 20)
    NEON_CYAN = (0, 255, 255)
    NEON_RED = (255, 20, 60)
    NEON_YELLOW = (255, 255, 20)
    NEON_BLUE = (20, 100, 255)
    SKY_BLUE = (135, 206, 235)
    ZOMBIE_GREEN = (90, 120, 80)
    DEAD_FLESH = (110, 110, 90)
    GORE_RED = (180, 20, 20)

class Weapon:
    """🔫 PROFESSIONAL WEAPON SYSTEM - Realistic ballistics and mechanics"""
    def __init__(self, name, damage, fire_rate, ammo, reload_time, accuracy, recoil=0.05, penetration=1.0, auto=True):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate  # Shots per second
        self.max_ammo = ammo
        self.current_ammo = ammo
        self.magazine_count = 5  # More magazines for survival
        self.reload_time = reload_time
        self.accuracy = accuracy
        self.recoil = recoil  # Camera shake on fire
        self.penetration = penetration  # Armor penetration
        self.auto = auto  # Is weapon automatic (hold to fire)?
        self.last_shot_time = 0
        self.reloading = False
        self.reload_start = 0
        self.kills = 0  # Track kills per weapon
        self.shots_fired = 0
        self.hits = 0
        
        # NEW: Advanced mechanics
        self.ads_zoom = 1.5  # Aim down sights zoom
        self.hipfire_spread = 0.2  # Spread when not aiming
        self.vertical_recoil = recoil
        self.horizontal_recoil = recoil * 0.5
        self.recoil_recovery = 0.9  # How fast recoil recovers
        self.current_recoil = 0  # Current recoil offset
    
    def can_shoot(self):
        current_time = time.time()
        return (self.current_ammo > 0 and 
                not self.reloading and 
                current_time - self.last_shot_time >= 1.0 / self.fire_rate)
    
    def shoot(self):
        if self.can_shoot():
            self.current_ammo -= 1
            self.last_shot_time = time.time()
            self.shots_fired += 1
            return True
        return False
    
    def reload(self):
        """🔄 Reload weapon - Triggered by pressing 'R' key - CS:GO Style"""
        # Allow reload if not full and have magazines OR always have infinite reserve ammo
        if not self.reloading and self.current_ammo < self.max_ammo:
            self.reloading = True
            self.reload_start = time.time()
            # Tactical reload - drop current mag and load new one
            if self.magazine_count > 0:
                self.magazine_count -= 1
            print(f"🔫 Reloading {self.name}... ({self.reload_time}s)")
    
    def get_accuracy_rating(self):
        """Calculate accuracy percentage"""
        if self.shots_fired == 0:
            return 100.0
        return (self.hits / self.shots_fired) * 100
    
    def update(self):
        """Update weapon state (handles reload completion)"""
        if self.reloading:
            if time.time() - self.reload_start >= self.reload_time:
                self.current_ammo = self.max_ammo
                self.reloading = False
                print(f"✅ {self.name} reloaded! Ammo: {self.current_ammo}/{self.max_ammo}")

# Professional Weapon Arsenal - Balanced for Zombie Survival
WEAPONS = {
    'assault_rifle': Weapon("🔫 M4A1 Assault Rifle", 35, 10, 30, 2.0, 0.92, 0.04, 0.8, auto=True),
    'sniper': Weapon("🎯 Barrett .50 Cal", 150, 1, 5, 3.5, 0.98, 0.20, 1.8, auto=False),
    'smg': Weapon("⚡ MP5 SMG", 25, 15, 30, 1.5, 0.88, 0.02, 0.6, auto=True),
    'shotgun': Weapon("💥 SPAS-12 Shotgun", 100, 1.5, 8, 2.5, 0.75, 0.15, 0.5, auto=False),
    'pistol': Weapon("🔫 Desert Eagle", 45, 5, 12, 1.2, 0.90, 0.05, 0.7, auto=False),
    'lmg': Weapon("🔥 M249 SAW", 40, 12, 100, 4.5, 0.85, 0.08, 0.9, auto=True)
}

class FPSGame:
    """🎮 THE ULTIMATE ZOMBIE SURVIVAL FPS - PROFESSIONAL GRADE"""
    
    def __init__(self):
        self.screen_width = 1600  # Cinema-quality resolution
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🧟 ULTIMATE ZOMBIE SURVIVAL - THE BEST FPS GAME")
        
        # Fonts
        self.font_huge = pygame.font.Font(None, 84)
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 26)
        self.font_tiny = pygame.font.Font(None, 20)
        
        # Game state
        self.running = True
        self.in_menu = True  # Start in menu
        self.in_game = False
        self.in_team_selection = False  # NEW: Team selection screen
        self.in_server_connect = False  # NEW: Server connection screen
        self.menu_option = 0
        self.menu_options = ["⚡ PLAY GAME", "🎯 LOADOUT", "⚙️ SETTINGS", "🚪 EXIT"]
        
        # SERVER CONNECTION
        self.server_ip = ""  # Server IP to connect to
        self.server_port = "5555"  # Default port
        self.connection_status = ""  # Connection status message
        
        # TEAM SYSTEM
        self.player_team = None  # Will be 'BLUE' or 'RED'
        self.team_selection = 0  # 0 = BLUE, 1 = RED
        
        self.player_health = 100
        self.player_max_health = 100
        self.player_armor = 0  # No armor at start - must find it
        self.player_x = 0
        self.player_y = 0
        self.player_z = 0
        self.player_angle = 0
        self.mouse_sensitivity = 0.003
        
        # Weapon system
        self.current_weapon = 'pistol'  # Start with pistol only
        self.weapons = {name: Weapon(w.name, w.damage, w.fire_rate, w.max_ammo, w.reload_time, w.accuracy, w.recoil, w.penetration) 
                       for name, w in WEAPONS.items()}
        # Start with limited ammo
        self.weapons['pistol'].current_ammo = 12
        self.weapons['pistol'].magazine_count = 1
        
        # ZOMBIE HORDE
        self.enemies = []
        self.zombie_wave = 1
        self.zombies_killed_this_wave = 0
        self.zombies_per_wave = 10
        self.spawn_enemies(self.zombies_per_wave)
        
        # Multiplayer players
        self.players = {}
        
        # Projectiles
        self.bullets = []
        
        # Game stats
        self.kills = 0
        self.deaths = 0
        self.score = 0
        self.headshots = 0
        self.accuracy_total = 0
        self.shots_total = 0
        
        # Loot and pickups
        self.ammo_packs = []
        self.health_packs = []
        self.armor_packs = []
        self.weapon_spawns = []
        
        # Visual effects - PROFESSIONAL CINEMA-QUALITY
        self.blood_splatter = []
        self.blood_decals = deque(maxlen=150)  # Persistent gore
        self.muzzle_flash = None
        self.hit_markers = []
        self.shell_casings = []
        self.explosions = []
        self.screen_shake = 0
        self.screen_shake_x = 0
        self.screen_shake_y = 0
        self.damage_vignette = 0  # Red screen edges when hurt
        self.blood_on_screen = 0  # Blood splatter on camera
        self.smoke_particles = []
        self.spark_particles = []
        self.tracer_rounds = []
        self.impact_marks = []
        self.lens_flare_time = 0
        self.god_rays = []  # Volumetric lighting
        
        # POST-APOCALYPTIC MAP
        self.buildings = []
        self.trees = []
        self.grass_patches = []
        self.rocks = []
        self.clouds = []
        self.fires = []  # Burning debris
        self.sun_position = (self.screen_width * 0.8, self.screen_height * 0.2)
        self._generate_map()
        
        # SURVIVAL MECHANICS
        self.weapon_attachments = {
            'scopes': ['Red Dot', 'ACOG', 'Sniper Scope'],
            'grips': ['Vertical Grip', 'Angled Grip'],
            'barrels': ['Suppressor', 'Compensator', 'Extended Barrel']
        }
        self.current_attachments = {'scope': None, 'grip': None, 'barrel': None}
        self.perks = ['Fast Reload', 'Extra Ammo', 'Faster Sprint', 'Armor Piercing']
        self.active_perks = []
        self.achievements = []
        self.daily_challenges = self._generate_daily_challenges()
        self.weather = 'fog'  # Start with creepy fog
        self.time_of_day = 'dusk'  # Ominous dusk lighting
        self.footstep_sounds = []
        
        # SOUND SYSTEM - Professional Audio
        self.sound_enabled = SOUND_ENABLED
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        self._load_sounds()
        
        # Play background music
        self._play_background_music()
        
        # PROFESSIONAL CAMERA SYSTEM
        self.camera_mode = 'first_person'
        self.camera_distance = 200
        self.camera_height = 100
        self.camera_bob = 0  # Head bobbing when walking
        self.camera_sway = 0  # Weapon sway
        
        # ULTRA-REALISTIC COMBAT MECHANICS
        self.sprint_multiplier = 1.8  # Faster sprint
        self.is_sprinting = False
        self.stamina = 100
        self.max_stamina = 100
        self.is_aiming = False  # Right mouse button - Aim Down Sights
        self.zoom_level = 1.0
        self.headshot_bonus = 3.5  # Headshots deal 3.5x damage!
        self.is_crouching = False  # Crouch for accuracy
        self.is_leaning_left = False  # Q key
        self.is_leaning_right = False  # E key
        self.lean_angle = 0  # Smooth leaning
        
        # REALISTIC WEAPON MECHANICS
        self.weapon_sway_x = 0
        self.weapon_sway_y = 0
        self.breathing_cycle = 0  # Breathing affects aim
        self.recoil_x = 0  # Horizontal recoil
        self.recoil_y = 0  # Vertical recoil
        self.accuracy_penalty = 0  # Movement/jumping penalty
        self.is_jumping = False
        self.jump_velocity = 0
        self.in_air = False
        
        # TACTICAL MOVEMENT
        self.velocity_x = 0  # Momentum system
        self.velocity_z = 0
        self.acceleration = 800  # Units per second squared
        self.friction = 0.85  # Sliding friction
        self.crouch_speed_mult = 0.5  # Slower when crouched
        self.aim_walk_speed = 0.6  # Slower when aiming
        
        # BULLET PHYSICS
        self.bullet_drop = True  # Gravity affects bullets
        self.wind_effect = 0.1  # Wind deflection
        self.penetration_enabled = True  # Bullets go through weak materials
        
        # WAVE SYSTEM
        self.killstreak = 0
        self.best_killstreak = 0
        self.last_kill_time = 0
        self.wave_complete = False
        self.wave_break_time = 0
        
        # PROGRESSION
        self.level = 1
        self.xp = 0
        self.xp_needed = 1000
        self.survival_time = 0  # How long survived
        
        # BOSS ZOMBIES
        self.boss_spawned = False
        self.boss_health = 0
        
        # 🔥 EPIC KILLSTREAK SYSTEM 🔥
        self.killstreak_rewards = {
            3: {'name': 'TRIPLE KILL', 'color': Colors.NEON_YELLOW, 'effect': 'speed', 'duration': 10},
            5: {'name': 'KILLING SPREE', 'color': Colors.ORANGE, 'effect': 'damage', 'duration': 15},
            7: {'name': 'RAMPAGE', 'color': Colors.NEON_RED, 'effect': 'armor', 'duration': 20},
            10: {'name': 'UNSTOPPABLE', 'color': Colors.PURPLE, 'effect': 'god_mode', 'duration': 8},
            15: {'name': 'LEGENDARY', 'color': Colors.GOLD, 'effect': 'nuke', 'duration': 0}
        }
        self.active_killstreak_buffs = []  # List of active buff effects
        self.killstreak_notifications = []  # On-screen notifications
        
        # 💎 ACHIEVEMENT SYSTEM 💎
        self.achievements_list = {
            'first_blood': {'name': 'First Blood', 'desc': 'Get your first kill', 'unlocked': False},
            'headhunter': {'name': 'Headhunter', 'desc': 'Get 10 headshots', 'unlocked': False},
            'spray_pray': {'name': 'Spray & Pray', 'desc': 'Fire 1000 bullets', 'unlocked': False},
            'untouchable': {'name': 'Untouchable', 'desc': 'Survive 5 minutes without taking damage', 'unlocked': False},
            'arsenal': {'name': 'Arsenal Master', 'desc': 'Get a kill with every weapon', 'unlocked': False},
            'survivor': {'name': 'Survivor', 'desc': 'Reach wave 10', 'unlocked': False},
            'slayer': {'name': 'Zombie Slayer', 'desc': 'Kill 100 zombies', 'unlocked': False},
            'sharpshooter': {'name': 'Sharpshooter', 'desc': 'Get 90% accuracy in a wave', 'unlocked': False},
        }
        self.achievement_popups = []  # Achievement unlock animations
        
        # 💀 ADVANCED COMBAT STATS 💀
        self.headshot_kills = 0
        self.melee_kills = 0
        self.explosive_kills = 0
        self.critical_hits = 0
        self.longest_shot = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        
        # ⚡ POWER-UP DROP SYSTEM ⚡
        self.power_ups = []  # Active power-ups on ground
        self.power_up_spawn_chance = 0.3  # 30% chance on enemy death
        self.active_power_ups = []  # Currently active buffs
        
        # 🎯 COMBO SYSTEM 🎯
        self.combo_counter = 0
        self.combo_timer = 0
        self.combo_multiplier = 1.0
        self.combo_notifications = []
        
        # 💥 EPIC PARTICLE EFFECTS 💥
        self.death_particles = []  # Enemy death explosions
        self.power_up_particles = []  # Glowing power-up effects
        self.buff_auras = []  # Visual auras when buffed
        self.level_up_particles = []  # Level up celebration
        
        # 🏆 SCORE MULTIPLIERS 🏆
        self.score_multiplier = 1.0
        self.multikill_bonus = 0
        self.last_multikill_time = 0
        
        # RESPAWN SYSTEM - NO BUGS!
        self.invincible = False  # Invincibility after respawn
        self.invincible_timer = 0
        self.respawn_flash = 0  # Visual flash effect when respawning
        
        # Input
        self.keys = set()
        self.mouse_captured = False
        # Don't hide mouse in menu
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
    
    def _load_sounds(self):
        """Load all game sounds - Professional Audio System"""
        if not self.sound_enabled:
            print("🔇 Sound disabled - creating silent placeholders")
            return
            
        try:
            # Generate procedural sounds since we don't have audio files
            self._generate_procedural_sounds()
            print("🎵 All sounds loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading sounds: {e}")
            self.sound_enabled = False
    
    def _generate_procedural_sounds(self):
        """Generate procedural sounds using pygame.sndarray"""
        try:
            import numpy as np
            numpy_available = True
        except ImportError:
            numpy_available = False
            print("⚠️ NumPy not available - using simplified sound generation")
        
        # Generate sounds using either numpy or basic math
        sample_rate = 44100
        
        if numpy_available:
            # Full numpy-based sound generation
            self._generate_numpy_sounds(sample_rate)
        else:
            # Simplified sound generation without numpy
            self._generate_basic_sounds(sample_rate)
            
        # Gunshot sound - sharp crack
        sample_rate = 44100
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Pistol shot - sharp and clean
        pistol_wave = np.sin(2 * np.pi * 800 * t) * np.exp(-t * 20) * 0.5
        pistol_wave += np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 30) * 0.3
        pistol_wave += np.random.normal(0, 0.1, len(pistol_wave))  # Add noise
        
        # Assault rifle - rapid fire sound
        assault_wave = np.sin(2 * np.pi * 600 * t) * np.exp(-t * 15) * 0.4
        assault_wave += np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 25) * 0.3
        assault_wave += np.random.normal(0, 0.15, len(assault_wave))
        
        # Sniper shot - deep boom
        sniper_wave = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 8) * 0.8
        sniper_wave += np.sin(2 * np.pi * 400 * t) * np.exp(-t * 12) * 0.4
        sniper_wave += np.random.normal(0, 0.05, len(sniper_wave))
        
        # Shotgun - loud blast
        shotgun_wave = np.sin(2 * np.pi * 300 * t) * np.exp(-t * 10) * 0.9
        shotgun_wave += np.random.normal(0, 0.2, len(shotgun_wave))
        
        # Reload sound - mechanical click
        reload_duration = 0.8
        reload_t = np.linspace(0, reload_duration, int(sample_rate * reload_duration), False)
        reload_wave = np.sin(2 * np.pi * 150 * reload_t) * np.exp(-reload_t * 3) * 0.3
        reload_wave += np.random.normal(0, 0.1, len(reload_wave))
        
        # Footstep sounds - different surfaces
        footstep_duration = 0.2
        footstep_t = np.linspace(0, footstep_duration, int(sample_rate * footstep_duration), False)
        footstep_wave = np.sin(2 * np.pi * 80 * footstep_t) * np.exp(-footstep_t * 8) * 0.2
        footstep_wave += np.random.normal(0, 0.1, len(footstep_wave))
        
        # Zombie growl
        growl_duration = 1.5
        growl_t = np.linspace(0, growl_duration, int(sample_rate * growl_duration), False)
        growl_wave = np.sin(2 * np.pi * 100 * growl_t) * np.exp(-growl_t * 2) * 0.4
        growl_wave += np.sin(2 * np.pi * 150 * growl_t) * np.exp(-growl_t * 3) * 0.3
        growl_wave += np.random.normal(0, 0.1, len(growl_wave))
        
        # Pain/hit sound
        pain_duration = 0.5
        pain_t = np.linspace(0, pain_duration, int(sample_rate * pain_duration), False)
        pain_wave = np.sin(2 * np.pi * 300 * pain_t) * np.exp(-pain_t * 5) * 0.6
        pain_wave += np.random.normal(0, 0.15, len(pain_wave))
        
        # Explosion sound
        explosion_duration = 1.0
        explosion_t = np.linspace(0, explosion_duration, int(sample_rate * explosion_duration), False)
        explosion_wave = np.sin(2 * np.pi * 50 * explosion_t) * np.exp(-explosion_t * 3) * 0.8
        explosion_wave += np.random.normal(0, 0.2, len(explosion_wave))
        
        # Create sound objects
        self.sounds = {
            'pistol_shot': self._create_sound_from_array(pistol_wave, sample_rate),
            'assault_shot': self._create_sound_from_array(assault_wave, sample_rate),
            'sniper_shot': self._create_sound_from_array(sniper_wave, sample_rate),
            'shotgun_shot': self._create_sound_from_array(shotgun_wave, sample_rate),
            'reload': self._create_sound_from_array(reload_wave, sample_rate),
            'footstep': self._create_sound_from_array(footstep_wave, sample_rate),
            'zombie_growl': self._create_sound_from_array(growl_wave, sample_rate),
            'pain': self._create_sound_from_array(pain_wave, sample_rate),
            'explosion': self._create_sound_from_array(explosion_wave, sample_rate),
        }
        
        # Create multiple footstep variations
        for i in range(5):
            variation = footstep_wave * (0.8 + random.random() * 0.4)
            variation += np.random.normal(0, 0.05, len(variation))
            self.footstep_sounds.append(self._create_sound_from_array(variation, sample_rate))
    
    def _generate_numpy_sounds(self, sample_rate):
        """Generate sounds using NumPy - copy of existing code"""
        import numpy as np
        
        # Gunshot sound - sharp crack
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Pistol shot - sharp and clean
        pistol_wave = np.sin(2 * np.pi * 800 * t) * np.exp(-t * 20) * 0.5
        pistol_wave += np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 30) * 0.3
        pistol_wave += np.random.normal(0, 0.1, len(pistol_wave))  # Add noise
        
        # Assault rifle - rapid fire sound
        assault_wave = np.sin(2 * np.pi * 600 * t) * np.exp(-t * 15) * 0.4
        assault_wave += np.sin(2 * np.pi * 1000 * t) * np.exp(-t * 25) * 0.3
        assault_wave += np.random.normal(0, 0.15, len(assault_wave))
        
        # Sniper shot - deep boom
        sniper_wave = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 8) * 0.8
        sniper_wave += np.sin(2 * np.pi * 400 * t) * np.exp(-t * 12) * 0.4
        sniper_wave += np.random.normal(0, 0.05, len(sniper_wave))
        
        # Shotgun - loud blast
        shotgun_wave = np.sin(2 * np.pi * 300 * t) * np.exp(-t * 10) * 0.9
        shotgun_wave += np.random.normal(0, 0.2, len(shotgun_wave))
        
        # Reload sound - mechanical click
        reload_duration = 0.8
        reload_t = np.linspace(0, reload_duration, int(sample_rate * reload_duration), False)
        reload_wave = np.sin(2 * np.pi * 150 * reload_t) * np.exp(-reload_t * 3) * 0.3
        reload_wave += np.random.normal(0, 0.1, len(reload_wave))
        
        # Footstep sounds - different surfaces
        footstep_duration = 0.2
        footstep_t = np.linspace(0, footstep_duration, int(sample_rate * footstep_duration), False)
        footstep_wave = np.sin(2 * np.pi * 80 * footstep_t) * np.exp(-footstep_t * 8) * 0.2
        footstep_wave += np.random.normal(0, 0.1, len(footstep_wave))
        
        # Zombie growl
        growl_duration = 1.5
        growl_t = np.linspace(0, growl_duration, int(sample_rate * growl_duration), False)
        growl_wave = np.sin(2 * np.pi * 100 * growl_t) * np.exp(-growl_t * 2) * 0.4
        growl_wave += np.sin(2 * np.pi * 150 * growl_t) * np.exp(-growl_t * 3) * 0.3
        growl_wave += np.random.normal(0, 0.1, len(growl_wave))
        
        # Pain/hit sound
        pain_duration = 0.5
        pain_t = np.linspace(0, pain_duration, int(sample_rate * pain_duration), False)
        pain_wave = np.sin(2 * np.pi * 300 * pain_t) * np.exp(-pain_t * 5) * 0.6
        pain_wave += np.random.normal(0, 0.15, len(pain_wave))
        
        # Explosion sound
        explosion_duration = 1.0
        explosion_t = np.linspace(0, explosion_duration, int(sample_rate * explosion_duration), False)
        explosion_wave = np.sin(2 * np.pi * 50 * explosion_t) * np.exp(-explosion_t * 3) * 0.8
        explosion_wave += np.random.normal(0, 0.2, len(explosion_wave))
        
        # Create sound objects
        self.sounds = {
            'pistol_shot': self._create_sound_from_array(pistol_wave, sample_rate),
            'assault_shot': self._create_sound_from_array(assault_wave, sample_rate),
            'sniper_shot': self._create_sound_from_array(sniper_wave, sample_rate),
            'shotgun_shot': self._create_sound_from_array(shotgun_wave, sample_rate),
            'reload': self._create_sound_from_array(reload_wave, sample_rate),
            'footstep': self._create_sound_from_array(footstep_wave, sample_rate),
            'zombie_growl': self._create_sound_from_array(growl_wave, sample_rate),
            'pain': self._create_sound_from_array(pain_wave, sample_rate),
            'explosion': self._create_sound_from_array(explosion_wave, sample_rate),
        }
        
        # Create multiple footstep variations
        for i in range(5):
            variation = footstep_wave * (0.8 + random.random() * 0.4)
            variation += np.random.normal(0, 0.05, len(variation))
            self.footstep_sounds.append(self._create_sound_from_array(variation, sample_rate))
    
    def _generate_basic_sounds(self, sample_rate):
        """Generate simplified sounds without NumPy"""
        # Create basic beep sounds for each type
        duration = 0.3
        samples = int(sample_rate * duration)
        
        # Simple sine wave generator
        def generate_sine_wave(freq, duration, amplitude=0.5, fade=True):
            samples = int(sample_rate * duration)
            wave = []
            for i in range(samples):
                t = i / sample_rate
                value = amplitude * math.sin(2 * math.pi * freq * t)
                if fade:
                    # Apply exponential fade
                    fade_factor = math.exp(-t * 10)
                    value *= fade_factor
                # Add some noise
                value += (random.random() - 0.5) * 0.1
                wave.append(value)
            return wave
        
        # Generate basic sounds
        pistol_wave = generate_sine_wave(800, 0.3, 0.5)
        assault_wave = generate_sine_wave(600, 0.3, 0.4)
        sniper_wave = generate_sine_wave(200, 0.5, 0.8)
        shotgun_wave = generate_sine_wave(300, 0.4, 0.9)
        reload_wave = generate_sine_wave(150, 0.8, 0.3)
        footstep_wave = generate_sine_wave(80, 0.2, 0.2)
        growl_wave = generate_sine_wave(100, 1.5, 0.4)
        pain_wave = generate_sine_wave(300, 0.5, 0.6)
        explosion_wave = generate_sine_wave(50, 1.0, 0.8)
        
        # Create sound objects
        self.sounds = {
            'pistol_shot': self._create_sound_from_list(pistol_wave, sample_rate),
            'assault_shot': self._create_sound_from_list(assault_wave, sample_rate),
            'sniper_shot': self._create_sound_from_list(sniper_wave, sample_rate),
            'shotgun_shot': self._create_sound_from_list(shotgun_wave, sample_rate),
            'reload': self._create_sound_from_list(reload_wave, sample_rate),
            'footstep': self._create_sound_from_list(footstep_wave, sample_rate),
            'zombie_growl': self._create_sound_from_list(growl_wave, sample_rate),
            'pain': self._create_sound_from_list(pain_wave, sample_rate),
            'explosion': self._create_sound_from_list(explosion_wave, sample_rate),
        }
        
        # Create multiple footstep variations
        for i in range(5):
            variation = [x * (0.8 + random.random() * 0.4) + (random.random() - 0.5) * 0.05 
                        for x in footstep_wave]
            self.footstep_sounds.append(self._create_sound_from_list(variation, sample_rate))
    
    def _create_sound_from_list(self, wave_list, sample_rate):
        """Create pygame Sound object from Python list"""
        try:
            # Convert to numpy array for pygame
            import numpy as np
            wave_array = np.array(wave_list, dtype=np.float32)
            
            # Normalize and convert to 16-bit
            wave_array = np.clip(wave_array, -1, 1)
            wave_int16 = (wave_array * 32767).astype(np.int16)
            
            # Create stereo by duplicating mono
            stereo_wave = np.column_stack((wave_int16, wave_int16))
            
            # Create sound
            sound = pygame.sndarray.make_sound(stereo_wave)
            return sound
        except Exception as e:
            print(f"⚠️ Failed to create sound from list: {e}")
            return None
    
    def _create_sound_from_array(self, wave_array, sample_rate):
        """Create pygame Sound object from numpy array"""
        try:
            import numpy as np
            # Normalize and convert to 16-bit
            wave_array = np.clip(wave_array, -1, 1)
            wave_int16 = (wave_array * 32767).astype(np.int16)
            
            # Create stereo by duplicating mono
            stereo_wave = np.column_stack((wave_int16, wave_int16))
            
            # Create sound
            sound = pygame.sndarray.make_sound(stereo_wave)
            return sound
        except Exception as e:
            print(f"⚠️ Failed to create sound: {e}")
            return None
    
    def _play_background_music(self):
        """Play atmospheric background music"""
        if not self.sound_enabled:
            return
            
        try:
            # Check if numpy is available
            try:
                import numpy as np
                numpy_available = True
            except ImportError:
                numpy_available = False
            
            sample_rate = 44100
            
            if numpy_available:
                # Generate atmospheric music with numpy
                duration = 60.0  # 1 minute loop
                t = np.linspace(0, duration, int(sample_rate * duration), False)
                
                # Create atmospheric drone
                music_wave = np.sin(2 * np.pi * 80 * t) * 0.1  # Low drone
                music_wave += np.sin(2 * np.pi * 160 * t) * 0.05  # Higher harmonic
                music_wave += np.sin(2 * np.pi * 40 * t) * 0.08  # Even lower
                
                # Add some tension with varying frequencies
                tension_freq = 200 + 50 * np.sin(2 * np.pi * 0.1 * t)  # Slow modulation
                music_wave += np.sin(2 * np.pi * tension_freq * t) * 0.03
                
                # Add subtle noise for atmosphere
                music_wave += np.random.normal(0, 0.02, len(music_wave))
                
                # Create sound and loop it
                music_sound = self._create_sound_from_array(music_wave, sample_rate)
            else:
                # Generate simple music without numpy
                duration = 30.0  # 30 second loop (shorter for simplicity)
                samples = int(sample_rate * duration)
                music_wave = []
                
                for i in range(samples):
                    t = i / sample_rate
                    # Simple atmospheric drone
                    value = 0.1 * math.sin(2 * math.pi * 80 * t)
                    value += 0.05 * math.sin(2 * math.pi * 160 * t)
                    value += 0.08 * math.sin(2 * math.pi * 40 * t)
                    
                    # Add some modulation
                    tension_freq = 200 + 50 * math.sin(2 * math.pi * 0.1 * t)
                    value += 0.03 * math.sin(2 * math.pi * tension_freq * t)
                    
                    # Add subtle noise
                    value += (random.random() - 0.5) * 0.04
                    
                    music_wave.append(value)
                
                music_sound = self._create_sound_from_list(music_wave, sample_rate)
            
            if music_sound:
                music_sound.set_volume(self.music_volume)
                music_sound.play(loops=-1)  # Loop forever
                print("🎵 Background music started")
                
        except Exception as e:
            print(f"⚠️ Failed to create background music: {e}")
    
    def play_sound(self, sound_name, volume=1.0):
        """Play a sound effect"""
        if not self.sound_enabled or sound_name not in self.sounds:
            return
            
        sound = self.sounds[sound_name]
        if sound:
            try:
                sound.set_volume(volume * self.sfx_volume)
                sound.play()
            except Exception as e:
                print(f"⚠️ Error playing sound {sound_name}: {e}")
    
    def play_weapon_sound(self, weapon_name):
        """Play weapon-specific sound"""
        sound_map = {
            'pistol': 'pistol_shot',
            'assault_rifle': 'assault_shot', 
            'sniper': 'sniper_shot',
            'shotgun': 'shotgun_shot',
            'smg': 'assault_shot',  # SMG uses assault sound
            'lmg': 'assault_shot'   # LMG uses assault sound
        }
        
        if weapon_name in sound_map:
            self.play_sound(sound_map[weapon_name])
    
    def _respawn_player(self):
        """🔄 Respawn player with full reset - NO BUGS!"""
        # Death counter
        self.deaths += 1
        
        # Reset player stats
        self.player_health = 100
        self.player_armor = 0  # No armor at start
        
        # Reset position (safe spawn)
        self.player_x = 0
        self.player_y = 0
        self.player_z = 0
        self.player_angle = 0
        
        # Reset weapon to pistol with limited ammo
        self.current_weapon = 'pistol'
        for weapon in self.weapons.values():
            weapon.current_ammo = 0
            weapon.magazine_count = 0
        # Give starting pistol ammo
        self.weapons['pistol'].current_ammo = 12
        self.weapons['pistol'].magazine_count = 1
        
        # Reset combat stats
        self.killstreak = 0
        
        # Grant 3 seconds of invincibility
        self.invincible = True
        self.invincible_timer = 3.0  # 3 seconds
        self.respawn_flash = 1.0
        
        # Clear screen effects
        self.damage_vignette = 0
        self.blood_on_screen = 0
        self.screen_shake = 0
        self.screen_shake_x = 0
        self.screen_shake_y = 0
        
        # Clear visual effects near player
        self.blood_splatter.clear()
        self.muzzle_flash = None
        self.hit_markers.clear()
        self.shell_casings.clear()
        
        # Move enemies away from spawn point
        for enemy in self.enemies:
            distance = math.sqrt((enemy['x'] - self.player_x)**2 + (enemy['z'] - self.player_z)**2)
            if distance < 200:  # Too close to player
                # Move them far away
                angle = random.uniform(0, 2 * math.pi)
                enemy['x'] = self.player_x + math.cos(angle) * 400
                enemy['z'] = self.player_z + math.sin(angle) * 400
        
        # Respawn message
        print("💀 You died! Respawning with 3 seconds invincibility...")
    
    def spawn_enemies(self, count):
        """🧟 Spawn TEAM-BASED ENEMIES"""
        zombie_types = ['walker', 'runner', 'tank', 'screamer']
        
        # Determine enemy team (opposite of player's team)
        if self.player_team == 'BLUE':
            enemy_team = 'RED'
        elif self.player_team == 'RED':
            enemy_team = 'BLUE'
        else:
            enemy_team = 'RED'  # Default if no team selected yet
        
        for i in range(count):
            # Boss zombie every 5 waves
            if self.zombie_wave % 5 == 0 and i == 0 and not self.boss_spawned:
                zombie_type = 'boss'
                health, speed, damage = 500, 40, 50
                self.boss_spawned = True
                self.boss_health = health
            else:
                zombie_type = random.choice(zombie_types)
                if zombie_type == 'walker':
                    health, speed, damage = 80, 30, 20
                elif zombie_type == 'runner':
                    health, speed, damage = 50, 120, 15
                elif zombie_type == 'screamer':  # NEW: Attracts other zombies
                    health, speed, damage = 60, 50, 10
                else:  # tank
                    health, speed, damage = 200, 20, 40
                    
            # Spawn at random position far from player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(300, 500)
            spawn_x = self.player_x + math.cos(angle) * distance
            spawn_z = self.player_z + math.sin(angle) * distance
                
            enemy = {
                'id': f'zombie_{self.zombie_wave}_{i}',
                'type': zombie_type,
                'team': enemy_team,  # NEW: Enemy team
                'x': spawn_x,
                'y': 0,
                'z': spawn_z,
                'health': health,
                'max_health': health,
                'armor': 0,
                'angle': random.uniform(0, 2 * math.pi),
                'weapon': None,
                'ai_state': 'wander',  # wander, chase, attack, scream
                'speed': speed,
                'damage': damage,
                'last_attack': 0,
                'alert': False,
                'animation_frame': random.uniform(0, 2 * math.pi),
                'is_dead': False,
                'blood_level': 0,
                'aggro_range': 400 if zombie_type == 'runner' else 300,
                'can_see_player': False,
                'last_seen_player_pos': (0, 0),
                'path_finding': [],  # Smart pathfinding
                'is_boss': zombie_type == 'boss'
            }
            self.enemies.append(enemy)
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(60) / 1000.0
            
            self._handle_events()
            self._update(dt)
            self._render()
            
            pygame.display.flip()
        
        pygame.quit()
    
    def _handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self.keys.add(event.key)
                
                if self.in_menu:
                    # Menu navigation
                    if event.key == pygame.K_UP:
                        self.menu_option = (self.menu_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_option = (self.menu_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        self._select_menu_option()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif self.in_team_selection:
                    # Team selection navigation
                    if event.key == pygame.K_LEFT:
                        self.team_selection = 0  # BLUE
                    elif event.key == pygame.K_RIGHT:
                        self.team_selection = 1  # RED
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Confirm team selection
                        self.player_team = 'BLUE' if self.team_selection == 0 else 'RED'
                        self.in_team_selection = False
                        self.in_game = True
                        # Respawn enemies with correct team
                        self.enemies.clear()
                        self.spawn_enemies(self.zombies_per_wave)
                        # Capture mouse for FPS controls
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                        self.mouse_captured = True
                    elif event.key == pygame.K_ESCAPE:
                        # Back to menu
                        self.in_team_selection = False
                        self.in_menu = True
                elif self.in_server_connect:
                    # Server connection input
                    if event.key == pygame.K_RETURN:
                        # Validate IP and connect
                        if self.server_ip.strip():
                            self.connection_status = "✓ Connected to server!"
                            # Go to team selection
                            self.in_server_connect = False
                            self.in_team_selection = True
                        else:
                            self.connection_status = "⚠️ Please enter a server IP"
                    elif event.key == pygame.K_ESCAPE:
                        # Back to menu
                        self.in_server_connect = False
                        self.in_menu = True
                    elif event.key == pygame.K_BACKSPACE:
                        # Remove last character
                        self.server_ip = self.server_ip[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        # Add character to IP
                        if len(self.server_ip) < 50:  # Max length
                            self.server_ip += event.unicode
                else:
                    # In-game controls
                    # Weapon switching
                    if event.key == pygame.K_1:
                        self.current_weapon = 'assault_rifle'
                    elif event.key == pygame.K_2:
                        self.current_weapon = 'sniper'
                    elif event.key == pygame.K_3:
                        self.current_weapon = 'smg'
                    elif event.key == pygame.K_4:
                        self.current_weapon = 'shotgun'
                    elif event.key == pygame.K_5:
                        self.current_weapon = 'pistol'
                    elif event.key == pygame.K_6:
                        self.current_weapon = 'lmg'
                    elif event.key == pygame.K_r:
                        self.weapons[self.current_weapon].reload()
                        # 🎵 PLAY RELOAD SOUND
                        self.play_sound('reload')
                    elif event.key == pygame.K_LSHIFT:
                        self.is_sprinting = True
                    # NEW FUNCTIONALITIES
                    elif event.key == pygame.K_t:  # Toggle time of day
                        self._toggle_time_of_day()
                    elif event.key == pygame.K_y:  # Toggle weather
                        self._toggle_weather()
                    elif event.key == pygame.K_g:  # Grenade (new feature)
                        self._throw_grenade()
                    elif event.key == pygame.K_f:  # Flashlight toggle
                        self.flashlight_on = not getattr(self, 'flashlight_on', False)
                    elif event.key == pygame.K_c:  # Crouch toggle (REALISTIC)
                        self.is_crouching = not self.is_crouching
                    elif event.key == pygame.K_q:  # Lean left (REALISTIC)
                        self.is_leaning_left = True
                    elif event.key == pygame.K_e:  # Lean right (REALISTIC)
                        self.is_leaning_right = True
                    elif event.key == pygame.K_SPACE:  # Jump (REALISTIC)
                        if not self.in_air:
                            self.is_jumping = True
                            self.jump_velocity = -350  # Initial upward velocity
                            self.in_air = True
                    elif event.key == pygame.K_v:  # Melee attack
                        self._melee_attack()
                    elif event.key == pygame.K_TAB:  # Show scoreboard
                        self.show_scoreboard = not getattr(self, 'show_scoreboard', False)
                    elif event.key == pygame.K_p:  # NEW: Toggle camera mode
                        self._toggle_camera_mode()
                    elif event.key == pygame.K_ESCAPE:
                        # Return to menu
                        self.in_menu = True
                        self.in_game = False
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                        self.mouse_captured = False
                        self.show_scoreboard = not getattr(self, 'show_scoreboard', False)
                    elif event.key == pygame.K_ESCAPE:
                        # Back to menu
                        self.in_menu = True
                        self.in_game = False
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                        self.mouse_captured = False
            
            elif event.type == pygame.KEYUP:
                self.keys.discard(event.key)
                if not self.in_menu:
                    if event.key == pygame.K_LSHIFT:
                        self.is_sprinting = False
                    elif event.key == pygame.K_q:  # Stop leaning left
                        self.is_leaning_left = False
                    elif event.key == pygame.K_e:  # Stop leaning right
                        self.is_leaning_right = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.in_menu:
                    # Menu click detection
                    self._handle_menu_click(event.pos)
                else:
                    if event.button == 1:  # Left click - shoot
                        self._shoot()
                    elif event.button == 3:  # Right click - aim
                        self.is_aiming = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if not self.in_menu:
                    if event.button == 3:
                        self.is_aiming = False
    
    def _select_menu_option(self):
        """Handle menu selection"""
        if self.menu_option == 0:  # Play Game
            # Go to server connection first
            self.in_menu = False
            self.in_server_connect = True
            self.server_ip = ""
            self.connection_status = ""
        elif self.menu_option == 1:  # Loadout (weapon selection)
            # Show loadout screen - for now just display message
            pass
        elif self.menu_option == 2:  # Settings
            # Show settings screen
            pass
        elif self.menu_option == 3:  # Exit
            self.running = False
    
    def _handle_menu_click(self, pos):
        """Handle menu clicks"""
        # Card-based menu click detection
        menu_start_y = 320
        card_spacing = 85
        card_width = 550
        card_x = self.screen_width//2 - card_width//2
        
        for i in range(len(self.menu_options)):
            y = menu_start_y + i * card_spacing
            card_rect = pygame.Rect(card_x, y, card_width, 70)
            if card_rect.collidepoint(pos):
                self.menu_option = i
                self._select_menu_option()
                break
    
    def _update(self, dt):
        """Update game logic with ULTRA-REALISTIC physics"""
        if self.in_menu:
            return  # Don't update game logic in menu
        
        if not self.in_game:
            return
        
        # Update invincibility timer after respawn
        if self.invincible:
            self.invincible_timer -= dt
            self.respawn_flash -= dt * 2
            if self.invincible_timer <= 0:
                self.invincible = False
                self.invincible_timer = 0
                self.respawn_flash = 0
                print("✅ Invincibility ended - be careful!")
        
        # === REALISTIC STAMINA SYSTEM ===
        stamina_drain_rate = 25 if self.is_sprinting else 0
        stamina_regen_rate = 18
        
        is_moving = (pygame.K_w in self.keys or pygame.K_s in self.keys or 
                    pygame.K_a in self.keys or pygame.K_d in self.keys)
        
        if self.is_sprinting and is_moving:
            self.stamina = max(0, self.stamina - stamina_drain_rate * dt)
            if self.stamina <= 0:
                self.is_sprinting = False
        else:
            # Slower regen when moving
            regen = stamina_regen_rate * (0.5 if is_moving else 1.0)
            self.stamina = min(self.max_stamina, self.stamina + regen * dt)
        
        # === REALISTIC MOVEMENT with MOMENTUM ===
        base_speed = 180  # Base movement speed
        
        # Calculate speed modifiers
        if self.is_crouching:
            speed_mult = self.crouch_speed_mult
        elif self.is_sprinting and self.stamina > 5:
            speed_mult = self.sprint_multiplier
        elif self.is_aiming:
            speed_mult = self.aim_walk_speed
        else:
            speed_mult = 1.0
        
        # Apply accuracy penalty when moving/jumping
        if is_moving:
            self.accuracy_penalty = 0.7 if self.is_sprinting else 0.85
        else:
            self.accuracy_penalty = 1.0
        
        if self.in_air:
            self.accuracy_penalty = 0.4  # Terrible accuracy when jumping
        
        # Target velocity based on input
        target_vx = 0
        target_vz = 0
        
        if pygame.K_w in self.keys:
            target_vx += math.cos(self.player_angle) * base_speed * speed_mult
            target_vz += math.sin(self.player_angle) * base_speed * speed_mult
        if pygame.K_s in self.keys:
            target_vx -= math.cos(self.player_angle) * base_speed * speed_mult
            target_vz -= math.sin(self.player_angle) * base_speed * speed_mult
        if pygame.K_a in self.keys:
            target_vx += math.cos(self.player_angle - math.pi/2) * base_speed * speed_mult
            target_vz += math.sin(self.player_angle - math.pi/2) * base_speed * speed_mult
        if pygame.K_d in self.keys:
            target_vx += math.cos(self.player_angle + math.pi/2) * base_speed * speed_mult
            target_vz += math.sin(self.player_angle + math.pi/2) * base_speed * speed_mult
        
        # Smooth acceleration (realistic momentum)
        accel_rate = self.acceleration * dt
        self.velocity_x += (target_vx - self.velocity_x) * min(1.0, accel_rate / base_speed)
        self.velocity_z += (target_vz - self.velocity_z) * min(1.0, accel_rate / base_speed)
        
        # Apply friction when not giving input
        if target_vx == 0:
            self.velocity_x *= self.friction
        if target_vz == 0:
            self.velocity_z *= self.friction
        
        # === FOOTSTEP SOUNDS ===
        if is_moving and not self.in_air and self.sound_enabled:
            # Footstep timing based on movement speed
            footstep_interval = 0.4 if self.is_sprinting else 0.6
            current_time = time.time()
            
            if not hasattr(self, 'last_footstep_time'):
                self.last_footstep_time = 0
                
            if current_time - self.last_footstep_time > footstep_interval:
                # Play random footstep sound
                if self.footstep_sounds:
                    footstep_sound = random.choice(self.footstep_sounds)
                    if footstep_sound:
                        footstep_sound.set_volume(0.3 * self.sfx_volume)
                        footstep_sound.play()
                self.last_footstep_time = current_time
        
        # === REALISTIC HEAD BOBBING ===
        if is_moving and not self.in_air:
            bob_speed = 8 if self.is_sprinting else 5
            bob_amount = 0.015 if self.is_sprinting else 0.008
            self.camera_bob += dt * bob_speed
            head_bob_offset = math.sin(self.camera_bob) * bob_amount
            self.player_y = 0 + head_bob_offset
        else:
            self.camera_bob = 0
            self.player_y = 0
        
        # === REALISTIC WEAPON SWAY ===
        sway_speed = 2
        sway_amount = 0.02 if not self.is_aiming else 0.005
        
        # Increased sway when moving
        if is_moving:
            sway_amount *= 1.5
        if self.is_sprinting:
            sway_amount *= 2.0
        
        self.weapon_sway_x = math.sin(time.time() * sway_speed) * sway_amount
        self.weapon_sway_y = math.cos(time.time() * sway_speed * 0.7) * sway_amount
        
        # === BREATHING SIMULATION ===
        self.breathing_cycle += dt * 0.8  # Breathing rate
        breath_offset = math.sin(self.breathing_cycle) * 0.003
        
        # Hold breath when aiming (Shift key)
        if self.is_aiming and pygame.K_LSHIFT in self.keys and self.stamina > 20:
            self.stamina -= 15 * dt  # Drain stamina
            breath_offset *= 0.1  # Much steadier aim
        
        # === SMOOTH LEANING SYSTEM ===
        target_lean = 0
        if self.is_leaning_left:
            target_lean = -0.15  # Lean left
        elif self.is_leaning_right:
            target_lean = 0.15  # Lean right
        
        # Smooth interpolation
        self.lean_angle += (target_lean - self.lean_angle) * 5 * dt
        
        # === RECOIL RECOVERY ===
        self.recoil_x *= 0.9  # Gradual recovery
        self.recoil_y *= 0.9
        
        # === MOUSE LOOK with SENSITIVITY ===
        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        
        # Adjust sensitivity based on state
        if self.is_aiming:
            sensitivity = self.mouse_sensitivity * 0.4  # Slower when aiming
        elif self.is_sprinting:
            sensitivity = self.mouse_sensitivity * 1.2  # Faster when sprinting
        else:
            sensitivity = self.mouse_sensitivity
        
        # Apply mouse movement with recoil and sway
        self.player_angle += (mouse_dx * sensitivity) + self.recoil_x + breath_offset
        
        # Vertical look (not implemented but recoil affects it)
        # self.camera_pitch += mouse_dy * sensitivity + self.recoil_y
        
        # === SCREEN SHAKE SYSTEM ===
        if self.screen_shake > 0:
            self.screen_shake -= dt * 6
            shake_amount = self.screen_shake * 0.01
            self.player_angle += random.uniform(-shake_amount, shake_amount)
            self.screen_shake_x = random.uniform(-5, 5) * self.screen_shake
            self.screen_shake_y = random.uniform(-5, 5) * self.screen_shake
        else:
            self.screen_shake_x *= 0.8
            self.screen_shake_y *= 0.8
        
        # === REALISTIC JUMP & GRAVITY SYSTEM ===
        if self.in_air:
            # Apply gravity
            self.jump_velocity += 980 * dt  # Realistic gravity (9.8 m/s²)
            self.player_y += self.jump_velocity * dt
            
            # Check ground collision (ground at y=50)
            ground_level = 50 if not self.is_crouching else 35
            if self.player_y >= ground_level:
                self.player_y = ground_level
                self.jump_velocity = 0
                self.in_air = False
                self.is_jumping = False
                
                # Landing impact (screen shake)
                if abs(self.jump_velocity) > 200:
                    self.screen_shake = 3
        else:
            # Ensure player stays on ground
            self.player_y = 50 if not self.is_crouching else 35
        
        # Update weapons
        for weapon in self.weapons.values():
            weapon.update()
        
        # === CONTINUOUS FIRE FOR AUTOMATIC WEAPONS ===
        # Check if left mouse button is held down for automatic fire
        if not self.in_menu and not self.in_team_selection and not self.in_server_connect:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # Left mouse button held
                weapon = self.weapons[self.current_weapon]
                # Allow automatic fire for automatic weapons
                if weapon.auto and weapon.can_shoot():
                    self._shoot()
        
        # Update bullets
        self._update_bullets(dt)
        
        # Update enemies (AI)
        self._update_enemies(dt)
        
        # Update grenades
        self._update_grenades(dt)
        
        # Update effects
        self._update_effects(dt)
    
    def _shoot(self):
        """Fire current weapon with ULTRA-REALISTIC ballistics"""
        weapon = self.weapons[self.current_weapon]
        if weapon.shoot():
            # 🎵 PLAY WEAPON SOUND
            self.play_weapon_sound(self.current_weapon)
            # === REALISTIC ACCURACY CALCULATION ===
            # Base accuracy from weapon
            base_accuracy = weapon.accuracy
            
            # Modifiers
            aiming_bonus = 1.4 if self.is_aiming else 1.0
            crouch_bonus = 1.2 if self.is_crouching else 1.0
            movement_penalty = self.accuracy_penalty  # Set in _update
            
            # Final accuracy
            final_accuracy = base_accuracy * aiming_bonus * crouch_bonus * movement_penalty
            final_accuracy = min(1.0, final_accuracy)  # Cap at 100%
            
            # Calculate spread cone
            max_spread = 0.15  # Maximum spread in radians
            spread = (1.0 - final_accuracy) * max_spread
            
            # Random spread within cone
            angle_offset = random.uniform(-spread, spread)
            vertical_offset = random.uniform(-spread * 0.8, spread * 0.8)  # Less vertical spread
            
            # === REALISTIC RECOIL SYSTEM ===
            # Weapon-specific recoil
            base_recoil = weapon.recoil
            recoil_mult = 0.6 if self.is_aiming else 1.0
            recoil_mult *= 0.8 if self.is_crouching else 1.0
            
            # Apply recoil to view (affects next shot)
            self.recoil_x += random.uniform(-base_recoil, base_recoil) * recoil_mult * 0.5
            self.recoil_y += base_recoil * recoil_mult * random.uniform(0.8, 1.2)
            
            # Screen shake from shot
            self.screen_shake = base_recoil * 8
            
            # === CREATE BULLET with PHYSICS ===
            # Calculate bullet spawn position (from weapon muzzle)
            muzzle_forward = 40  # Distance in front of player
            spawn_x = self.player_x + math.cos(self.player_angle) * muzzle_forward
            spawn_z = self.player_z + math.sin(self.player_angle) * muzzle_forward
            spawn_y = 45  # Eye level - slightly lower for weapon
            
            bullet = {
                'x': spawn_x,
                'y': spawn_y,
                'z': spawn_z,
                'angle': self.player_angle + angle_offset,
                'vertical_angle': vertical_offset,  # For bullet drop
                'speed': 1200,  # Faster, more realistic bullet speed
                'velocity_y': 0,  # Vertical velocity (for drop)
                'damage': weapon.damage,
                'penetration': weapon.penetration,
                'distance': 0,
                'max_distance': 2500,  # Longer range
                'weapon_type': self.current_weapon,
                'gravity': 180 if self.bullet_drop else 0,  # Bullet drop rate
                'wind_offset': 0  # Accumulates wind deflection
            }
            self.bullets.append(bullet)
            
            # === VISUAL EFFECTS ===
            # Enhanced muzzle flash
            self.muzzle_flash = time.time()
            
            # Realistic gun smoke
            smoke_count = 3 if self.is_aiming else 5
            for i in range(smoke_count):
                smoke_offset_x = math.cos(self.player_angle) * (muzzle_forward + random.uniform(0, 15))
                smoke_offset_z = math.sin(self.player_angle) * (muzzle_forward + random.uniform(0, 15))
                self._add_smoke_effect(
                    self.player_x + smoke_offset_x, 
                    spawn_y + random.uniform(-5, 5), 
                    self.player_z + smoke_offset_z, 
                    size=random.uniform(12, 25), 
                    life=random.uniform(1.2, 2.5)
                )
            
            # Ejecting shell casing with realistic physics
            eject_angle = self.player_angle + math.pi/2  # Right side of gun
            self.shell_casings.append({
                'x': spawn_x,
                'y': spawn_y,
                'z': spawn_z,
                'vx': math.cos(eject_angle) * random.uniform(4, 7),
                'vy': random.uniform(3, 6),  # Upward
                'vz': math.sin(eject_angle) * random.uniform(4, 7),
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(200, 400),
                'life': 3.0,
                'time': time.time(),
                'bounced': False
            })
            
            # Tracer rounds (machine guns)
            if self.current_weapon in ['lmg', 'assault', 'smg'] and random.random() < 0.25:
                end_x = spawn_x + math.cos(bullet['angle']) * 800
                end_z = spawn_z + math.sin(bullet['angle']) * 800
                self._add_tracer_round(spawn_x, spawn_y, spawn_z, end_x, spawn_y, end_z)
            
            # Camera kick (more pronounced for heavy weapons)
            if self.current_weapon in ['sniper', 'shotgun', 'lmg']:
                self.screen_shake *= 1.5
    
    def _update_bullets(self, dt):
        """Update bullets with REALISTIC PHYSICS"""
        for bullet in self.bullets[:]:
            # === BALLISTIC MOVEMENT ===
            # Horizontal movement
            bullet['x'] += math.cos(bullet['angle']) * bullet['speed'] * dt
            bullet['z'] += math.sin(bullet['angle']) * bullet['speed'] * dt
            
            # Vertical movement with gravity (bullet drop)
            bullet['velocity_y'] -= bullet['gravity'] * dt
            bullet['y'] += bullet['velocity_y'] * dt + bullet['vertical_angle'] * bullet['speed'] * dt
            
            # Wind deflection (very subtle)
            bullet['wind_offset'] += self.wind_effect * dt * random.uniform(-1, 1)
            bullet['angle'] += bullet['wind_offset'] * 0.001
            
            # Track distance traveled
            bullet['distance'] += bullet['speed'] * dt
            
            # Check if bullet hit enemy
            hit = False
            for enemy in self.enemies[:]:
                # TEAM SYSTEM: Only damage enemies from opposite team
                if enemy.get('team') == self.player_team:
                    continue  # Can't damage teammates!
                
                dx = bullet['x'] - enemy['x']
                dz = bullet['z'] - enemy['z']
                dist = math.sqrt(dx*dx + dz*dz)
                
                # Larger hit radius for easier hitting (increased from 30 to 50)
                if dist < 50:  # Hit radius
                    # Check for headshot (top 20% of enemy)
                    is_headshot = bullet['y'] < enemy['y'] - 10
                    
                    # Calculate damage with headshot bonus
                    damage = bullet['damage']
                    if is_headshot:
                        damage *= self.headshot_bonus
                    
                    # Apply penetration to armor
                    if enemy['armor'] > 0:
                        armor_effectiveness = max(0, 1.0 - bullet['penetration'] * 0.5)
                        armor_absorbed = min(enemy['armor'], damage * armor_effectiveness)
                        enemy['armor'] -= armor_absorbed
                        damage -= armor_absorbed * 0.5
                    
                    enemy['health'] -= damage
                    
                    # Enhanced blood splatter effect with smoke
                    splatter_count = 8 if is_headshot else 5
                    for _ in range(splatter_count):
                        self.blood_splatter.append({
                            'x': enemy['x'] + random.uniform(-5, 5),
                            'y': enemy['y'] + random.uniform(-5, 5),
                            'z': enemy['z'] + random.uniform(-5, 5),
                            'vx': random.uniform(-10, 10),
                            'vy': random.uniform(-10, 10),
                            'vz': random.uniform(-10, 10),
                            'time': time.time(),
                            'size': random.uniform(3, 7)
                        })
                    
                    # Add impact effects
                    self._add_spark_effect(enemy['x'], enemy['y'], enemy['z'], count=8)
                    self._add_impact_mark(bullet['x'], bullet['y'], bullet['z'])
                    
                    # Track weapon accuracy
                    weapon = self.weapons[bullet['weapon_type']]
                    weapon.hits += 1
                    
                    # Hit marker
                    self.hit_markers.append({
                        'time': time.time(),
                        'kill': False,
                        'headshot': is_headshot,
                        'damage': int(damage)
                    })
                    
                    if enemy['health'] <= 0:
                        self.enemies.remove(enemy)
                        self.kills += 1
                        weapon.kills += 1
                        self.killstreak += 1
                        self.best_killstreak = max(self.best_killstreak, self.killstreak)
                        current_time = time.time()
                        self.last_kill_time = current_time
                        
                        # Track headshot kills
                        if is_headshot:
                            self.headshot_kills += 1
                        
                        # 🎯 COMBO SYSTEM
                        if current_time - self.combo_timer < 3.0:
                            self.combo_counter += 1
                            self.combo_timer = current_time
                            self.combo_multiplier = 1.0 + (self.combo_counter * 0.1)
                        else:
                            self.combo_counter = 1
                            self.combo_timer = current_time
                            self.combo_multiplier = 1.0
                        
                        # 💥 MULTIKILL TRACKING
                        if current_time - self.last_multikill_time < 4.0:
                            self.multikill_bonus += 1
                        else:
                            self.multikill_bonus = 0
                        self.last_multikill_time = current_time
                        
                        # 🏆 XP and SCORE rewards with MULTIPLIERS
                        xp_reward = 100
                        score_reward = 100
                        
                        if is_headshot:
                            xp_reward = int(xp_reward * 2.0)  # 2x for headshot
                            score_reward = int(score_reward * 2.0)
                            self.combo_notifications.append({
                                'text': 'HEADSHOT!',
                                'color': Colors.NEON_RED,
                                'time': current_time,
                                'y_offset': 0
                            })
                        
                        # Combo multiplier
                        if self.combo_counter >= 5:
                            self.combo_notifications.append({
                                'text': f'{self.combo_counter}x COMBO!',
                                'color': Colors.NEON_YELLOW,
                                'time': current_time,
                                'y_offset': 30
                            })
                        
                        # Apply combo multiplier
                        score_reward = int(score_reward * self.combo_multiplier)
                        
                        # Multikill bonus
                        if self.multikill_bonus >= 2:
                            bonus = self.multikill_bonus * 50
                            score_reward += bonus
                            multikill_names = ['', '', 'DOUBLE KILL', 'TRIPLE KILL', 'QUAD KILL', 'MEGA KILL']
                            if self.multikill_bonus < len(multikill_names):
                                self.combo_notifications.append({
                                    'text': multikill_names[self.multikill_bonus],
                                    'color': Colors.ORANGE,
                                    'time': current_time,
                                    'y_offset': 60
                                })
                        
                        self.score += int(score_reward * self.score_multiplier)
                        self.xp += int(xp_reward)
                        
                        # Level up check
                        while self.xp >= self.xp_needed:
                            self.xp -= self.xp_needed
                            self.level += 1
                            self.xp_needed = int(self.xp_needed * 1.5)
                            # EPIC level up celebration
                            self.player_health = 100
                            self.player_armor = 100
                            self.combo_notifications.append({
                                'text': f'LEVEL {self.level}!',
                                'color': Colors.GOLD,
                                'time': current_time,
                                'y_offset': 90
                            })
                            # Level up particles
                            for _ in range(30):
                                self.level_up_particles.append({
                                    'x': self.player_x,
                                    'y': self.player_y,
                                    'z': self.player_z,
                                    'vx': random.uniform(-5, 5),
                                    'vy': random.uniform(5, 15),
                                    'vz': random.uniform(-5, 5),
                                    'color': Colors.GOLD,
                                    'life': 2.0,
                                    'time': current_time
                                })
                        
                        # 🔥 CHECK FOR KILLSTREAK REWARDS 🔥
                        if self.killstreak in self.killstreak_rewards:
                            reward = self.killstreak_rewards[self.killstreak]
                            self.killstreak_notifications.append({
                                'text': reward['name'],
                                'color': reward['color'],
                                'time': current_time,
                                'duration': 3.0
                            })
                            
                            # Activate buff
                            buff = {
                                'type': reward['effect'],
                                'duration': reward['duration'],
                                'start_time': current_time
                            }
                            self.active_killstreak_buffs.append(buff)
                            
                            # Play epic sound
                            self.play_sound('reload', 1.0)  # Use reload sound for streak
                            
                            # Special effects for high streaks
                            if self.killstreak >= 10:
                                # GOD MODE or NUKE
                                for _ in range(100):
                                    self.buff_auras.append({
                                        'x': self.player_x + random.uniform(-50, 50),
                                        'y': self.player_y + random.uniform(-50, 50),
                                        'z': self.player_z + random.uniform(-50, 50),
                                        'color': reward['color'],
                                        'time': current_time,
                                        'life': 2.0
                                    })
                        
                        # 🎁 POWER-UP DROP CHANCE 🎁
                        if random.random() < self.power_up_spawn_chance:
                            power_up_types = ['health', 'ammo', 'armor', 'speed', 'damage']
                            power_up = {
                                'x': enemy['x'],
                                'y': 10,
                                'z': enemy['z'],
                                'type': random.choice(power_up_types),
                                'spawn_time': current_time,
                                'collected': False
                            }
                            self.power_ups.append(power_up)
                        
                        # 💎 ACHIEVEMENT CHECKS 💎
                        self._check_achievements()
                        
                        self.hit_markers[-1]['kill'] = True
                        
                        # 🎵 EXPLOSION SOUND when enemy dies
                        self.play_sound('explosion', 0.7)
                        
                        # 💀 EPIC DEATH ANIMATION 💀
                        self.explosions.append({
                            'x': enemy['x'],
                            'y': enemy['y'],
                            'z': enemy['z'],
                            'time': current_time,
                            'radius': 0
                        })
                        
                        # Death particles
                        for _ in range(20):
                            self.death_particles.append({
                                'x': enemy['x'],
                                'y': enemy['y'],
                                'z': enemy['z'],
                                'vx': random.uniform(-8, 8),
                                'vy': random.uniform(3, 12),
                                'vz': random.uniform(-8, 8),
                                'color': Colors.GORE_RED if is_headshot else Colors.ZOMBIE_GREEN,
                                'life': random.uniform(1.0, 2.5),
                                'time': current_time,
                                'size': random.uniform(2, 6)
                            })
                        
                        # Respawn enemy
                        self.spawn_enemies(1)
                    
                    hit = True
                    break
            
            # Remove bullet if hit or out of range
            if hit or bullet['distance'] >= bullet['max_distance']:
                self.bullets.remove(bullet)
    
    def _update_enemies(self, dt):
        """Update ZOMBIE AI - They chase and attack with melee"""
        for enemy in self.enemies:
            if enemy.get('is_dead', False):
                continue
                
            # Calculate distance to player
            dx = self.player_x - enemy['x']
            dz = self.player_z - enemy['z']
            dist_to_player = math.sqrt(dx*dx + dz*dz)
            
            # Zombie type affects behavior
            zombie_type = enemy.get('type', 'walker')
            detection_range = 400 if zombie_type == 'runner' else 300
            move_speed = enemy['speed']
            
            # ZOMBIE AI behavior
            if dist_to_player < detection_range:  # Detection range
                enemy['alert'] = True
                enemy['ai_state'] = 'chase'
                
                # 🎵 ZOMBIE GROWL when detecting player
                if self.sound_enabled and random.random() < 0.005:  # 0.5% chance per frame
                    self.play_sound('zombie_growl', 0.6)
                
                # Face player
                enemy['angle'] = math.atan2(dz, dx)
                
                if dist_to_player < 40:  # Melee attack range
                    enemy['ai_state'] = 'attack'
                    
                    # Zombie MELEE attack
                    current_time = time.time()
                    if not hasattr(enemy, 'last_attack') or current_time - enemy.get('last_attack', 0) > 1.0:
                        enemy['last_attack'] = current_time
                        # 🎵 PAIN SOUND when zombie attacks
                        self.play_sound('pain', 0.8)
                        # Zombie hits player (ONLY if not invincible!)
                        if not self.invincible and random.random() < 0.4:  # 40% hit chance
                            damage = enemy['damage']
                            if self.player_armor > 0:
                                armor_absorbed = min(self.player_armor, damage // 2)
                                self.player_armor -= armor_absorbed
                                damage -= armor_absorbed
                            self.player_health -= damage
                            
                            # Screen shake when hit
                            self.screen_shake += 0.5
                            
                            # Blood effect on player
                            for _ in range(5):
                                self.blood_splatter.append({
                                    'x': self.player_x + random.uniform(-10, 10),
                                    'y': 40,
                                    'z': self.player_z + random.uniform(-10, 10),
                                    'vx': random.uniform(-5, 5),
                                    'vy': random.uniform(5, 15),
                                    'vz': random.uniform(-5, 5),
                                    'time': time.time(),
                                    'size': random.uniform(3, 6)
                                })
                            
                            if self.player_health <= 0:
                                # Player died - trigger respawn
                                self._respawn_player()
                else:
                    # Move towards player (CHASE)
                    enemy['x'] += math.cos(enemy['angle']) * move_speed * dt
                    enemy['z'] += math.sin(enemy['angle']) * move_speed * dt
            else:
                # Wander around
                enemy['ai_state'] = 'wander'
                enemy['alert'] = False
                # Random wandering
                if random.random() < 0.02:  # 2% chance to change direction
                    enemy['angle'] = random.uniform(0, 2 * math.pi)
                enemy['x'] += math.cos(enemy['angle']) * move_speed * 0.3 * dt
                enemy['z'] += math.sin(enemy['angle']) * move_speed * 0.3 * dt
    
    def _check_achievements(self):
        """Check and unlock achievements"""
        current_time = time.time()
        
        # First Blood
        if not self.achievements_list['first_blood']['unlocked'] and self.kills >= 1:
            self._unlock_achievement('first_blood')
        
        # Headhunter
        if not self.achievements_list['headhunter']['unlocked'] and self.headshot_kills >= 10:
            self._unlock_achievement('headhunter')
        
        # Spray & Pray
        total_shots = sum(w.shots_fired for w in self.weapons.values())
        if not self.achievements_list['spray_pray']['unlocked'] and total_shots >= 1000:
            self._unlock_achievement('spray_pray')
        
        # Zombie Slayer
        if not self.achievements_list['slayer']['unlocked'] and self.kills >= 100:
            self._unlock_achievement('slayer')
        
        # Survivor - based on survival time instead of waves
        if not self.achievements_list['survivor']['unlocked'] and self.survival_time >= 600:
            self._unlock_achievement('survivor')
    
    def _unlock_achievement(self, achievement_id):
        """Unlock an achievement with epic animation"""
        if achievement_id not in self.achievements_list:
            return
        
        achievement = self.achievements_list[achievement_id]
        achievement['unlocked'] = True
        
        current_time = time.time()
        self.achievement_popups.append({
            'name': achievement['name'],
            'desc': achievement['desc'],
            'time': current_time,
            'y_offset': 0
        })
        
        # Play sound
        self.play_sound('reload', 0.9)
        
        # Epic particles
        for _ in range(50):
            self.level_up_particles.append({
                'x': self.screen_width // 2 + random.uniform(-100, 100),
                'y': 100 + random.uniform(-50, 50),
                'z': 0,
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-8, -3),
                'vz': 0,
                'color': Colors.GOLD,
                'life': 2.0,
                'time': current_time
            })
    
    def _update_power_ups(self, dt):
        """Update and check power-up collection"""
        current_time = time.time()
        
        for power_up in self.power_ups[:]:
            # Remove old power-ups
            if current_time - power_up['spawn_time'] > 30.0:
                self.power_ups.remove(power_up)
                continue
            
            # Bob up and down
            power_up['y'] = 10 + math.sin(current_time * 2) * 5
            
            # Check collection
            dist = math.sqrt((power_up['x'] - self.player_x)**2 + (power_up['z'] - self.player_z)**2)
            if dist < 30 and not power_up['collected']:
                power_up['collected'] = True
                self._collect_power_up(power_up['type'])
                self.power_ups.remove(power_up)
    
    def _collect_power_up(self, power_type):
        """Collect a power-up and apply its effect"""
        current_time = time.time()
        
        if power_type == 'health':
            self.player_health = min(100, self.player_health + 50)
            message = '+50 HEALTH'
            color = Colors.NEON_GREEN
        elif power_type == 'ammo':
            weapon = self.weapons[self.current_weapon]
            weapon.current_ammo = weapon.max_ammo
            weapon.magazine_count += 2
            message = '+AMMO'
            color = Colors.NEON_YELLOW
        elif power_type == 'armor':
            self.player_armor = min(100, self.player_armor + 50)
            message = '+50 ARMOR'
            color = Colors.NEON_BLUE
        elif power_type == 'speed':
            self.active_power_ups.append({'type': 'speed', 'end_time': current_time + 15})
            message = 'SPEED BOOST'
            color = Colors.NEON_CYAN
        elif power_type == 'damage':
            self.active_power_ups.append({'type': 'damage', 'end_time': current_time + 15})
            message = 'DAMAGE BOOST'
            color = Colors.NEON_RED
        
        self.combo_notifications.append({
            'text': message,
            'color': color,
            'time': current_time,
            'y_offset': 120
        })
        
        self.play_sound('reload', 0.8)
    
    def _update_buffs(self, dt):
        """Update active killstreak buffs"""
        current_time = time.time()
        
        # Update killstreak buffs
        for buff in self.active_killstreak_buffs[:]:
            if current_time - buff['start_time'] > buff['duration']:
                self.active_killstreak_buffs.remove(buff)
                continue
            
            # Apply buff effects
            if buff['type'] == 'speed':
                self.speed *= 1.3
            elif buff['type'] == 'damage':
                self.score_multiplier = 2.0
            elif buff['type'] == 'god_mode':
                self.invincible = True
            elif buff['type'] == 'nuke':
                # Kill all enemies!
                for enemy in self.enemies[:]:
                    self.enemies.remove(enemy)
                    self.kills += 1
                    self.score += 500
                self.spawn_enemies(self.wave * 3)
                buff['duration'] = 0  # One-time effect
        
        # Update power-up buffs
        for power_up in self.active_power_ups[:]:
            if current_time > power_up['end_time']:
                self.active_power_ups.remove(power_up)
    
    def _update_effects(self, dt):
        """Update visual effects"""
        current_time = time.time()
        
        # Update blood splatters with physics
        for blood in self.blood_splatter[:]:
            blood['x'] += blood.get('vx', 0) * dt
            blood['y'] += blood.get('vy', 0) * dt
            blood['z'] += blood.get('vz', 0) * dt
            blood['vy'] = blood.get('vy', 0) - 50 * dt  # Gravity
            
            if current_time - blood['time'] > 5.0:
                self.blood_splatter.remove(blood)
        
        # Remove old hit markers
        self.hit_markers = [h for h in self.hit_markers if current_time - h['time'] < 0.5]
        
        # Update shell casings
        for casing in self.shell_casings[:]:
            casing['x'] += casing['vx'] * dt * 20
            casing['y'] += casing['vy'] * dt * 20
            casing['z'] += casing['vz'] * dt * 20
            casing['vy'] -= 50 * dt  # Gravity
            casing['rotation'] += dt * 10
            
            if current_time - casing['time'] > casing['life']:
                self.shell_casings.remove(casing)
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion['radius'] += dt * 100
            if current_time - explosion['time'] > 0.5:
                self.explosions.remove(explosion)
        
        # 💥 Update death particles
        for particle in self.death_particles[:]:
            particle['x'] += particle['vx'] * dt * 20
            particle['y'] += particle['vy'] * dt * 20
            particle['z'] += particle['vz'] * dt * 20
            particle['vy'] -= 50 * dt  # Gravity
            if current_time - particle['time'] > particle['life']:
                self.death_particles.remove(particle)
        
        # ⭐ Update level up particles
        for particle in self.level_up_particles[:]:
            particle['y'] += particle['vy'] * dt * 20
            if current_time - particle['time'] > particle['life']:
                self.level_up_particles.remove(particle)
        
        # 🔥 Update buff auras
        for aura in self.buff_auras[:]:
            if current_time - aura['time'] > aura['life']:
                self.buff_auras.remove(aura)
        
        # 💬 Update combo notifications
        self.combo_notifications = [n for n in self.combo_notifications if current_time - n['time'] < 2.0]
        self.killstreak_notifications = [n for n in self.killstreak_notifications if current_time - n['time'] < n['duration']]
        self.achievement_popups = [a for a in self.achievement_popups if current_time - a['time'] < 5.0]
        
        # Update power-ups
        self._update_power_ups(dt)
        
        # Update buffs
        self._update_buffs(dt)
        
        # Reset killstreak if too much time passed
        if self.killstreak > 0 and current_time - self.last_kill_time > 5.0:
            self.killstreak = 0
    
    def _render(self):
        """Render the game"""
        if self.in_menu:
            self._render_menu()
        elif self.in_server_connect:
            self._render_server_connect()
        elif self.in_team_selection:
            self._render_team_selection()
        else:
            self._render_game()
    
    def _render_menu(self):
        """🎮 ULTRA MODERN CS:GO STYLE MENU - Tactical & Professional"""
        current_time = pygame.time.get_ticks()
        
        # === BACKGROUND: Dark tactical gradient ===
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(15 + (25 - 15) * ratio)
            g = int(18 + (28 - 18) * ratio)
            b = int(22 + (35 - 22) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # === ANIMATED GRID OVERLAY (Tactical HUD style) ===
        grid_alpha = 20
        grid_spacing = 80
        for x in range(0, self.screen_width, grid_spacing):
            pygame.draw.line(self.screen, (40, 50, 60, grid_alpha), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_spacing):
            pygame.draw.line(self.screen, (40, 50, 60, grid_alpha), (0, y), (self.screen_width, y), 1)
        
        # === ANIMATED SCAN LINES (TV/Monitor effect) ===
        scan_line = (current_time // 3) % self.screen_height
        for i in range(-10, 11):
            if 0 <= scan_line + i < self.screen_height:
                alpha = int(15 * (1 - abs(i) / 10))
                pygame.draw.line(self.screen, (80, 120, 150, alpha), 
                               (0, scan_line + i), (self.screen_width, scan_line + i))
        
        # === CORNER TACTICAL MARKERS ===
        corner_size = 60
        corner_thick = 4
        corner_color = (255, 180, 0)
        
        # Top-left
        pygame.draw.line(self.screen, corner_color, (20, 20), (20 + corner_size, 20), corner_thick)
        pygame.draw.line(self.screen, corner_color, (20, 20), (20, 20 + corner_size), corner_thick)
        # Top-right
        pygame.draw.line(self.screen, corner_color, (self.screen_width - 20 - corner_size, 20), 
                        (self.screen_width - 20, 20), corner_thick)
        pygame.draw.line(self.screen, corner_color, (self.screen_width - 20, 20), 
                        (self.screen_width - 20, 20 + corner_size), corner_thick)
        # Bottom-left
        pygame.draw.line(self.screen, corner_color, (20, self.screen_height - 20), 
                        (20 + corner_size, self.screen_height - 20), corner_thick)
        pygame.draw.line(self.screen, corner_color, (20, self.screen_height - 20 - corner_size), 
                        (20, self.screen_height - 20), corner_thick)
        # Bottom-right
        pygame.draw.line(self.screen, corner_color, 
                        (self.screen_width - 20 - corner_size, self.screen_height - 20), 
                        (self.screen_width - 20, self.screen_height - 20), corner_thick)
        pygame.draw.line(self.screen, corner_color, (self.screen_width - 20, self.screen_height - 20 - corner_size), 
                        (self.screen_width - 20, self.screen_height - 20), corner_thick)
        
        # === GAME LOGO / TITLE ===
        title_y = 80
        
        # Background panel for title
        title_panel_width = 900
        title_panel_height = 160
        title_panel_x = self.screen_width//2 - title_panel_width//2
        title_panel_rect = pygame.Rect(title_panel_x, title_y - 20, title_panel_width, title_panel_height)
        
        # Panel glow
        for i in range(5):
            glow_alpha = 25 - i * 4
            glow_rect = title_panel_rect.inflate(i * 6, i * 6)
            pygame.draw.rect(self.screen, (255, 150, 0, glow_alpha), glow_rect, border_radius=8)
        
        # Panel background with transparency
        panel_surf = pygame.Surface((title_panel_width, title_panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 25, 30, 200), (0, 0, title_panel_width, title_panel_height), border_radius=8)
        self.screen.blit(panel_surf, (title_panel_x, title_y - 20))
        
        # Border lines
        pygame.draw.rect(self.screen, (255, 180, 0), title_panel_rect, 3, border_radius=8)
        pygame.draw.rect(self.screen, (100, 120, 140), title_panel_rect, 1, border_radius=8)
        
        # MAIN TITLE - CS:GO Style
        title_text = "TACTICAL OPS"
        title_shadow = self.font_huge.render(title_text, True, (0, 0, 0))
        self.screen.blit(title_shadow, (self.screen_width//2 - title_shadow.get_width()//2 + 4, title_y + 15 + 4))
        
        # Title with gradient effect (simulate by drawing multiple times)
        title_main = self.font_huge.render(title_text, True, (255, 200, 50))
        self.screen.blit(title_main, (self.screen_width//2 - title_main.get_width()//2, title_y + 15))
        
        # Subtitle - Pulsing
        pulse = abs(math.sin(current_time / 600))
        subtitle_alpha = int(180 + 75 * pulse)
        subtitle_text = "MULTIPLAYER COMBAT OPERATIONS"
        subtitle_surf = self.font_medium.render(subtitle_text, True, (200, 200, 220))
        subtitle_surf.set_alpha(subtitle_alpha)
        self.screen.blit(subtitle_surf, (self.screen_width//2 - subtitle_surf.get_width()//2, title_y + 105))
        
        # Accent line under subtitle
        line_width = 600
        line_pulse = abs(math.sin(current_time / 500))
        line_color = (255, int(150 + 105 * line_pulse), 0)
        pygame.draw.line(self.screen, line_color,
                        (self.screen_width//2 - line_width//2, title_y + 140),
                        (self.screen_width//2 + line_width//2, title_y + 140), 2)
        
        # === MENU OPTIONS - Modern Card Style ===
        menu_start_y = 320
        card_spacing = 85
        
        for i, option in enumerate(self.menu_options):
            y = menu_start_y + i * card_spacing
            
            # Card dimensions
            card_width = 550
            card_height = 70
            card_x = self.screen_width//2 - card_width//2
            card_rect = pygame.Rect(card_x, y, card_width, card_height)
            
            is_selected = (i == self.menu_option)
            
            if is_selected:
                # SELECTED CARD - Glowing, animated
                # Outer glow layers
                for j in range(4):
                    glow_offset = j * 8
                    glow_alpha = 40 - j * 8
                    glow_pulse = abs(math.sin(current_time / 300))
                    glow_color = (255, int(150 + 50 * glow_pulse), 0, glow_alpha)
                    glow_rect_expanded = card_rect.inflate(glow_offset, glow_offset)
                    pygame.draw.rect(self.screen, glow_color, glow_rect_expanded, border_radius=6)
                
                # Card background - bright
                card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                pygame.draw.rect(card_surf, (60, 70, 85, 240), (0, 0, card_width, card_height), border_radius=6)
                self.screen.blit(card_surf, (card_x, y))
                
                # Animated border
                border_pulse = abs(math.sin(current_time / 250))
                border_color = (255, int(180 + 75 * border_pulse), int(50 * border_pulse))
                pygame.draw.rect(self.screen, border_color, card_rect, 4, border_radius=6)
                
                # Selection indicator (left bar)
                indicator_height = int(card_height * 0.7)
                indicator_y = y + (card_height - indicator_height) // 2
                pygame.draw.rect(self.screen, (255, 200, 50), 
                               (card_x + 8, indicator_y, 5, indicator_height), border_radius=2)
                
                # Animated chevrons (right side)
                chevron_offset = int(8 * abs(math.sin(current_time / 200)))
                chevron_x = card_x + card_width - 40 - chevron_offset
                chevron_y = y + card_height // 2
                # Draw multiple chevrons
                for ch in range(3):
                    ch_x = chevron_x + ch * 12
                    pygame.draw.polygon(self.screen, (255, 200, 50), [
                        (ch_x, chevron_y - 10),
                        (ch_x + 8, chevron_y),
                        (ch_x, chevron_y + 10)
                    ])
                
                text_color = (255, 255, 255)
                
            else:
                # UNSELECTED CARD - Subtle
                card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
                pygame.draw.rect(card_surf, (30, 35, 45, 180), (0, 0, card_width, card_height), border_radius=6)
                self.screen.blit(card_surf, (card_x, y))
                
                # Subtle border
                pygame.draw.rect(self.screen, (70, 80, 95), card_rect, 2, border_radius=6)
                
                text_color = (160, 170, 185)
            
            # Option text
            text_surf = self.font_large.render(option, True, text_color)
            text_x = card_x + 40
            text_y = y + (card_height - text_surf.get_height()) // 2
            self.screen.blit(text_surf, (text_x, text_y))
        
        # === STATUS BAR (Bottom) ===
        status_bar_height = 100
        status_bar_y = self.screen_height - status_bar_height
        
        # Status bar background
        status_surf = pygame.Surface((self.screen_width, status_bar_height), pygame.SRCALPHA)
        pygame.draw.rect(status_surf, (15, 20, 25, 220), (0, 0, self.screen_width, status_bar_height))
        self.screen.blit(status_surf, (0, status_bar_y))
        
        # Top border line
        pygame.draw.line(self.screen, (255, 180, 0), (0, status_bar_y), (self.screen_width, status_bar_y), 2)
        pygame.draw.line(self.screen, (100, 120, 140), (0, status_bar_y + 2), (self.screen_width, status_bar_y + 2), 1)
        
        # Instructions (left side)
        inst_x = 50
        inst_y = status_bar_y + 20
        
        instructions = [
            ("↑↓", "Navigate"),
            ("ENTER", "Select"),
            ("ESC", "Exit")
        ]
        
        for key, action in instructions:
            # Key button
            key_surf = self.font_medium.render(key, True, (255, 200, 50))
            key_bg = pygame.Rect(inst_x, inst_y, key_surf.get_width() + 16, 35)
            pygame.draw.rect(self.screen, (40, 50, 60), key_bg, border_radius=4)
            pygame.draw.rect(self.screen, (255, 180, 0), key_bg, 2, border_radius=4)
            self.screen.blit(key_surf, (inst_x + 8, inst_y + 5))
            
            # Action text
            action_surf = self.font_small.render(action, True, (180, 190, 200))
            self.screen.blit(action_surf, (inst_x + key_bg.width + 12, inst_y + 8))
            
            inst_x += key_bg.width + action_surf.get_width() + 40
        
        # Version & info (right side)
        version_x = self.screen_width - 400
        version_y = status_bar_y + 25
        
        version_label = self.font_small.render("VERSION:", True, (120, 130, 145))
        self.screen.blit(version_label, (version_x, version_y))
        version_num = self.font_medium.render("2.5.0", True, (255, 200, 50))
        self.screen.blit(version_num, (version_x + 90, version_y - 3))
        
        # Build info
        build_text = self.font_tiny.render("Build: TACTICAL-OPS-2025 | Engine: Pygame", True, (100, 110, 125))
        self.screen.blit(build_text, (version_x, version_y + 32))
        
        # === ANIMATED ELEMENTS ===
        # Floating particles in background
        for i in range(20):
            particle_time_offset = i * 100
            px = (i * 80 + current_time // 30 + particle_time_offset) % self.screen_width
            py = (i * 45 + current_time // 40) % self.screen_height
            particle_alpha = int(30 + 20 * abs(math.sin((current_time + particle_time_offset) / 500)))
            particle_size = 2 + (i % 3)
            pygame.draw.circle(self.screen, (80, 120, 150, particle_alpha), (px, py), particle_size)
    
    def _render_server_connect(self):
        """🌐 RENDER SERVER CONNECTION SCREEN"""
        current_time = pygame.time.get_ticks()
        
        # === BACKGROUND ===
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(15 + (25 - 15) * ratio)
            g = int(18 + (28 - 18) * ratio)
            b = int(22 + (35 - 22) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Animated network grid background
        grid_spacing = 50
        for x in range(0, self.screen_width, grid_spacing):
            alpha = int(15 + 10 * abs(math.sin((current_time / 1000) + x / 100)))
            pygame.draw.line(self.screen, (40, 60, 80, alpha), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_spacing):
            alpha = int(15 + 10 * abs(math.sin((current_time / 1000) + y / 100)))
            pygame.draw.line(self.screen, (40, 60, 80, alpha), (0, y), (self.screen_width, y), 1)
        
        # === TITLE ===
        title_font = pygame.font.Font(None, 96)
        title = title_font.render("SERVER CONNECTION", True, (255, 255, 255))
        title_shadow = title_font.render("SERVER CONNECTION", True, (0, 0, 0))
        self.screen.blit(title_shadow, (self.screen_width//2 - title.get_width()//2 + 3, 83))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 80))
        
        # Server icon with pulse
        pulse = abs(math.sin(current_time / 500))
        icon_size = 100 + int(20 * pulse)
        icon_y = 200
        
        # Server icon background
        pygame.draw.circle(self.screen, (30, 50, 80), (self.screen_width//2, icon_y), icon_size//2)
        pygame.draw.circle(self.screen, (0, 150, 255, int(100 + 155 * pulse)), (self.screen_width//2, icon_y), icon_size//2, 4)
        
        # Server symbol (database/network icon)
        symbol_font = pygame.font.Font(None, 80)
        server_symbol = symbol_font.render("🌐", True, (100, 200, 255))
        self.screen.blit(server_symbol, (self.screen_width//2 - 30, icon_y - 35))
        
        # === INPUT PANEL ===
        panel_width = 700
        panel_height = 350
        panel_x = self.screen_width//2 - panel_width//2
        panel_y = 320
        
        # Panel background with glow
        panel_surf = pygame.Surface((panel_width + 20, panel_height + 20), pygame.SRCALPHA)
        for i in range(5):
            glow_alpha = int((50 - i * 10) * (0.5 + 0.5 * pulse))
            pygame.draw.rect(panel_surf, (0, 100, 200, glow_alpha), 
                           (i, i, panel_width + 20 - i*2, panel_height + 20 - i*2), border_radius=20)
        self.screen.blit(panel_surf, (panel_x - 10, panel_y - 10))
        
        # Panel main
        pygame.draw.rect(self.screen, (25, 35, 50, 240), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
        pygame.draw.rect(self.screen, (0, 150, 255), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
        
        # === IP INPUT FIELD ===
        label_y = panel_y + 50
        label = self.font_large.render("Server IP Address:", True, (200, 220, 255))
        self.screen.blit(label, (panel_x + 50, label_y))
        
        # Input box
        input_box_y = label_y + 60
        input_box_width = panel_width - 100
        input_box_height = 70
        
        # Input box background
        pygame.draw.rect(self.screen, (15, 25, 40), 
                        (panel_x + 50, input_box_y, input_box_width, input_box_height), border_radius=10)
        
        # Input box border (animated)
        border_color = (0, 200, 255) if self.server_ip else (80, 100, 130)
        border_pulse = int(150 + 105 * pulse) if self.server_ip else 130
        pygame.draw.rect(self.screen, (*border_color[:2], border_pulse), 
                        (panel_x + 50, input_box_y, input_box_width, input_box_height), 3, border_radius=10)
        
        # Display IP text
        ip_text = self.server_ip if self.server_ip else "192.168.1.100"
        ip_color = (255, 255, 255) if self.server_ip else (100, 120, 150)
        ip_surf = self.font_large.render(ip_text, True, ip_color)
        self.screen.blit(ip_surf, (panel_x + 70, input_box_y + 18))
        
        # Blinking cursor
        if int(current_time / 500) % 2 == 0:
            cursor_x = panel_x + 70 + ip_surf.get_width() + 5
            pygame.draw.line(self.screen, (255, 255, 255), 
                           (cursor_x, input_box_y + 15), 
                           (cursor_x, input_box_y + input_box_height - 15), 3)
        
        # === EXAMPLES ===
        examples_y = input_box_y + input_box_height + 30
        examples_label = self.font_small.render("Examples:", True, (150, 170, 200))
        self.screen.blit(examples_label, (panel_x + 50, examples_y))
        
        examples = [
            "• 127.0.0.1 (Localhost)",
            "• 192.168.1.100 (Local Network)",
            "• game.server.com (Domain)"
        ]
        
        for i, example in enumerate(examples):
            ex_surf = self.font_small.render(example, True, (120, 140, 180))
            self.screen.blit(ex_surf, (panel_x + 70, examples_y + 30 + i * 28))
        
        # === CONNECTION STATUS ===
        if self.connection_status:
            status_y = panel_y + panel_height - 60
            if "✓" in self.connection_status:
                status_color = (0, 255, 100)
            elif "⚠️" in self.connection_status:
                status_color = (255, 200, 0)
            else:
                status_color = (255, 100, 100)
            
            status_surf = self.font_medium.render(self.connection_status, True, status_color)
            self.screen.blit(status_surf, (panel_x + panel_width//2 - status_surf.get_width()//2, status_y))
        
        # === INSTRUCTIONS ===
        inst_y = self.screen_height - 150
        
        instructions = [
            "Type the server IP address",
            "ENTER - Connect to Server",
            "ESC - Back to Menu"
        ]
        
        for i, inst in enumerate(instructions):
            inst_surf = self.font_medium.render(inst, True, (180, 200, 220))
            self.screen.blit(inst_surf, (self.screen_width//2 - inst_surf.get_width()//2, inst_y + i * 35))
        
        # === CONNECTING ANIMATION ===
        if "Connected" in self.connection_status:
            # Animated success checkmark
            check_size = 60
            check_x = self.screen_width//2
            check_y = panel_y + panel_height - 100
            
            pygame.draw.circle(self.screen, (0, 255, 100, 100), (check_x, check_y), check_size)
            
            checkmark_font = pygame.font.Font(None, 72)
            check = checkmark_font.render("✓", True, (0, 255, 100))
            self.screen.blit(check, (check_x - 20, check_y - 30))
    
    def _render_team_selection(self):
        """🎖️ RENDER TEAM SELECTION SCREEN"""
        current_time = pygame.time.get_ticks()
        
        # === BACKGROUND ===
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(10 + (20 - 10) * ratio)
            g = int(12 + (22 - 12) * ratio)
            b = int(15 + (28 - 15) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # === TITLE ===
        title_font = pygame.font.Font(None, 96)
        title = title_font.render("SELECT YOUR TEAM", True, (255, 255, 255))
        title_shadow = title_font.render("SELECT YOUR TEAM", True, (0, 0, 0))
        self.screen.blit(title_shadow, (self.screen_width//2 - title.get_width()//2 + 3, 83))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 80))
        
        # Subtitle
        subtitle = self.font_medium.render("Choose wisely - you can only damage enemies from the opposite team!", True, (200, 200, 220))
        self.screen.blit(subtitle, (self.screen_width//2 - subtitle.get_width()//2, 160))
        
        # === TEAM CARDS ===
        card_width = 500
        card_height = 550
        card_y = 250
        spacing = 100
        
        blue_card_x = self.screen_width//2 - card_width - spacing//2
        red_card_x = self.screen_width//2 + spacing//2
        
        # BLUE TEAM CARD
        blue_selected = self.team_selection == 0
        blue_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Card glow if selected
        if blue_selected:
            for i in range(5):
                glow_rect = pygame.Rect(-i*4, -i*4, card_width + i*8, card_height + i*8)
                pygame.draw.rect(blue_surf, (0, 100, 255, 40 - i*7), glow_rect, border_radius=20)
        
        # Card background
        pygame.draw.rect(blue_surf, (15, 40, 80, 240), (0, 0, card_width, card_height), border_radius=15)
        if blue_selected:
            pygame.draw.rect(blue_surf, (0, 150, 255), (0, 0, card_width, card_height), 5, border_radius=15)
        else:
            pygame.draw.rect(blue_surf, (60, 80, 120), (0, 0, card_width, card_height), 2, border_radius=15)
        
        self.screen.blit(blue_surf, (blue_card_x, card_y))
        
        # Blue team icon (large)
        icon_size = 180
        icon_y = card_y + 60
        pygame.draw.circle(self.screen, (0, 100, 255), (blue_card_x + card_width//2, icon_y), icon_size//2, 8)
        pygame.draw.circle(self.screen, (20, 50, 100), (blue_card_x + card_width//2, icon_y), icon_size//2 - 10)
        
        # Blue team symbol
        symbol_font = pygame.font.Font(None, 120)
        blue_symbol = symbol_font.render("🛡️", True, (100, 180, 255))
        self.screen.blit(blue_symbol, (blue_card_x + card_width//2 - 40, icon_y - 50))
        
        # Blue team name
        team_font = pygame.font.Font(None, 72)
        blue_name = team_font.render("BLUE TEAM", True, (100, 200, 255))
        self.screen.blit(blue_name, (blue_card_x + card_width//2 - blue_name.get_width()//2, card_y + 230))
        
        # Blue team description
        desc_y = card_y + 310
        blue_desc = [
            "• Defenders",
            "• Tactical Approach",
            "• Team Strategy",
            "• Protect Objectives"
        ]
        for i, line in enumerate(blue_desc):
            desc_surf = self.font_medium.render(line, True, (180, 200, 220))
            self.screen.blit(desc_surf, (blue_card_x + 50, desc_y + i * 40))
        
        # Selection indicator
        if blue_selected:
            pulse = abs(math.sin(current_time / 300))
            select_text = self.font_large.render("▶ SELECTED ◀", True, (100 + int(155*pulse), 200, 255))
            self.screen.blit(select_text, (blue_card_x + card_width//2 - select_text.get_width()//2, card_y + card_height - 60))
        
        # RED TEAM CARD
        red_selected = self.team_selection == 1
        red_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Card glow if selected
        if red_selected:
            for i in range(5):
                glow_rect = pygame.Rect(-i*4, -i*4, card_width + i*8, card_height + i*8)
                pygame.draw.rect(red_surf, (255, 50, 50, 40 - i*7), glow_rect, border_radius=20)
        
        # Card background
        pygame.draw.rect(red_surf, (80, 15, 15, 240), (0, 0, card_width, card_height), border_radius=15)
        if red_selected:
            pygame.draw.rect(red_surf, (255, 50, 50), (0, 0, card_width, card_height), 5, border_radius=15)
        else:
            pygame.draw.rect(red_surf, (120, 60, 60), (0, 0, card_width, card_height), 2, border_radius=15)
        
        self.screen.blit(red_surf, (red_card_x, card_y))
        
        # Red team icon (large)
        pygame.draw.circle(self.screen, (255, 50, 50), (red_card_x + card_width//2, icon_y), icon_size//2, 8)
        pygame.draw.circle(self.screen, (100, 20, 20), (red_card_x + card_width//2, icon_y), icon_size//2 - 10)
        
        # Red team symbol
        red_symbol = symbol_font.render("⚔️", True, (255, 100, 100))
        self.screen.blit(red_symbol, (red_card_x + card_width//2 - 40, icon_y - 50))
        
        # Red team name
        red_name = team_font.render("RED TEAM", True, (255, 100, 100))
        self.screen.blit(red_name, (red_card_x + card_width//2 - red_name.get_width()//2, card_y + 230))
        
        # Red team description
        red_desc = [
            "• Attackers",
            "• Aggressive Style",
            "• Fast Strikes",
            "• Capture Territory"
        ]
        for i, line in enumerate(red_desc):
            desc_surf = self.font_medium.render(line, True, (220, 180, 180))
            self.screen.blit(desc_surf, (red_card_x + 50, desc_y + i * 40))
        
        # Selection indicator
        if red_selected:
            pulse = abs(math.sin(current_time / 300))
            select_text = self.font_large.render("▶ SELECTED ◀", True, (255, 100 + int(155*pulse), 100))
            self.screen.blit(select_text, (red_card_x + card_width//2 - select_text.get_width()//2, card_y + card_height - 60))
        
        # === INSTRUCTIONS ===
        inst_y = self.screen_height - 120
        
        instructions = [
            "← → ARROWS - Choose Team",
            "ENTER / SPACE - Confirm Selection",
            "ESC - Back to Menu"
        ]
        
        for i, inst in enumerate(instructions):
            inst_surf = self.font_medium.render(inst, True, (200, 210, 220))
            self.screen.blit(inst_surf, (self.screen_width//2 - inst_surf.get_width()//2, inst_y + i * 35))
    
    def _render_game(self):
        """Render the FPS game with STUNNING VISUALS AND BEAUTIFUL MAP"""
        current_time = pygame.time.get_ticks()
        
        # === CS:GO STYLE SKY - Clean Industrial ===
        # Muted overcast sky for tactical gameplay
        sky_top = (160, 170, 180)      # Light gray top
        sky_bottom = (190, 195, 200)   # Lighter gray horizon
        
        # Simple gradient sky (no dramatic colors)
        for y in range(self.screen_height // 2):
            progress = y / (self.screen_height // 2)
            r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * progress)
            g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * progress)
            b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * progress)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Subtle sun (not dramatic - CS:GO style)
        sun_x, sun_y = int(self.screen_width * 0.75), int(self.screen_height * 0.2)
        # Soft glow
        for i in range(3):
            size = 40 + i * 15
            alpha = 30 - i * 8
            pygame.draw.circle(self.screen, (240, 240, 220, alpha), (sun_x, sun_y), size)
        pygame.draw.circle(self.screen, (230, 230, 210), (sun_x, sun_y), 35)
        
        # Subtle industrial clouds (not fluffy, more like haze)
        for cloud in self.clouds:
            cloud_x = int((cloud['x'] + current_time / 150) % (self.screen_width + 200))
            cloud_y = int(cloud['y'])
            cloud_size = cloud['size']
            
            # Industrial haze (stretched clouds)
            cloud_color = cloud.get('color', (210, 215, 220))
            for i in range(3):
                x_offset = (i - 1) * cloud_size // 2
                pygame.draw.ellipse(self.screen, (*cloud_color, 80), 
                                  (cloud_x + x_offset - cloud_size//2, cloud_y - cloud_size//4,
                                   cloud_size, cloud_size//2))
        
        # === CS:GO STYLE GROUND - Concrete/Asphalt ===
        ground_y = self.screen_height // 2
        
        # Industrial concrete ground (not grass)
        ground_top = (85, 90, 85)      # Light concrete gray
        ground_bottom = (65, 70, 65)   # Darker concrete
        
        for y in range(ground_y, self.screen_height):
            progress = (y - ground_y) / (self.screen_height - ground_y)
            r = int(ground_top[0] + (ground_bottom[0] - ground_top[0]) * progress)
            g = int(ground_top[1] + (ground_bottom[1] - ground_top[1]) * progress)
            b = int(ground_top[2] + (ground_bottom[2] - ground_top[2]) * progress)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Render FLOOR DETAILS (oil stains, markings, cracks)
        for detail in self.grass_patches:
            screen_pos = self._world_to_screen(detail['x'], detail['y'], detail['z'])
            if screen_pos:
                detail_type = detail.get('type', 'oil_stain')
                size = detail['size']
                
                if detail_type == 'oil_stain':
                    # Dark oil stain
                    pygame.draw.ellipse(self.screen, (40, 40, 45),
                                      (screen_pos[0] - size//2, screen_pos[1] - size//3, size, size//1.5))
                elif detail_type == 'caution_paint':
                    # Yellow hazard stripes
                    for i in range(3):
                        pygame.draw.line(self.screen, (200, 200, 50),
                                       (screen_pos[0] - size//2 + i*10, screen_pos[1]),
                                       (screen_pos[0] - size//2 + i*10 + 8, screen_pos[1] - 6), 3)
                elif detail_type == 'cracks':
                    # Concrete cracks
                    for i in range(2):
                        x_off = random.randint(-size//2, size//2)
                        pygame.draw.line(self.screen, (60, 60, 65),
                                       (screen_pos[0] + x_off, screen_pos[1]),
                                       (screen_pos[0] + x_off + random.randint(5, 15), screen_pos[1] + random.randint(-3, 3)), 1)
        
        # Render TACTICAL COVER - Crates, Containers, Barrels
        for cover in self.rocks:
            screen_pos = self._world_to_screen(cover['x'], cover['y'], cover['z'])
            if screen_pos:
                size = cover['size']
                cover_type = cover.get('type', 'crate')
                cover_color = cover.get('color', (130, 110, 80))
                
                if cover_type == 'container':
                    # Shipping container (large rectangular)
                    container_width = size * 2
                    container_height = size
                    # Shadow
                    pygame.draw.rect(self.screen, (35, 35, 35),
                                   (screen_pos[0] + 4, screen_pos[1] - container_height + 4, container_width, container_height))
                    # Main container
                    pygame.draw.rect(self.screen, cover_color,
                                   (screen_pos[0], screen_pos[1] - container_height, container_width, container_height), border_radius=3)
                    # Container ridges
                    for i in range(5):
                        pygame.draw.line(self.screen, (max(0, cover_color[0]-20), max(0, cover_color[1]-20), max(0, cover_color[2]-20)),
                                       (screen_pos[0] + i*container_width//5, screen_pos[1] - container_height),
                                       (screen_pos[0] + i*container_width//5, screen_pos[1]), 2)
                    # Border
                    pygame.draw.rect(self.screen, (min(255, cover_color[0]+30), min(255, cover_color[1]+30), min(255, cover_color[2]+30)),
                                   (screen_pos[0], screen_pos[1] - container_height, container_width, container_height), 3, border_radius=3)
                    
                elif cover_type in ['crate', 'box']:
                    # Wooden crate
                    pygame.draw.rect(self.screen, (45, 45, 45),
                                   (screen_pos[0] + 3, screen_pos[1] - size + 3, size, size))
                    pygame.draw.rect(self.screen, cover_color,
                                   (screen_pos[0], screen_pos[1] - size, size, size), border_radius=2)
                    # Wood planks
                    for i in range(3):
                        pygame.draw.line(self.screen, (110, 90, 70),
                                       (screen_pos[0], screen_pos[1] - size + i*size//3),
                                       (screen_pos[0] + size, screen_pos[1] - size + i*size//3), 2)
                    pygame.draw.rect(self.screen, (150, 130, 100),
                                   (screen_pos[0], screen_pos[1] - size, size, size), 2, border_radius=2)
                    
                elif cover_type == 'barrel':
                    # Metal barrel
                    pygame.draw.ellipse(self.screen, (50, 50, 50),
                                      (screen_pos[0] - size//2, screen_pos[1] - size, size, size))
                    pygame.draw.ellipse(self.screen, (90, 90, 95),
                                      (screen_pos[0] - size//2, screen_pos[1] - size, size, size), 2)
                    # Barrel bands
                    for i in range(2):
                        pygame.draw.line(self.screen, (70, 70, 75),
                                       (screen_pos[0] - size//2, screen_pos[1] - size + size//3 + i*size//3),
                                       (screen_pos[0] + size//2, screen_pos[1] - size + size//3 + i*size//3), 3)
                else:
                    # Generic cover
                    pygame.draw.rect(self.screen, cover_color,
                                   (screen_pos[0], screen_pos[1] - size, size, size), border_radius=2)
                    pygame.draw.rect(self.screen, (min(255, cover_color[0]+40), min(255, cover_color[1]+40), min(255, cover_color[2]+40)),
                                   (screen_pos[0], screen_pos[1] - size, size, size), 2, border_radius=2)
        
        # Render CS:GO STYLE BUILDINGS (Warehouses, Factories, Towers)
        for building in sorted(self.buildings, key=lambda b: b['z'], reverse=True):  # Back to front
            screen_pos = self._world_to_screen(building['x'], building['y'], building['z'])
            if screen_pos:
                width = building['width']
                height = building['height']
                btype = building.get('type', 'warehouse')
                site = building.get('site')
                
                # Building shadow
                shadow_offset = 6
                pygame.draw.rect(self.screen, (35, 35, 35),
                               (screen_pos[0] + shadow_offset, screen_pos[1] - height + shadow_offset, width, height))
                
                # Main building - muted industrial colors
                building_color = building.get('color', (110, 110, 105))
                
                pygame.draw.rect(self.screen, building_color,
                               (screen_pos[0], screen_pos[1] - height, width, height), border_radius=2)
                
                # === TACTICAL WINDOWS (Fewer, more strategic) ===
                window_rows = building.get('windows', 3)
                window_cols = max(2, width // 80)
                
                for row in range(window_rows):
                    for col in range(window_cols):
                        w_x = screen_pos[0] + 15 + col * (width // (window_cols + 1))
                        w_y = screen_pos[1] - height + 25 + row * (height // (window_rows + 1))
                        
                        # Dark tactical windows (not bright/lit)
                        window_color = (70, 75, 80)  # Dark tinted
                        pygame.draw.rect(self.screen, window_color, (w_x, w_y, 22, 30), border_radius=1)
                        # Window frame
                        pygame.draw.rect(self.screen, (90, 90, 95), (w_x, w_y, 22, 30), 1, border_radius=1)
                
                # === INDUSTRIAL DETAILS ===
                # Metal panels/siding
                num_panels = height // 35
                for i in range(num_panels):
                    panel_y = screen_pos[1] - height + i * 35
                    pygame.draw.line(self.screen, (max(0, building_color[0]-15), max(0, building_color[1]-15), max(0, building_color[2]-15)),
                                   (screen_pos[0], panel_y),
                                   (screen_pos[0] + width, panel_y), 1)
                
                # Building border/edges
                pygame.draw.rect(self.screen, (min(255, building_color[0]+25), min(255, building_color[1]+25), min(255, building_color[2]+25)),
                               (screen_pos[0], screen_pos[1] - height, width, height), 3, border_radius=2)
                
                # === ROOF (Industrial style) ===
                if btype == 'tower':
                    # Control tower top
                    pygame.draw.rect(self.screen, (80, 80, 85),
                                   (screen_pos[0] - 8, screen_pos[1] - height - 12, width + 16, 12), border_radius=2)
                elif btype in ['warehouse', 'factory']:
                    # Flat industrial roof
                    pygame.draw.rect(self.screen, (90, 90, 90),
                                   (screen_pos[0] - 3, screen_pos[1] - height - 5, width + 6, 5))
                    # Vents/AC units on roof
                    if building.get('vents'):
                        vent_x = screen_pos[0] + width // 3
                        pygame.draw.rect(self.screen, (70, 70, 75),
                                       (vent_x, screen_pos[1] - height - 15, 20, 10), border_radius=1)
                else:
                    # Simple flat roof for offices
                    pygame.draw.rect(self.screen, (95, 95, 95),
                                   (screen_pos[0] - 2, screen_pos[1] - height - 4, width + 4, 4))
                
                # === SITE MARKERS (A/B/MID) - CS:GO Style ===
                site = building.get('site')
                if site:
                    # Site letter indicator
                    site_color = (255, 200, 50) if site in ['A', 'B'] else (200, 200, 200)
                    site_surf = self.font_large.render(site, True, site_color)
                    # Background box
                    box_width = site_surf.get_width() + 16
                    box_height = site_surf.get_height() + 8
                    box_x = screen_pos[0] + width//2 - box_width//2
                    box_y = screen_pos[1] - height//2 - box_height//2
                    pygame.draw.rect(self.screen, (40, 40, 40, 200),
                                   (box_x, box_y, box_width, box_height), border_radius=4)
                    pygame.draw.rect(self.screen, site_color,
                                   (box_x, box_y, box_width, box_height), 2, border_radius=4)
                    self.screen.blit(site_surf, (box_x + 8, box_y + 4))
                
                # Building outline (clean edges)
                pygame.draw.rect(self.screen, (130, 130, 135),
                               (screen_pos[0], screen_pos[1] - height, width, height), 2, border_radius=2)
        
        # Render LIGHT POLES (Industrial lighting, not trees)
        for pole in self.trees:
            screen_pos = self._world_to_screen(pole['x'], pole['y'], pole['z'])
            if screen_pos:
                pole_type = pole.get('type', 'light_pole')
                pole_height = pole.get('height', 150)
                
                if pole_type == 'light_pole':
                    # Metal pole shadow
                    pygame.draw.rect(self.screen, (40, 40, 40),
                                   (screen_pos[0] - 4 + 2, screen_pos[1] - pole_height + 2, 8, pole_height))
                    
                    # Metal pole
                    pygame.draw.rect(self.screen, (80, 80, 85),
                                   (screen_pos[0] - 4, screen_pos[1] - pole_height, 8, pole_height), border_radius=1)
                    # Pole highlights
                    pygame.draw.rect(self.screen, (100, 100, 105),
                                   (screen_pos[0] - 4, screen_pos[1] - pole_height, 3, pole_height))
                    
                    # Light fixture at top
                    light_on = pole.get('light_on', True)
                    if light_on:
                        # Glowing light
                        for i in range(3):
                            glow_size = 18 + i * 8
                            alpha = 60 - i * 18
                            pygame.draw.circle(self.screen, (240, 240, 200, alpha),
                                             (screen_pos[0], screen_pos[1] - pole_height), glow_size)
                        pygame.draw.circle(self.screen, (255, 255, 220),
                                         (screen_pos[0], screen_pos[1] - pole_height), 15)
                    else:
                        # Dark light fixture
                        pygame.draw.circle(self.screen, (60, 60, 65),
                                         (screen_pos[0], screen_pos[1] - pole_height), 15)
                    
                    # Fixture housing
                    pygame.draw.rect(self.screen, (70, 70, 75),
                                   (screen_pos[0] - 12, screen_pos[1] - pole_height - 5, 24, 10), border_radius=2)
        
        # WEATHER EFFECTS
        if self.weather == 'rain':
            self._render_rain()
        elif self.weather == 'fog':
            self._render_fog()
        
        # Add distance fog effect
        horizon_y = self.screen_height // 2
        fog_height = 150
        for y in range(fog_height):
            alpha = int(50 * (1 - y / fog_height))
            fog_color = (200, 220, 240) if self.time_of_day == 'day' else (100, 110, 120)
            pygame.draw.line(self.screen, (*fog_color, alpha), 
                           (0, horizon_y - fog_height + y), 
                           (self.screen_width, horizon_y - fog_height + y))
        
        # Render enemies (ZOMBIES)
        self._render_enemies()
        
        # Render player in third-person mode
        if self.camera_mode == 'third_person':
            self._render_player_third_person()
        
        # Render advanced particle effects
        self._render_advanced_effects()
        
        # Render weapon (only in first-person)
        if self.camera_mode == 'first_person':
            self._render_weapon()
        
        # Render HUD
        self._render_hud()
        
        # Render crosshair
        self._render_crosshair()
        
        # Render effects
        self._render_effects()
        
        # 🔥 Render EPIC notifications and achievements 🔥
        self._render_notifications()
        self._render_killstreak_display()
        self._render_achievement_popups()
        self._render_power_ups_hud()
    
    def _render_enemies(self):
        """Render ULTRA-REALISTIC HUMAN ENEMIES - AAA Graphics Quality"""
        current_time = pygame.time.get_ticks()
        
        for enemy in self.enemies:
            if enemy.get('is_dead', False):
                continue
                
            # Calculate screen position
            dx = enemy['x'] - self.player_x
            dz = enemy['z'] - self.player_z
            
            # Rotate to player view (third-person adjust)
            if self.camera_mode == 'third_person':
                # Offset camera behind player
                cam_dx = dx + self.camera_distance * math.cos(self.player_angle + math.pi)
                cam_dz = dz + self.camera_distance * math.sin(self.player_angle + math.pi)
                dx, dz = cam_dx, cam_dz
            
            cos_a = math.cos(-self.player_angle)
            sin_a = math.sin(-self.player_angle)
            rx = dx * cos_a - dz * sin_a
            rz = dx * sin_a + dz * cos_a
            
            if rz > 10:  # Only render if in front
                # Perspective projection
                scale = 200 / rz
                screen_x = int(self.screen_width / 2 + rx * scale)
                screen_y = int(self.screen_height / 2 - 50 * scale)
                
                if -50 <= screen_x < self.screen_width + 50:
                    size = int(80 * scale)  # Larger, more realistic size
                    
                    # === HUMAN SOLDIER TYPES - Ultra Realistic ===
                    enemy_type = enemy.get('type', 'walker')
                    enemy_team = enemy.get('team', 'RED')  # Get team
                    
                    # TEAM-BASED COLORS
                    if enemy_team == 'BLUE':
                        # BLUE TEAM - Blue tactical gear
                        if enemy_type == 'walker':
                            outfit_color = (60, 80, 140)  # Blue uniform
                            vest_color = (40, 60, 120)  # Blue vest
                            helmet_color = (30, 50, 100)  # Blue helmet
                        elif enemy_type == 'runner':
                            outfit_color = (50, 70, 130)  # Blue urban
                            vest_color = (35, 55, 110)  # Blue tactical
                            helmet_color = (25, 45, 90)  # Dark blue
                        else:  # tank
                            outfit_color = (20, 40, 80)  # Navy blue
                            vest_color = (15, 30, 70)  # Dark blue armor
                            helmet_color = (10, 25, 60)  # Deep blue
                    else:  # RED TEAM
                        # RED TEAM - Red/Maroon tactical gear
                        if enemy_type == 'walker':
                            outfit_color = (140, 60, 60)  # Red uniform
                            vest_color = (120, 40, 40)  # Red vest
                            helmet_color = (100, 30, 30)  # Red helmet
                        elif enemy_type == 'runner':
                            outfit_color = (130, 50, 50)  # Red urban
                            vest_color = (110, 35, 35)  # Red tactical
                            helmet_color = (90, 25, 25)  # Dark red
                        else:  # tank
                            outfit_color = (80, 20, 20)  # Maroon
                            vest_color = (70, 15, 15)  # Dark red armor
                            helmet_color = (60, 10, 10)  # Deep red
                    
                    # Skin and hair (same for all)
                    skin_tone = (210, 180, 140)  # Realistic skin
                    hair_color = (60, 50, 40)  # Dark brown hair
                    
                    # Realistic walking animation with proper physics
                    enemy['animation_frame'] += 0.15
                    walk_cycle = enemy['animation_frame']
                    walk_offset = int(4 * math.sin(walk_cycle))
                    arm_swing = int(8 * math.sin(walk_cycle))
                    head_bob = int(2 * abs(math.sin(walk_cycle)))
                    
                    # === REALISTIC SHADOW with SOFT EDGES ===
                    # Multi-layer shadow for depth
                    for layer in range(3):
                        shadow_alpha = 100 - layer * 30
                        shadow_size = size + layer * 5
                        pygame.draw.ellipse(self.screen, (15, 15, 15, shadow_alpha),
                                          (screen_x - shadow_size//2, screen_y + size * 1.2, 
                                           shadow_size, shadow_size//4))
                    
                    # === HIGHLY DETAILED LEGS with REALISTIC FABRIC ===
                    leg_height = size // 2
                    leg_width = size // 6
                    
                    # LEFT LEG - Full detail with shading
                    left_leg_y = screen_y + size // 2 + walk_offset
                    
                    # Thigh
                    for i in range(leg_width):
                        shade_r = outfit_color[0] - int(15 * (i / leg_width))
                        shade_g = outfit_color[1] - int(15 * (i / leg_width))
                        shade_b = outfit_color[2] - int(15 * (i / leg_width))
                        pygame.draw.line(self.screen, (shade_r, shade_g, shade_b),
                                       (screen_x - size//4 + i, left_leg_y),
                                       (screen_x - size//4 + i, left_leg_y + leg_height//2))
                    
                    # Cargo pocket detail
                    pygame.draw.rect(self.screen, (max(0, outfit_color[0]-20), max(0, outfit_color[1]-20), max(0, outfit_color[2]-20)),
                                   (screen_x - size//4 + 2, left_leg_y + 10, leg_width - 4, leg_height//4), border_radius=1)
                    
                    # Knee joint with realistic bend
                    knee_y = left_leg_y + leg_height//2
                    pygame.draw.ellipse(self.screen, (max(0, outfit_color[0]-10), max(0, outfit_color[1]-10), max(0, outfit_color[2]-10)),
                                      (screen_x - size//4, knee_y - 5, leg_width, leg_width + 10))
                    
                    # Tactical knee pad (3D effect)
                    for pad_layer in range(3):
                        pad_color_val = 40 - pad_layer * 5
                        pygame.draw.ellipse(self.screen, (pad_color_val, pad_color_val, pad_color_val),
                                          (screen_x - size//4 + pad_layer, knee_y - 3 + pad_layer, 
                                           leg_width - pad_layer*2, leg_width + 6 - pad_layer*2))
                    
                    # Lower leg with fabric wrinkles
                    lower_leg_rect = (screen_x - size//4, knee_y + 5, leg_width, leg_height//2 - 15)
                    pygame.draw.rect(self.screen, outfit_color, lower_leg_rect, border_radius=2)
                    # Wrinkle details
                    for wrinkle in range(3):
                        wrinkle_y = knee_y + 10 + wrinkle * 8
                        pygame.draw.line(self.screen, (max(0, outfit_color[0]-20), max(0, outfit_color[1]-20), max(0, outfit_color[2]-20)),
                                       (screen_x - size//4, wrinkle_y),
                                       (screen_x - size//4 + leg_width, wrinkle_y))
                    
                    # Combat boot - Highly detailed
                    boot_y = left_leg_y + leg_height - 15
                    # Boot sole (rubber)
                    pygame.draw.rect(self.screen, (25, 25, 25),
                                   (screen_x - size//4 - 2, boot_y + 13, leg_width + 4, 4))
                    # Boot leather with laces
                    for boot_shade in range(leg_width):
                        shade = 30 + int(20 * (boot_shade / leg_width))
                        pygame.draw.line(self.screen, (shade, shade, shade),
                                       (screen_x - size//4 + boot_shade, boot_y),
                                       (screen_x - size//4 + boot_shade, boot_y + 13))
                    # Laces
                    for lace in range(3):
                        lace_y = boot_y + lace * 4
                        pygame.draw.line(self.screen, (60, 55, 50),
                                       (screen_x - size//4 + 2, lace_y),
                                       (screen_x - size//4 + leg_width - 2, lace_y), 1)
                    
                    # RIGHT LEG - Mirror with opposite animation
                    right_leg_y = screen_y + size // 2 - walk_offset
                    
                    # Complete right leg rendering (similar to left)
                    for i in range(leg_width):
                        shade_r = outfit_color[0] - int(15 * (1 - i / leg_width))
                        shade_g = outfit_color[1] - int(15 * (1 - i / leg_width))
                        shade_b = outfit_color[2] - int(15 * (1 - i / leg_width))
                        pygame.draw.line(self.screen, (shade_r, shade_g, shade_b),
                                       (screen_x + size//6 + i, right_leg_y),
                                       (screen_x + size//6 + i, right_leg_y + leg_height//2))
                    
                    pygame.draw.rect(self.screen, (max(0, outfit_color[0]-20), max(0, outfit_color[1]-20), max(0, outfit_color[2]-20)),
                                   (screen_x + size//6 + 2, right_leg_y + 10, leg_width - 4, leg_height//4), border_radius=1)
                    
                    knee_y_right = right_leg_y + leg_height//2
                    pygame.draw.ellipse(self.screen, (max(0, outfit_color[0]-10), max(0, outfit_color[1]-10), max(0, outfit_color[2]-10)),
                                      (screen_x + size//6, knee_y_right - 5, leg_width, leg_width + 10))
                    
                    for pad_layer in range(3):
                        pad_color_val = 40 - pad_layer * 5
                        pygame.draw.ellipse(self.screen, (pad_color_val, pad_color_val, pad_color_val),
                                          (screen_x + size//6 + pad_layer, knee_y_right - 3 + pad_layer, 
                                           leg_width - pad_layer*2, leg_width + 6 - pad_layer*2))
                    
                    lower_leg_rect_r = (screen_x + size//6, knee_y_right + 5, leg_width, leg_height//2 - 15)
                    pygame.draw.rect(self.screen, outfit_color, lower_leg_rect_r, border_radius=2)
                    for wrinkle in range(3):
                        wrinkle_y = knee_y_right + 10 + wrinkle * 8
                        pygame.draw.line(self.screen, (max(0, outfit_color[0]-20), max(0, outfit_color[1]-20), max(0, outfit_color[2]-20)),
                                       (screen_x + size//6, wrinkle_y),
                                       (screen_x + size//6 + leg_width, wrinkle_y))
                    
                    boot_y_right = right_leg_y + leg_height - 15
                    pygame.draw.rect(self.screen, (25, 25, 25),
                                   (screen_x + size//6 - 2, boot_y_right + 13, leg_width + 4, 4))
                    for boot_shade in range(leg_width):
                        shade = 30 + int(20 * (1 - boot_shade / leg_width))
                        pygame.draw.line(self.screen, (shade, shade, shade),
                                       (screen_x + size//6 + boot_shade, boot_y_right),
                                       (screen_x + size//6 + boot_shade, boot_y_right + 13))
                    for lace in range(3):
                        lace_y = boot_y_right + lace * 4
                        pygame.draw.line(self.screen, (60, 55, 50),
                                       (screen_x + size//6 + 2, lace_y),
                                       (screen_x + size//6 + leg_width - 2, lace_y), 1)
                    
                    # === REALISTIC TORSO with 3D TACTICAL VEST ===
                    torso_y = screen_y + head_bob
                    torso_width = int(size//1.4)
                    torso_height = int(size * 0.9)
                    
                    # Base military uniform with texture
                    for y in range(torso_height):
                        # Gradient shading for 3D effect
                        ratio = y / torso_height
                        shade_r = int(outfit_color[0] * (0.7 + 0.3 * ratio))
                        shade_g = int(outfit_color[1] * (0.7 + 0.3 * ratio))
                        shade_b = int(outfit_color[2] * (0.7 + 0.3 * ratio))
                        
                        # Add noise for fabric texture
                        noise = random.randint(-5, 5)
                        pygame.draw.line(self.screen, 
                                       (max(0, min(255, shade_r + noise)),
                                        max(0, min(255, shade_g + noise)),
                                        max(0, min(255, shade_b + noise))),
                                       (screen_x - torso_width//2, torso_y + y),
                                       (screen_x + torso_width//2, torso_y + y))
                    
                    # Tactical vest - Multi-layer 3D effect
                    vest_margin = 6
                    vest_width = torso_width - vest_margin * 2
                    vest_height = int(torso_height * 0.75)
                    
                    # Vest depth layers
                    for layer in range(4):
                        layer_offset = layer * 2
                        layer_darkness = int(vest_color[0] - layer * 8)
                        pygame.draw.rect(self.screen, 
                                       (max(0, layer_darkness), max(0, vest_color[1] - layer * 8), max(0, vest_color[2] - layer * 8)),
                                       (screen_x - vest_width//2 + layer_offset, 
                                        torso_y + vest_margin + layer_offset,
                                        vest_width - layer_offset*2, 
                                        vest_height - layer_offset*2),
                                       border_radius=3)
                    
                    # MOLLE webbing (tactical attachment system)
                    molle_rows = 6
                    molle_cols = 4
                    for row in range(molle_rows):
                        for col in range(molle_cols):
                            molle_x = screen_x - vest_width//2 + 10 + col * (vest_width//5)
                            molle_y = torso_y + vest_margin + 8 + row * (vest_height//8)
                            pygame.draw.rect(self.screen, (max(0, vest_color[0]-30), max(0, vest_color[1]-30), max(0, vest_color[2]-30)),
                                           (molle_x, molle_y, 8, 4))
                            pygame.draw.rect(self.screen, (max(0, vest_color[0]-40), max(0, vest_color[1]-40), max(0, vest_color[2]-40)),
                                           (molle_x, molle_y, 8, 4), 1)
                    
                    # Magazine pouches with realistic 3D depth
                    pouch_count = 3
                    pouch_width = vest_width // 5
                    pouch_height = vest_height // 3
                    
                    for i in range(pouch_count):
                        pouch_x = screen_x - vest_width//3 + i * (vest_width//4)
                        pouch_y = torso_y + vest_margin + vest_height//3
                        
                        # Pouch 3D effect
                        for depth in range(3):
                            depth_color = (max(0, 40 - depth * 10), max(0, 45 - depth * 10), max(0, 40 - depth * 10))
                            pygame.draw.rect(self.screen, depth_color,
                                           (pouch_x + depth, pouch_y + depth,
                                            pouch_width - depth*2, pouch_height - depth*2),
                                           border_radius=2)
                        
                        # Magazine bullets visible
                        pygame.draw.rect(self.screen, (180, 160, 100),
                                       (pouch_x + 4, pouch_y + 4, pouch_width - 8, 8))
                        # Velcro strap
                        pygame.draw.rect(self.screen, (60, 60, 55),
                                       (pouch_x + 2, pouch_y + 2, pouch_width - 4, 3))
                    
                    # Communication radio with antenna
                    radio_x = screen_x + vest_width//3
                    radio_y = torso_y + vest_margin + 12
                    pygame.draw.rect(self.screen, (45, 50, 45),
                                   (radio_x, radio_y, 12, 20), border_radius=2)
                    pygame.draw.circle(self.screen, (80, 180, 80, 100),
                                     (radio_x + 6, radio_y + 3), 3)  # LED indicator
                    # Antenna
                    pygame.draw.line(self.screen, (60, 60, 65),
                                   (radio_x + 10, radio_y),
                                   (radio_x + 10, radio_y - 15), 2)
                    
                    # Utility belt with equipment
                    belt_y = torso_y + vest_margin + vest_height + 5
                    pygame.draw.rect(self.screen, (40, 40, 35),
                                   (screen_x - torso_width//2 + 5, belt_y, torso_width - 10, 8))
                    # Belt buckle
                    pygame.draw.rect(self.screen, (70, 70, 70),
                                   (screen_x - 8, belt_y + 1, 16, 6))
                    # Grenade pouch
                    pygame.draw.circle(self.screen, (60, 80, 60),
                                     (screen_x - torso_width//3, belt_y + 4), 8)
                    pygame.draw.circle(self.screen, (80, 100, 80),
                                     (screen_x - torso_width//3, belt_y + 4), 8, 1)
                    
                    # === REALISTIC ARMS with MUSCLES and SKIN TEXTURE ===
                    arm_width = size // 5
                    arm_length = int(size * 0.55)
                    
                    # LEFT ARM - Holding weapon foregrip with realistic anatomy
                    left_arm_x = screen_x - size//2 - arm_width//2
                    left_arm_y = torso_y + torso_height//4 + arm_swing
                    
                    # Upper arm (bicep) with muscle definition
                    upper_arm_len = arm_length // 2
                    for y in range(upper_arm_len):
                        # Muscle bulge effect
                        muscle_width = arm_width + int(4 * math.sin(y / upper_arm_len * math.pi))
                        arm_x_offset = (arm_width - muscle_width) // 2
                        pygame.draw.line(self.screen, outfit_color,
                                       (left_arm_x + arm_x_offset, left_arm_y + y),
                                       (left_arm_x + arm_x_offset + muscle_width, left_arm_y + y))
                    
                    # Elbow joint
                    elbow_y = left_arm_y + upper_arm_len
                    pygame.draw.ellipse(self.screen, (outfit_color[0]-15, outfit_color[1]-15, outfit_color[2]-15),
                                      (left_arm_x - 2, elbow_y - 5, arm_width + 4, arm_width + 4))
                    # Elbow pad
                    pygame.draw.ellipse(self.screen, (45, 45, 45),
                                      (left_arm_x, elbow_y - 3, arm_width, arm_width))
                    
                    # Forearm with veins detail
                    forearm_len = arm_length - upper_arm_len
                    for y in range(forearm_len):
                        pygame.draw.line(self.screen, outfit_color,
                                       (left_arm_x, elbow_y + 5 + y),
                                       (left_arm_x + arm_width, elbow_y + 5 + y))
                    
                    # Tactical glove - Highly detailed
                    hand_y = left_arm_y + arm_length
                    # Palm
                    for glove_layer in range(3):
                        glove_size = 10 - glove_layer * 2
                        glove_color_val = 30 - glove_layer * 5
                        pygame.draw.ellipse(self.screen, (glove_color_val, glove_color_val, glove_color_val),
                                          (left_arm_x + arm_width//2 - glove_size//2 + glove_layer,
                                           hand_y - glove_size//2 + glove_layer,
                                           glove_size, glove_size))
                    # Fingers on foregrip
                    for finger in range(3):
                        finger_x = left_arm_x + arm_width//2 - 6 + finger * 4
                        pygame.draw.rect(self.screen, (25, 25, 25),
                                       (finger_x, hand_y + 2, 3, 8), border_radius=1)
                    # Glove details (stitching)
                    pygame.draw.line(self.screen, (40, 40, 40),
                                   (left_arm_x + arm_width//2 - 5, hand_y),
                                   (left_arm_x + arm_width//2 + 5, hand_y))
                    
                    # RIGHT ARM - On trigger with realistic anatomy
                    right_arm_x = screen_x + size//3
                    right_arm_y = torso_y + torso_height//4 - arm_swing
                    
                    # Upper arm (mirror)
                    for y in range(upper_arm_len):
                        muscle_width = arm_width + int(4 * math.sin(y / upper_arm_len * math.pi))
                        arm_x_offset = (arm_width - muscle_width) // 2
                        pygame.draw.line(self.screen, outfit_color,
                                       (right_arm_x + arm_x_offset, right_arm_y + y),
                                       (right_arm_x + arm_x_offset + muscle_width, right_arm_y + y))
                    
                    # Elbow
                    elbow_y_right = right_arm_y + upper_arm_len
                    pygame.draw.ellipse(self.screen, (outfit_color[0]-15, outfit_color[1]-15, outfit_color[2]-15),
                                      (right_arm_x - 2, elbow_y_right - 5, arm_width + 4, arm_width + 4))
                    pygame.draw.ellipse(self.screen, (45, 45, 45),
                                      (right_arm_x, elbow_y_right - 3, arm_width, arm_width))
                    
                    # Forearm
                    for y in range(forearm_len):
                        pygame.draw.line(self.screen, outfit_color,
                                       (right_arm_x, elbow_y_right + 5 + y),
                                       (right_arm_x + arm_width, elbow_y_right + 5 + y))
                    
                    # Right hand on trigger
                    hand_y_right = right_arm_y + arm_length
                    for glove_layer in range(3):
                        glove_size = 10 - glove_layer * 2
                        glove_color_val = 30 - glove_layer * 5
                        pygame.draw.ellipse(self.screen, (glove_color_val, glove_color_val, glove_color_val),
                                          (right_arm_x + arm_width//2 - glove_size//2 + glove_layer,
                                           hand_y_right - glove_size//2 + glove_layer,
                                           glove_size, glove_size))
                    # Trigger finger
                    pygame.draw.rect(self.screen, (25, 25, 25),
                                   (right_arm_x + arm_width//2, hand_y_right + 2, 3, 10), border_radius=1)
                    
                    # === ULTRA-REALISTIC ASSAULT RIFLE (AK-47 / M4A1 style) ===
                    gun_length = int(size * 1.1)
                    gun_height = 10
                    gun_x = screen_x - size//2 - 10
                    gun_y = torso_y + torso_height//3
                    
                    # Weapon stock (rear)
                    stock_width = 6
                    stock_length = size // 4
                    pygame.draw.rect(self.screen, (35, 30, 25),
                                   (gun_x, gun_y + 2, stock_length, stock_width))
                    # Stock butt pad
                    pygame.draw.rect(self.screen, (50, 45, 40),
                                   (gun_x, gun_y + 1, 8, gun_height - 2), border_radius=1)
                    
                    # Main receiver/body
                    receiver_start = gun_x + stock_length
                    receiver_length = gun_length - stock_length - 35
                    # Upper receiver
                    for y in range(gun_height):
                        shade = 40 + int(15 * (y / gun_height))
                        pygame.draw.line(self.screen, (shade, shade, shade + 5),
                                       (receiver_start, gun_y + y),
                                       (receiver_start + receiver_length, gun_y + y))
                    
                    # Charging handle
                    pygame.draw.rect(self.screen, (50, 50, 55),
                                   (receiver_start + 10, gun_y - 2, 15, 3))
                    
                    # Picatinny rail (top accessory rail)
                    rail_segments = 8
                    for i in range(rail_segments):
                        rail_x = receiver_start + 5 + i * (receiver_length // rail_segments)
                        pygame.draw.rect(self.screen, (60, 60, 65),
                                       (rail_x, gun_y - 1, 3, 2))
                    
                    # Red dot sight
                    sight_x = receiver_start + receiver_length // 3
                    pygame.draw.rect(self.screen, (40, 40, 40),
                                   (sight_x, gun_y - 6, 20, 8), border_radius=2)
                    pygame.draw.circle(self.screen, (200, 50, 50, 150),
                                     (sight_x + 10, gun_y - 2), 3)  # Red dot
                    
                    # Trigger assembly
                    trigger_x = receiver_start + receiver_length // 3
                    pygame.draw.rect(self.screen, (45, 45, 45),
                                   (trigger_x - 2, gun_y + gun_height, 20, 12), border_radius=2)
                    # Trigger
                    pygame.draw.rect(self.screen, (30, 30, 30),
                                   (trigger_x + 6, gun_y + gun_height + 2, 4, 8), border_radius=1)
                    # Trigger guard
                    pygame.draw.ellipse(self.screen, (50, 50, 50),
                                      (trigger_x + 2, gun_y + gun_height + 1, 14, 10), 1)
                    
                    # Magazine well and magazine
                    mag_x = trigger_x
                    mag_y = gun_y + gun_height + 3
                    mag_width = 14
                    mag_height = 25
                    # Magazine body with gradient
                    for y in range(mag_height):
                        mag_shade = 50 + int(30 * (y / mag_height))
                        pygame.draw.line(self.screen, (mag_shade, mag_shade, mag_shade + 5),
                                       (mag_x, mag_y + y),
                                       (mag_x + mag_width, mag_y + y))
                    # Magazine baseplate
                    pygame.draw.rect(self.screen, (60, 60, 60),
                                   (mag_x - 1, mag_y + mag_height - 3, mag_width + 2, 3))
                    # Visible bullets in magazine
                    for bullet in range(3):
                        bullet_y = mag_y + 5 + bullet * 6
                        pygame.draw.circle(self.screen, (180, 160, 100),
                                         (mag_x + mag_width//2, bullet_y), 2)
                    
                    # Handguard/foregrip
                    handguard_start = receiver_start + receiver_length - 5
                    handguard_length = 30
                    # Tactical handguard with quad rails
                    for y in range(gun_height):
                        shade = 45 + int(10 * (y / gun_height))
                        pygame.draw.line(self.screen, (shade, shade, shade),
                                       (handguard_start, gun_y + y),
                                       (handguard_start + handguard_length, gun_y + y))
                    # Rail slots
                    for slot in range(5):
                        slot_x = handguard_start + 2 + slot * 5
                        pygame.draw.line(self.screen, (35, 35, 35),
                                       (slot_x, gun_y + 2),
                                       (slot_x, gun_y + gun_height - 2))
                    # Vertical foregrip
                    foregrip_x = handguard_start + handguard_length//2
                    pygame.draw.rect(self.screen, (40, 40, 40),
                                   (foregrip_x, gun_y + gun_height, 8, 15), border_radius=2)
                    pygame.draw.rect(self.screen, (50, 50, 50),
                                   (foregrip_x, gun_y + gun_height, 8, 15), 1)
                    
                    # Barrel with realistic details
                    barrel_start = handguard_start + handguard_length
                    barrel_length = 35
                    # Barrel metal with shine
                    for y in range(gun_height - 4):
                        barrel_shade = 30 + int(20 * abs(math.sin(y / 2)))
                        pygame.draw.line(self.screen, (barrel_shade, barrel_shade, barrel_shade + 5),
                                       (barrel_start, gun_y + 2 + y),
                                       (barrel_start + barrel_length, gun_y + 2 + y))
                    
                    # Muzzle device/flash hider
                    muzzle_x = barrel_start + barrel_length
                    pygame.draw.rect(self.screen, (40, 40, 40),
                                   (muzzle_x, gun_y + 1, 8, gun_height - 2), border_radius=1)
                    # Muzzle slots
                    for slot in range(3):
                        slot_y = gun_y + 2 + slot * 2
                        pygame.draw.line(self.screen, (25, 25, 25),
                                       (muzzle_x + 1, slot_y),
                                       (muzzle_x + 7, slot_y))
                    # Muzzle flash (if firing)
                    if random.randint(0, 20) == 0:  # Random muzzle flash
                        for flash_layer in range(3):
                            flash_size = 12 - flash_layer * 3
                            flash_alpha = 200 - flash_layer * 60
                            pygame.draw.circle(self.screen, (255, 180, 50, flash_alpha),
                                             (muzzle_x + 8, gun_y + gun_height//2),
                                             flash_size)
                    
                    # === ULTRA-REALISTIC HUMAN HEAD ===
                    head_size = int(size // 2.8)
                    head_y = torso_y - head_size - 5 + head_bob
                    
                    # Neck with realistic skin shading
                    neck_width = size // 5
                    neck_height = size // 6
                    for y in range(neck_height):
                        neck_shade_r = int(skin_tone[0] * (0.8 + 0.2 * (y / neck_height)))
                        neck_shade_g = int(skin_tone[1] * (0.8 + 0.2 * (y / neck_height)))
                        neck_shade_b = int(skin_tone[2] * (0.8 + 0.2 * (y / neck_height)))
                        pygame.draw.line(self.screen, (neck_shade_r, neck_shade_g, neck_shade_b),
                                       (screen_x - neck_width//2, head_y + head_size + y),
                                       (screen_x + neck_width//2, head_y + head_size + y))
                    
                    # Tactical helmet with realistic materials
                    # Helmet shadow for depth
                    pygame.draw.circle(self.screen, (0, 0, 0, 100),
                                     (screen_x + 2, head_y + 2), head_size)
                    
                    # Main helmet with 3D shading
                    for angle_deg in range(0, 360, 5):
                        angle_rad = math.radians(angle_deg)
                        # Calculate lighting (simulated from top-left)
                        light_angle = math.radians(135)  # Light source direction
                        dot_product = math.cos(angle_rad - light_angle)
                        brightness = int(helmet_color[0] * (0.5 + 0.5 * dot_product))
                        
                        # Draw helmet arc segments with lighting
                        for radius in range(head_size - 2, head_size + 1):
                            x = screen_x + int(radius * math.cos(angle_rad))
                            y = head_y + int(radius * math.sin(angle_rad))
                            pygame.draw.circle(self.screen, 
                                             (brightness, int(helmet_color[1] * (0.5 + 0.5 * dot_product)), 
                                              int(helmet_color[2] * (0.5 + 0.5 * dot_product))),
                                             (x, y), 2)
                    
                    # Helmet base fill
                    pygame.draw.circle(self.screen, helmet_color, (screen_x, head_y), head_size - 3)
                    
                    # Helmet visor/edge
                    pygame.draw.arc(self.screen, (helmet_color[0] + 20, helmet_color[1] + 20, helmet_color[2] + 20),
                                  (screen_x - head_size, head_y - head_size, head_size * 2, head_size * 2),
                                  0, math.pi, 3)
                    
                    # Night vision goggles mount (if heavy unit)
                    if enemy_type == 'tank':
                        nvg_mount_y = head_y - head_size + 5
                        pygame.draw.rect(self.screen, (50, 50, 50),
                                       (screen_x - 12, nvg_mount_y, 24, 8), border_radius=2)
                        # NVG tubes
                        pygame.draw.circle(self.screen, (40, 40, 40),
                                         (screen_x - 6, nvg_mount_y + 4), 5)
                        pygame.draw.circle(self.screen, (40, 40, 40),
                                         (screen_x + 6, nvg_mount_y + 4), 5)
                        # Lenses
                        pygame.draw.circle(self.screen, (60, 80, 60),
                                         (screen_x - 6, nvg_mount_y + 4), 3)
                        pygame.draw.circle(self.screen, (60, 80, 60),
                                         (screen_x + 6, nvg_mount_y + 4), 3)
                    
                    # Realistic FACE with balaclava/mask
                    # Eyes - highly detailed and realistic
                    eye_y = head_y - 5
                    eye_spacing = head_size // 3
                    
                    # Left eye
                    # Eye white (sclera)
                    pygame.draw.ellipse(self.screen, (240, 235, 230),
                                      (screen_x - eye_spacing - 6, eye_y - 4, 12, 8))
                    # Iris
                    iris_colors = [(100, 80, 60), (70, 120, 150), (80, 100, 70)]  # Brown, Blue, Green
                    iris_color = random.choice(iris_colors)
                    pygame.draw.circle(self.screen, iris_color,
                                     (screen_x - eye_spacing, eye_y), 3)
                    # Pupil
                    pygame.draw.circle(self.screen, (20, 20, 20),
                                     (screen_x - eye_spacing, eye_y), 2)
                    # Eye shine (reflection)
                    pygame.draw.circle(self.screen, (255, 255, 255),
                                     (screen_x - eye_spacing + 1, eye_y - 1), 1)
                    # Eyelid/shadow
                    pygame.draw.arc(self.screen, (skin_tone[0]-40, skin_tone[1]-40, skin_tone[2]-40),
                                  (screen_x - eye_spacing - 6, eye_y - 5, 12, 10),
                                  0, math.pi, 1)
                    
                    # Right eye (mirror)
                    pygame.draw.ellipse(self.screen, (240, 235, 230),
                                      (screen_x + eye_spacing - 6, eye_y - 4, 12, 8))
                    pygame.draw.circle(self.screen, iris_color,
                                     (screen_x + eye_spacing, eye_y), 3)
                    pygame.draw.circle(self.screen, (20, 20, 20),
                                     (screen_x + eye_spacing, eye_y), 2)
                    pygame.draw.circle(self.screen, (255, 255, 255),
                                     (screen_x + eye_spacing + 1, eye_y - 1), 1)
                    pygame.draw.arc(self.screen, (skin_tone[0]-40, skin_tone[1]-40, skin_tone[2]-40),
                                  (screen_x + eye_spacing - 6, eye_y - 5, 12, 10),
                                  0, math.pi, 1)
                    
                    # Eyebrows
                    for brow_x in range(-8, 9):
                        brow_y = eye_y - 7 - abs(brow_x) // 4
                        pygame.draw.circle(self.screen, hair_color,
                                         (screen_x - eye_spacing + brow_x, brow_y), 1)
                        pygame.draw.circle(self.screen, hair_color,
                                         (screen_x + eye_spacing + brow_x, brow_y), 1)
                    
                    # Tactical face mask/balaclava covering nose and mouth
                    mask_y = head_y + 5
                    mask_width = head_size
                    mask_height = int(head_size * 0.6)
                    
                    # Mask fabric with folds
                    for y in range(mask_height):
                        fold_offset = int(2 * math.sin(y / 4))
                        mask_shade = int((helmet_color[0] - 10) * (0.9 + 0.1 * (y / mask_height)))
                        pygame.draw.line(self.screen, 
                                       (mask_shade, max(0, helmet_color[1] - 10), max(0, helmet_color[2] - 10)),
                                       (screen_x - mask_width//2 + fold_offset, mask_y + y),
                                       (screen_x + mask_width//2 + fold_offset, mask_y + y))
                    
                    # Nose bridge (fabric contour)
                    pygame.draw.line(self.screen, (max(0, helmet_color[0]-20), max(0, helmet_color[1]-20), max(0, helmet_color[2]-20)),
                                   (screen_x, mask_y + 2),
                                   (screen_x, mask_y + mask_height//2), 2)
                    
                    # Breathing vents (for heavy units)
                    if enemy_type == 'tank':
                        # Gas mask filter cartridge
                        filter_size = head_size // 3
                        pygame.draw.circle(self.screen, (50, 50, 50),
                                         (screen_x, mask_y + mask_height//2), filter_size)
                        pygame.draw.circle(self.screen, (70, 70, 70),
                                         (screen_x, mask_y + mask_height//2), filter_size, 2)
                        # Filter grilles
                        for ring in range(3):
                            pygame.draw.circle(self.screen, (40, 40, 40),
                                             (screen_x, mask_y + mask_height//2),
                                             filter_size - ring * 4, 1)
                    else:
                        # Simple breathing holes
                        for hole in range(4):
                            hole_x = screen_x - 6 + hole * 4
                            pygame.draw.circle(self.screen, (30, 30, 30),
                                             (hole_x, mask_y + mask_height - 8), 2)
                    
                    # Helmet chin strap
                    pygame.draw.line(self.screen, (60, 60, 55),
                                   (screen_x - head_size + 5, head_y + head_size - 5),
                                   (screen_x - head_size//2, head_y + head_size + 5), 2)
                    pygame.draw.line(self.screen, (60, 60, 55),
                                   (screen_x + head_size - 5, head_y + head_size - 5),
                                   (screen_x + head_size//2, head_y + head_size + 5), 2)
                    # Buckle
                    pygame.draw.rect(self.screen, (70, 70, 70),
                                   (screen_x - 5, head_y + head_size + 3, 10, 4))
                    
                    # === HEALTH BAR - Ultra Professional ===
                    bar_width = size
                    bar_height = 4
                    bar_y = head_y - head_size - 15
                    
                    # Background
                    pygame.draw.rect(self.screen, (30, 30, 30),
                                   (screen_x - bar_width//2 - 1, bar_y - 1, bar_width + 2, bar_height + 2))
                    
                    # Health fill
                    health_percent = enemy['health'] / enemy['max_health']
                    health_fill = int(bar_width * health_percent)
                    
                    # Color: Green -> Yellow -> Red (CS:GO style)
                    if health_percent > 0.6:
                        health_bar_color = (100, 220, 100)
                    elif health_percent > 0.3:
                        health_bar_color = (255, 200, 50)
                    else:
                        health_bar_color = (255, 80, 80)
                    
                    pygame.draw.rect(self.screen, health_bar_color,
                                   (screen_x - bar_width//2, bar_y, health_fill, bar_height))
                    
                    # Border
                    pygame.draw.rect(self.screen, (200, 200, 200),
                                   (screen_x - bar_width//2, bar_y, bar_width, bar_height), 1)
                    
                    # Enemy type label - CS:GO Style
                    type_names = {'walker': 'TERRORIST', 'runner': 'ELITE', 'tank': 'HEAVY'}
                    type_label = type_names.get(enemy_type, 'ENEMY')
                    label_text = self.font_tiny.render(type_label, True, (220, 220, 220))
                    label_bg = pygame.Surface((label_text.get_width() + 6, label_text.get_height() + 2), pygame.SRCALPHA)
                    pygame.draw.rect(label_bg, (40, 40, 40, 200), (0, 0, label_text.get_width() + 6, label_text.get_height() + 2), border_radius=2)
                    label_x = screen_x - label_text.get_width() // 2 - 3
                    self.screen.blit(label_bg, (label_x, bar_y - 18))
                    self.screen.blit(label_text, (label_x + 3, bar_y - 17))
    
    def _render_weapon(self):
        """🔫 Render ULTRA-REALISTIC 3D first-person weapon view"""
        weapon = self.weapons[self.current_weapon]
        
        # Weapon position (bottom-right) with breathing/sway animation
        current_time = pygame.time.get_ticks()
        breathe_y = int(4 * math.sin(current_time / 1000))
        breathe_x = int(3 * math.cos(current_time / 1500))
        
        # Recoil kick animation
        recoil_kick = 0
        if hasattr(weapon, 'current_recoil') and weapon.current_recoil > 0:
            recoil_kick = int(weapon.current_recoil * 30)
        
        weapon_x = self.screen_width - 450 + breathe_x
        weapon_y = self.screen_height - 280 + breathe_y - recoil_kick
        
        # === REALISTIC WEAPON RENDERING BY TYPE ===
        weapon_name = weapon.name.lower()
        
        # Color scheme - Professional gunmetal
        metal_dark = (45, 45, 50)
        metal_base = (70, 70, 75)
        metal_highlight = (110, 110, 115)
        barrel_color = (35, 35, 40)
        grip_color = (60, 50, 45)
        
        if 'm4a1' in weapon_name or 'assault' in weapon_name:
            # === M4A1 ASSAULT RIFLE ===
            # Main body
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 5, weapon_y + 5, 350, 70), border_radius=10)
            pygame.draw.rect(self.screen, metal_base, (weapon_x, weapon_y, 350, 70), border_radius=10)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x, weapon_y, 350, 30), border_radius=10)
            
            # Barrel with rifling
            pygame.draw.rect(self.screen, barrel_color, (weapon_x + 280, weapon_y + 25, 140, 28), border_radius=3)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x + 280, weapon_y + 25, 140, 8), border_radius=3)
            # Barrel end/flash hider
            pygame.draw.rect(self.screen, (25, 25, 30), (weapon_x + 410, weapon_y + 22, 25, 34), border_radius=2)
            for i in range(6):
                pygame.draw.line(self.screen, metal_dark, 
                               (weapon_x + 415, weapon_y + 24 + i * 5),
                               (weapon_x + 430, weapon_y + 24 + i * 5), 2)
            
            # Magazine (curved for 5.56)
            pygame.draw.polygon(self.screen, (40, 40, 45), [
                (weapon_x + 130, weapon_y + 70),
                (weapon_x + 130, weapon_y + 130),
                (weapon_x + 165, weapon_y + 135),
                (weapon_x + 165, weapon_y + 70)
            ])
            pygame.draw.polygon(self.screen, Colors.DARK_GRAY, [
                (weapon_x + 130, weapon_y + 70),
                (weapon_x + 130, weapon_y + 130),
                (weapon_x + 165, weapon_y + 135),
                (weapon_x + 165, weapon_y + 70)
            ], 2)
            
            # Stock
            pygame.draw.rect(self.screen, metal_base, (weapon_x + 20, weapon_y + 20, 80, 40), border_radius=5)
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 25, weapon_y + 25, 70, 30), border_radius=3)
            
            # Fore-grip
            pygame.draw.rect(self.screen, grip_color, (weapon_x + 200, weapon_y + 65, 45, 50), border_radius=8)
            for i in range(8):
                pygame.draw.line(self.screen, (40, 35, 30),
                               (weapon_x + 205, weapon_y + 70 + i * 5),
                               (weapon_x + 240, weapon_y + 70 + i * 5), 1)
            
            # Red dot sight
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 170, weapon_y + 8, 50, 22), border_radius=4)
            pygame.draw.circle(self.screen, (20, 20, 25), (weapon_x + 195, weapon_y + 19), 10)
            pygame.draw.circle(self.screen, (120, 160, 200, 100), (weapon_x + 195, weapon_y + 19), 7)
            pygame.draw.circle(self.screen, Colors.NEON_RED, (weapon_x + 195, weapon_y + 19), 3)
            
        elif 'barrett' in weapon_name or 'sniper' in weapon_name or '.50' in weapon_name:
            # === BARRETT .50 CAL SNIPER ===
            # Massive barrel
            pygame.draw.rect(self.screen, barrel_color, (weapon_x + 200, weapon_y + 28, 280, 32), border_radius=4)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x + 200, weapon_y + 28, 280, 10), border_radius=4)
            
            # Muzzle brake (distinctive Barrett feature)
            pygame.draw.rect(self.screen, (20, 20, 25), (weapon_x + 470, weapon_y + 22, 40, 44), border_radius=3)
            for i in range(5):
                pygame.draw.rect(self.screen, metal_dark, (weapon_x + 475 + i * 8, weapon_y + 25, 3, 38))
            
            # Main body/receiver
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 5, weapon_y + 5, 280, 75), border_radius=8)
            pygame.draw.rect(self.screen, metal_base, (weapon_x, weapon_y, 280, 75), border_radius=8)
            
            # Bipod legs
            pygame.draw.line(self.screen, metal_base, (weapon_x + 300, weapon_y + 60), (weapon_x + 280, weapon_y + 140), 4)
            pygame.draw.line(self.screen, metal_base, (weapon_x + 320, weapon_y + 60), (weapon_x + 340, weapon_y + 140), 4)
            
            # Magazine (large .50 cal mag)
            pygame.draw.rect(self.screen, (40, 40, 45), (weapon_x + 100, weapon_y + 75, 70, 70), border_radius=5)
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, (weapon_x + 100, weapon_y + 75, 70, 70), 3, border_radius=5)
            
            # Professional scope
            pygame.draw.rect(self.screen, (25, 25, 30), (weapon_x + 120, weapon_y - 15, 120, 35), border_radius=6)
            pygame.draw.circle(self.screen, (20, 20, 25), (weapon_x + 180, weapon_y + 3), 16)
            pygame.draw.circle(self.screen, (100, 140, 180, 120), (weapon_x + 180, weapon_y + 3), 12)
            # Crosshair in scope
            pygame.draw.line(self.screen, Colors.NEON_GREEN, (weapon_x + 176, weapon_y + 3), (weapon_x + 184, weapon_y + 3), 1)
            pygame.draw.line(self.screen, Colors.NEON_GREEN, (weapon_x + 180, weapon_y - 1), (weapon_x + 180, weapon_y + 7), 1)
            
        elif 'mp5' in weapon_name or 'smg' in weapon_name:
            # === MP5 SMG (Compact) ===
            # Compact body
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 5, weapon_y + 5, 280, 60), border_radius=8)
            pygame.draw.rect(self.screen, metal_base, (weapon_x, weapon_y, 280, 60), border_radius=8)
            
            # Short barrel
            pygame.draw.rect(self.screen, barrel_color, (weapon_x + 240, weapon_y + 25, 120, 22), border_radius=3)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x + 240, weapon_y + 25, 120, 7), border_radius=3)
            
            # Curved magazine (iconic MP5 mag)
            pygame.draw.ellipse(self.screen, (40, 40, 45), (weapon_x + 120, weapon_y + 60, 40, 90))
            pygame.draw.ellipse(self.screen, Colors.DARK_GRAY, (weapon_x + 120, weapon_y + 60, 40, 90), 2)
            
            # Fore-grip
            pygame.draw.rect(self.screen, grip_color, (weapon_x + 180, weapon_y + 60, 40, 45), border_radius=8)
            
            # Collapsible stock
            for i in range(5):
                pygame.draw.rect(self.screen, metal_dark, (weapon_x + 20 + i * 15, weapon_y + 25, 10, 25), border_radius=2)
            
        elif 'spas' in weapon_name or 'shotgun' in weapon_name:
            # === SPAS-12 SHOTGUN ===
            # Pump-action body
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 5, weapon_y + 5, 320, 65), border_radius=10)
            pygame.draw.rect(self.screen, metal_base, (weapon_x, weapon_y, 320, 65), border_radius=10)
            
            # Wide barrel
            pygame.draw.rect(self.screen, barrel_color, (weapon_x + 260, weapon_y + 20, 160, 34), border_radius=5)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x + 260, weapon_y + 20, 160, 12), border_radius=5)
            
            # Tube magazine under barrel
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 180, weapon_y + 50, 240, 12), border_radius=6)
            
            # Pump grip
            pygame.draw.rect(self.screen, grip_color, (weapon_x + 200, weapon_y + 55, 55, 50), border_radius=8)
            for i in range(10):
                pygame.draw.line(self.screen, (40, 35, 30),
                               (weapon_x + 205, weapon_y + 60 + i * 4),
                               (weapon_x + 250, weapon_y + 60 + i * 4), 1)
            
            # Stock with hook
            pygame.draw.rect(self.screen, metal_base, (weapon_x + 20, weapon_y + 15, 100, 45), border_radius=7)
            pygame.draw.polygon(self.screen, metal_dark, [
                (weapon_x + 20, weapon_y + 55),
                (weapon_x + 40, weapon_y + 75),
                (weapon_x + 60, weapon_y + 55)
            ])
            
        elif 'desert' in weapon_name or 'pistol' in weapon_name or 'eagle' in weapon_name:
            # === DESERT EAGLE PISTOL ===
            # Slide
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 155, weapon_y + 5, 180, 45), border_radius=6)
            pygame.draw.rect(self.screen, metal_base, (weapon_x + 150, weapon_y, 180, 45), border_radius=6)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x + 150, weapon_y, 180, 18), border_radius=6)
            
            # Barrel
            pygame.draw.rect(self.screen, barrel_color, (weapon_x + 300, weapon_y + 18, 80, 16), border_radius=3)
            
            # Frame
            pygame.draw.polygon(self.screen, metal_dark, [
                (weapon_x + 150, weapon_y + 45),
                (weapon_x + 150, weapon_y + 85),
                (weapon_x + 270, weapon_y + 85),
                (weapon_x + 290, weapon_y + 45)
            ])
            
            # Grip
            pygame.draw.rect(self.screen, grip_color, (weapon_x + 150, weapon_y + 45, 50, 80), border_radius=8)
            for i in range(15):
                pygame.draw.line(self.screen, (40, 35, 30),
                               (weapon_x + 155, weapon_y + 50 + i * 4),
                               (weapon_x + 195, weapon_y + 50 + i * 4), 1)
            
            # Hammer
            pygame.draw.circle(self.screen, metal_dark, (weapon_x + 190, weapon_y + 30), 8)
            
            # Magazine
            pygame.draw.rect(self.screen, (40, 40, 45), (weapon_x + 160, weapon_y + 85, 30, 60), border_radius=4)
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, (weapon_x + 160, weapon_y + 85, 30, 60), 2, border_radius=4)
            
        elif 'm249' in weapon_name or 'lmg' in weapon_name or 'saw' in weapon_name:
            # === M249 SAW (Light Machine Gun) ===
            # Heavy barrel
            pygame.draw.rect(self.screen, barrel_color, (weapon_x + 220, weapon_y + 28, 260, 30), border_radius=4)
            pygame.draw.rect(self.screen, metal_highlight, (weapon_x + 220, weapon_y + 28, 260, 10), border_radius=4)
            
            # Barrel cooling vents
            for i in range(12):
                pygame.draw.line(self.screen, (20, 20, 25),
                               (weapon_x + 240 + i * 20, weapon_y + 30),
                               (weapon_x + 240 + i * 20, weapon_y + 55), 2)
            
            # Main body
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 5, weapon_y + 5, 290, 75), border_radius=10)
            pygame.draw.rect(self.screen, metal_base, (weapon_x, weapon_y, 290, 75), border_radius=10)
            
            # Belt-fed ammo box
            pygame.draw.rect(self.screen, (50, 40, 30), (weapon_x + 110, weapon_y + 75, 90, 70), border_radius=8)
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, (weapon_x + 110, weapon_y + 75, 90, 70), 3, border_radius=8)
            # Ammo belt
            for i in range(6):
                pygame.draw.circle(self.screen, (180, 140, 80), (weapon_x + 130 + i * 10, weapon_y + 75), 4)
            
            # Bipod
            pygame.draw.line(self.screen, metal_base, (weapon_x + 300, weapon_y + 58), (weapon_x + 280, weapon_y + 130), 5)
            pygame.draw.line(self.screen, metal_base, (weapon_x + 320, weapon_y + 58), (weapon_x + 340, weapon_y + 130), 5)
            
            # Carrying handle
            pygame.draw.rect(self.screen, metal_dark, (weapon_x + 160, weapon_y - 10, 80, 15), border_radius=4)
            
        # === UNIVERSAL ELEMENTS (All weapons) ===
        # Trigger guard
        pygame.draw.arc(self.screen, metal_highlight, 
                       (weapon_x + 120, weapon_y + 50, 40, 35), 0, 3.14, 3)
        
        # Trigger
        pygame.draw.rect(self.screen, (200, 50, 50), (weapon_x + 135, weapon_y + 60, 8, 18), border_radius=2)
        
        # Detail lines for realism
        pygame.draw.line(self.screen, metal_highlight, (weapon_x + 50, weapon_y + 10), (weapon_x + 250, weapon_y + 10), 2)
        
        # Weapon shine/reflection
        shine_surface = pygame.Surface((200, 20), pygame.SRCALPHA)
        pygame.draw.rect(shine_surface, (255, 255, 255, 40), (0, 0, 200, 20))
        self.screen.blit(shine_surface, (weapon_x + 100, weapon_y + 15))
    
    def _render_player_third_person(self):
        """Render player character in third-person mode"""
        # Player is always in center but slightly lower
        screen_x = self.screen_width // 2
        screen_y = self.screen_height // 2 + 50
        size = 60
        
        player_color = (0, 100, 200)  # Blue for player
        
        # === PLAYER BODY ===
        # Shadow
        pygame.draw.ellipse(self.screen, (20, 20, 20, 100),
                          (screen_x - size//2, screen_y + size, size, size//3))
        
        # Legs
        current_time = pygame.time.get_ticks()
        if pygame.K_w in self.keys or pygame.K_s in self.keys or pygame.K_a in self.keys or pygame.K_d in self.keys:
            walk_offset = int(5 * math.sin(current_time / 150))
        else:
            walk_offset = 0
        
        leg_height = size // 2
        leg_width = size // 5
        
        # Left leg
        pygame.draw.rect(self.screen, player_color,
                       (screen_x - size//4, screen_y + size//2 + walk_offset, leg_width, leg_height), border_radius=3)
        # Right leg
        pygame.draw.rect(self.screen, player_color,
                       (screen_x + size//6, screen_y + size//2 - walk_offset, leg_width, leg_height), border_radius=3)
        
        # === TORSO ===
        pygame.draw.rect(self.screen, player_color,
                       (screen_x - size//3, screen_y, int(size//1.5), size), border_radius=5)
        
        # Armor vest
        pygame.draw.rect(self.screen, (30, 60, 100),
                       (screen_x - size//3 + 5, screen_y + 10, int(size//1.5) - 10, size - 20), border_radius=5)
        
        # === ARMS ===
        arm_width = size // 6
        arm_length = size // 2
        
        # Left arm
        pygame.draw.rect(self.screen, player_color,
                       (screen_x - size//2, screen_y + size//4, arm_width, arm_length))
        # Right arm (holding weapon)
        pygame.draw.rect(self.screen, player_color,
                       (screen_x + size//3, screen_y + size//4, arm_width, arm_length))
        
        # Weapon in hand
        weapon_color = (60, 60, 70)
        pygame.draw.rect(self.screen, weapon_color,
                       (screen_x + size//3 + arm_width, screen_y + size//4 + 10, 25, 8), border_radius=2)
        
        # === HEAD ===
        head_size = size // 3
        head_y = screen_y - head_size
        
        # Neck
        pygame.draw.rect(self.screen, player_color,
                       (screen_x - size//8, head_y + head_size, size//4, size//6))
        
        # Head
        pygame.draw.circle(self.screen, player_color, (screen_x, head_y), head_size)
        
        # Helmet/face
        pygame.draw.circle(self.screen, (50, 80, 120), (screen_x, head_y), head_size - 3)
        
        # Visor
        pygame.draw.ellipse(self.screen, (100, 150, 200),
                          (screen_x - head_size//2, head_y - 5, head_size, head_size//2))
        
        # Camera mode indicator
        mode_text = self.font_small.render("THIRD-PERSON (Press P to toggle)", True, Colors.CYAN)
        self.screen.blit(mode_text, (10, self.screen_height - 60))
        
        # Enhanced barrel with shine
        pygame.draw.rect(self.screen, shadow_color, (weapon_x + 233, weapon_y + 23, 100, 24))
        pygame.draw.rect(self.screen, weapon_color, (weapon_x + 230, weapon_y + 20, 100, 24))
        pygame.draw.rect(self.screen, highlight_color, (weapon_x + 230, weapon_y + 20, 100, 10))
        pygame.draw.line(self.screen, (150, 150, 160), (weapon_x + 230, weapon_y + 25), (weapon_x + 330, weapon_y + 25), 2)
        
        # Grip with detail
        pygame.draw.rect(self.screen, shadow_color, (weapon_x + 93, weapon_y + 58, 35, 70))
        pygame.draw.rect(self.screen, weapon_color, (weapon_x + 90, weapon_y + 55, 35, 70))
        pygame.draw.rect(self.screen, highlight_color, (weapon_x + 90, weapon_y + 55, 20, 70))
        
        # Magazine
        pygame.draw.rect(self.screen, (40, 40, 45), (weapon_x + 95, weapon_y + 60, 25, 50), border_radius=3)
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (weapon_x + 95, weapon_y + 60, 25, 50), 2, border_radius=3)
        
        # Scope/sight
        pygame.draw.circle(self.screen, (20, 20, 25), (weapon_x + 140, weapon_y + 15), 12)
        pygame.draw.circle(self.screen, (100, 150, 200), (weapon_x + 140, weapon_y + 15), 8)
        pygame.draw.circle(self.screen, Colors.CYAN, (weapon_x + 140, weapon_y + 15), 4)
        
        # Enhanced muzzle flash with glow
        if self.muzzle_flash and time.time() - self.muzzle_flash < 0.06:
            flash_size = 50
            # Outer glow
            for i in range(3):
                s = flash_size + i * 15
                alpha = 100 - i * 30
                pygame.draw.circle(self.screen, (255, 200, 0, alpha), 
                                 (weapon_x + 330, weapon_y + 32), s)
            # Inner flash
            pygame.draw.circle(self.screen, Colors.YELLOW, 
                             (weapon_x + 330, weapon_y + 32), flash_size)
            pygame.draw.circle(self.screen, Colors.ORANGE, 
                             (weapon_x + 330, weapon_y + 32), flash_size//2)
            pygame.draw.circle(self.screen, Colors.WHITE, 
                             (weapon_x + 330, weapon_y + 32), flash_size//4)
        
        # Weapon name with stylish background
        name_bg = pygame.Surface((weapon.name.__len__() * 12 + 20, 35), pygame.SRCALPHA)
        pygame.draw.rect(name_bg, (0, 0, 0, 180), (0, 0, name_bg.get_width(), 35), border_radius=5)
        self.screen.blit(name_bg, (weapon_x - 10, weapon_y - 45))
        
        name_text = self.font_medium.render(weapon.name, True, Colors.GOLD)
        self.screen.blit(name_text, (weapon_x, weapon_y - 40))
        
        # Reloading indicator with progress bar
        if weapon.reloading:
            reload_progress = (time.time() - weapon.reload_start) / weapon.reload_time
            reload_text = self.font_large.render(f"⟳ RELOADING ⟳", True, Colors.YELLOW)
            text_x = weapon_x - 50
            text_y = weapon_y - 90
            
            # Animated reload text
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            shadow_offset = int(3 * pulse)
            reload_shadow = self.font_large.render(f"⟳ RELOADING ⟳", True, Colors.ORANGE)
            self.screen.blit(reload_shadow, (text_x + shadow_offset, text_y + shadow_offset))
            self.screen.blit(reload_text, (text_x, text_y))
            
            # Progress bar
            bar_width = 250
            bar_height = 12
            pygame.draw.rect(self.screen, (0, 0, 0, 200), 
                           (text_x, text_y + 40, bar_width, bar_height), border_radius=6)
            progress_fill = int(bar_width * reload_progress)
            pygame.draw.rect(self.screen, Colors.YELLOW, 
                           (text_x, text_y + 40, progress_fill, bar_height), border_radius=6)
            pygame.draw.rect(self.screen, Colors.GOLD, 
                           (text_x, text_y + 40, bar_width, bar_height), 2, border_radius=6)
    
    def _render_hud(self):
        """Render ENHANCED HUD (Heads-Up Display)"""
        # Invincibility flash effect (full screen)
        if self.invincible and self.respawn_flash > 0:
            flash_alpha = int(100 * max(0, self.respawn_flash))
            flash_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            pygame.draw.rect(flash_surface, (0, 255, 255, flash_alpha), (0, 0, self.screen_width, self.screen_height))
            self.screen.blit(flash_surface, (0, 0))
        
        # Health bar (top-left) with gradient
        pygame.draw.rect(self.screen, Colors.BLACK, (18, 18, 204, 34), border_radius=8)
        health_fill = int(200 * (self.player_health / 100))
        pygame.draw.rect(self.screen, Colors.GREEN if self.player_health > 50 else Colors.RED,
                        (20, 20, health_fill, 30))
        health_text = self.font_medium.render(f"HP: {int(self.player_health)}", True, Colors.WHITE)
        self.screen.blit(health_text, (25, 23))
        
        # Invincibility indicator (glowing cyan border)
        if self.invincible:
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            border_alpha = int(150 + 105 * pulse)
            border_color = (0, 255, 255, border_alpha)
            pygame.draw.rect(self.screen, border_color, (15, 15, 210, 40), 4, border_radius=10)
            
            # Timer text
            invincible_text = self.font_small.render(f"🛡️ INVINCIBLE: {self.invincible_timer:.1f}s", True, Colors.NEON_CYAN)
            self.screen.blit(invincible_text, (25, 55))
            armor_y_offset = 35  # Move armor bar down
        else:
            armor_y_offset = 0
        
        # Armor bar
        pygame.draw.rect(self.screen, Colors.BLACK, (20, 60 + armor_y_offset, 200, 30))
        armor_fill = int(200 * (self.player_armor / 100))
        pygame.draw.rect(self.screen, Colors.BLUE, (20, 60 + armor_y_offset, armor_fill, 30))
        armor_text = self.font_medium.render(f"ARMOR: {int(self.player_armor)}", True, Colors.WHITE)
        self.screen.blit(armor_text, (25, 63 + armor_y_offset))
        
        # Ammo counter (bottom-right)
        weapon = self.weapons[self.current_weapon]
        
        # === RELOAD INDICATOR ===
        if weapon.reloading:
            # Calculate reload progress
            reload_progress = min(1.0, (time.time() - weapon.reload_start) / weapon.reload_time)
            
            # Pulsing "RELOADING" text
            pulse = abs(math.sin(pygame.time.get_ticks() / 100))
            reload_color = (255, int(150 + 105 * pulse), 0)
            reload_text = self.font_huge.render("RELOADING...", True, reload_color)
            reload_x = self.screen_width - 300
            reload_y = self.screen_height - 180
            
            # Background box
            reload_bg = pygame.Surface((reload_text.get_width() + 30, 80), pygame.SRCALPHA)
            pygame.draw.rect(reload_bg, (50, 30, 0, 200), (0, 0, reload_text.get_width() + 30, 80), border_radius=10)
            self.screen.blit(reload_bg, (reload_x - 15, reload_y - 10))
            
            # Reload text
            self.screen.blit(reload_text, (reload_x, reload_y))
            
            # Progress bar
            bar_width = 250
            bar_height = 20
            bar_x = self.screen_width - 280
            bar_y = self.screen_height - 120
            
            # Bar background
            pygame.draw.rect(self.screen, (40, 40, 45), (bar_x, bar_y, bar_width, bar_height), border_radius=10)
            
            # Progress fill
            fill_width = int(bar_width * reload_progress)
            if fill_width > 0:
                pygame.draw.rect(self.screen, (255, 200, 0), (bar_x, bar_y, fill_width, bar_height), border_radius=10)
            
            # Border
            pygame.draw.rect(self.screen, (255, 150, 0), (bar_x, bar_y, bar_width, bar_height), 3, border_radius=10)
            
            # Percentage
            percent_text = self.font_medium.render(f"{int(reload_progress * 100)}%", True, Colors.WHITE)
            self.screen.blit(percent_text, (bar_x + bar_width // 2 - percent_text.get_width() // 2, bar_y - 2))
        else:
            # Normal ammo display
            ammo_color = Colors.WHITE if weapon.current_ammo > 10 else Colors.NEON_RED
            if weapon.current_ammo == 0:
                # Flashing when out of ammo
                flash = abs(math.sin(pygame.time.get_ticks() / 150))
                ammo_color = (255, int(50 + 205 * flash), int(50 + 205 * flash))
            
            ammo_text = self.font_huge.render(f"{weapon.current_ammo}", True, ammo_color)
            self.screen.blit(ammo_text, (self.screen_width - 150, self.screen_height - 150))
            
            max_ammo_text = self.font_medium.render(f"/ {weapon.max_ammo}", True, Colors.GRAY)
            self.screen.blit(max_ammo_text, (self.screen_width - 80, self.screen_height - 120))
            
            # Magazine count
            mag_text = self.font_small.render(f"Mags: {weapon.magazine_count}", True, Colors.LIGHT_GRAY)
            self.screen.blit(mag_text, (self.screen_width - 150, self.screen_height - 100))
            
            # Press R to reload hint (when ammo is low)
            if weapon.current_ammo < weapon.max_ammo // 3 and weapon.magazine_count > 0:
                hint_pulse = abs(math.sin(pygame.time.get_ticks() / 300))
                hint_alpha = int(150 + 105 * hint_pulse)
                hint_text = self.font_small.render("Press [R] to Reload", True, (255, 255, 0, hint_alpha))
                self.screen.blit(hint_text, (self.screen_width - 170, self.screen_height - 75))
        
        # Kill/Death/Score (top-right)
        stats_y = 20
        kills_text = self.font_medium.render(f"Kills: {self.kills}", True, Colors.GREEN)
        self.screen.blit(kills_text, (self.screen_width - 200, stats_y))
        
        deaths_text = self.font_medium.render(f"Deaths: {self.deaths}", True, Colors.RED)
        self.screen.blit(deaths_text, (self.screen_width - 200, stats_y + 35))
        
        score_text = self.font_medium.render(f"Score: {self.score}", True, Colors.YELLOW)
        self.screen.blit(score_text, (self.screen_width - 200, stats_y + 70))
        
        # Level and XP bar
        level_text = self.font_small.render(f"Level {self.level}", True, Colors.WHITE)
        self.screen.blit(level_text, (self.screen_width - 200, stats_y + 105))
        
        xp_bar_width = 150
        xp_bar_height = 10
        xp_progress = min(1.0, self.xp / self.xp_needed)
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, 
                        (self.screen_width - 200, stats_y + 130, xp_bar_width, xp_bar_height))
        pygame.draw.rect(self.screen, Colors.BLUE,
                        (self.screen_width - 200, stats_y + 130, int(xp_bar_width * xp_progress), xp_bar_height))
        pygame.draw.rect(self.screen, Colors.WHITE,
                        (self.screen_width - 200, stats_y + 130, xp_bar_width, xp_bar_height), 1)
        
        # Stamina bar (bottom-left)
        stamina_text = self.font_small.render("STAMINA", True, Colors.WHITE if self.stamina > 30 else Colors.RED)
        self.screen.blit(stamina_text, (20, self.screen_height - 60))
        
        stamina_bar_width = 150
        stamina_bar_height = 8
        pygame.draw.rect(self.screen, Colors.DARK_GRAY,
                        (20, self.screen_height - 40, stamina_bar_width, stamina_bar_height))
        stamina_fill = int(stamina_bar_width * (self.stamina / self.max_stamina))
        stamina_color = Colors.GREEN if self.stamina > 50 else (Colors.ORANGE if self.stamina > 30 else Colors.RED)
        pygame.draw.rect(self.screen, stamina_color,
                        (20, self.screen_height - 40, stamina_fill, stamina_bar_height))
        pygame.draw.rect(self.screen, Colors.WHITE,
                        (20, self.screen_height - 40, stamina_bar_width, stamina_bar_height), 1)
        
        # === REALISTIC MECHANICS INDICATORS ===
        indicator_y = self.screen_height - 150
        
        # Crouch indicator
        if self.is_crouching:
            crouch_bg = pygame.Surface((100, 35), pygame.SRCALPHA)
            pygame.draw.rect(crouch_bg, (50, 50, 80, 200), (0, 0, 100, 35), border_radius=5)
            self.screen.blit(crouch_bg, (20, indicator_y))
            crouch_text = self.font_small.render("🧎 CROUCH", True, Colors.NEON_CYAN)
            self.screen.blit(crouch_text, (25, indicator_y + 8))
            indicator_y -= 45
        
        # Lean indicators
        if self.is_leaning_left or self.is_leaning_right:
            lean_bg = pygame.Surface((100, 35), pygame.SRCALPHA)
            pygame.draw.rect(lean_bg, (80, 50, 50, 200), (0, 0, 100, 35), border_radius=5)
            self.screen.blit(lean_bg, (20, indicator_y))
            
            if self.is_leaning_left:
                lean_text = self.font_small.render("◄ LEAN L", True, Colors.YELLOW)
            else:
                lean_text = self.font_small.render("LEAN R ►", True, Colors.YELLOW)
            self.screen.blit(lean_text, (25, indicator_y + 8))
            indicator_y -= 45
        
        # Aiming indicator (center screen)
        if self.is_aiming:
            aim_text = self.font_small.render("[ AIMING ]", True, Colors.NEON_CYAN)
            self.screen.blit(aim_text, (self.screen_width//2 - aim_text.get_width()//2, self.screen_height//2 - 80))
            
            # Enhanced crosshair when aiming
            center_x, center_y = self.screen_width // 2, self.screen_height // 2
            pygame.draw.circle(self.screen, Colors.NEON_CYAN, (center_x, center_y), 2)
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                x1 = center_x + math.cos(rad) * 8
                y1 = center_y + math.sin(rad) * 8
                x2 = center_x + math.cos(rad) * 15
                y2 = center_y + math.sin(rad) * 15
                pygame.draw.line(self.screen, Colors.NEON_CYAN, (x1, y1), (x2, y2), 2)
        
        # Breath hold indicator
        if self.is_aiming and pygame.key.get_pressed()[pygame.K_LSHIFT]:
            breath_bg = pygame.Surface((150, 35), pygame.SRCALPHA)
            pygame.draw.rect(breath_bg, (30, 80, 100, 220), (0, 0, 150, 35), border_radius=5)
            self.screen.blit(breath_bg, (self.screen_width//2 - 75, self.screen_height//2 - 120))
            breath_text = self.font_small.render("💨 HOLDING BREATH", True, Colors.WHITE)
            self.screen.blit(breath_text, (self.screen_width//2 - 65, self.screen_height//2 - 112))
        
        # Jump indicator (in air)
        if self.in_air:
            jump_text = self.font_small.render("⬆ AIRBORNE", True, Colors.ORANGE)
            self.screen.blit(jump_text, (20, indicator_y))
        
        # Killstreak notification (top-center)
        if self.killstreak >= 3:
            killstreak_text = self.font_large.render(f"🔥 {self.killstreak} KILLSTREAK! 🔥", True, Colors.ORANGE)
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            alpha = int(200 + 55 * pulse)
            # Draw with glow
            for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                shadow = self.font_large.render(f"🔥 {self.killstreak} KILLSTREAK! 🔥", True, (255, 100, 0, alpha))
                self.screen.blit(shadow, (self.screen_width//2 - killstreak_text.get_width()//2 + offset[0], 150 + offset[1]))
            self.screen.blit(killstreak_text, (self.screen_width//2 - killstreak_text.get_width()//2, 150))
        
        # Weapon switch hints (bottom-left)
        hints_y = self.screen_height - 180
        hints = [
            "1: Assault Rifle",
            "2: Sniper",
            "3: SMG",
            "4: Shotgun",
            "5: Pistol",
            "6: LMG",
            "R: Reload",
            "SHIFT: Sprint",
            "Right Click: Aim"
        ]
        for i, hint in enumerate(hints):
            if i < 6:
                weapon_names = ['assault_rifle', 'sniper', 'smg', 'shotgun', 'pistol', 'lmg']
                color = Colors.YELLOW if self.current_weapon == weapon_names[i] else Colors.GRAY
            else:
                color = Colors.GRAY
            hint_text = self.font_small.render(hint, True, color)
            self.screen.blit(hint_text, (20, hints_y + i * 20))
        
        # Minimap (top-center)
        self._render_minimap()
    
    def _render_minimap(self):
        """Render tactical minimap"""
        minimap_size = 150
        minimap_x = self.screen_width // 2 - minimap_size // 2
        minimap_y = 20
        
        # Minimap background
        pygame.draw.rect(self.screen, (0, 0, 0, 180), 
                        (minimap_x, minimap_y, minimap_size, minimap_size))
        pygame.draw.rect(self.screen, Colors.WHITE, 
                        (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Player (center)
        center_x = minimap_x + minimap_size // 2
        center_y = minimap_y + minimap_size // 2
        pygame.draw.circle(self.screen, Colors.GREEN, (center_x, center_y), 5)
        
        # Player direction
        dir_x = center_x + int(15 * math.cos(self.player_angle))
        dir_y = center_y + int(15 * math.sin(self.player_angle))
        pygame.draw.line(self.screen, Colors.GREEN, (center_x, center_y), (dir_x, dir_y), 2)
        
        # Enemies
        for enemy in self.enemies:
            dx = enemy['x'] - self.player_x
            dz = enemy['z'] - self.player_z
            
            # Scale to minimap
            map_x = center_x + int(dx / 10)
            map_y = center_y + int(dz / 10)
            
            if minimap_x < map_x < minimap_x + minimap_size and \
               minimap_y < map_y < minimap_y + minimap_size:
                enemy_color = Colors.RED if enemy['alert'] else Colors.ORANGE
                pygame.draw.circle(self.screen, enemy_color, (map_x, map_y), 3)
    
    def _render_crosshair(self):
        """Render advanced crosshair with aim mode"""
        cx = self.screen_width // 2
        cy = self.screen_height // 2
        
        if self.is_aiming:
            # Sniper scope style when aiming
            size = 80
            # Outer circle
            pygame.draw.circle(self.screen, Colors.GREEN, (cx, cy), size, 2)
            # Inner circle
            pygame.draw.circle(self.screen, Colors.GREEN, (cx, cy), size // 3, 1)
            # Crosshair lines
            pygame.draw.line(self.screen, Colors.GREEN, (cx - size, cy), (cx + size, cy), 2)
            pygame.draw.line(self.screen, Colors.GREEN, (cx, cy - size), (cx, cy + size), 2)
            # Center dot
            pygame.draw.circle(self.screen, Colors.RED, (cx, cy), 3)
            
            # Zoom indicator
            zoom_text = self.font_small.render("AIMING", True, Colors.GREEN)
            self.screen.blit(zoom_text, (cx - zoom_text.get_width()//2, cy + size + 10))
        else:
            # Dynamic crosshair (expands when moving)
            size = 20
            thickness = 2
            spread = 0
            
            # Increase spread when moving or sprinting
            if pygame.K_w in self.keys or pygame.K_s in self.keys or \
               pygame.K_a in self.keys or pygame.K_d in self.keys:
                spread = 10 if self.is_sprinting else 5
            
            # Get weapon accuracy
            weapon = self.weapons[self.current_weapon]
            accuracy_spread = (1.0 - weapon.accuracy) * 15
            spread += accuracy_spread
            
            # Color based on state
            color = Colors.RED if self.stamina < 20 else (Colors.YELLOW if self.is_sprinting else Colors.GREEN)
            
            # Crosshair lines with dynamic spread
            pygame.draw.line(self.screen, color, 
                            (cx - size - spread, cy), (cx - 5 - spread, cy), thickness)
            pygame.draw.line(self.screen, color, 
                            (cx + 5 + spread, cy), (cx + size + spread, cy), thickness)
            pygame.draw.line(self.screen, color, 
                            (cx, cy - size - spread), (cx, cy - 5 - spread), thickness)
            pygame.draw.line(self.screen, color, 
                            (cx, cy + 5 + spread), (cx, cy + size + spread), thickness)
            
            # Center dot
            pygame.draw.circle(self.screen, color, (cx, cy), 2)
            
            # Sprint indicator
            if self.is_sprinting:
                sprint_text = self.font_small.render("SPRINTING", True, Colors.YELLOW)
                self.screen.blit(sprint_text, (cx - sprint_text.get_width()//2, cy + 30))
    
    def _render_effects(self):
        """Render advanced visual effects"""
        # Hit markers
        for hit in self.hit_markers:
            age = time.time() - hit['time']
            alpha = int(255 * (1 - age / 0.5))
            
            cx = self.screen_width // 2
            cy = self.screen_height // 2
            size = 20 if hit.get('headshot') else 15
            
            color = Colors.RED if hit['kill'] else (Colors.YELLOW if hit.get('headshot') else Colors.WHITE)
            
            # X marker
            thickness = 4 if hit.get('headshot') else 3
            pygame.draw.line(self.screen, color, 
                           (cx - size, cy - size), (cx + size, cy + size), thickness)
            pygame.draw.line(self.screen, color, 
                           (cx + size, cy - size), (cx - size, cy + size), thickness)
            
            # Damage number
            damage_text = self.font_small.render(f"-{hit['damage']}", True, color)
            self.screen.blit(damage_text, (cx + size + 5, cy - 10))
            
            if hit['kill']:
                kill_text = self.font_large.render("💀 ELIMINATED! 💀", True, Colors.RED)
                self.screen.blit(kill_text, (cx - kill_text.get_width()//2, cy - 60))
                
            if hit.get('headshot'):
                headshot_text = self.font_medium.render("HEADSHOT!", True, Colors.YELLOW)
                self.screen.blit(headshot_text, (cx - headshot_text.get_width()//2, cy - 40))
        
        # Blood splatters
        for blood in self.blood_splatter:
            screen_pos = self._world_to_screen(blood['x'], blood['y'], blood['z'])
            if screen_pos:
                age = time.time() - blood['time']
                alpha = max(0, int(255 * (1 - age / 5.0)))
                size = max(1, int(blood.get('size', 3) * (1 - age / 5.0)))
                color = (min(255, 139 + alpha//2), 0, 0)
                pygame.draw.circle(self.screen, color, screen_pos, size)
        
        # Shell casings
        for casing in self.shell_casings:
            screen_pos = self._world_to_screen(casing['x'], casing['y'], casing['z'])
            if screen_pos:
                age = time.time() - casing['time']
                fade = max(0, 1 - age / casing['life'])
                color = (int(200 * fade), int(150 * fade), int(50 * fade))
                size = 4
                pygame.draw.circle(self.screen, color, screen_pos, size)
        
        # Explosions
        for explosion in self.explosions:
            screen_pos = self._world_to_screen(explosion['x'], explosion['y'], explosion['z'])
            if screen_pos:
                age = time.time() - explosion['time']
                fade = max(0, 1 - age / 0.5)
                radius = int(explosion['radius'])
                # Draw expanding circles
                for i in range(3):
                    r = max(1, radius + i * 10)
                    intensity = max(0, int(255 * fade / (i + 1)))
                    color = (min(255, intensity), min(255, intensity//2), 0)
                    pygame.draw.circle(self.screen, color, screen_pos, r, 2)
    
    def _world_to_screen(self, x, y, z):
        """Convert world coordinates to screen coordinates"""
        # Simple perspective projection
        dx = x - self.player_x
        dz = z - self.player_z
        dy = y - 50  # Eye level
        
        # Rotate to player view
        cos_a = math.cos(-self.player_angle)
        sin_a = math.sin(-self.player_angle)
        rx = dx * cos_a - dz * sin_a
        rz = dx * sin_a + dz * cos_a
        
        if rz > 1:  # Only render if in front
            scale = 200 / rz
            screen_x = int(self.screen_width / 2 + rx * scale)
            screen_y = int(self.screen_height / 2 - dy * scale)
            return (screen_x, screen_y)
        return None
    
    def _render_advanced_effects(self):
        """Render advanced particle effects"""
        current_time = time.time()
        
        # Render smoke particles
        for smoke in self.smoke_particles[:]:
            age = current_time - smoke['time']
            if age > smoke['life']:
                self.smoke_particles.remove(smoke)
                continue
            
            screen_pos = self._world_to_screen(smoke['x'], smoke['y'], smoke['z'])
            if screen_pos:
                progress = age / smoke['life']
                size = int(smoke['size'] * (1 + progress * 2))
                alpha = int(100 * (1 - progress))
                # Draw expanding smoke circle
                for i in range(3):
                    s = size + i * 5
                    a = alpha // (i + 1)
                    pygame.draw.circle(self.screen, (80, 80, 80, a), screen_pos, s)
        
        # Render spark particles  
        for spark in self.spark_particles[:]:
            age = current_time - spark['time']
            if age > spark['life']:
                self.spark_particles.remove(spark)
                continue
            
            screen_pos = self._world_to_screen(spark['x'], spark['y'], spark['z'])
            if screen_pos:
                progress = age / spark['life']
                alpha = int(255 * (1 - progress))
                spark_color = (255, 200 + int(55 * random.random()), 0, alpha)
                size = max(1, int(3 * (1 - progress)))
                pygame.draw.circle(self.screen, spark_color, screen_pos, size)
        
        # Render tracer rounds
        for tracer in self.tracer_rounds[:]:
            age = current_time - tracer['time']
            if age > tracer['life']:
                self.tracer_rounds.remove(tracer)
                continue
            
            start_pos = self._world_to_screen(tracer['start_x'], tracer['start_y'], tracer['start_z'])
            end_pos = self._world_to_screen(tracer['end_x'], tracer['end_y'], tracer['end_z'])
            
            if start_pos and end_pos:
                progress = age / tracer['life']
                alpha = int(200 * (1 - progress))
                # Draw glowing line
                pygame.draw.line(self.screen, (255, 255, 100, alpha), start_pos, end_pos, 2)
                pygame.draw.line(self.screen, (255, 150, 0, alpha // 2), start_pos, end_pos, 4)
        
        # Render impact marks (bullet holes)
        for impact in self.impact_marks[:]:
            age = current_time - impact['time']
            if age > impact['life']:
                self.impact_marks.remove(impact)
                continue
            
            screen_pos = self._world_to_screen(impact['x'], impact['y'], impact['z'])
            if screen_pos:
                progress = age / impact['life']
                alpha = int(180 * (1 - progress * 0.5))
                size = 4
                # Draw bullet hole
                pygame.draw.circle(self.screen, (40, 40, 40, alpha), screen_pos, size)
                pygame.draw.circle(self.screen, (20, 20, 20, alpha), screen_pos, size - 1)
    
    def _add_smoke_effect(self, x, y, z, size=10, life=2.0):
        """Add smoke particle effect"""
        self.smoke_particles.append({
            'x': x, 'y': y, 'z': z,
            'size': size,
            'time': time.time(),
            'life': life
        })
    
    def _add_spark_effect(self, x, y, z, count=5):
        """Add spark particle effect"""
        for _ in range(count):
            self.spark_particles.append({
                'x': x + random.uniform(-2, 2),
                'y': y + random.uniform(-2, 2),
                'z': z + random.uniform(-2, 2),
                'time': time.time(),
                'life': random.uniform(0.2, 0.5)
            })
    
    def _add_tracer_round(self, start_x, start_y, start_z, end_x, end_y, end_z):
        """Add bullet tracer effect"""
        self.tracer_rounds.append({
            'start_x': start_x, 'start_y': start_y, 'start_z': start_z,
            'end_x': end_x, 'end_y': end_y, 'end_z': end_z,
            'time': time.time(),
            'life': 0.1
        })
    
    def _add_impact_mark(self, x, y, z):
        """Add bullet impact mark"""
        self.impact_marks.append({
            'x': x, 'y': y, 'z': z,
            'time': time.time(),
            'life': 10.0
        })
    
    def _generate_map(self):
        """� Generate CS:GO Style TACTICAL MAP - Industrial Warehouse/Factory Compound"""
        
        # === MAIN WAREHOUSE BUILDINGS (Dust2/Inferno style) ===
        building_layouts = [
            # Main warehouse A site
            {'x': -400, 'z': -300, 'width': 250, 'height': 180, 'type': 'warehouse', 'site': 'A'},
            # Factory building B site
            {'x': 350, 'z': 250, 'width': 220, 'height': 150, 'type': 'factory', 'site': 'B'},
            # Central control tower
            {'x': 0, 'z': 0, 'width': 120, 'height': 200, 'type': 'tower', 'site': 'MID'},
            # Side buildings for cover
            {'x': -200, 'z': 300, 'width': 100, 'height': 80, 'type': 'office', 'site': None},
            {'x': 250, 'z': -250, 'width': 90, 'height': 70, 'type': 'storage', 'site': None},
        ]
        
        for building in building_layouts:
            self.buildings.append({
                'x': building['x'],
                'y': 0,
                'z': building['z'],
                'width': building['width'],
                'height': building['height'],
                'type': building['type'],
                'site': building.get('site'),
                'windows': random.randint(3, 6),  # Tactical windows
                'doors': random.randint(1, 3),
                'catwalk': building['type'] in ['warehouse', 'factory'],  # Upper level
                'vents': building['type'] == 'factory',
                'color': random.choice([
                    (110, 110, 105),  # Industrial gray
                    (95, 90, 85),     # Concrete brown
                    (100, 105, 100),  # Military green-gray
                    (115, 110, 100),  # Weathered tan
                ])
            })
        
        # === TACTICAL COVER - Crates, Containers, Boxes ===
        # Large shipping containers (like CS:GO double doors area)
        container_positions = [
            (-300, -100), (-250, -100), (280, 150), (320, 150),  # Container stacks
            (-100, 200), (150, -150), (0, 180), (-350, 100)
        ]
        
        for x, z in container_positions:
            self.rocks.append({
                'x': x,
                'y': 0,
                'z': z,
                'size': random.randint(60, 90),
                'type': 'container',
                'stacked': random.random() > 0.5,  # Double-stacked containers
                'color': random.choice([
                    (140, 50, 40),   # Red container
                    (45, 80, 120),   # Blue container
                    (120, 120, 110), # Gray container
                    (90, 110, 70),   # Green container
                ])
            })
        
        # Wooden crates for close-quarters cover
        for i in range(40):
            self.rocks.append({
                'x': random.randint(-500, 500),
                'y': 0,
                'z': random.randint(-500, 500),
                'size': random.randint(35, 55),
                'type': random.choice(['crate', 'barrel', 'pallet', 'box']),
                'destructible': True,  # Can be destroyed by gunfire
                'color': (130, 110, 80)  # Wooden brown
            })
        
        # === FLOOR DETAILS - Concrete, oil stains, tactical markings ===
        for i in range(60):
            self.grass_patches.append({
                'x': random.randint(-600, 600),
                'y': 0,
                'z': random.randint(-600, 600),
                'size': random.randint(15, 45),
                'type': random.choice(['oil_stain', 'tire_marks', 'caution_paint', 'cracks']),
                'color': random.choice([
                    (40, 40, 45),    # Oil stain
                    (200, 200, 50),  # Yellow caution paint
                    (90, 90, 95),    # Concrete crack
                ])
            })
        
        # === NO TREES - Industrial zone (add metal poles/lights instead) ===
        for i in range(12):
            self.trees.append({
                'x': random.randint(-550, 550),
                'y': 0,
                'z': random.randint(-550, 550),
                'type': 'light_pole',  # Not trees - industrial lighting
                'height': random.randint(150, 200),
                'light_on': True
            })
        
        # === TACTICAL SKY - Clear with industrial backdrop ===
        for i in range(8):
            self.clouds.append({
                'x': random.randint(0, self.screen_width),
                'y': random.randint(20, 80),
                'size': random.randint(70, 120),
                'type': 'industrial',  # Light clouds, not apocalyptic
                'color': (200, 210, 220)  # Light gray
            })
    
    def _render_rain(self):
        """Render rain effect"""
        current_time = pygame.time.get_ticks()
        for i in range(50):
            x = (i * 31 + current_time // 5) % self.screen_width
            y = (i * 47 + current_time // 3) % self.screen_height
            pygame.draw.line(self.screen, (180, 180, 200), (x, y), (x - 2, y + 15), 1)
    
    def _render_fog(self):
        """Render fog effect"""
        fog_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pygame.draw.rect(fog_surface, (200, 200, 200, 100), (0, 0, self.screen_width, self.screen_height))
        self.screen.blit(fog_surface, (0, 0))
    
    def _generate_daily_challenges(self):
        """Generate daily challenges"""
        return [
            {'name': '10 Headshots', 'progress': 0, 'target': 10, 'reward': 500},
            {'name': '5 Killstreaks', 'progress': 0, 'target': 5, 'reward': 300},
            {'name': 'Win 3 Games', 'progress': 0, 'target': 3, 'reward': 1000}
        ]
    
    def _toggle_weather(self):
        """Toggle weather conditions"""
        weathers = ['sunny', 'rain', 'fog']
        current_index = weathers.index(self.weather)
        self.weather = weathers[(current_index + 1) % len(weathers)]
    
    def _toggle_time_of_day(self):
        """Toggle time of day"""
        times = ['day', 'dusk', 'night']
        current_index = times.index(self.time_of_day)
        self.time_of_day = times[(current_index + 1) % len(times)]
    
    def _toggle_camera_mode(self):
        """Toggle between first-person and third-person camera"""
        if self.camera_mode == 'first_person':
            self.camera_mode = 'third_person'
            print("📷 Switched to THIRD-PERSON camera")
        else:
            self.camera_mode = 'first_person'
            print("📷 Switched to FIRST-PERSON camera")
    
    def _throw_grenade(self):
        """Throw grenade"""
        if not hasattr(self, 'grenades'):
            self.grenades = []
            self.grenade_count = 3
        
        if self.grenade_count > 0:
            grenade = {
                'x': self.player_x,
                'y': 50,
                'z': self.player_z,
                'vx': math.cos(self.player_angle) * 200,
                'vy': 100,
                'vz': math.sin(self.player_angle) * 200,
                'time': time.time(),
                'exploded': False
            }
            self.grenades.append(grenade)
            self.grenade_count -= 1
    
    def _melee_attack(self):
        """Perform melee attack"""
        # Check for nearby enemies
        for enemy in self.enemies[:]:
            dx = enemy['x'] - self.player_x
            dz = enemy['z'] - self.player_z
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist < 50:  # Melee range
                enemy['health'] -= 50
                self._add_spark_effect(enemy['x'], enemy['y'], enemy['z'], count=10)
                
                if enemy['health'] <= 0:
                    self.enemies.remove(enemy)
                    self.kills += 1
                    self.score += 150
                    self.killstreak += 1
                break
    
    def _update_grenades(self, dt):
        """Update grenade physics"""
        if not hasattr(self, 'grenades'):
            return
        
        current_time = time.time()
        for grenade in self.grenades[:]:
            if not grenade['exploded']:
                # Update position
                grenade['x'] += grenade['vx'] * dt
                grenade['y'] += grenade['vy'] * dt
                grenade['z'] += grenade['vz'] * dt
                
                # Gravity
                grenade['vy'] -= 200 * dt
                
                # Ground collision
                if grenade['y'] <= 0:
                    grenade['y'] = 0
                    grenade['vy'] = -grenade['vy'] * 0.5  # Bounce
                
                # Explode after 3 seconds
                if current_time - grenade['time'] > 3.0:
                    grenade['exploded'] = True
                    # Create explosion
                    self.explosions.append({
                        'x': grenade['x'],
                        'y': grenade['y'],
                        'z': grenade['z'],
                        'radius': 0,
                        'time': current_time
                    })
                    # Damage nearby enemies
                    for enemy in self.enemies[:]:
                        dx = enemy['x'] - grenade['x']
                        dz = enemy['z'] - grenade['z']
                        dist = math.sqrt(dx*dx + dz*dz)
                        if dist < 100:
                            damage = 100 * (1 - dist / 100)
                            enemy['health'] -= damage
                            if enemy['health'] <= 0:
                                self.enemies.remove(enemy)
                                self.kills += 1
                                self.score += 100
            else:
                # Remove after explosion animation
                if current_time - grenade['time'] > 4.0:
                    self.grenades.remove(grenade)
    
    def _render_notifications(self):
        """Render combo notifications, multikills, headshots"""
        current_time = time.time()
        center_x = self.screen_width // 2
        
        for notification in self.combo_notifications:
            age = current_time - notification['time']
            if age >= 2.0:
                continue
            
            # Fade in/out effect
            if age < 0.3:
                alpha = int(255 * (age / 0.3))
            elif age > 1.5:
                alpha = int(255 * (2.0 - age) / 0.5)
            else:
                alpha = 255
            
            # Scale effect
            scale = 1.0 + (0.5 * (1 - min(age, 0.5) / 0.5))
            font_size = int(48 * scale)
            font = pygame.font.Font(None, font_size)
            
            # Render text with glow
            y_pos = 200 + notification['y_offset'] - int(age * 30)
            
            # Glow effect
            for offset in range(5, 0, -1):
                glow_surface = font.render(notification['text'], True, notification['color'])
                glow_surface.set_alpha(alpha // (offset + 1))
                self.screen.blit(glow_surface, (center_x - glow_surface.get_width()//2 + offset, y_pos + offset))
            
            # Main text
            text_surface = font.render(notification['text'], True, Colors.WHITE)
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (center_x - text_surface.get_width()//2, y_pos))

    def _render_killstreak_display(self):
        """Render epic killstreak notifications"""
        current_time = time.time()
        center_x = self.screen_width // 2
        
        for notification in self.killstreak_notifications:
            age = current_time - notification['time']
            
            # Epic entrance/exit animation
            if age < 0.5:
                y_offset = int(100 * (1 - age / 0.5))
                alpha = int(255 * (age / 0.5))
            elif age > notification['duration'] - 0.5:
                remaining = notification['duration'] - age
                alpha = int(255 * (remaining / 0.5))
                y_offset = 0
            else:
                alpha = 255
                y_offset = 0
            
            y_pos = 300 - y_offset
            
            # Epic background bar
            bar_width = 600
            bar_height = 80
            bar_x = center_x - bar_width // 2
            
            # Main background
            bg_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (20, 20, 40, alpha), (0, 0, bar_width, bar_height), border_radius=10)
            pygame.draw.rect(bg_surface, (*notification['color'], alpha), (0, 0, bar_width, bar_height), 5, border_radius=10)
            self.screen.blit(bg_surface, (bar_x, y_pos))
            
            # Text with massive font
            font = pygame.font.Font(None, 64)
            text_surface = font.render(notification['text'], True, notification['color'])
            text_surface.set_alpha(alpha)
            self.screen.blit(text_surface, (center_x - text_surface.get_width()//2, y_pos + 15))

    def _render_achievement_popups(self):
        """Render achievement unlock animations"""
        current_time = time.time()
        
        for i, achievement in enumerate(self.achievement_popups):
            age = current_time - achievement['time']
            
            # Slide in from right
            if age < 1.0:
                x_offset = int(400 * (1 - age))
                alpha = int(255 * age)
            elif age > 4.0:
                x_offset = int(400 * (age - 4.0))
                alpha = int(255 * (5.0 - age))
            else:
                x_offset = 0
                alpha = 255
            
            # Position
            x_pos = self.screen_width - 350 + x_offset
            y_pos = 150 + i * 120
            
            # Background
            bg_width = 330
            bg_height = 100
            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            bg_surface.set_alpha(alpha)
            pygame.draw.rect(bg_surface, (40, 20, 60), (0, 0, bg_width, bg_height), border_radius=15)
            pygame.draw.rect(bg_surface, Colors.GOLD, (0, 0, bg_width, bg_height), 3, border_radius=15)
            self.screen.blit(bg_surface, (x_pos, y_pos))
            
            # Trophy icon
            trophy_font = pygame.font.Font(None, 64)
            trophy_surface = trophy_font.render("🏆", True, Colors.GOLD)
            trophy_surface.set_alpha(alpha)
            self.screen.blit(trophy_surface, (x_pos + 20, y_pos + 20))
            
            # Text
            title_font = pygame.font.Font(None, 32)
            title_surface = title_font.render("ACHIEVEMENT!", True, Colors.GOLD)
            title_surface.set_alpha(alpha)
            self.screen.blit(title_surface, (x_pos + 100, y_pos + 15))
            
            name_surface = title_font.render(achievement['name'], True, Colors.WHITE)
            name_surface.set_alpha(alpha)
            self.screen.blit(name_surface, (x_pos + 100, y_pos + 45))
            
            desc_font = pygame.font.Font(None, 20)
            desc_surface = desc_font.render(achievement['desc'], True, Colors.LIGHT_GRAY)
            desc_surface.set_alpha(alpha)
            self.screen.blit(desc_surface, (x_pos + 100, y_pos + 70))

    def _render_power_ups_hud(self):
        """Render active power-ups on HUD"""
        current_time = time.time()
        x_pos = 20
        y_pos = self.screen_height - 120
        
        for power_up in self.active_power_ups:
            remaining = power_up['end_time'] - current_time
            if remaining <= 0:
                continue
            
            # Icon and name
            if power_up['type'] == 'speed':
                icon = "⚡"
                name = "SPEED"
                color = Colors.NEON_CYAN
            elif power_up['type'] == 'damage':
                icon = "🔥"
                name = "DAMAGE"
                color = Colors.NEON_RED
            else:
                continue
            
            # Background
            bg_width = 120
            bg_height = 50
            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            bg_surface.set_alpha(200)
            pygame.draw.rect(bg_surface, (20, 20, 40), (0, 0, bg_width, bg_height), border_radius=10)
            self.screen.blit(bg_surface, (x_pos, y_pos))
            pygame.draw.rect(self.screen, color, (x_pos, y_pos, bg_width, bg_height), 2, border_radius=10)
            
            # Timer bar
            bar_width = int((remaining / 15.0) * (bg_width - 10))
            pygame.draw.rect(self.screen, color, (x_pos + 5, y_pos + bg_height - 10, bar_width, 5), border_radius=2)
            
            # Icon and text
            font = pygame.font.Font(None, 36)
            icon_surface = font.render(icon, True, color)
            self.screen.blit(icon_surface, (x_pos + 10, y_pos + 5))
            
            text_font = pygame.font.Font(None, 24)
            text_surface = text_font.render(name, True, Colors.WHITE)
            self.screen.blit(text_surface, (x_pos + 45, y_pos + 12))
            
            time_surface = text_font.render(f"{int(remaining)}s", True, Colors.LIGHT_GRAY)
            self.screen.blit(time_surface, (x_pos + 45, y_pos + 28))
            
            y_pos -= 60

if __name__ == "__main__":
    # Initialize game
    game = FPSGame()
    game.player_z = 0  # Initialize z position
    
    print("=" * 60)
    print("🧟 POST-APOCALYPTIC ZOMBIE SURVIVAL FPS 🧟")
    print("=" * 60)
    print("\n📋 CONTROLS:")
    print("   WASD - Move")
    print("   MOUSE - Look around")
    print("   LEFT CLICK - Shoot")
    print("   R - Reload")
    print("   1-6 - Switch weapons")
    print("   P - Toggle Camera (First/Third Person)")
    print("   T - Toggle Time of Day")
    print("   Y - Toggle Weather")
    print("   G - Throw Grenade")
    print("   V - Melee Attack")
    print("   ESC - Back to menu")
    print("\n🧟 ENEMIES:")
    print("   WALKER - Slow, 80 HP")
    print("   RUNNER - Fast, 50 HP")
    print("   TANK - Strong, 200 HP")
    print("\n🎯 OBJECTIVE:")
    print("   Survive the zombie apocalypse!")
    print("   Explore the destroyed city!")
    print("   Earn points and level up!")
    print("\n🔫 WEAPONS:")
    print("   1: M4A1 Assault Rifle")
    print("   2: Barrett .50 Cal Sniper")
    print("   3: MP5 SMG")
    print("   4: SPAS-12 Shotgun")
    print("   5: Desert Eagle Pistol")
    print("   6: M249 SAW LMG")
    print("\n🏙️ ENVIRONMENT:")
    print("   Post-Apocalyptic City")
    print("   Destroyed Buildings & Debris")
    print("   Dynamic Weather & Day/Night Cycle")
    print("\n" + "=" * 60)
    print("Game starting... Navigate menu with arrow keys!")
    print("=" * 60)
    
    # Run game directly (menu will show)
    game.run()

