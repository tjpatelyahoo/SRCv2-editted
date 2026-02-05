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

# ---------------- TELETHON CLIENTS ---------------- #

sex = TelegramClient('sexrepo', API_ID, API_HASH)
telethon_client = TelegramClient('telethon_session', API_ID, API_HASH)

# ---------------- OPTIONAL USER CLIENTS ---------------- #

if STRING:
    pro = Client("ggbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)
else:
    pro = None

# userrbot exists but does NOT auto-start
if DEFAULT_SESSION:
    userrbot = Client("userrbot", API_ID, API_HASH, session_string=DEFAULT_SESSION)
else:
    userrbot = Client("userrbot", API_ID, API_HASH)

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

    # start main bot
    await app.start()

    # start telethon
    await sex.start(bot_token=BOT_TOKEN)
    await telethon_client.start(bot_token=BOT_TOKEN)

    # optional client
    if pro:
        await pro.start()

    # DO NOT start userrbot here
    # it will start later via /login

    getme = await app.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    BOT_NAME = f"{getme.first_name} {getme.last_name}" if getme.last_name else getme.first_name

loop.run_until_complete(restrict_bot())
