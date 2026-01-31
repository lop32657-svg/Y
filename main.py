from telethon.sync import TelegramClient
from telethon import events
from funcions import getcards
import os
import csv
import random
import zipfile
import shutil

def unzip_and_fix(zip_path, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    marker = os.path.join(extract_to, ".unzipped")

    if os.path.exists(marker):
        return

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_to)

    # 🔧 FIX double-folder issue
    inner = os.path.join(extract_to, extract_to)
    if os.path.isdir(inner):
        for f in os.listdir(inner):
            shutil.move(os.path.join(inner, f), os.path.join(extract_to, f))
        try:
            os.rmdir(inner)
        except:
            pass

    open(marker, "w").close()

# 👉 AUTO UNZIP
unzip_and_fix("binsList.zip", "binsList")
unzip_and_fix("images.zip", "images")

# 👉 DEBUG (အရမ်းအရေးကြီး)
print("binsList files:", os.listdir("binsList"))

# ================== TELEGRAM API ==================
api_id = 34151962
api_hash = '2b9f91b43a858f3fd3c23c6faec41aa4'

# ================== OUTPUT CHANNELS ==================
scarscapper = -1003506416886
vipscrapper = -1003530017927

# ================== INPUT CHANNELS ==================
chats = [
    -1003640922476,
    -1003486042896,
    -1003790471863,
    -1002262244580,
]

# ================== CONTROL ==================
is_active = True

# ===== FILE PATHS =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_FILE = os.path.join(BASE_DIR, "cards.txt")
BINS_CSV = os.path.join(BASE_DIR, "binsList", "ranges.csv")
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# ===== DUPLICATE CACHE (memory) =====
# (program start မှာ cards.txt ထဲက already saved တွေ load လုပ်ထားမယ်)
seen = set()
if os.path.exists(CARDS_FILE):
    try:
        with open(CARDS_FILE, "r", encoding="utf-8", errors="ignore") as rf:
            for line in rf:
                s = line.strip()
                if s:
                    seen.add(s)
        print(f"✅ Loaded {len(seen)} saved cards from cards.txt")
    except Exception as e:
        print("⚠️ Could not load cards.txt:", e)

# ================== CLIENT ==================
with TelegramClient('session_name', api_id, api_hash) as client:

    @client.on(events.NewMessage(chats=chats))
    async def handle_message(event):
        if not is_active:
            return

        text_raw = event.raw_text or ""
        if not text_raw:
            return

        # ===== GET CARD (2 cards ထက်ပိုပါရင် funcions.py က None ပြန်ပေးမယ်) =====
        cards = getcards(text_raw)
        if not cards:
            return

        cc, mes, ano, cvv = cards
        card_line = f"{cc}|{mes}|{ano}|{cvv}"

        # ===== DUPLICATE CHECK =====
        if card_line in seen:
            print("⏭️ Duplicate skipped:", card_line)
            return

        # ===== BIN LOOKUP =====
        scheme = card_type = brand = bank_name = country = "UNKNOWN"
        emoji = ""

        try:
            with open(BINS_CSV, mode='r', encoding='utf-8', errors="ignore") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if (row.get('number') or "") == cc[:6]:
                        scheme = (row.get('vendor') or 'UNKNOWN').upper()
                        card_type = (row.get('type') or 'UNKNOWN').upper()
                        brand = (row.get('level') or 'UNKNOWN').upper()
                        bank_name = (row.get('bank_name') or 'UNKNOWN').upper()
                        country = (row.get('country') or 'UNKNOWN').upper()
                        emoji = row.get('flag') or ''
                        break
        except FileNotFoundError:
            print("⚠️ binsList/ranges.csv not found")
        except Exception as e:
            print("⚠️ BIN lookup error:", e)

        # ===== SAVE (only after passing duplicate check) =====
        try:
            with open(CARDS_FILE, "a", encoding="utf-8") as f:
                f.write(card_line + "\n")
            seen.add(card_line)
        except Exception as e:
            print("⚠️ Save error:", e)

        # ===== MESSAGE (CAPTION) =====
        caption = f"""
<b>APPROVED ✅</b>

<b>{scheme} • {card_type} • {brand}</b>

<code>{cc}|{mes}|{ano}|{cvv}</code>

{bank_name} | {country} {emoji}
BIN: <code>{cc[:6]}</code>

<code>{cc[:12]}xxxx|{mes}|{ano}|xxx</code>

@Mydev1
""".strip()

        # ===== IMAGE (RANDOM) =====
        image_path = None
        if os.path.isdir(IMAGES_DIR):
            imgs = [f for f in os.listdir(IMAGES_DIR)
                    if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
            if imgs:
                image_path = os.path.join(IMAGES_DIR, random.choice(imgs))

        # ===== SEND =====
        try:
            if image_path and os.path.exists(image_path):
                await client.send_file(
                    scarscapper,
                    image_path,
                    caption=caption,
                    parse_mode="html"
                )
            else:
                await client.send_message(
                    scarscapper,
                    caption,
                    parse_mode="html"
                )
        except Exception as e:
            print("⚠️ Send error:", e)

    # ================== RUN ==================
    print("✅ Scrapper running...")
    client.run_until_disconnected()