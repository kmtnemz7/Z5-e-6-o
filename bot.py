import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphane")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats="zeropingphane"))
async def handle(event):
    try:
        msg = event.message
        await bot.send_message(
            "ZeroPingX",
            msg.text or "",  # Handle empty text
            file=msg.media,  # Include media
            parse_mode="md"  # Match main.py's Markdown parsing
        )
    except Exception as e:
        print(f"Error sending to ZeroPingX: {e}")

bot.run_until_disconnected()
