# config.py
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# Brute force configuration
CHARSET = "abc"
MIN_LEN = 1
MAX_LEN = 4
USERNAME = "testuser@gmail.com"
TARGET_URL = "http://127.0.0.1:5000/signin"
PASSWORD_FIELD = "password"
USERNAME_FIELD = "email"  # Important: your form uses "email"
TIMEOUT = 10
DELAY_SECONDS = 0.5
PASSWORD_LIST_CHECKPOINT = "bf_checkpoint.txt"
CSV_OUT = "exhaustive_bf_results.csv"
RESUME_FROM = None