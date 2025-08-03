import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "BACKENDZEROPINGxc_vy")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

# ✅ Correct way to init bot client
bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

from telethon import events

# Main handler

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def handle(event):
    msg = event.message
    if not msg or not msg.text:
        await bot.send_message(SOURCE_GROUP, "⚠️ Skipped: No message text")
        return

    full_text = msg.text
    if "DEF" in full_text:
        cutoff_index = full_text.find("DEF")
        trimmed_text = full_text[:cutoff_index].strip()

        # Filter entities that fall within trimmed range
        safe_entities = [
            e for e in msg.entities or []
            if e.offset < cutoff_index
        ]

        await bot.send_message(
            TARGET_GROUP,
            trimmed_text,
            formatting_entities=safe_entities
        )

        await bot.send_message(SOURCE_GROUP, "✅ Sent trimmed message with formatting")
    else:
        await bot.send_message(SOURCE_GROUP, "⚠️ Skipped: 'DEF' not found in message")

bot.run_until_disconnected()
