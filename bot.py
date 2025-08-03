import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "BACKENDZEROPINGxc_vy")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

# ✅ Correct way to init bot client
bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats="SOURCE_GROUP"))
async def handle(event):
    # Filter: only messages from PhanesBot
    if not event.sender or event.sender.username != "PhanesGoldBot":
        return

    msg = event.message
    if not msg.raw_text:
        return

    # Split before "DEF"
    full_text = msg.raw_text
    if "DEF" in full_text:
        trimmed = full_text.split("DEF")[0].strip()
        if trimmed:
            await bot.send_message("TargetChannel", trimmed)
            print("✅ Sent text before DEF")
        else:
            print("⚠️ Trimmed message was empty")
    else:
        print("⚠️ Skipped: 'DEF' not in message")

bot.run_until_disconnected()
