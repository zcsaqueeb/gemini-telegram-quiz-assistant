# ----------------- Telegram API -----------------
API_ID = <YOUR_API_ID>
API_HASH = "<YOUR_API_HASH>"

# ----------------- Telegram Bot -----------------
BOT_TOKEN = "<YOUR_BOT_TOKEN>"

# ----------------- Multi-Group Support -----------------
TARGET_GROUPS = [
    "group_name_here"
]

# ----------------- Answer Speed -----------------
# Options: "instant", "superfast", "fast", "normal"
ANSWER_SPEED = "superfast"

# Mapping speeds to internal delays (seconds)
SPEED_DELAY = {
    "instant": 0,
    "superfast": 0.05,
    "fast": 0.2,
    "normal": 0.5
}

# Enable FAST_MODE (reduces wait times, uses short prompts)
FAST_MODE = True

# Auto-tick correct poll option (do NOT send message, just vote)
AUTO_TICK = True

# ----------------- Gemini API -----------------
# Supports multiple keys; fallback automatically if one fails
GEMINI_API_KEYS = [
    "<YOUR_GEMINI_API_KEY_1>",
    "<YOUR_GEMINI_API_KEY_2>"
]
GEMINI_MODEL = "gemini-2.5-flash"

# ----------------- Session Management -----------------
SESSION_FOLDER = "sessions"

# ----------------- Other Settings -----------------
# Max number of QR login attempts per account
MAX_QR_ATTEMPTS = 3
COUNTDOWN_SECONDS = 1

# Max number of mobile/2FA login attempts per account
MAX_2FA_ATTEMPTS = 3

# Telegram internal delays for async tasks (optional fine-tuning)
ASYNC_DELAY = 0.05

# ----------------- Logging -----------------
LOG_LEVEL = "INFO"
