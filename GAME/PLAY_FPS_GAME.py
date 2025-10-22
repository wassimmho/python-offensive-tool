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
        
        # ULTRA REALISTIC MECHANICS
        self.weight = self._calculate_weight(name)  # Weapon weight in kg
        self.ergo = self._calculate_ergonomics(name)  # Ergonomics rating
        self.ads_time = self._calculate_ads_time(name)  # Time to ADS
        
        # ADVANCED REALISTIC FEATURES
        self.barrel_heat = 0  # 0-100, affects accuracy
        self.durability = 100  # 0-100, affects jam chance
        self.jam_chance = 0.001  # Base jam chance (0.1%)
        self.maintenance_level = 100  # Needs cleaning
        self.muzzle_velocity = self._get_muzzle_velocity(name)  # m/s
        self.effective_range = self._get_effective_range(name)  # meters
        self.bullet_drop = self._get_bullet_drop(name)  # gravity effect
    
    def _calculate_weight(self, name):
        """Calculate realistic weapon weight"""
        weights = {
            'M4A1': 3.4, 'Barrett': 14.0, 'MP5': 2.5,
            'SPAS-12': 4.2, 'Desert Eagle': 1.9, 'M249': 7.5
        }
        for key, weight in weights.items():
            if key in name:
                return weight
        return 3.0
    
    def _calculate_ergonomics(self, name):
        """Calculate ergonomics (0-100, higher = better handling)"""
        ergo_map = {
            'M4A1': 70, 'Barrett': 30, 'MP5': 85,
            'SPAS-12': 50, 'Desert Eagle': 75, 'M249': 40
        }
        for key, ergo in ergo_map.items():
            if key in name:
                return ergo
        return 60
    
    def _calculate_ads_time(self, name):
        """Calculate ADS time in seconds"""
        ads_times = {
            'M4A1': 0.25, 'Barrett': 0.45, 'MP5': 0.18,
            'SPAS-12': 0.35, 'Desert Eagle': 0.20, 'M249': 0.40
        }
        for key, ads_time in ads_times.items():
            if key in name:
                return ads_time
        return 0.25
    
    def _get_muzzle_velocity(self, name):
        """Get realistic muzzle velocity in m/s"""
        velocities = {
            'M4A1': 910, 'Barrett': 853, 'MP5': 400,
            'SPAS-12': 430, 'Desert Eagle': 470, 'M249': 915
        }
        for key, vel in velocities.items():
            if key in name:
                return vel
        return 800
    
    def _get_effective_range(self, name):
        """Get effective range in meters"""
        ranges = {
            'M4A1': 500, 'Barrett': 1800, 'MP5': 200,
            'SPAS-12': 40, 'Desert Eagle': 50, 'M249': 800
        }
        for key, range_val in ranges.items():
            if key in name:
                return range_val
        return 300
    
    def _get_bullet_drop(self, name):
        """Get bullet drop factor"""
        drops = {
            'M4A1': 0.8, 'Barrett': 0.5, 'MP5': 1.2,
            'SPAS-12': 2.0, 'Desert Eagle': 1.5, 'M249': 0.7
        }
        for key, drop in drops.items():
            if key in name:
                return drop
        return 1.0
    
    def can_shoot(self):
        current_time = time.time()
        return (self.current_ammo > 0 and 
                not self.reloading and 
                current_time - self.last_shot_time >= 1.0 / self.fire_rate)
    
    def shoot(self):
        if self.can_shoot():
            # REALISTIC: Check for weapon jam
            jam_chance = self.jam_chance * (1 + (100 - self.durability) / 100)
            jam_chance *= (1 + self.barrel_heat / 200)  # Heat increases jam chance
            
            if random.random() < jam_chance:
                print(f"❌ WEAPON JAMMED! {self.name} - Clear the jam!")
                self.reloading = True  # Must clear jam
                self.reload_start = time.time()
                return False
            
            # Fire successfully
            self.current_ammo -= 1
            self.last_shot_time = time.time()
            self.shots_fired += 1
            
            # REALISTIC: Weapon degradation
            self.barrel_heat = min(100, self.barrel_heat + 5)
            self.durability = max(0, self.durability - 0.1)
            self.maintenance_level = max(0, self.maintenance_level - 0.05)
            
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
    """�️ TACTICAL COMBAT SIMULATOR - MILITARY GRADE REALISTIC FPS"""
    
    def __init__(self):
        self.screen_width = 1600  # Cinema-quality resolution
        self.screen_height = 900
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("🎖️ TACTICAL COMBAT SIMULATOR - Operation Blackout")
        
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
        self.in_loadout = False  # NEW: Loadout selection screen
        self.in_settings = False  # NEW: Settings screen
        self.menu_option = 0
        self.menu_options = ["⚡ PLAY GAME", "🎯 LOADOUT", "⚙️ SETTINGS", "🚪 EXIT"]
        
        # SETTINGS SYSTEM
        self.settings_selection = 0  # Current selected setting
        self.settings_scroll_offset = 0  # Scroll position for settings
        self.settings = {
            'master_volume': {'name': '🔊 Master Volume', 'value': 0.7, 'min': 0.0, 'max': 1.0, 'step': 0.1, 'type': 'slider'},
            'music_volume': {'name': '🎵 Music Volume', 'value': 0.5, 'min': 0.0, 'max': 1.0, 'step': 0.1, 'type': 'slider'},
            'sfx_volume': {'name': '🔫 SFX Volume', 'value': 0.8, 'min': 0.0, 'max': 1.0, 'step': 0.1, 'type': 'slider'},
            'mouse_sensitivity': {'name': '🖱️ Mouse Sensitivity', 'value': 0.003, 'min': 0.001, 'max': 0.010, 'step': 0.001, 'type': 'slider'},
            'fov': {'name': '👁️ Field of View', 'value': 90, 'min': 60, 'max': 120, 'step': 5, 'type': 'slider'},
            'brightness': {'name': '💡 Brightness', 'value': 1.0, 'min': 0.5, 'max': 1.5, 'step': 0.1, 'type': 'slider'},
            'show_fps': {'name': '📊 Show FPS', 'value': True, 'type': 'toggle'},
            'vsync': {'name': '⚡ VSync', 'value': True, 'type': 'toggle'},
            'particles': {'name': '✨ Particle Effects', 'value': True, 'type': 'toggle'},
            'blood_effects': {'name': '🩸 Blood Effects', 'value': True, 'type': 'toggle'},
            'screen_shake': {'name': '📳 Screen Shake', 'value': True, 'type': 'toggle'},
            'crosshair_style': {'name': '🎯 Crosshair Style', 'value': 0, 'options': ['Classic', 'Dot', 'Cross', 'Circle'], 'type': 'choice'}
        }
        self.settings_keys = list(self.settings.keys())
        
        # LOADOUT SYSTEM
        self.current_loadout = 0  # Selected loadout (0-3)
        self.loadout_selection = 0  # Current selection in loadout menu
        self.loadouts = [
            {
                'name': '🎯 ASSAULT',
                'icon': '🔫',
                'description': 'Balanced for medium range combat',
                'primary': 'assault_rifle',
                'secondary': 'pistol',
                'equipment': 'frag_grenade',
                'perk': 'Extra Ammo',
                'stats': {'damage': 7, 'range': 8, 'mobility': 6, 'accuracy': 7}
            },
            {
                'name': '🎯 SNIPER',
                'icon': '🔭',
                'description': 'Long range precision elimination',
                'primary': 'sniper',
                'secondary': 'pistol',
                'equipment': 'claymore',
                'perk': 'Steady Aim',
                'stats': {'damage': 10, 'range': 10, 'mobility': 4, 'accuracy': 10}
            },
            {
                'name': '🎯 RUN & GUN',
                'icon': '⚡',
                'description': 'High mobility close quarters',
                'primary': 'smg',
                'secondary': 'shotgun',
                'equipment': 'flash_grenade',
                'perk': 'Fast Movement',
                'stats': {'damage': 6, 'range': 5, 'mobility': 10, 'accuracy': 6}
            },
            {
                'name': '🎯 TANK',
                'icon': '🛡️',
                'description': 'Heavy firepower and armor',
                'primary': 'lmg',
                'secondary': 'shotgun',
                'equipment': 'smoke_grenade',
                'perk': 'Extra Armor',
                'stats': {'damage': 9, 'range': 7, 'mobility': 4, 'accuracy': 5}
            }
        ]
        
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
        
        # COD STYLE MOVEMENT - Fast & Responsive
        self.player_velocity_x = 0
        self.player_velocity_y = 0
        self.player_velocity_z = 0
        self.walk_speed = 3.5  # COD-style fast walk
        self.sprint_speed = 6.0  # Tactical sprint (fast like COD)
        self.crouch_speed = 2.0  # Faster crouch movement
        self.current_speed = self.walk_speed
        self.is_sprinting = False
        self.is_crouching = False
        self.is_aiming = False  # ADS (Aim Down Sights)
        self.stamina = 100  # Stamina for sprinting
        self.max_stamina = 100
        self.stamina_drain = 15  # Slower drain - can sprint longer (COD style)
        self.stamina_regen = 25  # Fast recovery (COD style)
        self.breath_sway = 0  # Weapon sway from breathing
        self.movement_sway = 0  # Weapon sway from movement
        
        # COD DAMAGE SYSTEM - Balanced TTK (Time To Kill)
        self.headshot_multiplier = 2.5  # COD headshot bonus
        self.body_multiplier = 1.0  # Normal damage
        self.limb_multiplier = 0.9  # Slight reduction
        self.last_damage_time = 0
        self.damage_direction = 0  # Direction damage came from
        self.is_bleeding = False
        self.bleed_damage = 1  # Less punishing (COD style)
        self.bleed_timer = 0
        
        # ADVANCED INJURY SYSTEM - ULTRA REALISTIC
        self.injuries = {
            'head': {'damage': 0, 'bleeding': False, 'fracture': False},
            'chest': {'damage': 0, 'bleeding': False, 'fracture': False},
            'stomach': {'damage': 0, 'bleeding': False, 'fracture': False},
            'left_arm': {'damage': 0, 'bleeding': False, 'fracture': False},
            'right_arm': {'damage': 0, 'bleeding': False, 'fracture': False},
            'left_leg': {'damage': 0, 'bleeding': False, 'fracture': False},
            'right_leg': {'damage': 0, 'bleeding': False, 'fracture': False}
        }
        self.pain_level = 0  # 0-100, affects aim and movement
        self.blood_loss = 0  # Accumulated blood loss
        self.hydration = 100  # Water level
        self.energy = 100  # Food/energy level
        self.body_temperature = 37.0  # Normal body temp in Celsius
        self.infection_risk = 0  # Untreated wounds get infected
        
        # Weapon system
        self.current_weapon = 'pistol'  # Start with pistol only
        self.weapons = {name: Weapon(w.name, w.damage, w.fire_rate, w.max_ammo, w.reload_time, w.accuracy, w.recoil, w.penetration) 
                       for name, w in WEAPONS.items()}
        # Start with limited ammo
        self.weapons['pistol'].current_ammo = 12
        self.weapons['pistol'].magazine_count = 1
        
        # REALISTIC WEAPON MECHANICS
        self.recoil_x = 0  # Current horizontal recoil
        self.recoil_y = 0  # Current vertical recoil
        self.recoil_recovery_speed = 10  # How fast recoil recovers
        self.weapon_sway_x = 0
        self.weapon_sway_y = 0
        self.ads_time = 0.2  # Time to aim down sights
        self.ads_progress = 0  # 0-1, current ADS animation progress
        
        # ULTRA REALISTIC HEALING SYSTEM
        self.is_healing = False
        self.healing_progress = 0
        self.healing_type = None  # 'bandage', 'medkit', 'surgery'
        self.medkits = 2  # Start with 2 medkits
        self.bandages = 3  # Start with 3 bandages
        
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
        
        # KILL MILESTONE REWARDS SYSTEM
        self.kill_milestones = [5, 10, 25, 50, 100, 150, 200, 300, 500, 1000]
        self.last_milestone_reached = 0
        self.reward_notifications = []  # List of active reward notifications
        self.total_rewards_earned = 0
        
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
        
        # SURVIVAL MECHANICS - ULTRA REALISTIC
        self.weapon_attachments = {
            'scopes': ['Red Dot', 'ACOG', 'Sniper Scope'],
            'grips': ['Vertical Grip', 'Angled Grip'],
            'barrels': ['Suppressor', 'Compensator', 'Extended Barrel']
        }
        
        # ENVIRONMENTAL SURVIVAL SYSTEM
        self.noise_level = 0  # 0-100, attracts enemies
        self.visibility = 100  # Affected by weather/time
        self.wind_speed = 0  # Affects bullet trajectory
        self.wind_direction = 0  # In degrees
        self.rain_intensity = 0  # 0-100
        self.ambient_temperature = 20  # Celsius
        self.time_of_day_hour = 12  # 0-24 hours
        self.stealth_rating = 100  # How hidden you are
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
        
        # RESPAWN SYSTEM - HARDCORE MODE (NO INVINCIBILITY!)
        self.invincible = False  # NO invincibility - death has consequences
        self.invincible_timer = 0
        self.respawn_flash = 0  # Visual flash effect when respawning
        self.lives = 3  # Only 3 lives before GAME OVER
        
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
        
        # COD STYLE: Fast respawn - 3 second protection
        self.invincible = True
        self.invincible_timer = 3.0  # 3 seconds spawn protection (COD style)
        self.respawn_flash = 1.0
        
        # Lose a life
        self.lives -= 1
        if self.lives <= 0:
            print("💀💀💀 GAME OVER - FINAL KILLCAM 💀💀💀")
            self.state = 'menu'  # Back to menu
            self.lives = 3  # Reset for next game
        
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
        print(f"☠️ KIA! [{self.lives} lives left] Respawning in 3... 2... 1...")
    
    def spawn_enemies(self, count):
        """🎖️ Spawn HOSTILE COMBATANTS - TACTICAL UNITS"""
        enemy_types = ['terrorist', 'elite', 'heavy', 'sniper']
        
        # Determine enemy team (opposite of player's team)
        if self.player_team == 'BLUE':
            enemy_team = 'RED'
        elif self.player_team == 'RED':
            enemy_team = 'BLUE'
        else:
            enemy_team = 'RED'  # Default if no team selected yet
        
        for i in range(count):
            # Commander unit every 5 waves
            if self.zombie_wave % 5 == 0 and i == 0 and not self.boss_spawned:
                enemy_type = 'commander'
                health, speed, damage = 500, 40, 50
                self.boss_spawned = True
                self.boss_health = health
            else:
                enemy_type = random.choice(enemy_types)
                if enemy_type == 'terrorist':
                    health, speed, damage = 100, 40, 30  # Standard Infantry
                elif enemy_type == 'elite':
                    health, speed, damage = 70, 150, 25  # Fast Operators
                elif enemy_type == 'sniper':
                    health, speed, damage = 80, 35, 40  # Long Range Specialist
                else:  # heavy
                    health, speed, damage = 250, 30, 50  # Heavy Gunner
                    
            # Spawn at random position far from player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(300, 500)
            spawn_x = self.player_x + math.cos(angle) * distance
            spawn_z = self.player_z + math.sin(angle) * distance
                
            enemy = {
                'id': f'hostile_{self.zombie_wave}_{i}',
                'type': enemy_type,
                'team': enemy_team,  # Hostile team
                'x': spawn_x,
                'y': 0,
                'z': spawn_z,
                'health': health,
                'max_health': health,
                'armor': 0,
                'angle': random.uniform(0, 2 * math.pi),
                'weapon': None,
                'ai_state': 'patrol',  # patrol, chase, attack, cover
                'speed': speed,
                'damage': damage,
                'last_attack': 0,
                'alert': False,
                'animation_frame': random.uniform(0, 2 * math.pi),
                'is_dead': False,
                'blood_level': 0,
                'aggro_range': 400 if enemy_type == 'elite' else 300,
                'can_see_player': False,
                'last_seen_player_pos': (0, 0),
                'path_finding': [],  # Smart pathfinding
                'is_boss': enemy_type == 'commander'
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
                elif self.in_loadout:
                    # Loadout selection input
                    if event.key == pygame.K_UP:
                        self.loadout_selection = (self.loadout_selection - 1) % len(self.loadouts)
                    elif event.key == pygame.K_DOWN:
                        self.loadout_selection = (self.loadout_selection + 1) % len(self.loadouts)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Confirm loadout selection
                        self.current_loadout = self.loadout_selection
                        loadout = self.loadouts[self.current_loadout]
                        # Apply loadout to player
                        self.current_weapon = loadout['primary']
                        # Give full ammo for selected weapons
                        if loadout['primary'] in self.weapons:
                            self.weapons[loadout['primary']].current_ammo = self.weapons[loadout['primary']].max_ammo
                            self.weapons[loadout['primary']].magazine_count = 5
                        if loadout['secondary'] in self.weapons:
                            self.weapons[loadout['secondary']].current_ammo = self.weapons[loadout['secondary']].max_ammo
                            self.weapons[loadout['secondary']].magazine_count = 3
                        # Apply perk bonuses
                        if loadout['perk'] == 'Extra Ammo':
                            for weapon in self.weapons.values():
                                weapon.magazine_count += 3
                        elif loadout['perk'] == 'Extra Armor':
                            self.player_armor = 50
                        # Show confirmation and return to menu
                        self.in_loadout = False
                        self.in_menu = True
                    elif event.key == pygame.K_ESCAPE:
                        # Back to menu
                        self.in_loadout = False
                        self.in_menu = True
                elif self.in_settings:
                    # Settings input
                    if event.key == pygame.K_UP:
                        self.settings_selection = (self.settings_selection - 1) % len(self.settings_keys)
                        # Auto-scroll to keep selection visible
                        self._update_settings_scroll()
                    elif event.key == pygame.K_DOWN:
                        self.settings_selection = (self.settings_selection + 1) % len(self.settings_keys)
                        # Auto-scroll to keep selection visible
                        self._update_settings_scroll()
                    elif event.key == pygame.K_LEFT:
                        # Decrease value
                        self._adjust_setting(-1)
                    elif event.key == pygame.K_RIGHT:
                        # Increase value
                        self._adjust_setting(1)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        # Toggle for boolean settings
                        key = self.settings_keys[self.settings_selection]
                        setting = self.settings[key]
                        if setting['type'] == 'toggle':
                            setting['value'] = not setting['value']
                            self._apply_settings()
                        elif setting['type'] == 'choice':
                            # Cycle through options
                            setting['value'] = (setting['value'] + 1) % len(setting['options'])
                            self._apply_settings()
                    elif event.key == pygame.K_ESCAPE:
                        # Save and return to menu
                        self._apply_settings()
                        self.in_settings = False
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
                    elif event.key == pygame.K_h:  # HEAL with medkit
                        if self.medkits > 0 and self.player_health < 100 and not self.is_healing:
                            self.is_healing = True
                            self.healing_type = 'medkit'
                            self.healing_progress = 0
                            self.medkits -= 1
                            print(f"🏥 Using medkit... ({self.medkits} left)")
                    elif event.key == pygame.K_b:  # BANDAGE (stop bleeding)
                        if self.bandages > 0 and self.player_health < 100 and not self.is_healing:
                            self.is_healing = True
                            self.healing_type = 'bandage'
                            self.healing_progress = 0
                            self.bandages -= 1
                            print(f"🩹 Applying bandage... ({self.bandages} left)")
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
                elif self.in_loadout:
                    # Loadout click detection
                    self._handle_loadout_click(event.pos)
                elif self.in_settings:
                    # Settings click detection
                    self._handle_settings_click(event.pos)
                    # Mouse wheel scrolling in settings
                    if event.button == 4:  # Scroll up
                        self.settings_scroll_offset = max(0, self.settings_scroll_offset - 1)
                    elif event.button == 5:  # Scroll down
                        max_scroll = max(0, len(self.settings_keys) - 6)  # Show 6 items at a time
                        self.settings_scroll_offset = min(max_scroll, self.settings_scroll_offset + 1)
                else:
                    if event.button == 1:  # Left click - shoot
                        self._shoot()
                    elif event.button == 3:  # Right click - aim
                        self.is_aiming = True
                    elif event.button == 4:  # Scroll up
                        pass  # Could be used for weapon switching
                    elif event.button == 5:  # Scroll down
                        pass  # Could be used for weapon switching
            
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
            # Show loadout screen
            self.in_menu = False
            self.in_loadout = True
            self.loadout_selection = self.current_loadout
        elif self.menu_option == 2:  # Settings
            # Show settings screen
            self.in_menu = False
            self.in_settings = True
            self.settings_selection = 0
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
    
    def _handle_loadout_click(self, pos):
        """Handle loadout screen clicks"""
        card_width = 700
        card_height = 140
        card_spacing = 20
        start_y = 180
        card_x = self.screen_width//2 - card_width//2
        
        # Check loadout cards
        for i in range(len(self.loadouts)):
            y = start_y + i * (card_height + card_spacing)
            card_rect = pygame.Rect(card_x, y, card_width, card_height)
            if card_rect.collidepoint(pos):
                self.loadout_selection = i
                # Auto-confirm on click
                self.current_loadout = self.loadout_selection
                loadout = self.loadouts[self.current_loadout]
                # Apply loadout to player
                self.current_weapon = loadout['primary']
                # Give full ammo for selected weapons
                if loadout['primary'] in self.weapons:
                    self.weapons[loadout['primary']].current_ammo = self.weapons[loadout['primary']].max_ammo
                    self.weapons[loadout['primary']].magazine_count = 5
                if loadout['secondary'] in self.weapons:
                    self.weapons[loadout['secondary']].current_ammo = self.weapons[loadout['secondary']].max_ammo
                    self.weapons[loadout['secondary']].magazine_count = 3
                # Apply perk bonuses
                if loadout['perk'] == 'Extra Ammo':
                    for weapon in self.weapons.values():
                        weapon.magazine_count += 3
                elif loadout['perk'] == 'Extra Armor':
                    self.player_armor = 50
                # Play sound
                self.play_sound('reload')
                break
        
        # Check back button
        back_button_rect = pygame.Rect(50, self.screen_height - 100, 200, 60)
        if back_button_rect.collidepoint(pos):
            self.in_loadout = False
            self.in_menu = True
    
    def _handle_settings_click(self, pos):
        """Handle settings screen clicks"""
        setting_height = 80
        start_y = 180
        setting_x = self.screen_width//2 - 400
        
        # Check each VISIBLE setting (accounting for scroll)
        visible_start = self.settings_scroll_offset
        visible_end = min(visible_start + 6, len(self.settings_keys))  # Show 6 items
        
        for i in range(visible_start, visible_end):
            key = self.settings_keys[i]
            # Adjust y position based on scroll offset
            y = start_y + (i - self.settings_scroll_offset) * setting_height
            setting_rect = pygame.Rect(setting_x, y, 800, 70)
            
            if setting_rect.collidepoint(pos):
                self.settings_selection = i
                setting = self.settings[key]
                
                # Check if clicking on slider
                if setting['type'] == 'slider':
                    slider_x = setting_x + 450
                    slider_width = 300
                    if slider_x <= pos[0] <= slider_x + slider_width:
                        # Calculate new value based on click position
                        ratio = (pos[0] - slider_x) / slider_width
                        new_value = setting['min'] + ratio * (setting['max'] - setting['min'])
                        setting['value'] = round(new_value / setting['step']) * setting['step']
                        setting['value'] = max(setting['min'], min(setting['max'], setting['value']))
                        self._apply_settings()
                        self.play_sound('reload')
                
                # Check if clicking on toggle
                elif setting['type'] == 'toggle':
                    toggle_x = setting_x + 600
                    if toggle_x <= pos[0] <= toggle_x + 100:
                        setting['value'] = not setting['value']
                        self._apply_settings()
                        self.play_sound('reload')
                
                # Check if clicking on choice arrows
                elif setting['type'] == 'choice':
                    left_arrow_x = setting_x + 500
                    right_arrow_x = setting_x + 720
                    if left_arrow_x <= pos[0] <= left_arrow_x + 40:
                        setting['value'] = (setting['value'] - 1) % len(setting['options'])
                        self._apply_settings()
                        self.play_sound('reload')
                    elif right_arrow_x <= pos[0] <= right_arrow_x + 40:
                        setting['value'] = (setting['value'] + 1) % len(setting['options'])
                        self._apply_settings()
                        self.play_sound('reload')
                break
        
        # Check back button
        back_button_rect = pygame.Rect(50, self.screen_height - 100, 200, 60)
        if back_button_rect.collidepoint(pos):
            self._apply_settings()
            self.in_settings = False
            self.in_menu = True
        
        # Check reset button
        reset_button_rect = pygame.Rect(self.screen_width - 250, self.screen_height - 100, 200, 60)
        if reset_button_rect.collidepoint(pos):
            self._reset_settings()
            self.play_sound('reload')
    
    def _adjust_setting(self, direction):
        """Adjust selected setting value"""
        key = self.settings_keys[self.settings_selection]
        setting = self.settings[key]
        
        if setting['type'] == 'slider':
            setting['value'] += direction * setting['step']
            setting['value'] = max(setting['min'], min(setting['max'], setting['value']))
            self._apply_settings()
        elif setting['type'] == 'choice':
            setting['value'] = (setting['value'] + direction) % len(setting['options'])
            self._apply_settings()
    
    def _apply_settings(self):
        """Apply current settings to game"""
        # Apply mouse sensitivity
        self.mouse_sensitivity = self.settings['mouse_sensitivity']['value']
        
        # Apply volume settings
        if hasattr(pygame.mixer, 'music'):
            try:
                pygame.mixer.music.set_volume(self.settings['music_volume']['value'] * self.settings['master_volume']['value'])
            except:
                pass
        
        # Apply FOV (field of view would require camera matrix changes)
        # This is a placeholder - actual FOV implementation would be more complex
        self.fov = self.settings['fov']['value']
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        self.settings['master_volume']['value'] = 0.7
        self.settings['music_volume']['value'] = 0.5
        self.settings['sfx_volume']['value'] = 0.8
        self.settings['mouse_sensitivity']['value'] = 0.003
        self.settings['fov']['value'] = 90
        self.settings['brightness']['value'] = 1.0
        self.settings['show_fps']['value'] = True
        self.settings['vsync']['value'] = True
        self.settings['particles']['value'] = True
        self.settings['blood_effects']['value'] = True
        self.settings['screen_shake']['value'] = True
        self.settings['crosshair_style']['value'] = 0
        self._apply_settings()
    
    def _update_settings_scroll(self):
        """Auto-scroll to keep selected setting visible"""
        visible_items = 6  # Number of settings visible at once
        
        # If selection is above visible area, scroll up
        if self.settings_selection < self.settings_scroll_offset:
            self.settings_scroll_offset = self.settings_selection
        
        # If selection is below visible area, scroll down
        elif self.settings_selection >= self.settings_scroll_offset + visible_items:
            self.settings_scroll_offset = self.settings_selection - visible_items + 1
        
        # Ensure scroll offset is within bounds
        max_scroll = max(0, len(self.settings_keys) - visible_items)
        self.settings_scroll_offset = max(0, min(self.settings_scroll_offset, max_scroll))
    
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
        
        # === WEAPON WEIGHT PENALTY ===
        current_weapon = self.weapons.get(self.current_weapon)
        if current_weapon:
            # Heavy weapons slow you down (Barrett 14kg = -70% speed!)
            weight_penalty = 1.0 - (current_weapon.weight / 20.0)
            weight_penalty = max(0.3, weight_penalty)  # Minimum 30% speed
        else:
            weight_penalty = 1.0
        
        # Calculate speed modifiers
        if self.is_crouching:
            speed_mult = self.crouch_speed_mult
        elif self.is_sprinting and self.stamina > 5:
            speed_mult = self.sprint_multiplier
        elif self.is_aiming:
            speed_mult = self.aim_walk_speed
        else:
            speed_mult = 1.0
        
        # Apply weapon weight penalty
        speed_mult *= weight_penalty
        
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
        
        # === WEAPON SWAY based on WEIGHT and STAMINA ===
        if current_weapon:
            # More sway with heavy weapons and low stamina
            base_sway = (current_weapon.weight / 10.0) * (1.0 - self.stamina / 100.0)
            movement_sway = 1.5 if is_moving else 1.0
            total_sway = base_sway * movement_sway
            
            # Apply random sway
            self.weapon_sway_x += random.uniform(-total_sway, total_sway) * dt * 50
            self.weapon_sway_y += random.uniform(-total_sway, total_sway) * dt * 50
            
            # Dampen sway (return to center)
            self.weapon_sway_x *= 0.9
            self.weapon_sway_y *= 0.9
            
            # Limit max sway
            max_sway = 0.5
            self.weapon_sway_x = max(-max_sway, min(max_sway, self.weapon_sway_x))
            self.weapon_sway_y = max(-max_sway, min(max_sway, self.weapon_sway_y))
        
        # === HEALING SYSTEM ===
        if self.is_healing:
            healing_speeds = {
                'bandage': 2.0,  # 2 seconds, +25 HP, stops bleeding
                'medkit': 5.0,   # 5 seconds, +50 HP
                'surgery': 10.0  # 10 seconds, full heal + stops bleeding
            }
            
            heal_time = healing_speeds.get(self.healing_type, 3.0)
            self.healing_progress += dt / heal_time
            
            if self.healing_progress >= 1.0:
                # Healing complete!
                if self.healing_type == 'bandage':
                    self.player_health = min(100, self.player_health + 25)
                    self.is_bleeding = False
                elif self.healing_type == 'medkit':
                    self.player_health = min(100, self.player_health + 50)
                elif self.healing_type == 'surgery':
                    self.player_health = 100
                    self.is_bleeding = False
                
                self.is_healing = False
                self.healing_progress = 0
                self.healing_type = None
                print(f"✅ Healing complete! HP: {self.player_health}")
        
        # Update weapons
        for weapon in self.weapons.values():
            weapon.update()
        
        # === CONTINUOUS FIRE FOR AUTOMATIC WEAPONS ===
        # Check if left mouse button is held down for automatic fire
        if not self.in_menu and not self.in_team_selection and not self.in_server_connect:
            # Can't shoot while healing!
            if not self.is_healing:
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
        
        # ULTRA REALISTIC SYSTEMS
        self._update_realistic_mechanics(dt)
    
    def _update_realistic_mechanics(self, dt):
        """🎯 ULTRA REALISTIC SURVIVAL & COMBAT MECHANICS"""
        
        # === WEAPON MAINTENANCE ===
        current_weapon = self.weapons.get(self.current_weapon)
        if current_weapon:
            # Barrel cooling (affects accuracy)
            current_weapon.barrel_heat = max(0, current_weapon.barrel_heat - 2 * dt)
            
            # Durability slowly degrades
            if random.random() < 0.001:  # Random wear
                current_weapon.durability = max(0, current_weapon.durability - 0.5)
        
        # === INJURY SYSTEM ===
        # Calculate total pain from all injuries
        total_injury_damage = sum(injury['damage'] for injury in self.injuries.values())
        self.pain_level = min(100, total_injury_damage * 2)
        
        # Pain affects everything
        if self.pain_level > 50:
            # Severe pain: slower movement, worse aim
            pain_factor = (100 - self.pain_level) / 100
            self.current_speed *= pain_factor
        
        # Bleeding from injuries
        bleeding_parts = [p for p, inj in self.injuries.items() if inj['bleeding']]
        if bleeding_parts:
            self.is_bleeding = True
            self.blood_loss += len(bleeding_parts) * 2 * dt  # Multiple bleeds = faster death
            self.player_health -= len(bleeding_parts) * self.bleed_damage * dt
        
        # Fractures affect mobility
        leg_fractures = (self.injuries['left_leg']['fracture'] or 
                        self.injuries['right_leg']['fracture'])
        if leg_fractures:
            self.walk_speed = 1.0  # Very slow with broken leg
            self.sprint_speed = 1.5  # Can barely run
        
        # Arm fractures affect aim
        arm_fractures = (self.injuries['left_arm']['fracture'] or 
                        self.injuries['right_arm']['fracture'])
        if arm_fractures:
            self.weapon_sway_x *= 2.0  # Double weapon sway
            self.weapon_sway_y *= 2.0
        
        # === SURVIVAL NEEDS ===
        # Hydration drains over time
        self.hydration = max(0, self.hydration - 1.5 * dt)
        if self.hydration < 30:
            # Dehydration: stamina penalty
            self.max_stamina = 50
        elif self.hydration < 60:
            self.max_stamina = 75
        else:
            self.max_stamina = 100
        
        # Energy/hunger drains faster when moving
        is_moving = (pygame.K_w in self.keys or pygame.K_s in self.keys or 
                    pygame.K_a in self.keys or pygame.K_d in self.keys)
        energy_drain = 2.0 if is_moving else 0.8
        self.energy = max(0, self.energy - energy_drain * dt)
        
        if self.energy < 20:
            # Starvation: health slowly drains
            self.player_health -= 0.5 * dt
        
        # === ENVIRONMENTAL EFFECTS ===
        # Temperature affects performance
        temp_diff = abs(self.body_temperature - 37.0)
        if temp_diff > 2.0:
            # Hypothermia or fever
            self.stamina_drain = 40  # Faster exhaustion
            if temp_diff > 4.0:
                self.player_health -= 1 * dt  # Taking damage
        
        # Adjust body temp toward ambient
        if self.body_temperature > self.ambient_temperature:
            self.body_temperature -= 0.5 * dt
        elif self.body_temperature < self.ambient_temperature:
            self.body_temperature += 0.5 * dt
        
        # === NOISE SYSTEM ===
        # Noise attracts enemies
        if self.is_sprinting:
            self.noise_level = min(100, self.noise_level + 50 * dt)
        else:
            self.noise_level = max(0, self.noise_level - 30 * dt)
        
        # Shooting makes LOTS of noise
        if current_weapon and current_weapon.shots_fired > 0:
            weapon_loudness = {
                'pistol': 60, 'assault_rifle': 85, 'sniper': 95,
                'smg': 70, 'shotgun': 90, 'lmg': 88
            }
            loudness = weapon_loudness.get(self.current_weapon, 75)
            # Suppressor reduces noise
            barrel_attachment = self.current_attachments.get('barrel', '')
            if barrel_attachment and 'Suppressor' in str(barrel_attachment):
                loudness *= 0.3
            self.noise_level = min(100, self.noise_level + loudness)
        
        # === INFECTION RISK ===
        # Untreated injuries get infected
        for body_part, injury in self.injuries.items():
            if injury['bleeding'] or injury['damage'] > 20:
                self.infection_risk += 0.5 * dt
        
        if self.infection_risk > 50:
            # Infection: fever and health drain
            self.body_temperature += 0.1 * dt
            self.player_health -= 0.3 * dt
        
        # === WEATHER EFFECTS ===
        # Rain affects visibility and sound
        if self.weather == 'rain':
            self.visibility = 60  # Reduced visibility
            self.noise_level *= 0.7  # Rain masks sounds
        elif self.weather == 'fog':
            self.visibility = 40  # Very low visibility
        else:
            self.visibility = 100
        
        # Wind affects bullet trajectory
        self.wind_speed = random.uniform(0, 15)  # m/s
        self.wind_direction = random.uniform(0, 360)
    
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
    
    def _get_body_part_hit(self, bullet_y, enemy_y):
        """Determine which body part was hit - ULTRA REALISTIC"""
        hit_height = enemy_y - bullet_y
        
        # Body zones (from top to bottom)
        if hit_height < 5:
            return 'head', 3.0  # Head: 3.0x damage (instant kill potential)
        elif hit_height < 15:
            return 'chest', 1.0  # Chest/Upper torso: 1.0x damage (vital organs)
        elif hit_height < 25:
            return 'stomach', 0.85  # Stomach/Lower torso: 0.85x damage
        elif hit_height < 35:
            return 'arms', 0.6  # Arms: 0.6x damage (causes bleeding)
        else:
            return 'legs', 0.7  # Legs: 0.7x damage (slows movement)
    
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
                    # === ULTRA REALISTIC DAMAGE ZONES ===
                    body_part, damage_mult = self._get_body_part_hit(bullet['y'], enemy['y'])
                    is_headshot = (body_part == 'head')
                    
                    # Calculate damage with body part multiplier
                    damage = bullet['damage'] * damage_mult
                    
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
                        
                        # 🎁 CHECK FOR KILL MILESTONE REWARDS
                        self._check_kill_milestones()
                        
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
    
    def _check_kill_milestones(self):
        """🎁 Check if player reached a kill milestone and give rewards"""
        for milestone in self.kill_milestones:
            if self.kills >= milestone and milestone > self.last_milestone_reached:
                self.last_milestone_reached = milestone
                self._give_kill_reward(milestone)
                break
    
    def _give_kill_reward(self, kills):
        """🎁 Give rewards based on kill milestone"""
        current_time = time.time()
        
        # Calculate rewards based on milestone
        if kills <= 10:
            health_reward = 25
            armor_reward = 15
            ammo_mult = 0.5
            reward_tier = "BRONZE"
            tier_color = (205, 127, 50)
        elif kills <= 50:
            health_reward = 50
            armor_reward = 30
            ammo_mult = 1.0
            reward_tier = "SILVER"
            tier_color = (192, 192, 192)
        elif kills <= 100:
            health_reward = 75
            armor_reward = 50
            ammo_mult = 1.5
            reward_tier = "GOLD"
            tier_color = (255, 215, 0)
        elif kills <= 300:
            health_reward = 100
            armor_reward = 75
            ammo_mult = 2.0
            reward_tier = "PLATINUM"
            tier_color = (229, 228, 226)
        else:
            health_reward = 100
            armor_reward = 100
            ammo_mult = 3.0
            reward_tier = "DIAMOND"
            tier_color = (185, 242, 255)
        
        # Apply rewards
        rewards_text = []
        
        # Health reward
        if self.player_health < self.player_max_health:
            old_health = self.player_health
            self.player_health = min(self.player_max_health, self.player_health + health_reward)
            actual_health = int(self.player_health - old_health)
            rewards_text.append(f"+{actual_health} HP")
        
        # Armor reward
        old_armor = self.player_armor
        self.player_armor = min(100, self.player_armor + armor_reward)
        actual_armor = int(self.player_armor - old_armor)
        if actual_armor > 0:
            rewards_text.append(f"+{actual_armor} ARMOR")
        
        # Ammo for all weapons
        ammo_given = 0
        for weapon_name, weapon in self.weapons.items():
            if weapon.magazine_count < 10:  # Don't overflow
                mags_to_give = int(2 * ammo_mult)
                weapon.magazine_count += mags_to_give
                ammo_given += mags_to_give
        
        if ammo_given > 0:
            rewards_text.append(f"+{ammo_given} MAGAZINES")
        
        # Score bonus
        score_bonus = kills * 100
        self.score += score_bonus
        rewards_text.append(f"+{score_bonus} SCORE")
        
        # XP bonus
        xp_bonus = kills * 50
        self.xp += xp_bonus
        rewards_text.append(f"+{xp_bonus} XP")
        
        # Track total rewards
        self.total_rewards_earned += 1
        
        # Create epic notification
        self.reward_notifications.append({
            'kills': kills,
            'tier': reward_tier,
            'tier_color': tier_color,
            'rewards': rewards_text,
            'time': current_time,
            'duration': 8.0,  # Show for 8 seconds
            'alpha': 255
        })
        
        # Play reward sound (if available)
        if self.sound_enabled:
            self.play_sound('achievement')
        
        print(f"\n🎁 MILESTONE REWARD!")
        print(f"✨ {kills} KILLS - {reward_tier} TIER")
        print(f"💰 Rewards: {', '.join(rewards_text)}")
    
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
                # Speed boost affects sprint speed
                pass  # Speed is handled by sprint_multiplier
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
        elif self.in_loadout:
            self._render_loadout()
        elif self.in_settings:
            self._render_settings()
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
        """🌐 ULTRA MODERN SERVER CONNECTION GUI - REDESIGNED"""
        current_time = pygame.time.get_ticks()
        pulse = abs(math.sin(current_time / 600))
        
        # === PREMIUM DARK BACKGROUND WITH HEXAGON GRID ===
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(10 + (20 - 10) * ratio)
            g = int(12 + (24 - 12) * ratio)
            b = int(18 + (32 - 18) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Animated hexagon grid pattern (futuristic)
        hex_spacing = 60
        for x in range(-30, self.screen_width + 30, hex_spacing):
            for y in range(-30, self.screen_height + 30, int(hex_spacing * 0.866)):
                offset_x = (y // int(hex_spacing * 0.866)) % 2 * (hex_spacing // 2)
                hex_x = x + offset_x
                hex_y = y
                alpha = int(8 + 12 * abs(math.sin((current_time / 2000) + hex_x / 150 + hex_y / 150)))
                size = 10
                points = []
                for i in range(6):
                    angle = math.pi / 3 * i
                    px = hex_x + size * math.cos(angle)
                    py = hex_y + size * math.sin(angle)
                    points.append((px, py))
                if len(points) > 2:
                    try:
                        pygame.draw.aalines(self.screen, (30, 50, 80), True, points, 1)
                    except:
                        pass
        
        # Floating particles
        for i in range(15):
            particle_x = (self.screen_width // 2 + int(200 * math.sin(current_time / 1000 + i))) % self.screen_width
            particle_y = (i * 50 + int(30 * math.cos(current_time / 800 + i))) % self.screen_height
            pygame.draw.circle(self.screen, (50, 100, 200), (particle_x, particle_y), 2)
        
        # === ULTRA MODERN TITLE WITH GLOW ===
        title_y = 60
        title_font = pygame.font.Font(None, 110)
        title_text = "SERVER CONNECTION"
        
        # Multi-layer shadow
        for i in range(5, 0, -1):
            shadow = title_font.render(title_text, True, (0, 20, 40))
            self.screen.blit(shadow, (self.screen_width//2 - shadow.get_width()//2 + i, title_y + i))
        
        # Glow effect
        title_glow = title_font.render(title_text, True, (0, 180, 255))
        self.screen.blit(title_glow, (self.screen_width//2 - title_glow.get_width()//2 - 2, title_y - 2))
        
        # Main title
        title = title_font.render(title_text, True, (255, 255, 255))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, title_y))
        
        # === PREMIUM SERVER ICON WITH NETWORK ANIMATION ===
        icon_y = 190
        icon_size = int(110 + 15 * pulse)
        
        # Multi-layer glow rings
        for i in range(4):
            ring_size = icon_size + i * 25
            ring_alpha = int((80 - i * 15) * (0.7 + 0.3 * pulse))
            pygame.draw.circle(self.screen, (0, 150, 255), 
                             (self.screen_width//2, icon_y), ring_size//2, 2)
        
        # Icon background
        pygame.draw.circle(self.screen, (20, 40, 70), (self.screen_width//2, icon_y), icon_size//2 - 10)
        pygame.draw.circle(self.screen, (0, 120, 220), (self.screen_width//2, icon_y), icon_size//2 - 10, 4)
        
        # Animated network nodes
        for i in range(6):
            angle = (current_time / 1500 + i * math.pi / 3) % (2 * math.pi)
            node_x = self.screen_width//2 + int(40 * math.cos(angle))
            node_y = icon_y + int(40 * math.sin(angle))
            pygame.draw.circle(self.screen, (0, 200, 255), (node_x, node_y), 5)
            pygame.draw.line(self.screen, (0, 150, 255), 
                           (self.screen_width//2, icon_y), (node_x, node_y), 2)
        
        # Center hub
        pygame.draw.circle(self.screen, (0, 220, 255), (self.screen_width//2, icon_y), 12)
        pygame.draw.circle(self.screen, (255, 255, 255), (self.screen_width//2, icon_y), 6)
        
        # === PREMIUM INPUT PANEL WITH GLASS EFFECT ===
        panel_width = 750
        panel_height = 380
        panel_x = self.screen_width//2 - panel_width//2
        panel_y = 310
        
        # Multi-layer panel glow (more intense)
        for i in range(8):
            glow_offset = i * 3
            glow_alpha = int((60 - i * 6) * (0.6 + 0.4 * pulse))
            glow_rect = (panel_x - glow_offset, panel_y - glow_offset, 
                        panel_width + glow_offset * 2, panel_height + glow_offset * 2)
            pygame.draw.rect(self.screen, (0, 120, 220), glow_rect, border_radius=22)
        
        # Glass panel effect
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (18, 28, 45, 250), (0, 0, panel_width, panel_height), border_radius=18)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        # Panel borders (dual-layer)
        pygame.draw.rect(self.screen, (0, 180, 255), (panel_x, panel_y, panel_width, panel_height), 4, border_radius=18)
        pygame.draw.rect(self.screen, (100, 200, 255), (panel_x + 2, panel_y + 2, panel_width - 4, panel_height - 4), 2, border_radius=16)
        
        # === MODERN INPUT FIELD WITH 3D EFFECT ===
        label_y = panel_y + 60
        label_font = pygame.font.Font(None, 44)
        label = label_font.render("Server IP Address:", True, (180, 220, 255))
        self.screen.blit(label, (panel_x + 60, label_y))
        
        # Input box with shadow (3D effect)
        input_y = label_y + 65
        input_width = panel_width - 120
        input_height = 80
        input_x = panel_x + 60
        
        # Shadow
        pygame.draw.rect(self.screen, (5, 10, 20), 
                        (input_x + 4, input_y + 4, input_width, input_height), border_radius=12)
        
        # Input background (dark)
        pygame.draw.rect(self.screen, (25, 38, 58), 
                        (input_x, input_y, input_width, input_height), border_radius=12)
        
        # Animated glowing border
        border_brightness = int(180 + 75 * pulse)
        border_color = (0, border_brightness, 255) if self.server_ip else (60, 90, 140)
        pygame.draw.rect(self.screen, border_color, 
                        (input_x, input_y, input_width, input_height), 3, border_radius=12)
        
        # IP text (larger font)
        ip_font = pygame.font.Font(None, 52)
        ip_text = self.server_ip if self.server_ip else "192.168.1.100"
        ip_color = (255, 255, 255) if self.server_ip else (90, 110, 140)
        ip_surf = ip_font.render(ip_text, True, ip_color)
        self.screen.blit(ip_surf, (input_x + 25, input_y + 22))
        
        # Smooth animated cursor
        if int(current_time / 530) % 2 == 0:
            cursor_x = input_x + 25 + ip_surf.get_width() + 8
            cursor_alpha = int(200 + 55 * pulse)
            pygame.draw.rect(self.screen, (0, 220, 255), 
                           (cursor_x, input_y + 18, 3, input_height - 36))
        
        # === EXAMPLES SECTION (MODERN STYLE) ===
        examples_y = input_y + input_height + 45
        examples_title = pygame.font.Font(None, 36).render("Examples:", True, (140, 180, 220))
        self.screen.blit(examples_title, (input_x, examples_y))
        
        examples = [
            ("127.0.0.1", "Localhost"),
            ("192.168.1.100", "Local Network"),
            ("game.server.com", "Domain")
        ]
        
        ex_font = pygame.font.Font(None, 32)
        for i, (ip, desc) in enumerate(examples):
            ex_y = examples_y + 40 + i * 32
            # Modern bullet point (circle)
            pygame.draw.circle(self.screen, (0, 180, 255), (input_x + 18, ex_y + 10), 4)
            # Example text with IP and description
            ex_text = f"{ip} ({desc})"
            ex_surf = ex_font.render(ex_text, True, (110, 150, 200))
            self.screen.blit(ex_surf, (input_x + 35, ex_y))
        
        # === STATUS MESSAGE WITH BACKGROUND ===
        if self.connection_status:
            status_y = panel_y + panel_height - 65
            status_font = pygame.font.Font(None, 42)
            
            if "✓" in self.connection_status or "Connected" in self.connection_status:
                status_color = (0, 255, 120)
                icon = "✓"
            elif "⚠️" in self.connection_status or "warn" in self.connection_status.lower():
                status_color = (255, 200, 50)
                icon = "⚠"
            else:
                status_color = (255, 80, 80)
                icon = "✗"
            
            # Status with icon and background
            status_text = f"{icon} {self.connection_status}"
            status_surf = status_font.render(status_text, True, status_color)
            status_bg_width = status_surf.get_width() + 40
            status_bg_x = panel_x + panel_width//2 - status_bg_width//2
            pygame.draw.rect(self.screen, (status_color[0]//5, status_color[1]//5, status_color[2]//5),
                           (status_bg_x, status_y - 10, status_bg_width, 50), border_radius=8)
            self.screen.blit(status_surf, (panel_x + panel_width//2 - status_surf.get_width()//2, status_y))
        
        # === BOTTOM INSTRUCTIONS (MODERN KEY BUTTONS) ===
        inst_y = self.screen_height - 140
        inst_font = pygame.font.Font(None, 38)
        
        instructions = [
            ("Type the server IP address", (150, 180, 220)),
            ("ENTER", (0, 220, 255), "Connect to Server", (180, 200, 230)),
            ("ESC", (255, 100, 100), "Back to Menu", (180, 200, 230))
        ]
        
        for i, inst in enumerate(instructions):
            y_pos = inst_y + i * 40
            if len(inst) == 2:
                # Simple text
                text, color = inst
                surf = inst_font.render(text, True, color)
                self.screen.blit(surf, (self.screen_width//2 - surf.get_width()//2, y_pos))
            else:
                # Key button + action
                key, key_color, action, action_color = inst
                key_surf = pygame.font.Font(None, 36).render(key, True, (255, 255, 255))
                key_bg_width = key_surf.get_width() + 30
                key_x = self.screen_width//2 - 100
                # Draw key button
                pygame.draw.rect(self.screen, key_color, (key_x, y_pos - 5, key_bg_width, 35), border_radius=6)
                self.screen.blit(key_surf, (key_x + 15, y_pos))
                # Draw action text
                action_surf = inst_font.render(action, True, action_color)
                self.screen.blit(action_surf, (key_x + key_bg_width + 15, y_pos))
        
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
    
    def _draw_weapon_icon(self, surface, weapon_name, x, y, scale=1.0):
        """Draw a detailed weapon icon"""
        # Brighter colors for visibility
        gun_metal = (120, 130, 145)
        barrel_color = (90, 95, 105)
        accent_color = (150, 160, 175)
        highlight = (180, 190, 205)
        dark_metal = (70, 75, 85)
        
        if weapon_name in ['rifle', 'assault_rifle']:
            # AR-15 style rifle
            # Stock
            pygame.draw.rect(surface, gun_metal, (x, y+15, 15*scale, 8*scale))
            pygame.draw.rect(surface, dark_metal, (x, y+15, 15*scale, 8*scale), 1)
            # Receiver (main body)
            pygame.draw.rect(surface, gun_metal, (x+10, y+12, 35*scale, 12*scale))
            pygame.draw.rect(surface, highlight, (x+10, y+12, 35*scale, 12*scale), 1)
            # Barrel
            pygame.draw.rect(surface, barrel_color, (x+40, y+15, 40*scale, 6*scale))
            pygame.draw.line(surface, (50, 55, 65), (x+40, y+15), (x+80, y+15), 1)
            # Magazine (with color accent)
            pygame.draw.rect(surface, (180, 160, 100), (x+25, y+24, 10*scale, 15*scale))
            pygame.draw.rect(surface, dark_metal, (x+25, y+24, 10*scale, 15*scale), 1)
            # Grip
            pygame.draw.rect(surface, dark_metal, (x+30, y+24, 6*scale, 8*scale))
            # Rail/sight
            pygame.draw.line(surface, highlight, (x+20, y+12), (x+60, y+12), 2)
            # Red dot sight
            pygame.draw.circle(surface, (255, 50, 50), (x+25, y+10), 2)
            # Handguard details
            for i in range(3):
                pygame.draw.line(surface, (100, 110, 125), (x+40+i*5, y+14), (x+40+i*5, y+22), 1)
                
        elif weapon_name == 'sniper':
            # Bolt-action sniper rifle
            # Stock (wooden)
            pygame.draw.polygon(surface, (140, 100, 70), [(x, y+18), (x+20, y+15), (x+20, y+25), (x, y+22)])
            pygame.draw.polygon(surface, dark_metal, [(x, y+18), (x+20, y+15), (x+20, y+25), (x, y+22)], 1)
            # Receiver
            pygame.draw.rect(surface, gun_metal, (x+15, y+13, 25*scale, 14*scale))
            pygame.draw.rect(surface, highlight, (x+15, y+13, 25*scale, 14*scale), 1)
            # Long barrel
            pygame.draw.rect(surface, barrel_color, (x+35, y+16, 50*scale, 5*scale))
            pygame.draw.line(surface, (50, 55, 65), (x+35, y+16), (x+85, y+16), 1)
            # Scope (large with blue tint)
            pygame.draw.ellipse(surface, dark_metal, (x+25, y+8, 25*scale, 8*scale))
            pygame.draw.circle(surface, (60, 120, 180), (x+37, y+12), 5)
            pygame.draw.circle(surface, (100, 160, 220), (x+37, y+12), 3)
            pygame.draw.circle(surface, (255, 100, 100), (x+37, y+12), 1)  # Crosshair
            # Bipod
            pygame.draw.line(surface, gun_metal, (x+60, y+21), (x+55, y+28), 2)
            pygame.draw.line(surface, gun_metal, (x+70, y+21), (x+75, y+28), 2)
            # Magazine
            pygame.draw.rect(surface, (180, 160, 100), (x+30, y+27, 8*scale, 10*scale))
            pygame.draw.rect(surface, dark_metal, (x+30, y+27, 8*scale, 10*scale), 1)
            
        elif weapon_name == 'smg':
            # Compact SMG (MP5 style)
            # Receiver (compact)
            pygame.draw.rect(surface, gun_metal, (x+10, y+15, 30*scale, 10*scale))
            pygame.draw.rect(surface, highlight, (x+10, y+15, 30*scale, 10*scale), 1)
            # Short barrel
            pygame.draw.rect(surface, barrel_color, (x+35, y+17, 25*scale, 6*scale))
            pygame.draw.line(surface, (50, 55, 65), (x+35, y+17), (x+60, y+17), 1)
            # Magazine (vertical with yellow accent)
            pygame.draw.rect(surface, (180, 160, 100), (x+22, y+25, 8*scale, 18*scale))
            pygame.draw.rect(surface, dark_metal, (x+22, y+25, 8*scale, 18*scale), 1)
            # Stock (folded)
            pygame.draw.line(surface, dark_metal, (x+5, y+18), (x+12, y+18), 3)
            pygame.draw.line(surface, dark_metal, (x+5, y+22), (x+12, y+22), 3)
            # Grip
            pygame.draw.rect(surface, gun_metal, (x+25, y+25, 5*scale, 8*scale))
            # Front sight
            pygame.draw.rect(surface, highlight, (x+55, y+15, 2, 4))
            # Suppressor
            pygame.draw.rect(surface, (35, 38, 45), (x+60, y+18, 12*scale, 4*scale))
            
        elif weapon_name == 'lmg':
            # Heavy machine gun
            # Stock (thick)
            pygame.draw.rect(surface, gun_metal, (x, y+16, 18*scale, 10*scale))
            pygame.draw.rect(surface, highlight, (x, y+16, 18*scale, 10*scale), 1)
            # Large receiver
            pygame.draw.rect(surface, gun_metal, (x+15, y+14, 30*scale, 14*scale))
            pygame.draw.rect(surface, highlight, (x+15, y+14, 30*scale, 14*scale), 1)
            # Heavy barrel
            pygame.draw.rect(surface, barrel_color, (x+40, y+17, 45*scale, 7*scale))
            pygame.draw.line(surface, (50, 55, 65), (x+40, y+17), (x+85, y+17), 1)
            # Barrel cooling holes (orange hot)
            for i in range(5):
                pygame.draw.circle(surface, (255, 100, 50), (x+50+i*7, y+20), 2)
            # Box magazine (large with ammo color)
            pygame.draw.rect(surface, (200, 180, 120), (x+25, y+28, 20*scale, 15*scale))
            pygame.draw.rect(surface, dark_metal, (x+25, y+28, 20*scale, 15*scale), 2)
            pygame.draw.rect(surface, (180, 160, 100), (x+27, y+30, 16*scale, 11*scale))
            # Bipod
            pygame.draw.line(surface, gun_metal, (x+60, y+24), (x+55, y+32), 3)
            pygame.draw.line(surface, gun_metal, (x+70, y+24), (x+75, y+32), 3)
            # Grip
            pygame.draw.rect(surface, dark_metal, (x+35, y+28, 6*scale, 10*scale))
            
        elif weapon_name == 'shotgun':
            # Pump-action shotgun
            # Stock (wooden color)
            pygame.draw.rect(surface, (140, 100, 70), (x, y+16, 20*scale, 9*scale))
            pygame.draw.rect(surface, dark_metal, (x, y+16, 20*scale, 9*scale), 1)
            # Receiver
            pygame.draw.rect(surface, gun_metal, (x+18, y+15, 22*scale, 11*scale))
            pygame.draw.rect(surface, highlight, (x+18, y+15, 22*scale, 11*scale), 1)
            # Barrel (large diameter)
            pygame.draw.rect(surface, barrel_color, (x+35, y+16, 40*scale, 9*scale))
            pygame.draw.line(surface, (50, 55, 65), (x+35, y+16), (x+75, y+16), 2)
            # Pump grip (wooden)
            pygame.draw.rect(surface, (120, 90, 60), (x+45, y+17, 12*scale, 7*scale))
            pygame.draw.rect(surface, dark_metal, (x+45, y+17, 12*scale, 7*scale), 1)
            pygame.draw.line(surface, dark_metal, (x+45, y+24), (x+45, y+28), 2)
            # Front sight
            pygame.draw.rect(surface, (255, 200, 100), (x+70, y+14, 2, 5))
            # Shell holder on side (red shells)
            for i in range(4):
                pygame.draw.circle(surface, (220, 60, 60), (x+25+i*7, y+12), 2)
                pygame.draw.circle(surface, (255, 200, 100), (x+25+i*7, y+12), 1)
            
        elif weapon_name == 'pistol':
            # Semi-auto pistol
            # Slide
            pygame.draw.rect(surface, gun_metal, (x+15, y+18, 30*scale, 7*scale))
            pygame.draw.rect(surface, highlight, (x+15, y+18, 30*scale, 7*scale), 1)
            pygame.draw.line(surface, (50, 55, 65), (x+15, y+18), (x+45, y+18), 1)
            # Frame (with tan/FDE color)
            pygame.draw.rect(surface, (160, 140, 110), (x+18, y+23, 22*scale, 8*scale))
            pygame.draw.rect(surface, dark_metal, (x+18, y+23, 22*scale, 8*scale), 1)
            # Grip
            pygame.draw.polygon(surface, (140, 120, 90), [(x+20, y+31), (x+28, y+31), (x+25, y+40), (x+20, y+40)])
            pygame.draw.polygon(surface, dark_metal, [(x+20, y+31), (x+28, y+31), (x+25, y+40), (x+20, y+40)], 1)
            # Barrel
            pygame.draw.rect(surface, barrel_color, (x+43, y+19, 12*scale, 5*scale))
            # Trigger guard
            pygame.draw.arc(surface, dark_metal, (x+25, y+28, 10, 8), 0, 3.14, 2)
            # Sights (tritium green dots)
            pygame.draw.rect(surface, (100, 255, 100), (x+22, y+16, 2, 3))
            pygame.draw.rect(surface, (100, 255, 100), (x+40, y+16, 2, 3))
            # Magazine release
            pygame.draw.circle(surface, (255, 200, 100), (x+23, y+27), 2)
            
        else:
            # Default gun shape
            pygame.draw.rect(surface, gun_metal, (x+10, y+15, 40*scale, 12*scale))
            pygame.draw.rect(surface, barrel_color, (x+45, y+17, 20*scale, 8*scale))
    
    def _render_loadout(self):
        """🎯 MODERN CLEAN LOADOUT SCREEN - Sleek & Professional"""
        current_time = pygame.time.get_ticks()
        
        # === CLEAN MODERN BACKGROUND ===
        # Smooth gradient background
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(18 + (28 - 18) * ratio)
            g = int(20 + (32 - 20) * ratio)
            b = int(25 + (40 - 25) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # Minimal grid pattern
        grid_spacing = 100
        for x in range(0, self.screen_width, grid_spacing):
            pygame.draw.line(self.screen, (35, 40, 48), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_spacing):
            pygame.draw.line(self.screen, (35, 40, 48), (0, y), (self.screen_width, y), 1)
        
        # === SIMPLE TITLE ===
        title_font = pygame.font.Font(None, 72)
        title = "LOADOUT SELECTION"
        
        # Simple shadow
        shadow = title_font.render(title, True, (10, 10, 10))
        self.screen.blit(shadow, (self.screen_width//2 - shadow.get_width()//2 + 2, 42))
        
        # Main title
        title_surf = title_font.render(title, True, (220, 230, 240))
        self.screen.blit(title_surf, (self.screen_width//2 - title_surf.get_width()//2, 40))
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 26)
        subtitle = "Choose your combat class"
        subtitle_surf = subtitle_font.render(subtitle, True, (140, 150, 160))
        self.screen.blit(subtitle_surf, (self.screen_width//2 - subtitle_surf.get_width()//2, 95))
        
        # === CLEAN LOADOUT CARDS ===
        card_width = 750
        card_height = 165
        card_spacing = 15
        start_y = 150
        card_x = self.screen_width//2 - card_width//2
        
        for i, loadout in enumerate(self.loadouts):
            y = start_y + i * (card_height + card_spacing)
            is_selected = (i == self.loadout_selection)
            is_current = (i == self.current_loadout)
            
            # === CLEAN CARD DESIGN ===
            if is_selected:
                # Selected card - subtle highlight
                pygame.draw.rect(self.screen, (45, 55, 70), (card_x, y, card_width, card_height), border_radius=12)
                pygame.draw.rect(self.screen, (100, 180, 255), (card_x, y, card_width, card_height), 3, border_radius=12)
                
                # Left accent bar
                pygame.draw.rect(self.screen, (100, 180, 255), (card_x, y, 6, card_height), border_radius=12)
                
            elif is_current:
                # Equipped card - gold accent
                pygame.draw.rect(self.screen, (40, 45, 55), (card_x, y, card_width, card_height), border_radius=12)
                pygame.draw.rect(self.screen, (255, 200, 80), (card_x, y, card_width, card_height), 3, border_radius=12)
                
                # Left accent bar
                pygame.draw.rect(self.screen, (255, 200, 80), (card_x, y, 6, card_height), border_radius=12)
                
            else:
                # Normal card
                pygame.draw.rect(self.screen, (30, 35, 45), (card_x, y, card_width, card_height), border_radius=12)
                pygame.draw.rect(self.screen, (60, 70, 85), (card_x, y, card_width, card_height), 2, border_radius=12)
            
            # === ICON ===
            icon_x = card_x + 70
            icon_y = y + card_height//2
            
            # Icon background circle
            if is_selected:
                pygame.draw.circle(self.screen, (60, 100, 140), (icon_x, icon_y), 45)
                pygame.draw.circle(self.screen, (100, 180, 255), (icon_x, icon_y), 45, 2)
            elif is_current:
                pygame.draw.circle(self.screen, (80, 70, 40), (icon_x, icon_y), 45)
                pygame.draw.circle(self.screen, (255, 200, 80), (icon_x, icon_y), 45, 2)
            else:
                pygame.draw.circle(self.screen, (40, 50, 65), (icon_x, icon_y), 45)
                pygame.draw.circle(self.screen, (70, 80, 100), (icon_x, icon_y), 45, 2)
            
            # Icon
            icon_font = pygame.font.Font(None, 65)
            icon_color = (255, 255, 255) if (is_selected or is_current) else (180, 190, 200)
            icon_surf = icon_font.render(loadout['icon'], True, icon_color)
            self.screen.blit(icon_surf, (icon_x - icon_surf.get_width()//2, icon_y - icon_surf.get_height()//2))
            
            # === TEXT CONTENT ===
            text_x = card_x + 140
            
            # Loadout name
            name_font = pygame.font.Font(None, 48)
            if is_current:
                name_color = (255, 200, 80)
            elif is_selected:
                name_color = (200, 230, 255)
            else:
                name_color = (200, 210, 220)
            
            name_surf = name_font.render(loadout['name'], True, name_color)
            self.screen.blit(name_surf, (text_x, y + 18))
            
            # Description
            desc_surf = self.font_medium.render(loadout['description'], True, (150, 160, 170))
            self.screen.blit(desc_surf, (text_x, y + 58))
            
            # === WEAPON DISPLAY WITH IMAGES ===
            weapons_y = y + 75
            weapon_font = self.font_small
            
            # Primary Weapon Box
            primary_box_x = text_x
            primary_box_y = weapons_y
            primary_box_width = 165
            primary_box_height = 58
            
            # Background with darker interior
            pygame.draw.rect(self.screen, (25, 30, 38), (primary_box_x, primary_box_y, primary_box_width, primary_box_height), border_radius=6)
            pygame.draw.rect(self.screen, (120, 200, 255), (primary_box_x, primary_box_y, primary_box_width, primary_box_height), 2, border_radius=6)
            
            # Label
            primary_label = weapon_font.render("PRIMARY", True, (120, 200, 255))
            self.screen.blit(primary_label, (primary_box_x + 5, primary_box_y + 2))
            
            # Draw weapon image (centered better)
            weapon_icon_y = primary_box_y + 16
            self._draw_weapon_icon(self.screen, loadout['primary'], primary_box_x + 8, weapon_icon_y, 1.1)
            
            # Weapon name at bottom
            weapon_name_surf = weapon_font.render(loadout['primary'].upper().replace('_', ' '), True, (200, 220, 240))
            self.screen.blit(weapon_name_surf, (primary_box_x + 5, primary_box_y + primary_box_height - 16))
            
            # Secondary Weapon Box
            secondary_box_x = text_x + primary_box_width + 10
            secondary_box_y = weapons_y
            secondary_box_width = 165
            secondary_box_height = 58
            
            # Background with darker interior
            pygame.draw.rect(self.screen, (25, 35, 30), (secondary_box_x, secondary_box_y, secondary_box_width, secondary_box_height), border_radius=6)
            pygame.draw.rect(self.screen, (120, 255, 150), (secondary_box_x, secondary_box_y, secondary_box_width, secondary_box_height), 2, border_radius=6)
            
            # Label
            secondary_label = weapon_font.render("SECONDARY", True, (120, 255, 150))
            self.screen.blit(secondary_label, (secondary_box_x + 5, secondary_box_y + 2))
            
            # Draw weapon image (centered better)
            weapon_icon_y = secondary_box_y + 16
            self._draw_weapon_icon(self.screen, loadout['secondary'], secondary_box_x + 8, weapon_icon_y, 1.1)
            
            # Weapon name at bottom
            weapon_name_surf = weapon_font.render(loadout['secondary'].upper().replace('_', ' '), True, (200, 220, 240))
            self.screen.blit(weapon_name_surf, (secondary_box_x + 5, secondary_box_y + secondary_box_height - 16))
            
            # Perk display
            perk_y = weapons_y + secondary_box_height + 8
            perk_text = f"⚡ PERK: {loadout['perk']}"
            perk_color = (255, 200, 80) if is_current else (180, 150, 255)
            perk_surf = weapon_font.render(perk_text, True, perk_color)
            self.screen.blit(perk_surf, (text_x, perk_y))
            
            # === STATS - SIMPLE BARS ===
            stats_x = card_x + card_width - 200
            stats_y = y + 22
            stats = loadout['stats']
            stat_info = [
                ('DMG', 'damage', (255, 100, 100)),
                ('RNG', 'range', (100, 180, 255)),
                ('MOB', 'mobility', (120, 255, 150)),
                ('ACC', 'accuracy', (255, 200, 100))
            ]
            
            for j, (stat_name, stat_key, stat_color) in enumerate(stat_info):
                stat_y_pos = stats_y + j * 30
                
                # Stat name (compact)
                stat_label = self.font_small.render(stat_name, True, (140, 150, 160))
                self.screen.blit(stat_label, (stats_x, stat_y_pos))
                
                # Stat bar
                bar_width = 110
                bar_height = 12
                bar_x = stats_x + 35
                bar_y = stat_y_pos + 2
                
                # Background
                pygame.draw.rect(self.screen, (20, 25, 32), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
                
                # Value bar with glow
                value_width = int((stats[stat_key] / 10) * bar_width)
                if value_width > 0:
                    pygame.draw.rect(self.screen, stat_color, (bar_x, bar_y, value_width, bar_height), border_radius=6)
                
                # Border
                pygame.draw.rect(self.screen, (60, 70, 85), (bar_x, bar_y, bar_width, bar_height), 1, border_radius=6)
                
                # Value text
                value_text = f"{stats[stat_key]}"
                value_surf = self.font_small.render(value_text, True, (200, 210, 220))
                self.screen.blit(value_surf, (bar_x + bar_width + 6, stat_y_pos))
            
            # === EQUIPPED BADGE ===
            if is_current:
                badge_x = card_x + card_width - 120
                badge_y = y + card_height - 28
                
                # Badge background with glow
                pygame.draw.rect(self.screen, (60, 120, 60), (badge_x-2, badge_y-2, 104, 24), border_radius=8)
                pygame.draw.rect(self.screen, (80, 160, 80), (badge_x, badge_y, 100, 20), border_radius=6)
                
                # Badge text
                badge_font = pygame.font.Font(None, 24)
                badge_text = badge_font.render("✓ EQUIPPED", True, (255, 255, 255))
                self.screen.blit(badge_text, (badge_x + 50 - badge_text.get_width()//2, badge_y + 10 - badge_text.get_height()//2))
        
        # === INSTRUCTIONS ===
        inst_y = self.screen_height - 100
        
        instructions = [
            "↑↓ ARROWS - Select   |   ENTER - Equip   |   ESC - Back"
        ]
        
        for i, inst in enumerate(instructions):
            inst_surf = self.font_medium.render(inst, True, (140, 150, 160))
            self.screen.blit(inst_surf, (self.screen_width//2 - inst_surf.get_width()//2, inst_y + i * 30))
        
        # === BACK BUTTON ===
        back_button_rect = pygame.Rect(50, self.screen_height - 80, 150, 50)
        mouse_pos = pygame.mouse.get_pos()
        back_hover = back_button_rect.collidepoint(mouse_pos)
        
        # Button background
        if back_hover:
            pygame.draw.rect(self.screen, (50, 60, 75), back_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (100, 180, 255), back_button_rect, 2, border_radius=8)
        else:
            pygame.draw.rect(self.screen, (35, 45, 60), back_button_rect, border_radius=8)
            pygame.draw.rect(self.screen, (70, 80, 100), back_button_rect, 2, border_radius=8)
        
        # Button text
        back_text = self.font_large.render("← BACK", True, (200, 210, 220) if back_hover else (150, 160, 170))
        self.screen.blit(back_text, (50 + 75 - back_text.get_width()//2, self.screen_height - 80 + 25 - back_text.get_height()//2))
    
    def _render_settings(self):
        """⚙️ SETTINGS SCREEN - Professional & Comprehensive"""
        current_time = pygame.time.get_ticks()
        
        # === BACKGROUND: Dark tactical gradient ===
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(15 + (25 - 15) * ratio)
            g = int(18 + (28 - 18) * ratio)
            b = int(22 + (35 - 22) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        for i in range(particle_count):
            seed = i * 1000
            x = ((current_time + seed) % (self.screen_width * 3)) / 3
            y = ((current_time * 0.3 + seed * 0.7) % (self.screen_height * 2)) / 2
            size = 1 + (i % 3)
            alpha = int(50 + 50 * math.sin(current_time / 500 + i))
            particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            particle_surf.fill((200, 220, 255, alpha))
            self.screen.blit(particle_surf, (int(x), int(y)))
        
        # === HEXAGON GRID PATTERN (Advanced Military Tech) ===
        hex_alpha = 20
        hex_spacing = 60
        for x in range(-hex_spacing, self.screen_width + hex_spacing, hex_spacing):
            for y_pos in range(-hex_spacing, self.screen_height + hex_spacing, int(hex_spacing * 0.866)):
                offset = hex_spacing // 2 if (y_pos // int(hex_spacing * 0.866)) % 2 == 0 else 0
                hex_x = x + offset
                # Animated hexagons
                pulse = abs(math.sin(current_time / 2000 + hex_x / 100 + y_pos / 100)) * hex_alpha
                for angle in range(0, 360, 60):
                    angle_rad = math.radians(angle)
                    x1 = hex_x + math.cos(angle_rad) * 15
                    y1 = y_pos + math.sin(angle_rad) * 15
                    angle_rad2 = math.radians(angle + 60)
                    x2 = hex_x + math.cos(angle_rad2) * 15
                    y2 = y_pos + math.sin(angle_rad2) * 15
                    if 0 <= x1 < self.screen_width and 0 <= y1 < self.screen_height:
                        color_intensity = int(40 + pulse)
                        pygame.draw.line(self.screen, (color_intensity, color_intensity + 10, color_intensity + 20, hex_alpha), 
                                       (x1, y1), (x2, y2), 1)
        
        # === CINEMATIC LIGHT RAYS ===
        ray_count = 5
        for i in range(ray_count):
            ray_x = self.screen_width * (0.2 + i * 0.15)
            ray_angle = -60 + math.sin(current_time / 1000 + i) * 10
            ray_length = self.screen_height * 1.5
            ray_width = 150
            
            ray_surf = pygame.Surface((ray_width, ray_length), pygame.SRCALPHA)
            for w in range(ray_width):
                alpha = int(8 * (1 - abs(w - ray_width/2) / (ray_width/2)))
                pygame.draw.line(ray_surf, (100, 150, 255, alpha), (w, 0), (w, ray_length))
            
            rotated_ray = pygame.transform.rotate(ray_surf, ray_angle)
            self.screen.blit(rotated_ray, (ray_x - rotated_ray.get_width()//2, -ray_length//2))
        
        # === ANIMATED SCAN LINES (Multiple layers) ===
        scan_line_1 = (current_time // 3) % self.screen_height
        scan_line_2 = (current_time // 5) % self.screen_height
        
        for scan_line, speed in [(scan_line_1, 3), (scan_line_2, 5)]:
            for i in range(-30, 31, 2):
                if 0 <= scan_line + i < self.screen_height:
                    alpha = int(30 * (1 - abs(i) / 30))
                    scan_surf = pygame.Surface((self.screen_width, 1), pygame.SRCALPHA)
                    scan_surf.fill((120, 180, 255, alpha))
                    self.screen.blit(scan_surf, (0, scan_line + i))
        
        # === GLOWING CORNER BRACKETS (Animated) ===
        bracket_size = 50
        bracket_thickness = 4
        pulse_brightness = abs(math.sin(current_time / 400))
        bracket_r = int(80 + 175 * pulse_brightness)
        bracket_g = int(180 + 75 * pulse_brightness)
        bracket_b = 255
        bracket_color = (bracket_r, bracket_g, bracket_b)
        
        # Add glow to brackets
        for glow_offset in range(8, 0, -2):
            glow_alpha = int(40 * pulse_brightness * (9 - glow_offset) / 8)
            glow_color = (*bracket_color, glow_alpha)
            
            # Top-left
            glow_surf = pygame.Surface((bracket_size + glow_offset * 2, bracket_size + glow_offset * 2), pygame.SRCALPHA)
            pygame.draw.line(glow_surf, glow_color, (glow_offset, glow_offset), (bracket_size + glow_offset, glow_offset), bracket_thickness)
            pygame.draw.line(glow_surf, glow_color, (glow_offset, glow_offset), (glow_offset, bracket_size + glow_offset), bracket_thickness)
            self.screen.blit(glow_surf, (20 - glow_offset, 20 - glow_offset))
        
        # Main brackets
        pygame.draw.line(self.screen, bracket_color, (20, 20), (20 + bracket_size, 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (20, 20), (20, 20 + bracket_size), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, 20), (self.screen_width - 20 - bracket_size, 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, 20), (self.screen_width - 20, 20 + bracket_size), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (20, self.screen_height - 20), (20 + bracket_size, self.screen_height - 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (20, self.screen_height - 20), (20, self.screen_height - 20 - bracket_size), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, self.screen_height - 20), (self.screen_width - 20 - bracket_size, self.screen_height - 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, self.screen_height - 20), (self.screen_width - 20, self.screen_height - 20 - bracket_size), bracket_thickness)
        
        # === EPIC TITLE WITH GLOW EFFECTS ===
        title_font = pygame.font.Font(None, 88)
        title = "⚔️ TACTICAL LOADOUT ARMORY ⚔️"
        
        # Outer glow (multiple layers for blur effect)
        for glow_size in range(12, 0, -2):
            glow_alpha = int(20 * (13 - glow_size) / 12)
            glow_surf = title_font.render(title, True, (100, 200, 255))
            glow_surf.set_alpha(glow_alpha)
            for angle in range(0, 360, 45):
                offset_x = math.cos(math.radians(angle)) * glow_size
                offset_y = math.sin(math.radians(angle)) * glow_size
                self.screen.blit(glow_surf, (self.screen_width//2 - glow_surf.get_width()//2 + offset_x, 
                                             28 + offset_y))
        
        # Multi-layer shadow for 3D depth
        for offset in range(6, 0, -1):
            shadow_alpha = 50 * (7 - offset)
            shadow = title_font.render(title, True, (0, 0, 0))
            shadow.set_alpha(shadow_alpha)
            self.screen.blit(shadow, (self.screen_width//2 - shadow.get_width()//2 + offset, 28 + offset))
        
        # Main title with gradient effect
        title_surf = title_font.render(title, True, (255, 220, 100))
        self.screen.blit(title_surf, (self.screen_width//2 - title_surf.get_width()//2, 28))
        
        # Title shine effect (animated)
        shine_pos = ((current_time // 10) % (title_surf.get_width() + 200)) - 100
        shine_surf = pygame.Surface((50, title_surf.get_height()), pygame.SRCALPHA)
        for x in range(50):
            alpha = int(100 * (1 - abs(x - 25) / 25))
            pygame.draw.line(shine_surf, (255, 255, 255, alpha), (x, 0), (x, title_surf.get_height()))
        self.screen.blit(shine_surf, (self.screen_width//2 - title_surf.get_width()//2 + shine_pos, 28))
        
        # Epic subtitle with typing effect
        subtitle_font = pygame.font.Font(None, 32)
        subtitle_full = "⚡ SELECT YOUR COMBAT CLASS • DOMINATE THE BATTLEFIELD ⚡"
        char_count = int((current_time / 50) % (len(subtitle_full) + 20))
        subtitle = subtitle_full[:min(char_count, len(subtitle_full))]
        
        # Subtitle glow
        sub_glow = subtitle_font.render(subtitle, True, (100, 200, 255))
        sub_glow.set_alpha(150)
        self.screen.blit(sub_glow, (self.screen_width//2 - sub_glow.get_width()//2 + 2, 107))
        
        subtitle_surf = subtitle_font.render(subtitle, True, (180, 220, 255))
        self.screen.blit(subtitle_surf, (self.screen_width//2 - subtitle_surf.get_width()//2, 105))
        
        # === ULTRA-BEAUTIFUL LOADOUT CARDS ===
        card_width = 780
        card_height = 175
        card_spacing = 12
        start_y = 155
        card_x = self.screen_width//2 - card_width//2
        
        for i, loadout in enumerate(self.loadouts):
            y = start_y + i * (card_height + card_spacing)
            is_selected = (i == self.loadout_selection)
            is_current = (i == self.current_loadout)
            
            # === CARD WITH CINEMATIC EFFECTS ===
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            
            if is_selected:
                # MEGA OUTER GLOW (Pulsing)
                pulse = abs(math.sin(current_time / 200))
                for glow_offset in range(20, 0, -3):
                    glow_alpha = int(25 * pulse * (21 - glow_offset) / 20)
                    glow_surf = pygame.Surface((card_width + glow_offset * 2, card_height + glow_offset * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (100, 200, 255, glow_alpha), 
                                   (0, 0, card_width + glow_offset * 2, card_height + glow_offset * 2), 
                                   border_radius=20)
                    self.screen.blit(glow_surf, (card_x - glow_offset, y - glow_offset))
                
                # Card gradient background
                for gradient_y in range(card_height):
                    ratio = gradient_y / card_height
                    r = int(40 + (60 - 40) * ratio + pulse * 10)
                    g = int(50 + (80 - 50) * ratio + pulse * 15)
                    b = int(80 + (120 - 80) * ratio + pulse * 20)
                    pygame.draw.line(card_surf, (r, g, b), (0, gradient_y), (card_width, gradient_y))
                
                # Animated border (multiple layers)
                pygame.draw.rect(card_surf, (150 + int(105 * pulse), 220, 255), (0, 0, card_width, card_height), 5, border_radius=18)
                pygame.draw.rect(card_surf, (100, 180, 255), (2, 2, card_width - 4, card_height - 4), 2, border_radius=16)
                
            elif is_current:
                # GOLD LEGENDARY EFFECT
                for glow_offset in range(15, 0, -2):
                    glow_alpha = int(30 * (16 - glow_offset) / 15)
                    glow_surf = pygame.Surface((card_width + glow_offset * 2, card_height + glow_offset * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (255, 200, 50, glow_alpha), 
                                   (0, 0, card_width + glow_offset * 2, card_height + glow_offset * 2), 
                                   border_radius=20)
                    self.screen.blit(glow_surf, (card_x - glow_offset, y - glow_offset))
                
                # Gold gradient
                for gradient_y in range(card_height):
                    ratio = gradient_y / card_height
                    r = int(35 + (50 - 35) * ratio)
                    g = int(40 + (55 - 40) * ratio)
                    b = int(60 + (80 - 60) * ratio)
                    pygame.draw.line(card_surf, (r, g, b), (0, gradient_y), (card_width, gradient_y))
                
                pygame.draw.rect(card_surf, (255, 215, 0), (0, 0, card_width, card_height), 5, border_radius=18)
                pygame.draw.rect(card_surf, (200, 170, 50), (2, 2, card_width - 4, card_height - 4), 2, border_radius=16)
                
                # Sparkle effects on equipped card
                for sparkle_i in range(8):
                    sparkle_time = (current_time + sparkle_i * 500) / 1000
                    sparkle_x = int((math.sin(sparkle_time + sparkle_i) * 0.4 + 0.5) * card_width)
                    sparkle_y = int((math.cos(sparkle_time * 1.3 + sparkle_i) * 0.4 + 0.5) * card_height)
                    sparkle_alpha = int(abs(math.sin(sparkle_time * 3)) * 200)
                    sparkle_size = 3 + int(abs(math.sin(sparkle_time * 2)) * 3)
                    pygame.draw.circle(card_surf, (255, 255, 200, sparkle_alpha), (sparkle_x, sparkle_y), sparkle_size)
                
            else:
                # Normal card with subtle gradient
                for gradient_y in range(card_height):
                    ratio = gradient_y / card_height
                    r = int(20 + (35 - 20) * ratio)
                    g = int(25 + (40 - 25) * ratio)
                    b = int(35 + (55 - 35) * ratio)
                    pygame.draw.line(card_surf, (r, g, b), (0, gradient_y), (card_width, gradient_y))
                
                pygame.draw.rect(card_surf, (70, 85, 110), (0, 0, card_width, card_height), 3, border_radius=18)
            
            # Inner shadow for depth
            shadow_surf = pygame.Surface((card_width - 10, 8), pygame.SRCALPHA)
            for shadow_y in range(8):
                alpha = int(40 * (8 - shadow_y) / 8)
                pygame.draw.line(shadow_surf, (0, 0, 0, alpha), (0, shadow_y), (card_width - 10, shadow_y))
            card_surf.blit(shadow_surf, (5, 5))
            
            self.screen.blit(card_surf, (card_x, y))
            
            # === ICON WITH MEGA GLOW ===
            icon_bg_x = card_x + 90
            icon_bg_y = y + card_height//2
            icon_radius = 62
            
            # Icon outer glow (pulsing)
            icon_pulse = abs(math.sin(current_time / 300 + i * 0.5))
            for glow_r in range(icon_radius + 25, icon_radius, -3):
                glow_alpha = int(30 * icon_pulse * (icon_radius + 26 - glow_r) / 25)
                glow_color = Colors.GOLD if is_current else ((120, 200, 255) if is_selected else (80, 100, 140))
                pygame.draw.circle(self.screen, (*glow_color, glow_alpha), (icon_bg_x, icon_bg_y), glow_r)
            
            # Icon background (gradient circle)
            for r in range(icon_radius, 0, -1):
                ratio = r / icon_radius
                if is_current:
                    color = (int(100 * ratio), int(80 * ratio), int(20 * ratio))
                elif is_selected:
                    color = (int(50 * ratio), int(90 * ratio), int(140 * ratio))
                else:
                    color = (int(40 * ratio), int(50 * ratio), int(70 * ratio))
                pygame.draw.circle(self.screen, color, (icon_bg_x, icon_bg_y), r)
            
            # Icon border (triple layer)
            icon_border_color = Colors.GOLD if is_current else (Colors.NEON_CYAN if is_selected else (100, 110, 130))
            pygame.draw.circle(self.screen, icon_border_color, (icon_bg_x, icon_bg_y), icon_radius, 4)
            pygame.draw.circle(self.screen, (*icon_border_color, 100), (icon_bg_x, icon_bg_y), icon_radius + 3, 2)
            
            # Icon with glow
            icon_font = pygame.font.Font(None, 80)
            icon_color = Colors.WHITE
            
            # Icon shadow
            icon_shadow = icon_font.render(loadout['icon'], True, (0, 0, 0))
            icon_shadow.set_alpha(100)
            self.screen.blit(icon_shadow, (icon_bg_x - icon_shadow.get_width()//2 + 3, icon_bg_y - icon_shadow.get_height()//2 + 3))
            
            # Icon main
            icon_surf = icon_font.render(loadout['icon'], True, icon_color)
            self.screen.blit(icon_surf, (icon_bg_x - icon_surf.get_width()//2, icon_bg_y - icon_surf.get_height()//2))
            
            # === TEXT CONTENT WITH SHADOWS ===
            text_start_x = card_x + 180
            
            # Loadout name (large with glow)
            name_font = pygame.font.Font(None, 58)
            name_color = (255, 215, 0) if is_current else ((100, 220, 255) if is_selected else (220, 230, 240))
            
            # Name glow
            name_glow = name_font.render(loadout['name'], True, name_color)
            name_glow.set_alpha(80)
            self.screen.blit(name_glow, (text_start_x + 2, y + 13))
            
            # Name shadow
            name_shadow = name_font.render(loadout['name'], True, (0, 0, 0))
            name_shadow.set_alpha(150)
            self.screen.blit(name_shadow, (text_start_x + 2, y + 12))
            
            # Name main
            name_surf = name_font.render(loadout['name'], True, name_color)
            self.screen.blit(name_surf, (text_start_x, y + 10))
            
            # Description
            desc_surf = self.font_medium.render(loadout['description'], True, (190, 200, 220))
            self.screen.blit(desc_surf, (text_start_x, y + 65))
            
            # Weapons with fancy icons and boxes
            weapons_y = y + 95
            
            # PRIMARY weapon box
            prim_box_width = 220
            prim_box_height = 28
            prim_box_surf = pygame.Surface((prim_box_width, prim_box_height), pygame.SRCALPHA)
            prim_box_surf.fill((40, 60, 90, 180))
            pygame.draw.rect(prim_box_surf, (100, 180, 255), (0, 0, prim_box_width, prim_box_height), 2, border_radius=6)
            self.screen.blit(prim_box_surf, (text_start_x, weapons_y))
            
            primary_icon = "🔫"
            primary_label = self.font_small.render(f"{primary_icon} PRIMARY:", True, (120, 160, 200))
            self.screen.blit(primary_label, (text_start_x + 5, weapons_y + 6))
            
            primary_name = self.font_small.render(loadout['primary'].upper().replace('_', ' '), True, Colors.NEON_CYAN)
            self.screen.blit(primary_name, (text_start_x + 105, weapons_y + 6))
            
            # SECONDARY weapon box
            sec_box_surf = pygame.Surface((prim_box_width, prim_box_height), pygame.SRCALPHA)
            sec_box_surf.fill((40, 70, 50, 180))
            pygame.draw.rect(sec_box_surf, (100, 255, 150), (0, 0, prim_box_width, prim_box_height), 2, border_radius=6)
            self.screen.blit(sec_box_surf, (text_start_x, weapons_y + 33))
            
            secondary_icon = "🔪"
            secondary_label = self.font_small.render(f"{secondary_icon} SECONDARY:", True, (120, 200, 150))
            self.screen.blit(secondary_label, (text_start_x + 5, weapons_y + 39))
            
            secondary_name = self.font_small.render(loadout['secondary'].upper().replace('_', ' '), True, Colors.NEON_GREEN)
            self.screen.blit(secondary_name, (text_start_x + 130, weapons_y + 39))
            
            # Perk badge with glow
            perk_x = text_start_x
            perk_y = y + 143
            perk_bg_width = 200
            perk_bg_height = 26
            
            perk_surf = pygame.Surface((perk_bg_width, perk_bg_height), pygame.SRCALPHA)
            perk_color = (100, 70, 20, 220) if is_current else ((30, 50, 80, 220) if is_selected else (50, 60, 80, 200))
            perk_surf.fill(perk_color)
            
            perk_border_color = Colors.GOLD if is_current else (Colors.NEON_CYAN if is_selected else (100, 120, 150))
            pygame.draw.rect(perk_surf, perk_border_color, (0, 0, perk_bg_width, perk_bg_height), 2, border_radius=8)
            self.screen.blit(perk_surf, (perk_x, perk_y))
            
            perk_text = f"🎖️ {loadout['perk']}"
            perk_text_color = (255, 220, 100) if is_current else (Colors.NEON_CYAN if is_selected else (200, 210, 230))
            perk_text_surf = self.font_small.render(perk_text, True, perk_text_color)
            self.screen.blit(perk_text_surf, (perk_x + 8, perk_y + 5))
            
            # === CINEMATIC STATS DISPLAY ===
            stats_x = card_x + card_width - 215
            stats_y = y + 22
            stats = loadout['stats']
            stat_info = [
                ('💥 DAMAGE', 'damage', (255, 80, 80)),
                ('🎯 RANGE', 'range', (100, 200, 255)),
                ('⚡ MOBILITY', 'mobility', (100, 255, 150)),
                ('📊 ACCURACY', 'accuracy', (255, 220, 100))
            ]
            
            for j, (stat_name, stat_key, stat_color) in enumerate(stat_info):
                stat_y_pos = stats_y + j * 35
                
                # Stat label with glow
                stat_label = self.font_small.render(stat_name, True, (200, 210, 230))
                self.screen.blit(stat_label, (stats_x, stat_y_pos))
                
                # Epic 3D stat bar
                bar_width = 130
                bar_height = 14
                bar_x = stats_x + 10
                bar_y = stat_y_pos + 16
                
                # Bar shadow
                shadow_surf = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
                shadow_surf.fill((0, 0, 0, 60))
                self.screen.blit(shadow_surf, (bar_x + 2, bar_y + 2))
                
                # Bar background (dark with border)
                pygame.draw.rect(self.screen, (15, 20, 30), (bar_x, bar_y, bar_width, bar_height), border_radius=7)
                pygame.draw.rect(self.screen, (50, 60, 80), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=7)
                
                # Value bar with gradient and glow
                value_width = int((stats[stat_key] / 10) * (bar_width - 4))
                if value_width > 0:
                    # Outer glow
                    glow_surf = pygame.Surface((value_width + 10, bar_height + 10), pygame.SRCALPHA)
                    for glow_i in range(5, 0, -1):
                        glow_alpha = int(40 * (6 - glow_i) / 5)
                        pygame.draw.rect(glow_surf, (*stat_color, glow_alpha), 
                                       (5 - glow_i, 5 - glow_i, value_width + glow_i * 2, bar_height + glow_i * 2), 
                                       border_radius=7)
                    self.screen.blit(glow_surf, (bar_x - 5, bar_y - 5))
                    
                    # Gradient fill
                    for k in range(value_width):
                        ratio = k / bar_width
                        color_intensity = 0.5 + 0.5 * ratio
                        bar_r = int(stat_color[0] * color_intensity)
                        bar_g = int(stat_color[1] * color_intensity)
                        bar_b = int(stat_color[2] * color_intensity)
                        pygame.draw.rect(self.screen, (bar_r, bar_g, bar_b), 
                                       (bar_x + 2 + k, bar_y + 2, 1, bar_height - 4))
                    
                    # Shine effect on bar
                    shine_surf = pygame.Surface((value_width - 4, (bar_height - 4) // 2), pygame.SRCALPHA)
                    shine_surf.fill((*stat_color, 80))
                    self.screen.blit(shine_surf, (bar_x + 2, bar_y + 2))
                    
                    # Bar border
                    pygame.draw.rect(self.screen, stat_color, (bar_x + 2, bar_y + 2, value_width - 4, bar_height - 4), 1, border_radius=6)
                
                # Value text with shadow
                value_text = f"{stats[stat_key]}/10"
                value_shadow = self.font_small.render(value_text, True, (0, 0, 0))
                value_shadow.set_alpha(120)
                self.screen.blit(value_shadow, (bar_x + bar_width + 9, stat_y_pos + 11))
                
                value_surf = self.font_small.render(value_text, True, (240, 245, 255))
                self.screen.blit(value_surf, (bar_x + bar_width + 8, stat_y_pos + 10))
            
            # === LEGENDARY "EQUIPPED" BADGE ===
            if is_current:
                equipped_bg_width = 155
                equipped_bg_height = 38
                equipped_x = card_x + card_width - equipped_bg_width - 18
                equipped_y = y + card_height - equipped_bg_height - 12
                
                # Badge glow
                for glow_size in range(6, 0, -1):
                    glow_alpha = int(60 * (7 - glow_size) / 6)
                    glow_surf = pygame.Surface((equipped_bg_width + glow_size * 2, equipped_bg_height + glow_size * 2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surf, (100, 255, 100, glow_alpha), 
                                   (0, 0, equipped_bg_width + glow_size * 2, equipped_bg_height + glow_size * 2), 
                                   border_radius=10)
                    self.screen.blit(glow_surf, (equipped_x - glow_size, equipped_y - glow_size))
                
                # Badge background
                badge_surf = pygame.Surface((equipped_bg_width, equipped_bg_height), pygame.SRCALPHA)
                badge_surf.fill((40, 150, 40, 240))
                pygame.draw.rect(badge_surf, (100, 255, 100), (0, 0, equipped_bg_width, equipped_bg_height), 3, border_radius=10)
                self.screen.blit(badge_surf, (equipped_x, equipped_y))
                
                # Badge text with shadow
                equipped_font = pygame.font.Font(None, 36)
                equipped_shadow = equipped_font.render("✓ EQUIPPED", True, (0, 0, 0))
                equipped_shadow.set_alpha(120)
                self.screen.blit(equipped_shadow, (equipped_x + equipped_bg_width//2 - equipped_shadow.get_width()//2 + 2,
                                                   equipped_y + equipped_bg_height//2 - equipped_shadow.get_height()//2 + 2))
                
                equipped_text = equipped_font.render("✓ EQUIPPED", True, (255, 255, 255))
                self.screen.blit(equipped_text, (equipped_x + equipped_bg_width//2 - equipped_text.get_width()//2, 
                                                 equipped_y + equipped_bg_height//2 - equipped_text.get_height()//2))
        
        # === CINEMATIC INSTRUCTIONS PANEL ===
        inst_y = self.screen_height - 115
        inst_panel_width = 750
        inst_panel_height = 90
        inst_panel_x = self.screen_width//2 - inst_panel_width//2
        
        # Panel glow
        for glow_offset in range(8, 0, -2):
            glow_alpha = int(20 * (9 - glow_offset) / 8)
            glow_surf = pygame.Surface((inst_panel_width + glow_offset * 2, inst_panel_height + glow_offset * 2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (100, 180, 255, glow_alpha), 
                           (0, 0, inst_panel_width + glow_offset * 2, inst_panel_height + glow_offset * 2), 
                           border_radius=15)
            self.screen.blit(glow_surf, (inst_panel_x - glow_offset, inst_y - glow_offset))
        
        # Panel background
        inst_panel_surf = pygame.Surface((inst_panel_width, inst_panel_height), pygame.SRCALPHA)
        inst_panel_surf.fill((15, 25, 40, 230))
        pygame.draw.rect(inst_panel_surf, (100, 150, 220), (0, 0, inst_panel_width, inst_panel_height), 3, border_radius=12)
        self.screen.blit(inst_panel_surf, (inst_panel_x, inst_y))
        
        instructions = [
            "↑↓ ARROWS - Select Loadout",
            "ENTER / CLICK - Confirm & Equip",
            "ESC - Back to Menu"
        ]
        
        for i, inst in enumerate(instructions):
            # Instruction shadow
            inst_shadow = self.font_medium.render(inst, True, (0, 0, 0))
            inst_shadow.set_alpha(100)
            self.screen.blit(inst_shadow, (self.screen_width//2 - inst_shadow.get_width()//2 + 2, inst_y + 12 + i * 27))
            
            # Instruction main
            inst_surf = self.font_medium.render(inst, True, (220, 235, 255))
            self.screen.blit(inst_surf, (self.screen_width//2 - inst_surf.get_width()//2, inst_y + 10 + i * 27))
        
        # === HEXAGON GRID PATTERN (Military Tech Style) ===
        hex_alpha = 15
        hex_spacing = 60
        for x in range(-hex_spacing, self.screen_width + hex_spacing, hex_spacing):
            for y_pos in range(-hex_spacing, self.screen_height + hex_spacing, int(hex_spacing * 0.866)):
                offset = hex_spacing // 2 if (y_pos // int(hex_spacing * 0.866)) % 2 == 0 else 0
                hex_x = x + offset
                # Draw small hexagon corners
                for angle in range(0, 360, 60):
                    angle_rad = math.radians(angle)
                    x1 = hex_x + math.cos(angle_rad) * 15
                    y1 = y_pos + math.sin(angle_rad) * 15
                    angle_rad2 = math.radians(angle + 60)
                    x2 = hex_x + math.cos(angle_rad2) * 15
                    y2 = y_pos + math.sin(angle_rad2) * 15
                    if 0 <= x1 < self.screen_width and 0 <= y1 < self.screen_height:
                        pygame.draw.line(self.screen, (40, 50, 60, hex_alpha), (x1, y1), (x2, y2), 1)
        
        # === ANIMATED SCAN LINES ===
        scan_line = (current_time // 5) % self.screen_height
        for i in range(-20, 21, 2):
            if 0 <= scan_line + i < self.screen_height:
                alpha = int(20 * (1 - abs(i) / 20))
                scan_surf = pygame.Surface((self.screen_width, 1), pygame.SRCALPHA)
                scan_surf.fill((100, 150, 200, alpha))
                self.screen.blit(scan_surf, (0, scan_line + i))
        
        # === CORNER BRACKETS (HUD Style) ===
        bracket_size = 40
        bracket_thickness = 3
        bracket_color = (80, 180, 255)
        # Top-left
        pygame.draw.line(self.screen, bracket_color, (20, 20), (20 + bracket_size, 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (20, 20), (20, 20 + bracket_size), bracket_thickness)
        # Top-right
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, 20), (self.screen_width - 20 - bracket_size, 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, 20), (self.screen_width - 20, 20 + bracket_size), bracket_thickness)
        # Bottom-left
        pygame.draw.line(self.screen, bracket_color, (20, self.screen_height - 20), (20 + bracket_size, self.screen_height - 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (20, self.screen_height - 20), (20, self.screen_height - 20 - bracket_size), bracket_thickness)
        # Bottom-right
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, self.screen_height - 20), (self.screen_width - 20 - bracket_size, self.screen_height - 20), bracket_thickness)
        pygame.draw.line(self.screen, bracket_color, (self.screen_width - 20, self.screen_height - 20), (self.screen_width - 20, self.screen_height - 20 - bracket_size), bracket_thickness)
        
        # === TITLE WITH MILITARY STYLING ===
        title_font = pygame.font.Font(None, 80)
        title = "⚔️ TACTICAL LOADOUT SELECTION ⚔️"
        
        # Multi-layer shadow for depth
        for offset in range(5, 0, -1):
            shadow_alpha = 40 * (6 - offset)
            shadow = title_font.render(title, True, (0, 0, 0))
            shadow.set_alpha(shadow_alpha)
            self.screen.blit(shadow, (self.screen_width//2 - shadow.get_width()//2 + offset, 35 + offset))
        
        # Main title with glow
        title_surf = title_font.render(title, True, Colors.GOLD)
        self.screen.blit(title_surf, (self.screen_width//2 - title_surf.get_width()//2, 35))
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 28)
        subtitle = "SELECT YOUR COMBAT CLASS"
        subtitle_surf = subtitle_font.render(subtitle, True, (150, 170, 200))
        self.screen.blit(subtitle_surf, (self.screen_width//2 - subtitle_surf.get_width()//2, 100))
        
        # === LOADOUT CARDS - REDESIGNED ===
        card_width = 750
        card_height = 160
        card_spacing = 15
        start_y = 160
        card_x = self.screen_width//2 - card_width//2
        
        for i, loadout in enumerate(self.loadouts):
            y = start_y + i * (card_height + card_spacing)
            is_selected = (i == self.loadout_selection)
            is_current = (i == self.current_loadout)
            
            # === CARD BACKGROUND WITH DEPTH ===
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            
            # Multiple layers for depth
            if is_selected:
                # Outer glow (pulsing)
                pulse = abs(math.sin(current_time / 250))
                for glow_offset in range(8, 0, -2):
                    glow_alpha = int(15 * pulse * (9 - glow_offset) / 8)
                    glow_rect = pygame.Rect(-glow_offset, -glow_offset, 
                                           card_width + glow_offset * 2, 
                                           card_height + glow_offset * 2)
                    pygame.draw.rect(card_surf, (80, 180, 255, glow_alpha), glow_rect, border_radius=20)
                
                # Main card with gradient
                pygame.draw.rect(card_surf, (35, 45, 70), (0, 0, card_width, card_height), border_radius=15)
                # Highlight edge
                pygame.draw.rect(card_surf, (100, 200, 255), (0, 0, card_width, card_height), 4, border_radius=15)
                
            elif is_current:
                # Gold outline for equipped
                pygame.draw.rect(card_surf, (30, 40, 60), (0, 0, card_width, card_height), border_radius=15)
                pygame.draw.rect(card_surf, Colors.GOLD, (0, 0, card_width, card_height), 4, border_radius=15)
                
                # Gold corner accents
                corner_size = 20
                corners = [(5, 5), (card_width - 25, 5), (5, card_height - 25), (card_width - 25, card_height - 25)]
                for cx, cy in corners:
                    pygame.draw.line(card_surf, Colors.GOLD, (cx, cy), (cx + corner_size, cy), 3)
                    pygame.draw.line(card_surf, Colors.GOLD, (cx, cy), (cx, cy + corner_size), 3)
            else:
                # Normal card
                pygame.draw.rect(card_surf, (25, 30, 45), (0, 0, card_width, card_height), border_radius=15)
                pygame.draw.rect(card_surf, (60, 70, 90), (0, 0, card_width, card_height), 2, border_radius=15)
            
            # Inner shadow for depth
            shadow_surf = pygame.Surface((card_width - 6, 4), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 30))
            card_surf.blit(shadow_surf, (3, 3))
            
            self.screen.blit(card_surf, (card_x, y))
            
            # === ICON WITH BACKGROUND CIRCLE ===
            icon_bg_x = card_x + 80
            icon_bg_y = y + card_height//2
            icon_radius = 55
            
            # Icon background circle with gradient effect
            for r in range(icon_radius, 0, -2):
                alpha = int(80 * (icon_radius - r) / icon_radius)
                color = Colors.GOLD if is_current else ((100, 180, 255) if is_selected else (60, 80, 120))
                pygame.draw.circle(self.screen, (*color, alpha), (icon_bg_x, icon_bg_y), r)
            
            # Icon border
            icon_border_color = Colors.GOLD if is_current else (Colors.NEON_CYAN if is_selected else (100, 110, 130))
            pygame.draw.circle(self.screen, icon_border_color, (icon_bg_x, icon_bg_y), icon_radius, 3)
            
            # Icon
            icon_font = pygame.font.Font(None, 70)
            icon_color = Colors.WHITE if (is_selected or is_current) else Colors.LIGHT_GRAY
            icon_surf = icon_font.render(loadout['icon'], True, icon_color)
            self.screen.blit(icon_surf, (icon_bg_x - icon_surf.get_width()//2, icon_bg_y - icon_surf.get_height()//2))
            
            # === TEXT CONTENT ===
            text_start_x = card_x + 160
            
            # Loadout name (large and bold)
            name_font = pygame.font.Font(None, 52)
            name_color = Colors.GOLD if is_current else (Colors.NEON_CYAN if is_selected else Colors.WHITE)
            name_surf = name_font.render(loadout['name'], True, name_color)
            self.screen.blit(name_surf, (text_start_x, y + 15))
            
            # Description (smaller, italicized look)
            desc_surf = self.font_medium.render(loadout['description'], True, (170, 180, 200))
            self.screen.blit(desc_surf, (text_start_x, y + 60))
            
            # Weapons with icons
            weapons_y = y + 90
            primary_icon = "🔫"
            secondary_icon = "🔪"
            
            primary_label = self.font_small.render(f"{primary_icon} PRIMARY:", True, (120, 140, 160))
            self.screen.blit(primary_label, (text_start_x, weapons_y))
            
            primary_name = self.font_small.render(loadout['primary'].upper().replace('_', ' '), True, Colors.NEON_CYAN)
            self.screen.blit(primary_name, (text_start_x + 95, weapons_y))
            
            secondary_label = self.font_small.render(f"{secondary_icon} SECONDARY:", True, (120, 140, 160))
            self.screen.blit(secondary_label, (text_start_x, weapons_y + 22))
            
            secondary_name = self.font_small.render(loadout['secondary'].upper().replace('_', ' '), True, Colors.NEON_GREEN)
            self.screen.blit(secondary_name, (text_start_x + 120, weapons_y + 22))
            
            # Perk with badge background
            perk_x = text_start_x
            perk_y = y + 130
            perk_bg_width = 180
            perk_bg_height = 22
            
            # Perk badge background
            perk_surf = pygame.Surface((perk_bg_width, perk_bg_height), pygame.SRCALPHA)
            perk_surf.fill((80, 100, 140, 150))
            self.screen.blit(perk_surf, (perk_x, perk_y))
            
            perk_text = f"🎖️ {loadout['perk']}"
            perk_color = Colors.GOLD if is_current else Colors.NEON_CYAN
            perk_text_surf = self.font_small.render(perk_text, True, perk_color)
            self.screen.blit(perk_text_surf, (perk_x + 5, perk_y + 3))
            
            # === STATS - REDESIGNED WITH BETTER BARS ===
            stats_x = card_x + card_width - 200
            stats_y = y + 20
            stats = loadout['stats']
            stat_info = [
                ('💥 DAMAGE', 'damage', Colors.NEON_RED),
                ('🎯 RANGE', 'range', Colors.NEON_CYAN),
                ('⚡ MOBILITY', 'mobility', Colors.NEON_GREEN),
                ('📊 ACCURACY', 'accuracy', Colors.NEON_YELLOW)
            ]
            
            for j, (stat_name, stat_key, stat_color) in enumerate(stat_info):
                stat_y_pos = stats_y + j * 32
                
                # Stat label
                stat_label = self.font_small.render(stat_name, True, (180, 190, 200))
                self.screen.blit(stat_label, (stats_x, stat_y_pos))
                
                # Stat bar (3D effect)
                bar_width = 120
                bar_height = 12
                bar_x = stats_x + 10
                bar_y = stat_y_pos + 14
                
                # Bar background (dark)
                pygame.draw.rect(self.screen, (20, 25, 35), (bar_x, bar_y, bar_width, bar_height), border_radius=6)
                
                # Bar border
                pygame.draw.rect(self.screen, (60, 70, 90), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=6)
                
                # Value bar with gradient effect
                value_width = int((stats[stat_key] / 10) * bar_width)
                if value_width > 0:
                    for k in range(value_width):
                        ratio = k / bar_width
                        color_intensity = 0.6 + 0.4 * ratio
                        bar_r = int(stat_color[0] * color_intensity)
                        bar_g = int(stat_color[1] * color_intensity)
                        bar_b = int(stat_color[2] * color_intensity)
                        pygame.draw.rect(self.screen, (bar_r, bar_g, bar_b), 
                                       (bar_x + k, bar_y + 1, 1, bar_height - 2))
                    
                    # Glow on top of bar
                    glow_surf = pygame.Surface((value_width, bar_height // 2), pygame.SRCALPHA)
                    glow_surf.fill((*stat_color, 60))
                    self.screen.blit(glow_surf, (bar_x, bar_y))
                
                # Value text
                value_text = f"{stats[stat_key]}/10"
                value_surf = self.font_small.render(value_text, True, Colors.WHITE)
                self.screen.blit(value_surf, (bar_x + bar_width + 8, stat_y_pos + 10))
            
            # === "EQUIPPED" BADGE ===
            if is_current:
                equipped_bg_width = 140
                equipped_bg_height = 35
                equipped_x = card_x + card_width - equipped_bg_width - 15
                equipped_y = y + card_height - equipped_bg_height - 10
                
                # Badge background with glow
                badge_surf = pygame.Surface((equipped_bg_width, equipped_bg_height), pygame.SRCALPHA)
                pygame.draw.rect(badge_surf, (50, 180, 50, 200), (0, 0, equipped_bg_width, equipped_bg_height), border_radius=8)
                pygame.draw.rect(badge_surf, Colors.NEON_GREEN, (0, 0, equipped_bg_width, equipped_bg_height), 2, border_radius=8)
                self.screen.blit(badge_surf, (equipped_x, equipped_y))
                
                equipped_font = pygame.font.Font(None, 32)
                equipped_text = equipped_font.render("✓ EQUIPPED", True, Colors.WHITE)
                self.screen.blit(equipped_text, (equipped_x + equipped_bg_width//2 - equipped_text.get_width()//2, 
                                                 equipped_y + equipped_bg_height//2 - equipped_text.get_height()//2))
        
        # === INSTRUCTIONS WITH STYLING ===
        inst_y = self.screen_height - 110
        
        # Instructions background panel
        inst_panel_width = 700
        inst_panel_height = 85
        inst_panel_x = self.screen_width//2 - inst_panel_width//2
        inst_panel_surf = pygame.Surface((inst_panel_width, inst_panel_height), pygame.SRCALPHA)
        inst_panel_surf.fill((20, 30, 45, 200))
        pygame.draw.rect(inst_panel_surf, (80, 100, 140), (0, 0, inst_panel_width, inst_panel_height), 2, border_radius=10)
        self.screen.blit(inst_panel_surf, (inst_panel_x, inst_y))
        
        instructions = [
            "↑↓ ARROWS - Select Loadout",
            "ENTER / CLICK - Confirm & Equip",
            "ESC - Back to Menu"
        ]
        
        for i, inst in enumerate(instructions):
            inst_surf = self.font_medium.render(inst, True, (200, 220, 240))
            self.screen.blit(inst_surf, (self.screen_width//2 - inst_surf.get_width()//2, inst_y + 10 + i * 25))
        
        # === BACK BUTTON ===
        back_button_rect = pygame.Rect(50, self.screen_height - 100, 200, 60)
        mouse_pos = pygame.mouse.get_pos()
        back_hover = back_button_rect.collidepoint(mouse_pos)
        
        back_surf = pygame.Surface((200, 60), pygame.SRCALPHA)
        if back_hover:
            pygame.draw.rect(back_surf, (80, 90, 110, 200), (0, 0, 200, 60), border_radius=10)
            pygame.draw.rect(back_surf, Colors.NEON_CYAN, (0, 0, 200, 60), 2, border_radius=10)
        else:
            pygame.draw.rect(back_surf, (40, 40, 60, 150), (0, 0, 200, 60), border_radius=10)
            pygame.draw.rect(back_surf, (80, 90, 110), (0, 0, 200, 60), 2, border_radius=10)
        
        self.screen.blit(back_surf, (50, self.screen_height - 100))
        
        back_text = self.font_large.render("← BACK", True, Colors.WHITE if back_hover else Colors.LIGHT_GRAY)
        self.screen.blit(back_text, (50 + 100 - back_text.get_width()//2, self.screen_height - 100 + 30 - back_text.get_height()//2))
    
    def _render_settings(self):
        """⚙️ SETTINGS SCREEN - Professional & Comprehensive"""
        current_time = pygame.time.get_ticks()
        
        # === BACKGROUND: Dark tactical gradient ===
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = int(15 + (25 - 15) * ratio)
            g = int(18 + (28 - 18) * ratio)
            b = int(22 + (35 - 22) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen_width, y))
        
        # === GRID OVERLAY ===
        grid_alpha = 20
        grid_spacing = 80
        for x in range(0, self.screen_width, grid_spacing):
            pygame.draw.line(self.screen, (40, 50, 60, grid_alpha), (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, grid_spacing):
            pygame.draw.line(self.screen, (40, 50, 60, grid_alpha), (0, y), (self.screen_width, y), 1)
        
        # === TITLE ===
        title_font = pygame.font.Font(None, 72)
        title = title_font.render("⚙️ GAME SETTINGS ⚙️", True, Colors.NEON_CYAN)
        title_shadow = title_font.render("⚙️ GAME SETTINGS ⚙️", True, (20, 20, 20))
        self.screen.blit(title_shadow, (self.screen_width//2 - title.get_width()//2 + 3, 53))
        self.screen.blit(title, (self.screen_width//2 - title.get_width()//2, 50))
        
        # === SETTINGS LIST ===
        setting_height = 80
        start_y = 180
        setting_x = self.screen_width//2 - 400
        mouse_pos = pygame.mouse.get_pos()
        
        # Calculate visible settings (scrollable list)
        visible_items = 6  # Show 6 settings at a time
        visible_start = self.settings_scroll_offset
        visible_end = min(visible_start + visible_items, len(self.settings_keys))
        
        for idx in range(visible_start, visible_end):
            i = idx
            key = self.settings_keys[i]
            setting = self.settings[key]
            # Adjust y position based on scroll offset
            y = start_y + (i - self.settings_scroll_offset) * setting_height
            is_selected = (i == self.settings_selection)
            
            # Setting background
            setting_rect = pygame.Rect(setting_x, y, 800, 70)
            setting_hover = setting_rect.collidepoint(mouse_pos)
            
            setting_surf = pygame.Surface((800, 70), pygame.SRCALPHA)
            if is_selected or setting_hover:
                pulse = abs(math.sin(current_time / 300)) if is_selected else 0.5
                glow_alpha = int(50 + 50 * pulse)
                pygame.draw.rect(setting_surf, (60, 70, 90, glow_alpha), (0, 0, 800, 70), border_radius=10)
                pygame.draw.rect(setting_surf, Colors.NEON_CYAN, (0, 0, 800, 70), 2, border_radius=10)
            else:
                pygame.draw.rect(setting_surf, (40, 40, 60, 100), (0, 0, 800, 70), border_radius=10)
                pygame.draw.rect(setting_surf, (80, 90, 110), (0, 0, 800, 70), 1, border_radius=10)
            
            self.screen.blit(setting_surf, (setting_x, y))
            
            # Setting name
            name_color = Colors.WHITE if is_selected else Colors.LIGHT_GRAY
            name_surf = self.font_large.render(setting['name'], True, name_color)
            self.screen.blit(name_surf, (setting_x + 20, y + 25))
            
            # Setting control (slider, toggle, or choice)
            control_x = setting_x + 450
            
            if setting['type'] == 'slider':
                # Slider
                slider_width = 300
                slider_height = 8
                slider_y = y + 35
                
                # Slider track
                pygame.draw.rect(self.screen, (60, 60, 80), (control_x, slider_y, slider_width, slider_height), border_radius=4)
                
                # Slider fill
                value_ratio = (setting['value'] - setting['min']) / (setting['max'] - setting['min'])
                fill_width = int(value_ratio * slider_width)
                pygame.draw.rect(self.screen, Colors.NEON_CYAN, (control_x, slider_y, fill_width, slider_height), border_radius=4)
                
                # Slider handle
                handle_x = control_x + fill_width
                pygame.draw.circle(self.screen, Colors.WHITE, (handle_x, slider_y + slider_height//2), 12)
                pygame.draw.circle(self.screen, Colors.NEON_CYAN, (handle_x, slider_y + slider_height//2), 10)
                
                # Value display
                if key == 'mouse_sensitivity':
                    value_text = f"{setting['value']:.3f}"
                elif key in ['fov', 'brightness']:
                    value_text = f"{setting['value']:.1f}" if key == 'brightness' else f"{int(setting['value'])}"
                else:
                    value_text = f"{int(setting['value'] * 100)}%"
                
                value_surf = self.font_medium.render(value_text, True, Colors.WHITE)
                self.screen.blit(value_surf, (control_x + slider_width + 15, y + 22))
            
            elif setting['type'] == 'toggle':
                # Toggle switch
                toggle_width = 100
                toggle_height = 40
                toggle_y = y + 20
                
                # Toggle background
                toggle_color = Colors.NEON_GREEN if setting['value'] else (80, 80, 100)
                pygame.draw.rect(self.screen, toggle_color, (control_x, toggle_y, toggle_width, toggle_height), border_radius=20)
                
                # Toggle circle
                circle_x = control_x + toggle_width - 25 if setting['value'] else control_x + 25
                pygame.draw.circle(self.screen, Colors.WHITE, (circle_x, toggle_y + toggle_height//2), 15)
                
                # Status text
                status_text = "ON" if setting['value'] else "OFF"
                status_color = Colors.NEON_GREEN if setting['value'] else Colors.LIGHT_GRAY
                status_surf = self.font_medium.render(status_text, True, status_color)
                self.screen.blit(status_surf, (control_x + toggle_width + 15, y + 22))
            
            elif setting['type'] == 'choice':
                # Choice selector with arrows
                choice_text = setting['options'][setting['value']]
                
                # Left arrow
                left_arrow = self.font_large.render("◄", True, Colors.NEON_CYAN if setting_hover else Colors.LIGHT_GRAY)
                self.screen.blit(left_arrow, (control_x, y + 20))
                
                # Choice text
                choice_surf = self.font_large.render(choice_text, True, Colors.WHITE)
                self.screen.blit(choice_surf, (control_x + 50, y + 20))
                
                # Right arrow
                right_arrow = self.font_large.render("►", True, Colors.NEON_CYAN if setting_hover else Colors.LIGHT_GRAY)
                self.screen.blit(right_arrow, (control_x + 220, y + 20))
        
        # === SCROLL INDICATORS ===
        max_scroll = max(0, len(self.settings_keys) - visible_items)
        
        # Show scroll up indicator
        if self.settings_scroll_offset > 0:
            scroll_up_y = start_y - 40
            scroll_up_text = self.font_large.render("▲ MORE SETTINGS ▲", True, Colors.NEON_CYAN)
            pulse = abs(math.sin(current_time / 200))
            scroll_up_text.set_alpha(int(150 + 105 * pulse))
            self.screen.blit(scroll_up_text, (self.screen_width//2 - scroll_up_text.get_width()//2, scroll_up_y))
        
        # Show scroll down indicator
        if self.settings_scroll_offset < max_scroll:
            scroll_down_y = start_y + visible_items * setting_height + 10
            scroll_down_text = self.font_large.render("▼ MORE SETTINGS ▼", True, Colors.NEON_CYAN)
            pulse = abs(math.sin(current_time / 200))
            scroll_down_text.set_alpha(int(150 + 105 * pulse))
            self.screen.blit(scroll_down_text, (self.screen_width//2 - scroll_down_text.get_width()//2, scroll_down_y))
        
        # Scrollbar on the right side
        if len(self.settings_keys) > visible_items:
            scrollbar_x = setting_x + 820
            scrollbar_y = start_y
            scrollbar_height = visible_items * setting_height
            scrollbar_width = 8
            
            # Scrollbar track
            pygame.draw.rect(self.screen, (40, 40, 60), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height), border_radius=4)
            
            # Scrollbar thumb
            thumb_height = int((visible_items / len(self.settings_keys)) * scrollbar_height)
            thumb_y = scrollbar_y + int((self.settings_scroll_offset / max_scroll) * (scrollbar_height - thumb_height)) if max_scroll > 0 else scrollbar_y
            pygame.draw.rect(self.screen, Colors.NEON_CYAN, (scrollbar_x, thumb_y, scrollbar_width, thumb_height), border_radius=4)
        
        # === INSTRUCTIONS ===
        inst_y = self.screen_height - 180
        instructions = [
            "↑↓ ARROWS / SCROLL - Navigate",
            "←→ ARROWS - Adjust Value",
            "CLICK - Interact with Controls",
            "ESC - Save & Back to Menu"
        ]
        
        for i, inst in enumerate(instructions):
            inst_surf = self.font_medium.render(inst, True, (180, 190, 200))
            self.screen.blit(inst_surf, (self.screen_width//2 - inst_surf.get_width()//2, inst_y + i * 30))
        
        # === BACK BUTTON ===
        back_button_rect = pygame.Rect(50, self.screen_height - 100, 200, 60)
        back_hover = back_button_rect.collidepoint(mouse_pos)
        
        back_surf = pygame.Surface((200, 60), pygame.SRCALPHA)
        if back_hover:
            pygame.draw.rect(back_surf, (80, 90, 110, 200), (0, 0, 200, 60), border_radius=10)
            pygame.draw.rect(back_surf, Colors.NEON_CYAN, (0, 0, 200, 60), 2, border_radius=10)
        else:
            pygame.draw.rect(back_surf, (40, 40, 60, 150), (0, 0, 200, 60), border_radius=10)
            pygame.draw.rect(back_surf, (80, 90, 110), (0, 0, 200, 60), 2, border_radius=10)
        
        self.screen.blit(back_surf, (50, self.screen_height - 100))
        
        back_text = self.font_large.render("← BACK", True, Colors.WHITE if back_hover else Colors.LIGHT_GRAY)
        self.screen.blit(back_text, (50 + 100 - back_text.get_width()//2, self.screen_height - 100 + 30 - back_text.get_height()//2))
        
        # === RESET BUTTON ===
        reset_button_rect = pygame.Rect(self.screen_width - 250, self.screen_height - 100, 200, 60)
        reset_hover = reset_button_rect.collidepoint(mouse_pos)
        
        reset_surf = pygame.Surface((200, 60), pygame.SRCALPHA)
        if reset_hover:
            pygame.draw.rect(reset_surf, (120, 60, 60, 200), (0, 0, 200, 60), border_radius=10)
            pygame.draw.rect(reset_surf, Colors.NEON_RED, (0, 0, 200, 60), 2, border_radius=10)
        else:
            pygame.draw.rect(reset_surf, (40, 40, 60, 150), (0, 0, 200, 60), border_radius=10)
            pygame.draw.rect(reset_surf, (100, 80, 80), (0, 0, 200, 60), 2, border_radius=10)
        
        self.screen.blit(reset_surf, (self.screen_width - 250, self.screen_height - 100))
        
        reset_text = self.font_large.render("🔄 RESET", True, Colors.WHITE if reset_hover else Colors.LIGHT_GRAY)
        self.screen.blit(reset_text, (self.screen_width - 250 + 100 - reset_text.get_width()//2, self.screen_height - 100 + 30 - reset_text.get_height()//2))
    
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
        self._render_reward_notifications()
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
        
        # LIVES COUNTER - HARDCORE MODE
        lives_color = Colors.GREEN if self.lives > 1 else Colors.RED
        lives_text = self.font_medium.render(f"♥ LIVES: {self.lives}", True, lives_color)
        self.screen.blit(lives_text, (240, 23))
        
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
        
        # Sprint indicator (when sprinting)
        if self.is_sprinting:
            sprint_bg = pygame.Surface((120, 35), pygame.SRCALPHA)
            pulse = abs(math.sin(pygame.time.get_ticks() / 200))
            pygame.draw.rect(sprint_bg, (50, 100, 50, int(150 + 105 * pulse)), (0, 0, 120, 35), border_radius=5)
            self.screen.blit(sprint_bg, (20, indicator_y))
            sprint_text = self.font_small.render("⚡ SPRINT", True, Colors.NEON_GREEN)
            self.screen.blit(sprint_text, (25, indicator_y + 8))
            indicator_y -= 45
        
        # ADS (Aim Down Sights) indicator
        if self.is_aiming:
            ads_bg = pygame.Surface((120, 35), pygame.SRCALPHA)
            pygame.draw.rect(ads_bg, (80, 50, 50, 200), (0, 0, 120, 35), border_radius=5)
            self.screen.blit(ads_bg, (20, indicator_y))
            ads_text = self.font_small.render("🎯 AIMING", True, Colors.NEON_RED)
            self.screen.blit(ads_text, (25, indicator_y + 8))
            indicator_y -= 45
        
        # Crouch indicator
        if self.is_crouching:
            crouch_bg = pygame.Surface((120, 35), pygame.SRCALPHA)
            pygame.draw.rect(crouch_bg, (50, 50, 80, 200), (0, 0, 120, 35), border_radius=5)
            self.screen.blit(crouch_bg, (20, indicator_y))
            crouch_text = self.font_small.render("🧎 CROUCH", True, Colors.NEON_CYAN)
            self.screen.blit(crouch_text, (25, indicator_y + 8))
            indicator_y -= 45
        
        # Low stamina warning
        if self.stamina < 20:
            warn_bg = pygame.Surface((150, 35), pygame.SRCALPHA)
            flash = abs(math.sin(pygame.time.get_ticks() / 150))
            pygame.draw.rect(warn_bg, (100, 0, 0, int(150 + 105 * flash)), (0, 0, 150, 35), border_radius=5)
            self.screen.blit(warn_bg, (20, indicator_y))
            warn_text = self.font_small.render("⚠️ LOW STAMINA", True, Colors.RED)
            self.screen.blit(warn_text, (25, indicator_y + 8))
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
        
        # === HEALING PROGRESS INDICATOR ===
        if self.is_healing:
            # Center healing UI
            heal_box_width = 400
            heal_box_height = 120
            heal_x = self.screen_width // 2 - heal_box_width // 2
            heal_y = self.screen_height // 2 + 150
            
            # Background with glow
            for i in range(3):
                glow_rect = pygame.Surface((heal_box_width + i*10, heal_box_height + i*10), pygame.SRCALPHA)
                pygame.draw.rect(glow_rect, (0, 255, 100, 30 - i*5), 
                               (0, 0, heal_box_width + i*10, heal_box_height + i*10), border_radius=15)
                self.screen.blit(glow_rect, (heal_x - i*5, heal_y - i*5))
            
            # Main background
            pygame.draw.rect(self.screen, (20, 40, 20, 230), 
                           (heal_x, heal_y, heal_box_width, heal_box_height), border_radius=10)
            
            # Title
            heal_names = {'bandage': '🩹 APPLYING BANDAGE', 'medkit': '🏥 USING MEDKIT', 'surgery': '⚕️ SURGERY'}
            title = heal_names.get(self.healing_type, '🏥 HEALING')
            title_text = self.font_large.render(title, True, Colors.NEON_GREEN)
            self.screen.blit(title_text, (heal_x + heal_box_width//2 - title_text.get_width()//2, heal_y + 15))
            
            # Progress bar
            bar_width = 350
            bar_height = 30
            bar_x = heal_x + (heal_box_width - bar_width) // 2
            bar_y = heal_y + 60
            
            # Bar background
            pygame.draw.rect(self.screen, (30, 30, 30), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
            
            # Progress fill with pulse
            pulse = abs(math.sin(pygame.time.get_ticks() / 100))
            fill_width = int(bar_width * self.healing_progress)
            if fill_width > 0:
                fill_color = (int(50 + 50*pulse), int(200 + 55*pulse), int(50 + 50*pulse))
                pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=5)
            
            # Border
            pygame.draw.rect(self.screen, Colors.NEON_GREEN, (bar_x, bar_y, bar_width, bar_height), 3, border_radius=5)
            
            # Percentage
            percent = int(self.healing_progress * 100)
            percent_text = self.font_medium.render(f"{percent}%", True, Colors.WHITE)
            self.screen.blit(percent_text, (bar_x + bar_width//2 - percent_text.get_width()//2, bar_y + 5))
            
            # Warning: Don't move!
            warning_text = self.font_small.render("⚠️ Hold still! Healing in progress...", True, Colors.YELLOW)
            self.screen.blit(warning_text, (heal_x + heal_box_width//2 - warning_text.get_width()//2, heal_y + 95))
        
        # === MEDICAL SUPPLIES COUNTER ===
        med_y = self.screen_height - 280
        
        # Medkit count
        medkit_bg = pygame.Surface((140, 40), pygame.SRCALPHA)
        pygame.draw.rect(medkit_bg, (40, 60, 40, 200), (0, 0, 140, 40), border_radius=5)
        self.screen.blit(medkit_bg, (self.screen_width - 180, med_y))
        medkit_text = self.font_medium.render(f"🏥 Medkits: {self.medkits}", True, Colors.GREEN)
        self.screen.blit(medkit_text, (self.screen_width - 175, med_y + 8))
        
        # Bandage count
        bandage_bg = pygame.Surface((140, 40), pygame.SRCALPHA)
        pygame.draw.rect(bandage_bg, (60, 50, 40, 200), (0, 0, 140, 40), border_radius=5)
        self.screen.blit(bandage_bg, (self.screen_width - 180, med_y + 50))
        bandage_text = self.font_medium.render(f"🩹 Bandages: {self.bandages}", True, Colors.YELLOW)
        self.screen.blit(bandage_text, (self.screen_width - 175, med_y + 58))
        
        # Healing hints
        hint_h = self.font_small.render("H: Use Medkit (+50 HP)", True, Colors.GRAY)
        self.screen.blit(hint_h, (self.screen_width - 180, med_y + 95))
        hint_b = self.font_small.render("B: Apply Bandage (+25 HP)", True, Colors.GRAY)
        self.screen.blit(hint_b, (self.screen_width - 180, med_y + 115))
        
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
            bg_color = (20, 20, 40, min(255, alpha))
            border_color = (*notification['color'], min(255, alpha))
            pygame.draw.rect(bg_surface, bg_color, (0, 0, bar_width, bar_height), border_radius=10)
            pygame.draw.rect(bg_surface, border_color, (0, 0, bar_width, bar_height), 5, border_radius=10)
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
    
    def _render_reward_notifications(self):
        """🎁 Render kill milestone reward notifications - EPIC STYLE"""
        current_time = time.time()
        
        # Remove expired notifications
        self.reward_notifications = [r for r in self.reward_notifications 
                                     if current_time - r['time'] < r['duration']]
        
        for i, reward in enumerate(self.reward_notifications):
            age = current_time - reward['time']
            duration = reward['duration']
            
            # Animation phases
            if age < 0.8:
                # Slide in from top with bounce
                progress = age / 0.8
                bounce = math.sin(progress * math.pi) * 0.2
                y_offset = int(-300 * (1 - progress) * (1 + bounce))
                alpha = int(255 * progress)
                scale = 0.8 + (0.2 * progress)
            elif age > duration - 1.5:
                # Fade out
                fade_progress = (duration - age) / 1.5
                y_offset = int(-50 * (1 - fade_progress))
                alpha = int(255 * fade_progress)
                scale = 1.0
            else:
                # Stay visible with pulse
                pulse = abs(math.sin((age - 0.8) * 2))
                y_offset = int(5 * math.sin((age - 0.8) * 3))
                alpha = 255
                scale = 1.0 + (0.05 * pulse)
            
            # Position - Center top
            base_y = 100 + i * 280
            x_pos = self.screen_width // 2
            y_pos = base_y + y_offset
            
            # === EPIC BACKGROUND BOX ===
            box_width = int(600 * scale)
            box_height = int(240 * scale)
            box_x = x_pos - box_width // 2
            box_y = y_pos
            
            # Multi-layer glow effect
            for glow_size in range(30, 0, -5):
                glow_alpha = int(alpha * 0.3 * (31 - glow_size) / 30)
                glow_surf = pygame.Surface((box_width + glow_size * 2, box_height + glow_size * 2), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*reward['tier_color'], glow_alpha), 
                               (glow_size, glow_size, box_width, box_height), border_radius=20)
                self.screen.blit(glow_surf, (box_x - glow_size, box_y - glow_size))
            
            # Main background
            bg_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            bg_surf.set_alpha(alpha)
            
            # Gradient background
            for y_line in range(box_height):
                ratio = y_line / box_height
                r = int(20 + (40 - 20) * ratio)
                g = int(15 + (30 - 15) * ratio)
                b = int(35 + (50 - 35) * ratio)
                pygame.draw.line(bg_surf, (r, g, b, 200), (0, y_line), (box_width, y_line))
            
            # Border with tier color
            pygame.draw.rect(bg_surf, reward['tier_color'], (0, 0, box_width, box_height), 5, border_radius=20)
            pygame.draw.rect(bg_surf, (255, 255, 255, 100), (5, 5, box_width-10, box_height-10), 2, border_radius=18)
            
            self.screen.blit(bg_surf, (box_x, box_y))
            
            # === MILESTONE TITLE ===
            title_font = pygame.font.Font(None, int(72 * scale))
            title_text = f"🎯 {reward['kills']} KILLS!"
            title_surf = title_font.render(title_text, True, Colors.WHITE)
            title_surf.set_alpha(alpha)
            
            # Title shadow
            shadow_surf = title_font.render(title_text, True, (0, 0, 0))
            shadow_surf.set_alpha(int(alpha * 0.7))
            self.screen.blit(shadow_surf, (x_pos - title_surf.get_width()//2 + 3, box_y + 23))
            
            # Title main
            self.screen.blit(title_surf, (x_pos - title_surf.get_width()//2, box_y + 20))
            
            # === TIER BADGE ===
            tier_font = pygame.font.Font(None, int(42 * scale))
            tier_text = f"⭐ {reward['tier']} TIER ⭐"
            tier_surf = tier_font.render(tier_text, True, reward['tier_color'])
            tier_surf.set_alpha(alpha)
            
            # Tier glow
            for glow in range(6, 0, -1):
                glow_surf = tier_font.render(tier_text, True, reward['tier_color'])
                glow_surf.set_alpha(int(alpha * 0.15 * (7 - glow) / 6))
                self.screen.blit(glow_surf, (x_pos - tier_surf.get_width()//2 + glow, box_y + 85 + glow))
            
            self.screen.blit(tier_surf, (x_pos - tier_surf.get_width()//2, box_y + 85))
            
            # === REWARD LIST ===
            reward_y = box_y + 135
            reward_font = pygame.font.Font(None, int(32 * scale))
            
            for j, reward_text in enumerate(reward['rewards']):
                # Determine icon and color based on reward type
                if 'HP' in reward_text:
                    icon = "❤️"
                    text_color = (255, 100, 100)
                elif 'ARMOR' in reward_text:
                    icon = "🛡️"
                    text_color = (100, 150, 255)
                elif 'MAGAZINE' in reward_text:
                    icon = "📦"
                    text_color = (255, 200, 100)
                elif 'SCORE' in reward_text:
                    icon = "⭐"
                    text_color = (255, 255, 100)
                elif 'XP' in reward_text:
                    icon = "✨"
                    text_color = (150, 255, 200)
                else:
                    icon = "🎁"
                    text_color = (200, 200, 200)
                
                reward_line = f"{icon} {reward_text}"
                reward_surf = reward_font.render(reward_line, True, text_color)
                reward_surf.set_alpha(alpha)
                
                # Calculate position for centering
                line_x = x_pos - reward_surf.get_width()//2
                line_y = reward_y + j * int(28 * scale)
                
                # Text shadow
                shadow_surf = reward_font.render(reward_line, True, (0, 0, 0))
                shadow_surf.set_alpha(int(alpha * 0.6))
                self.screen.blit(shadow_surf, (line_x + 2, line_y + 2))
                
                # Main text
                self.screen.blit(reward_surf, (line_x, line_y))

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
    print("🎖️  TACTICAL COMBAT SIMULATOR - OPERATION BLACKOUT  🎖️")
    print("⚠️  REALISTIC MILITARY SIMULATION | 3 LIVES | PERMADEATH ⚠️")
    print("=" * 60)
    print("\n📋 CONTROLS:")
    print("   WASD - Tactical Movement")
    print("   MOUSE - Aim | Look Around")
    print("   LEFT CLICK - Fire Weapon")
    print("   R - Reload Magazine")
    print("   1-6 - Switch Weapon")
    print("   SHIFT - Sprint (Drains Stamina)")
    print("   CTRL - Crouch (Stealth & Accuracy)")
    print("   RIGHT CLICK - Aim Down Sights (ADS)")
    print("   G - Frag Grenade")
    print("   V - Melee Attack")
    print("   ESC - Pause Menu")
    print("\n🎯 HOSTILE FORCES:")
    print("   TERRORIST - Infantry, 100 HP, Tactical")
    print("   ELITE OPERATOR - Fast, 70 HP, Flanks")
    print("   HEAVY GUNNER - Tank, 250 HP, High Firepower")
    print("   SNIPER - Long range, 80 HP, Precision")
    print("\n� MISSION OBJECTIVES:")
    print("   > Eliminate all hostile combatants")
    print("   > Survive and secure the area")
    print("   > Manage resources (Ammo, Health, Stamina)")
    print("   > Complete tactical objectives")
    print("\n🔫 ARSENAL:")
    print("   1: M4A1 Carbine - 5.56mm (Balanced)")
    print("   2: Barrett M82 - .50 BMG (Anti-Material)")
    print("   3: MP5 SMG - 9mm (CQB Specialist)")
    print("   4: SPAS-12 - 12 Gauge (Breaching)")
    print("   5: Desert Eagle - .50 AE (Sidearm)")
    print("   6: M249 SAW - 5.56mm Belt-Fed (Suppression)")
    print("\n🗺️  COMBAT ZONE:")
    print("   Urban Warfare Environment")
    print("   Multi-Story Buildings & Cover Points")
    print("   Dynamic Weather & Time of Day")
    print("   Realistic Ballistics & Bullet Drop")
    print("\n" + "=" * 60)
    print("Game starting... Navigate menu with arrow keys!")
    print("=" * 60)
    
    # Run game directly (menu will show)
    game.run()

