import asyncio
import logging
import time
from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_ID, API_HASH, BOT_TOKEN, STRING, MONGO_DB, DEFAULT_SESSION
from telethon import TelegramClient
from motor.motor_asyncio import AsyncIOMotorClient

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

botStartTime = time.time()

# ---------------- PYROGRAM BOT ---------------- #

app = Client(
    "pyrobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    parse_mode=ParseMode.MARKDOWN
)

# ---------------- TELETHON CLIENTS (NO START HERE) ---------------- #

sex = TelegramClient('sexrepo', API_ID, API_HASH)
telethon_client = TelegramClient('telethon_session', API_ID, API_HASH)

# ---------------- OPTIONAL USER CLIENTS ---------------- #

if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None

# userrbot should NEVER be None
if DEFAULT_SESSION:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = Client("userrbot", api_id=API_ID, api_hash=API_HASH)

# ---------------- MONGODB ---------------- #

tclient = AsyncIOMotorClient(MONGO_DB)
tdb = tclient["telegram_bot"]
token = tdb["tokens"]

async def create_ttl_index():
    await token.create_index("expires_at", expireAfterSeconds=0)

async def setup_database():
    await create_ttl_index()
    print("MongoDB TTL index created.")

# ---------------- BOOT SEQUENCE ---------------- #

async def restrict_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME

    await setup_database()

    # start Pyrogram bot
    await app.start()

    # start Telethon safely
    await sex.start(bot_token=BOT_TOKEN)
    await telethon_client.start(bot_token=BOT_TOKEN)

    # optional clients
    if pro:
        await pro.start()

    if userrbot:
        await userrbot.start()

    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name

loop.run_until_complete(restrict_bot())
