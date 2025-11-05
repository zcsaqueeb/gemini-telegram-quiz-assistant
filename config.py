# ============================================================
# ⚙️ CONFIGURATION FILE — Gemini Telegram Quiz Assistant
# ============================================================

# 🔐 Telegram API credentials (replace with your own)
API_ID = 123456
API_HASH = "your_api_hash_here"

# 🤖 Telegram Bot Token (optional, if using bot mode)
BOT_TOKEN = "your_bot_token_here"

# 🎯 Target groups (support multiple)
TARGET_GROUPS = [
    "your_group_name_or_bot_username"
]

# 🕓 Answer Speed Settings (for AUTO_TICK)
# Options: "instant", "superfast", "fast", "normal"
ANSWER_SPEED = "instant"

# FAST_MODE reduces thinking + voting delay
FAST_MODE = True

# Automatically tick the correct answer in polls
AUTO_TICK = True

# Delay mapping in seconds for each speed mode
SPEED_DELAY = {
    "instant": 0.05,
    "superfast": 0.1,
    "fast": 0.2,
    "normal": 0.5
}

# Choose answer provider: "gemini" or "gpt"
ANSWER_PROVIDER = "gemini"

# Gemini API keys (replace with your own)
GEMINI_API_KEYS = [
    "your_gemini_api_key_1",
    "your_gemini_api_key_2"
]

# Gemini model version
GEMINI_MODEL = "gemini-2.5-flash"

# GPT API config (optional fallback)
USE_GPT = True
GPT_API_URL = "https://your_gpt_api_url_here"

# Session folder
SESSION_FOLDER = "sessions"
