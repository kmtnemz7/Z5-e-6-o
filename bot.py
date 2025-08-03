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
        await bot.send_message(SOURCE_GROUP, "⚠️ Skipped: No message text")
        return

    try:
        await bot.send_message(
            TARGET_GROUP,
            msg.text,
            parse_mode="md"  # or "MarkdownV2" if needed
        )
        await bot.send_message(SOURCE_GROUP, "✅ Relayed message with formatting")
    except Exception as e:
        await bot.send_message(SOURCE_GROUP, f"❌ Failed to send message: {e}")
        
        

bot.run_until_disconnected()
