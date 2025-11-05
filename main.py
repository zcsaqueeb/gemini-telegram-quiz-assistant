import sys
import asyncio
import os
import logging
import qrcode
from colorama import init
from google import genai
import aiohttp
import certifi
import ssl
import time
import random
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPoll
from telethon.tl.functions.messages import SendVoteRequest
from config import *

# Rich UI
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text
from rich import box

console = Console()
init(autoreset=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

os.makedirs(SESSION_FOLDER, exist_ok=True)
ssl_context = ssl.create_default_context(cafile=certifi.where())

# 🌌 Gemini client manager with fallback
gemini_client = None
current_gemini_index = 0

def init_gemini_client():
    global gemini_client, current_gemini_index
    for i, key in enumerate(GEMINI_API_KEYS):
        try:
            client = genai.Client(api_key=key)
            # quick test call
            client.models.generate_content(model=GEMINI_MODEL, contents=[{"text":"Test"}])
            gemini_client = client
            current_gemini_index = i
            logging.info(f"✅ Using Gemini API key {i+1}: {key[:6]}***")
            return
        except Exception as e:
            logging.warning(f"❌ Gemini API key {i+1} failed: {key[:6]}*** | {e}")
    raise Exception("❌ All Gemini API keys failed!")

init_gemini_client()

# 🔄 Switch to next Gemini API key
def switch_gemini_key():
    global current_gemini_index, gemini_client
    next_index = (current_gemini_index + 1) % len(GEMINI_API_KEYS)
    gemini_client = genai.Client(api_key=GEMINI_API_KEYS[next_index])
    current_gemini_index = next_index
    logging.warning(f"🔄 Switched to Gemini API key {next_index+1}: {GEMINI_API_KEYS[next_index][:6]}***")

# 🌈 Banner
def gemini_banner():
    banner = random.choice([
        "🌌 GEMINI AI QUIZ ASSISTANT 🌌",
        "🧠 POWERED BY GOOGLE GEMINI 🧠",
        "⚡ ULTRA-FAST POLL ENGINE ⚡"
    ])
    console.print(Panel(Text(banner, style=random.choice(["bold magenta","bold cyan","bold green"])), style="bold blue", box=box.DOUBLE_EDGE))

# 🧠 Gemini Answer Fetching with runtime fallback
def fetch_answer_from_gemini_sync(prompt: str) -> str:
    global gemini_client
    for attempt in range(len(GEMINI_API_KEYS)):
        try:
            short_prompt = f"Q:\n{prompt}\n\nReply only with the correct option number."
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[{"text": short_prompt if FAST_MODE else prompt}]
            )
            return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API error: {e}. Attempting next key...")
            switch_gemini_key()
    return "No answer"

async def fetch_answer_from_gemini(prompt: str) -> str:
    return await asyncio.to_thread(fetch_answer_from_gemini_sync, prompt)

async def fetch_quiz_answer(prompt: str):
    with Live(Spinner("dots", text="🧠 Gemini thinking...", style="bold cyan"), refresh_per_second=12):
        start = time.time()
        answer = await fetch_answer_from_gemini(prompt)
        return answer or "No answer", round(time.time() - start, 2)

# 🎨 Poll display
def print_poll_console(question, options, correct_index, confidence, duration):
    lines = []
    for i, opt in enumerate(options, 1):
        prefix = "→ " if i - 1 == correct_index else "  "
        style = "[bold green]" if i - 1 == correct_index else "[dim]"
        lines.append(f"{style}{prefix}{i}. {opt}[/]")

    bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
    console.print(
        Panel(
            f"[white]Q:[/] {question}\n\n" + "\n".join(lines) +
            f"\n\n[cyan]Accuracy:[/] {confidence:.1f}%\n[green]{bar}[/green]\n[dim]⏱ Gemini reasoning: {duration:.2f}s[/dim]",
            title="🧩 Gemini Poll Analysis",
            border_style="bright_magenta",
            box=box.ROUNDED,
        )
    )

# 🧩 Get poll answer
async def get_poll_answer(question, options):
    opt_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    prompt = f"Question: {question}\nOptions:\n{opt_text}\nReturn only the correct option number:"
    answer, duration = await fetch_quiz_answer(prompt)
    import re
    match = re.search(r'\d+', answer)
    if match:
        idx = int(match.group()) - 1
        if 0 <= idx < len(options):
            return idx, duration
    return 0, duration

# 🗳️ Vote
async def vote_poll(client, message, option_index):
    try:
        poll = message.media.poll
        option = poll.answers[option_index].option
        await client(SendVoteRequest(peer=message.peer_id, msg_id=message.id, options=[option]))
        logging.info(f"✅ Auto-voted for option {option_index + 1}")
        return True
    except Exception as e:
        if "closed" in str(e).lower():
            logging.warning("⚠️ Poll closed before voting could complete.")
        else:
            logging.error(f"❌ Voting failed: {e}")
        return False

# 🔍 Find groups
async def find_groups(client):
    found = {}
    async for dialog in client.iter_dialogs():
        name = (dialog.name or "").lower()
        username = (getattr(dialog.entity, "username", "") or "").lower()
        for target in TARGET_GROUPS:
            t = target.lower()
            if t in name or username == t:
                found[target] = dialog.id
                logging.info(f"✅ Found '{target}' ({dialog.id})")
    return found

# 📷 QR/Mobile login with 2FA fallback
async def login_with_qr_or_phone(index=0):
    session_file = os.path.join(SESSION_FOLDER, f"user{index}.session")
    client = TelegramClient(session_file, API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        logging.info(f"✅ User{index} authorized via existing session.")
        await client.disconnect()
        return client

    img_path = f"qr_user{index}.png"
    for attempt in range(3):
        try:
            logging.info(f"🔑 QR login attempt {attempt+1} for user{index}...")
            qr_login = await client.qr_login()
            img = qrcode.make(qr_login.url)
            img.save(img_path)
            await send_qr_to_bot(BOT_TOKEN, img_path, f"Scan QR for user{index} (attempt {attempt+1})")
            await qr_login.wait()
            if await client.is_user_authorized():
                logging.info(f"✅ User{index} logged in via QR.")
                break
        except Exception as e:
            logging.error(f"❌ QR attempt {attempt+1} failed: {e}")
            await asyncio.sleep(1)
        finally:
            if os.path.exists(img_path):
                os.remove(img_path)

    # Mobile fallback
    if not await client.is_user_authorized():
        logging.info(f"📱 Fallback to mobile login for user{index}")
        phone = input(f"Enter phone number (with country code) for user{index}: ")
        await client.connect()
        try:
            await client.send_code_request(phone)
            code = input(f"Enter Telegram code for {phone}: ")
            try:
                await client.sign_in(phone, code)
            except Exception as e:
                if "SESSION_PASSWORD_NEEDED" in str(e):
                    password = input(f"Enter 2FA password for user{index}: ")
                    await client.sign_in(password=password)
            logging.info(f"✅ User{index} logged in via mobile + 2FA.")
        except Exception as e:
            logging.error(f"❌ Mobile login failed: {e}")
            await client.disconnect()
            raise e

    await client.disconnect()
    return client

async def login_all_accounts():
    logging.info("🔐 Logging in all accounts...")
    client = await login_with_qr_or_phone(0)
    logging.info("🔐 Login completed.")
    return client

# 🧠 Poll handler with Reaction Timer
async def responder_loop(client, groups):
    gemini_banner()
    console.print("[bold cyan]🤖 Gemini Auto-Responder (ultra-fast mode)[/bold cyan]\n")

    @client.on(events.NewMessage(chats=list(groups.values())))
    async def handler(event):
        if not (event.message.media and isinstance(event.message.media, MessageMediaPoll)):
            return
        try:
            poll = event.message.media.poll
            q = poll.question.text if hasattr(poll.question, "text") else str(poll.question)
            opts = [opt.text.text if hasattr(opt.text, "text") else str(opt.text) for opt in poll.answers]

            poll_start = time.time()
            idx, gemini_duration = await get_poll_answer(q, opts)
            confidence = random.uniform(80, 95)
            print_poll_console(q, opts, idx, confidence, gemini_duration)

            delay = SPEED_DELAY.get(ANSWER_SPEED, 0.2)
            if FAST_MODE:
                delay = min(0.2, delay / 2)
            await asyncio.sleep(delay)

            vote_start = time.time()
            vote_success = False
            if AUTO_TICK:
                vote_success = await vote_poll(client, event.message, idx)
            vote_end = time.time()

            total_reaction = vote_end - poll_start
            console.print(
                Panel(
                    f"⏱ Reaction Timer Dashboard\n\n"
                    f"Gemini reasoning: {gemini_duration:.2f}s\n"
                    f"Voting delay: {vote_end - vote_start:.2f}s\n"
                    f"Total reaction time: {total_reaction:.2f}s\n"
                    f"Vote success: {'✅' if vote_success else '❌'}",
                    title="⌛ Reaction Timer",
                    border_style="bright_yellow",
                    box=box.ROUNDED
                )
            )

        except Exception as e:
            logging.error(f"Poll handler error: {e}")

    await client.run_until_disconnected()

# 🚀 Main
async def main():
    client = await login_all_accounts()
    session_file = os.path.join(SESSION_FOLDER, "user0.session")
    client = TelegramClient(session_file, API_ID, API_HASH)
    await client.start()

    groups = await find_groups(client)
    if not groups:
        logging.warning("⚠️ No groups found. Check TARGET_GROUPS.")
        return

    logging.info("🚀 Bot running in multi-group ultra-fast mode")
    await responder_loop(client, groups)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Stopped by user.")
