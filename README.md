# 🌌 Gemini AI Quiz Auto-Ticker Bot

**Gemini AI Quiz Bot** is a professional Telegram automation tool designed to **auto-tick correct poll answers** in groups and channels using **Google Gemini AI**, supporting **multi-account**, **multi-group**, and **advanced speed controls**.

No messages are sent — the bot only selects the correct poll option automatically.

---

## ⚡ Features

* ✅ **Auto-tick correct poll options** (no messages sent)
* 🤖 **Gemini AI-powered** poll answering
* 🔄 **Multi-account support** with async login
* 🏆 **Multi-group support** — single API call for all accounts in same group
* ⏱ **Answer speed modes**: `instant`, `superfast`, `fast`, `normal`
* 🔑 **QR login** with fallback to **phone + 2FA**
* 🔄 **Gemini API fallback** — supports multiple keys
* 📊 **Professional console UI** with confidence bar and reasoning time
* 🗂 **Session management** — keeps logged-in sessions in `sessions/`
* ⚡ **Optimized performance** with async delays and caching

---

## 📝 Configuration

Edit the `config.py` file to customize your setup:

```python
# ----------------- Telegram API -----------------
API_ID = 1595346
API_HASH = "your_api_hash_here"
BOT_TOKEN = "your_bot_token_here"

# ----------------- Multi-Group Support -----------------
TARGET_GROUPS = ["group1", "group2"]

# ----------------- Answer Speed -----------------
ANSWER_SPEED = "superfast"  # Options: "instant", "superfast", "fast", "normal"
SPEED_DELAY = {"instant":0, "superfast":0.05, "fast":0.2, "normal":0.5}
FAST_MODE = True  # Reduce prompt length for speed

# Auto-tick correct poll option
AUTO_TICK = True

# ----------------- Gemini API -----------------
GEMINI_API_KEYS = [
    "your_gemini_key_1",
    "your_gemini_key_2"
]
GEMINI_MODEL = "gemini-2.5-flash"

# ----------------- Session Management -----------------
SESSION_FOLDER = "sessions"
MAX_QR_ATTEMPTS = 3
MAX_2FA_ATTEMPTS = 3

# Countdown before voting
COUNTDOWN_SECONDS = 1

# Async fine-tuning
ASYNC_DELAY = 0.05

# Logging
LOG_LEVEL = "INFO"
```

---

## 🚀 How to Run

1. Clone this repository:

```bash
git clone https://github.com/yourusername/gemini-quiz-bot.git
cd gemini-quiz-bot
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Edit `config.py` with your API credentials, target groups, and preferences.

4. Run the bot:

```bash
number_login_only.py
```
```bash
qr_code_and_number_loin_and_multiple_accoutns.py
```


5. Enter the number of accounts to login when prompted. The bot will attempt **QR login** first, then fallback to **phone + 2FA** if needed.

---

## 🖥 Console Dashboard

* ✅ Clean professional display of question, options, confidence, and AI reasoning time.
* 📊 Confidence bar shows AI confidence in the answer.
* ⏱ Timer shows Gemini reasoning duration.

Example:

```
Q: How does LERN360 differ from traditional platforms?
→ 1. It relies on AI, blockchain, and tokenized incentives
  2. It uses paper certificates
  3. It has no online system
Confidence: 86%
⏱ Gemini reasoning: 1.36s
✅ Auto-ticked option 1
```

---

## ⚙ Requirements

* Python 3.11+
* Telethon
* google-genai
* aiohttp
* certifi
* colorama
* rich
* qrcode

---

## 📄 License

MIT License © 2025

**Author:** Saqueeb

---

## 💡 Notes

* The bot only **ticks the correct poll option**; it does **not send any messages**.
* Multiple accounts in the same group **share answers** to reduce API calls.
* Supports **auto-fallback between Gemini API keys** if one fails.

---
