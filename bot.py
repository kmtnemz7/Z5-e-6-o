import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphan")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

# Init bot client
bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats="zeropingphane"))
async def handle(event):
    msg = event.message
    if not msg or not msg.text:
        return

    full_text = msg.text
    trimmed_text = full_text.strip()

    # Keep all formatting entities safely
    safe_entities = msg.entities or []

    await bot.send_message(
        "ZeroPingX",
        trimmed_text,
        formatting_entities=safe_entities
    )
bot.run_until_disconnected()






