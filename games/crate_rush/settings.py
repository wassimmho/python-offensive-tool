WIDTH = 1280
HEIGHT = 720
FPS = 60
GRAVITY = 2000
PLAYER_SPEED = 300
JUMP_VELOCITY = -800
PLAYER_SHOOT_COOLDOWN = 0.2
ENEMY_SPAWN_START = 2.2
ENEMY_SPAWN_MIN = 0.6
ENEMY_SPAWN_ACCEL = 0.015
CRATE_RESPAWN_DELAY = 0.6
HAZARD_HEIGHT = HEIGHT - 24
BG_COLOR = (14, 14, 18)
FG_COLOR = (235, 235, 240)
ACCENT = (80, 200, 120)
DANGER = (235, 80, 90)
PLATFORM_COLOR = (62, 66, 88)
BULLET_COLOR = (250, 230, 90)

# UI states
STATE_TITLE = 0
STATE_RUNNING = 1
STATE_PAUSED = 2
STATE_GAMEOVER = 3
STATE_DIFFICULTY = 4  # Difficulty selection screen
STATE_MENU = 5  # Main menu (Offline/Online selection)
STATE_MULTIPLAYER_SOON = 6  # Coming soon message (kept for reference)
STATE_MULTIPLAYER_MENU = 7  # Multiplayer menu (Host/Join)
STATE_MULTIPLAYER_HOST = 8  # Hosting lobby
STATE_MULTIPLAYER_JOIN = 9  # Join screen (enter IP)
STATE_MULTIPLAYER_LOBBY = 10  # Waiting in lobby
STATE_MULTIPLAYER_RUNNING = 11  # Multiplayer game running
STATE_MAP_SELECT = 12  # Map selection for offline mode

# Menu options
MENU_OFFLINE = 0
MENU_ONLINE = 1

# Multiplayer menu options
MP_HOST = 0
MP_JOIN = 1

# Connection modes
CONN_LAN = 0      # Private IP (LAN)
CONN_PUBLIC = 1   # Public IP (ngrok/port forwarding)

# Multiplayer settings
DEFAULT_PORT = 5555
MAX_PLAYER_NAME_LENGTH = 16

# Difficulty levels
DIFF_EASY = 0
DIFF_NORMAL = 1
DIFF_HARD = 2
DIFF_SUPERHARD = 3

# Difficulty settings: (inaccuracy, cooldown_multiplier, shoot_range, reaction_delay, shoot_chance)
# inaccuracy: radians of random spread (higher = miss more)
# cooldown_multiplier: multiply weapon cooldown (higher = shoot slower)
# shoot_range: distance to detect player
# reaction_delay: minimum time before first shot
# shoot_chance: probability to actually shoot when able (0.0-1.0)
DIFFICULTY_SETTINGS = {
    DIFF_EASY: {
        'name': 'Easy',
        'color': (100, 255, 100),
        'inaccuracy': 0.45,      # Miss a lot
        'cooldown_mult': 2.5,    # Shoot very slow
        'shoot_range': 300,      # Short range
        'reaction_delay': 1.0,   # Slow to react
        'shoot_chance': 0.4,     # Only 40% chance to shoot
        'enemy_speed_mult': 0.8, # Slower enemies
        'chase_range': 300,      # Short chase range
        'jump_chance': 0.3,      # Rarely jumps
        'ai_aggression': 0.3,    # Passive AI
        'player_health': 5,      # Player max health
        'enemy_damage': 1,       # Damage per hit
    },
    DIFF_NORMAL: {
        'name': 'Normal',
        'color': (255, 255, 100),
        'inaccuracy': 0.25,      # Some misses
        'cooldown_mult': 1.8,    # Moderate fire rate
        'shoot_range': 380,      # Normal range
        'reaction_delay': 0.5,   # Normal reaction
        'shoot_chance': 0.6,     # 60% chance to shoot
        'enemy_speed_mult': 1.0, # Normal speed
        'chase_range': 450,      # Normal chase range
        'jump_chance': 0.5,      # Sometimes jumps
        'ai_aggression': 0.5,    # Balanced AI
        'player_health': 4,      # Player max health
        'enemy_damage': 1,       # Damage per hit
    },
    DIFF_HARD: {
        'name': 'Hard',
        'color': (255, 150, 50),
        'inaccuracy': 0.12,      # Pretty accurate
        'cooldown_mult': 1.3,    # Fast fire rate
        'shoot_range': 450,      # Long range
        'reaction_delay': 0.2,   # Quick reaction
        'shoot_chance': 0.8,     # 80% chance to shoot
        'enemy_speed_mult': 1.2, # Faster enemies
        'chase_range': 550,      # Long chase range
        'jump_chance': 0.7,      # Often jumps
        'ai_aggression': 0.75,   # Aggressive AI
        'player_health': 3,      # Player max health
        'enemy_damage': 2,       # Damage per hit
    },
    DIFF_SUPERHARD: {
        'name': 'SUPER HARD',
        'color': (255, 50, 50),
        'inaccuracy': 0.04,      # Almost perfect aim
        'cooldown_mult': 1.0,    # Maximum fire rate
        'shoot_range': 550,      # Very long range
        'reaction_delay': 0.05,  # Instant reaction
        'shoot_chance': 0.95,    # Almost always shoots
        'enemy_speed_mult': 1.4, # Very fast enemies
        'chase_range': 700,      # Very long chase range
        'jump_chance': 0.9,      # Almost always jumps when needed
        'ai_aggression': 1.0,    # Maximum aggression
        'player_health': 2,      # Player max health
        'enemy_damage': 2,       # Damage per hit
    },
}

# Heal drop settings
HEAL_DROP_INTERVAL = 8.0    # Seconds between heal drops
HEAL_DROP_AMOUNT = 1        # Health restored per heal
HEAL_DROP_SPEED = 150       # Fall speed in pixels/sec

# UI colors
PANEL_BG = (18, 18, 28)
PANEL_BORDER = (90, 120, 180)
TIP_COLOR = (160, 200, 240)
WEAPON_BADGE = (60, 140, 255)
GLOW_COLOR = (100, 160, 255)
TITLE_COLOR = (255, 220, 100)
SCORE_GLOW = (255, 200, 80)

# Effects
SHAKE_DECAY = 14.0
SHAKE_MAX = 16.0

# Background
BG_OPACITY = 255
BG_PARALLAX_SPEED = 0.2
