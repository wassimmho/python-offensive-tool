# Python Offensive Security Toolkit

A comprehensive Python-based security toolkit featuring networking utilities, brute-force testing capabilities, and a 2D platformer game.

## Project Description

This university project demonstrates the implementation of multiple security and networking concepts in Python:

- **Network Communication**: Server-client architecture with socket programming
- **Brute Force Testing**: Multiple approaches to password testing (HTTP requests, Selenium automation, distributed processing)
- **Game Development**: A complete 2D platformer game with multiplayer support using Pygame
- **Distributed Computing**: Task distribution using Celery and Redis
- **Automation**: Browser automation for JavaScript-heavy websites

## Key Features

### Networking Component
- Multi-client server with connection management
- File transfer with compression support
- Hash discovery system using Celery
- Socket-based communication protocol

### Brute Force Testing
- **Sequential Mode**: Single-threaded password testing
- **Selenium Mode**: Browser-based testing for JavaScript sites
- **Hybrid Mode**: Automatic fallback from HTTP to browser automation
- **Distributed Mode**: Celery-based task distribution across multiple workers
- CSV logging and checkpointing for resumable attacks

### Crate Rush Game
- 2D action platformer built with Pygame
- Multiplayer network support
- Enemy AI and weapon systems
- Controller/gamepad support
- Save system with high scores

## Project Architecture

```
python-offensive-tool/
├── Networking/
│   ├── Server.py                 # Main server implementation
│   ├── Client.py                 # Client interface
│   ├── Function_Net/             # Network utilities
│   │   ├── sending.py           # File sending functions
│   │   └── recieving.py         # File receiving functions
│   ├── OFFLINE_bruteforce/      # Offline hash cracking
│   │   └── Mohamed/
│   │       ├── socket_client.py
│   │       ├── socket_tasks.py
│   │       ├── task_broker.py
│   │       ├── task_dispatcher.py
│   │       └── config.py
│   └── ONLINE_bruteforce/       # Online password testing
│       ├── guessing.py          # Main brute force script
│       ├── Signup.py            # Test signup form
│       └── requirements.txt
│
├── games/
│   └── crate_rush/              # Game source code
│       ├── main.py              # Game entry point
│       ├── player.py            # Player mechanics
│       ├── enemies.py           # Enemy AI
│       ├── weapons.py           # Weapon systems
│       ├── level.py             # Level management
│       ├── multiplayer.py       # Network multiplayer
│       ├── ui.py                # User interface
│       ├── settings.py          # Game configuration
│       └── requirements.txt
│
└── README.md
```

## Requirements

### System Requirements
- Python 3.8 or higher
- pip package manager
- Redis server (for distributed features)

### Python Dependencies
- requests - HTTP library
- selenium - Browser automation
- webdriver-manager - Automatic ChromeDriver management
- pygame - Game development
- celery - Distributed task queue
- redis - Message broker

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/wassimmho/python-offensive-tool.git
cd python-offensive-tool
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### Step 3: Install Dependencies

For Networking Tools:
```bash
cd Networking
pip install -r requirements.txt
```

For Game:
```bash
cd games/crate_rush
pip install -r requirements.txt
```

### Step 4: Install Redis

**Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Extract and add to PATH

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
```

## Usage Guide

### Networking Server

```bash
cd Networking
python Server.py
```

This starts the server listening on port 5555. Features:
- Multi-client connection handling
- File transfer with compression
- Hash discovery system
- Custom socket protocol

### Networking Client

```bash
cd Networking
python Client.py
```

Commands available:
- `upload` - Upload files to server
- `download` - Download files from server
- `execute` - Execute commands
- `discover` - Hash discovery
- `quit` - Disconnect

### Online Brute Force

Create `config.py` in `Networking/ONLINE_bruteforce/`:
```python
TARGET_URL = "http://example.com/login"
USERNAME = "test@email.com"
USERNAME_FIELD = "email"
PASSWORD_FIELD = "password"
CHARSET = "abcdefghijklmnopqrstuvwxyz0123456789"
MIN_LEN = 4
MAX_LEN = 6
DELAY_SECONDS = 0.5
USE_SELENIUM = False
USE_HYBRID = False
```

Run brute force:
```bash
cd Networking/ONLINE_bruteforce

# Sequential mode
python guessing.py

# With Selenium (browser automation)
python guessing.py --selenium

# Hybrid mode (auto-fallback)
python guessing.py --hybrid

# Distributed mode (multiple workers)
python guessing.py --distributed --workers=4
```

Results are saved to CSV with timestamps and success indicators.

### Crate Rush Game

```bash
cd games/crate_rush
python -m crate_rush.main
```

Controls:
- Arrow Keys / WASD - Move
- Space - Jump
- Mouse/Controller Button - Shoot
- ESC - Pause

Multiplayer:
1. Host selects "Host Game" from menu
2. Clients select "Join Game"
3. Enter host IP address
4. Play cooperatively

## Technical Implementation

### Networking Module
- Uses Python sockets for low-level network communication
- Threading for concurrent client handling
- Custom protocol for file transfer with zlib compression
- Session management and authentication

### Brute Force Module
- Iterative password generation from configurable character set
- Multiple success detection mechanisms:
  - JSON response parsing
  - HTTP redirect detection
  - Session cookie detection
  - HTML content analysis
- Checkpointing system saves progress for resume capability
- CSV logging with detailed attempt metadata

### Game Engine
- Pygame for rendering and game loop
- Entity-based architecture (Player, Enemies, Weapons)
- Network synchronization for multiplayer gameplay
- Sprite animation and collision detection
- Particle effects and particle system
- State machine for menu and gameplay states

### Distributed Computing
- Celery task queue for parallel processing
- Redis message broker for task distribution
- Task chunking for efficient load distribution
- Callback-based result handling

## Key Implementation Details

1. **Socket Programming**: Custom protocol with header-based message framing
2. **Thread Safety**: Locks and thread-safe structures for concurrent operations
3. **Browser Automation**: Selenium with intelligent field detection for various website layouts
4. **Distributed Tasks**: Celery group and chord operations for parallel execution
5. **Game State Management**: Finite state machine for menu and gameplay
6. **Checkpoint System**: File-based tracking for resumable operations
7. **Compression**: zlib compression for file transfer optimization
