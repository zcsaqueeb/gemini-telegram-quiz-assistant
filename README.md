# 🌌 Gemini AI Quiz Auto-Tick Bot

[![Python](https://img.shields.io/badge/python-3.11+-blue)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://telegram.org/)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/gemini-quiz-bot)](https://github.com/yourusername/gemini-quiz-bot/issues)

---

## 🚀 Overview

**Gemini AI Quiz Bot** is a **professional, multi-account, multi-group Telegram bot** that automatically detects quizzes and polls, fetches the correct answer using **Google Gemini API**, and ticks the correct option in real-time.

It’s designed for **speed, reliability, and pro-level console UI**, supporting multiple accounts, multi-group auto-tick, and multiple Gemini API keys with automatic failover.

---

## ✨ Features

* ✅ Multi-account login via **QR code** or **mobile + 2FA**.
* ✅ Multi-group & channel support.
* ✅ Auto-tick correct quiz option only (no message spam).
* ✅ Gemini API integration with multiple keys and **failover**.
* ✅ Professional console dashboard:

  * Clean question display
  * Correct answer highlighted
  * Accuracy & confidence meter
  * Reasoning time displayed
* ✅ Async polling & caching to reduce redundant API calls.
* ✅ Countdown timers for automatic voting.
* ✅ Fully configurable via `config.py`.

---

## 📦 Installation

1. **Clone this repository**

```bash
git clone https://github.com/yourusername/gemini-quiz-bot.git
cd gemini-quiz-bot
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Create a `config.py` file in the project root:

```python
# Telegram API
API_ID = 123456
API_HASH = "your_api_hash"
BOT_TOKEN = "your_telegram_bot_token"

# Session folder
SESSION_FOLDER = "sessions"

# Gemini API
GEMINI_API_KEYS = ["your_first_api_key", "your_second_api_key"]
GEMINI_MODEL = "gemini-2.5-flash"

# Target Telegram groups or channels (name or username)
TARGET_GROUPS = ["group1", "group2"]

# Optional: enable fast mode for shorter prompts
FAST_MODE = True

# Countdown before auto-tick
COUNTDOWN_SECONDS = 3
```

---

## ⚡ Usage

1. Run the main script:

```bash
qr_code_and_number_loin_and_multiple_accoutns.py
```

```bash
number_login_only.py
```

2. Enter the number of accounts you want to login.
3. Scan the QR code sent to your Telegram bot **or enter phone + 2FA code**.
4. The bot will automatically detect polls, fetch answers from Gemini, and tick the correct option.
5. Multi-account and multi-group support is fully automated.

---

## 🖥️ Console UI

* Questions are displayed clearly, with correct answers highlighted.
* Confidence meter shows how confident Gemini is about the answer.
* Reasoning time is displayed in seconds.
* No `TextWithEntities` clutter – clean and professional.

---

## ⚡ Advanced Features

* Automatic caching of poll answers across multiple accounts to reduce API calls.
* Gemini API failover: if one key fails, the bot automatically switches to the next key.
* Configurable countdown for automated ticking.
* Supports both QR code login and mobile login with 2FA fallback.

---

## 📝 Example

```
🌌 GEMINI AI QUIZ ASSISTANT 🌌
🤖 Gemini v2.10 - Multi-account & Multi-group Auto-Tick

🧩 Gemini Poll Analysis
Q: Who discovered penicillin?
→ 1. Alexander Fleming
  2. Marie Curie
  3. Louis Pasteur
  4. Thomas Edison

Accuracy: 90%
⏱ Gemini reasoning: 1.23s

✅ Auto-ticked option 1
```

---

## 🔒 Security & Privacy

* **Sessions** are stored locally in the `sessions/` folder.
* Your Telegram credentials are never shared or stored outside your machine.
* Gemini API keys are used securely and can be rotated automatically.

---

## 📚 Requirements

* Python 3.11+
* Telethon
* aiohttp
* google-genai
* rich
* colorama
* qrcode
* certifi

---

## 💡 Contribution

Feel free to submit issues or pull requests! This bot is open-source and designed for **educational and automation purposes only**.

---

## ⚖️ Disclaimer

This bot **automatically interacts with Telegram polls**. Use responsibly. The author is not responsible for account restrictions if misused.

---

## 📌 License

MIT License – see [LICENSE](LICENSE)



Do you want me to create that enhanced README next?
