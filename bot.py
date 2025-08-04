import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Use chat IDs (replace with actual IDs)
SOURCE_GROUP = "zeropingphane"  
TARGET_GROUP = "ZeroPingX"      

# Init bot client
bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def handle(event):
    try:
        msg = event.message
        await bot.send_message(
            TARGET_GROUP,
            msg.text or "",  # Handle empty text
            file=msg.media,  # Include media
            parse_mode="md"  # Match main.py
        )
    except Exception as e:
        print(f"Error sending to {TARGET_GROUP}: {e}")

bot.run_until_disconnected()
