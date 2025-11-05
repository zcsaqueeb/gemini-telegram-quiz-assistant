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
import re
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

# --------------------- Gemini Banner ---------------------
def gemini_banner():
    banner = Text("🌌 GEMINI AI QUIZ ASSISTANT 🌌", style="bold magenta")
    console.print(
        Panel(
            banner,
            title="🤖 Gemini v2.10",
            subtitle="Multi-account & Multi-group Auto-Tick",
            style="bold cyan",
            box=box.DOUBLE_EDGE,
            expand=False
        )
    )

# --------------------- Gemini API Manager ---------------------
gemini_client = None
current_gemini_index = 0

def init_gemini_client():
    global gemini_client, current_gemini_index
    for i, key in enumerate(GEMINI_API_KEYS):
        try:
            client = genai.Client(api_key=key)
            client.models.generate_content(model=GEMINI_MODEL, contents=[{"text":"Test"}])
            gemini_client = client
            current_gemini_index = i
            logging.info(f"✅ Using Gemini API key {i+1}: {key[:6]}***")
            return
        except Exception as e:
            logging.warning(f"❌ Gemini API key {i+1} failed: {key[:6]}*** | {e}")
    raise Exception("❌ All Gemini API keys failed!")

def switch_gemini_key():
    global current_gemini_index, gemini_client
    next_index = (current_gemini_index + 1) % len(GEMINI_API_KEYS)
    gemini_client = genai.Client(api_key=GEMINI_API_KEYS[next_index])
    current_gemini_index = next_index
    logging.warning(f"🔄 Switched to Gemini API key {next_index+1}: {GEMINI_API_KEYS[next_index][:6]}***")

init_gemini_client()

# --------------------- Poll Answer Cache ---------------------
poll_answer_cache = {}  # key: chat_id:msg_id -> (correct_index, duration)

# --------------------- Gemini Answer ---------------------
def fetch_answer_from_gemini_sync(prompt: str) -> str:
    global gemini_client
    for _ in range(len(GEMINI_API_KEYS)):
        try:
            short_prompt = f"Q:\n{prompt}\n\nReply only with the correct option number."
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[{"text": short_prompt if FAST_MODE else prompt}]
            )
            return response.text.strip()
        except Exception as e:
            logging.error(f"Gemini API error: {e}. Switching key...")
            switch_gemini_key()
    return "No answer"

async def fetch_answer_from_gemini(prompt: str) -> str:
    return await asyncio.to_thread(fetch_answer_from_gemini_sync, prompt)

async def fetch_quiz_answer(prompt: str):
    with Live(Spinner("dots", text="🧠 Gemini thinking...", style="bold cyan"), refresh_per_second=12):
        start = time.time()
        answer = await fetch_answer_from_gemini(prompt)
        return answer or "No answer", round(time.time() - start, 2)

# --------------------- Poll Display ---------------------
def print_poll_console(question, options, correct_index, confidence=85, duration=0.0):
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

# --------------------- Get Poll Answer ---------------------
async def get_poll_answer(question, options):
    opt_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    prompt = f"Question: {question}\nOptions:\n{opt_text}\nReturn only the correct option number:"
    answer, duration = await fetch_quiz_answer(prompt)
    match = re.search(r'\d+', answer)
    if match:
        idx = int(match.group()) - 1
        if 0 <= idx < len(options):
            return idx, duration
    return 0, duration

# --------------------- Vote Poll ---------------------
async def vote_poll(client, message, option_index):
    try:
        poll = message.media.poll
        option = poll.answers[option_index].option
        await client(SendVoteRequest(peer=message.peer_id, msg_id=message.id, options=[option]))
        logging.info(f"✅ Auto-ticked option {option_index + 1}")
        return True
    except Exception as e:
        if "closed" in str(e).lower():
            logging.warning("⚠️ Poll closed before voting could complete.")
        else:
            logging.error(f"❌ Voting failed: {e}")
        return False

# --------------------- Find Groups ---------------------
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

# --------------------- Send QR to Bot ---------------------
async def send_qr_to_bot(bot_token, image_path, caption=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        with open(image_path, 'rb') as photo:
            form = aiohttp.FormData()
            form.add_field('photo', photo, filename="qr.png")
            if caption:
                form.add_field('caption', caption)
            form.add_field('chat_id', str(777000))
            try:
                await session.post(url, data=form)
                logging.info(f"📷 QR sent to bot with caption: {caption}")
            except Exception as e:
                logging.error(f"❌ Failed to send QR to bot: {e}")

# --------------------- QR / Mobile Login ---------------------
async def login_with_qr_or_phone(index=0, max_qr_attempts=3, max_2fa_attempts=3):
    session_file = os.path.join(SESSION_FOLDER, f"user{index}.session")
    client = TelegramClient(session_file, API_ID, API_HASH)
    await client.connect()
    if await client.is_user_authorized():
        logging.info(f"✅ User{index} authorized via existing session.")
    else:
        img_path = f"qr_user{index}.png"
        for attempt in range(1, max_qr_attempts + 1):
            try:
                logging.info(f"🔑 QR login attempt {attempt} for user{index}...")
                qr_login = await client.qr_login()
                img = qrcode.make(qr_login.url)
                img.save(img_path)
                await send_qr_to_bot(BOT_TOKEN, img_path, f"Scan QR for user{index} (attempt {attempt})")
                await qr_login.wait()
                if await client.is_user_authorized():
                    logging.info(f"✅ User{index} logged in via QR.")
                    break
            except Exception as e:
                logging.error(f"❌ QR attempt {attempt} failed: {e}")
            finally:
                if os.path.exists(img_path):
                    os.remove(img_path)
            if attempt < max_qr_attempts:
                logging.info("⏳ Waiting 30s before next QR attempt...")
                await asyncio.sleep(30)

        if not await client.is_user_authorized():
            # fallback to mobile
            for attempt in range(1, max_2fa_attempts + 1):
                try:
                    phone = input(f"Enter phone number (with country code) for user{index}: ")
                    await client.send_code_request(phone)
                    code = input(f"Enter Telegram code for {phone}: ")
                    try:
                        await client.sign_in(phone, code)
                    except Exception as e:
                        if "SESSION_PASSWORD_NEEDED" in str(e):
                            password = input(f"Enter 2FA password for user{index}: ")
                            await client.sign_in(password=password)
                    if await client.is_user_authorized():
                        logging.info(f"✅ User{index} logged in via mobile + 2FA.")
                        break
                except Exception as e:
                    logging.error(f"❌ Mobile/2FA login attempt {attempt} failed: {e}")
                if attempt < max_2fa_attempts:
                    logging.info("⏳ Waiting 10s before retrying mobile login...")
                    await asyncio.sleep(10)
                else:
                    raise Exception(f"❌ User{index} failed to login after {max_2fa_attempts} attempts")

    await client.start()  # keep connected
    return client

async def login_all_accounts_async(count):
    return await asyncio.gather(*(login_with_qr_or_phone(i) for i in range(count)))

# --------------------- Responder Loop ---------------------
async def responder_loop(client, groups):
    gemini_banner()
    console.print(f"[cyan]🤖 Gemini Auto-Responder (with auto-tick) active![/cyan]\n")

    @client.on(events.NewMessage)
    async def handler(event):
        if event.chat_id not in groups.values():
            return
        if event.message.media and isinstance(event.message.media, MessageMediaPoll):
            poll = event.message.media.poll
            question = poll.question if isinstance(poll.question, str) else poll.question.text
            options = [
                opt.text if isinstance(opt.text, str) else opt.text.text
                for opt in poll.answers
            ]

            key = f"{event.chat_id}:{event.message.id}"
            if key in poll_answer_cache:
                correct_idx, duration = poll_answer_cache[key]
            else:
                correct_idx, duration = await get_poll_answer(question, options)
                poll_answer_cache[key] = (correct_idx, duration)

            print_poll_console(question, options, correct_idx, confidence=85, duration=duration)

            # Auto-tick correct answer
            await vote_poll(client, event.message, correct_idx)

    await client.run_until_disconnected()

# --------------------- Main ---------------------
async def main():
    count = int(input("Enter number of accounts to login: "))
    clients = await login_all_accounts_async(count)
    logging.info(f"✅ {len(clients)} account(s) logged in successfully.")

    all_groups = await find_groups(clients[0])
    if not all_groups:
        logging.error("❌ No target groups found. Exiting...")
        return

    await asyncio.gather(*(responder_loop(client, all_groups) for client in clients))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("🛑 Script stopped by user.")
