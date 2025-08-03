import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphan")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

# ✅ Correct way to init bot client
bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

from telethon import events

# Main handler

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def handle(event):
    msg = event.message
    if not msg or not msg.text:
        return

    await client.send_message(
        TARGET_GROUP,
        msg.text,
        parse_mode="md"  # or "MarkdownV2" if needed
    )
bot.run_until_disconnected()

