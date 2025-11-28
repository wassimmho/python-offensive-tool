# config.py

import os
from string import ascii_lowercase, digits

# --- Environment Configuration (Non-Localhost) ---
# IMPORTANT: Define these variables on the machine running the dispatcher and the broker.
# Example: export REDIS_HOST="192.168.1.10"
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '') 
REDIS_AUTH = f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""

# Celery Broker (Queue) and Backend (Results) URLs
CELERY_BROKER_URL = f'redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_AUTH}{REDIS_HOST}:{REDIS_PORT}/1' 

# --- Hashing/Cracking Constants (Shared across Dispatcher and Client) ---
CHARACTER_SET = ascii_lowercase + digits 
MAX_PATTERN_LENGTH = 6

# --- Socket Server Constants ---
SERVER_HOST = '0.0.0.0' # Server listens on all interfaces
SERVER_PORT = 12345