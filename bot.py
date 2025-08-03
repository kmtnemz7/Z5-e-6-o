import os
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "BACKENDZEROPINGxc_vy")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

# ✅ Correct way to init bot client
bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay(event):
    try:
        msg = event.message
        if msg.raw_text:
            await bot.send_message(TARGET_GROUP, msg.raw_text, parse_mode="Markdown")
            print("✅ Relayed message.")
        else:
            print("⚠️ Skipped non-text message.")
    except Exception as e:
        print(f"❌ Relay failed: {e}")

bot.run_until_disconnected()
