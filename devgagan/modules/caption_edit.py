import re
import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait

from devgagan import userrbot
from config import OWNER_ID

# ================= STORAGE ================= #

CAPSET = {}          # owner_id -> {from, to}
CAPEDIT_STATE = {}   # owner_id -> state

# ================= HELPERS ================= #

def owner_only(_, __, m):
    return m.from_user and m.from_user.id == OWNER_ID

owner_filter = filters.create(owner_only)

def parse_capset(text):
    m = re.match(r"^'(.+?)'\s+'(.*?)'$", text.strip())
    if not m:
        return None, None
    return m.group(1), m.group(2)

def normalize_text(text):
    for x in ("**", "__", "`"):
        text = text.replace(x, "")
    return text

def parse_message_link(link: str):
    if "/c/" in link:
        parts = link.rstrip("/").split("/")
        chat_id = int("-100" + parts[-2])
        msg_id = int(parts[-1])
        return chat_id, msg_id
    else:
        parts = link.rstrip("/").split("/")
        return parts[-2], int(parts[-1])

# ================= /capset ================= #

@userrbot.on_message(filters.command("capset") & owner_filter)
async def capset_start(_, m):
    CAPEDIT_STATE[m.from_user.id] = {"step": "capset"}
    await m.reply_text(
        "✏️ **Send caption rule**\n\n"
        "`'OLD' 'NEW'`\n\n"
        "Example:\n"
        "`'EduVision' 'Admin'`\n\n"
        "Remove word:\n"
        "`'EduVision' ' '`"
    )

@userrbot.on_message(filters.private & owner_filter)
async def capset_save(_, m):
    state = CAPEDIT_STATE.get(m.from_user.id)
    if not state or state.get("step") != "capset":
        return

    old, new = parse_capset(m.text)
    if old is None:
        await m.reply_text("❌ Invalid format. Use `'old' 'new'`")
        return

    CAPSET[m.from_user.id] = {"from": old, "to": new}
    CAPEDIT_STATE.pop(m.from_user.id, None)

    await m.reply_text(
        f"✅ **Caption rule saved**\n\n"
        f"`{old}` → `{new or '(removed)'}`\n\n"
        f"Now use `/capedit`"
    )

# ================= /capedit ================= #

@userrbot.on_message(filters.command("capedit") & owner_filter)
async def capedit_start(_, m):
    if m.from_user.id not in CAPSET:
        await m.reply_text("❌ No rule found. Use /capset first.")
        return

    CAPEDIT_STATE[m.from_user.id] = {"step": "link"}
    await m.reply_text("📎 Send starting message link")

@userrbot.on_message(filters.private & owner_filter)
async def capedit_flow(_, m):
    state = CAPEDIT_STATE.get(m.from_user.id)
    if not state:
        return

    # Step 1: link
    if state["step"] == "link":
        try:
            chat_id, start_id = parse_message_link(m.text)
        except Exception:
            await m.reply_text("❌ Invalid message link")
            return

        state.update({
            "chat_id": chat_id,
            "start_id": start_id,
            "step": "count"
        })
        await m.reply_text("🔢 How many next messages?")

    # Step 2: count
    elif state["step"] == "count":
        try:
            limit = int(m.text)
            if limit <= 0:
                raise ValueError
        except Exception:
            await m.reply_text("❌ Send a valid number")
            return

        state["limit"] = limit
        CAPEDIT_STATE.pop(m.from_user.id, None)

        await m.reply_text("⏳ Editing captions...")
        await apply_caption_edit(m.from_user.id, state)

# ================= CORE ================= #

async def apply_caption_edit(owner_id, state):
    rule = CAPSET[owner_id]
    edited = skipped = failed = 0

    for i in range(state["limit"]):
        mid = state["start_id"] + i

        try:
            msg = await userrbot.get_messages(state["chat_id"], mid)

            if not msg or not msg.from_user or not msg.from_user.is_self:
                skipped += 1
                continue

            text = msg.text or msg.caption
            if not text or rule["from"] not in text:
                skipped += 1
                continue

            clean = normalize_text(text)
            new_text = clean.replace(rule["from"], rule["to"])

            if new_text == text:
                skipped += 1
                continue

            await msg.edit_text(new_text)
            edited += 1
            await asyncio.sleep(1.2)

        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            failed += 1

    await userrbot.send_message(
        owner_id,
        f"✅ **Caption edit completed**\n\n"
        f"✏️ Edited: `{edited}`\n"
        f"⏭ Skipped: `{skipped}`\n"
        f"⚠️ Failed: `{failed}`"
    )