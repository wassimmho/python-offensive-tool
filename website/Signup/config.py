# --- Celery Configuration ---
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# --- Brute-force Constants ---
CHARSET = "abc"
MIN_LEN = 1
MAX_LEN = 4
USERNAME = "testuser@gmail.com"
TARGET_URL = "http://127.0.0.1:5000/signin"
PASSWORD_FIELD = "password"
USERNAME_FIELD = "username"
TIMEOUT = 10
