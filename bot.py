mport os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphane")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

async def start_with_retry(client, bot_token, retries=3, base_delay=60):
    for attempt in range(retries):
        try:
            await client.start(bot_token=bot_token)
            print("Bot started successfully")
            return True
        except FloodWaitError as e:
            print(f"FloodWaitError: Waiting {e.seconds} seconds (attempt {attempt + 1}/{retries})")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:
            print(f"Startup error: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(base_delay)
    print("Failed to start bot after retries")
    return False

bot = TelegramClient("zeroping_bot", api_id, api_hash)

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def handle(event):
    try:
        msg = event.message
        # Debug: Log message start and sender
        start_text = msg.text[:20] if msg.text else "No text"
        sender_id = msg.sender_id
        has_media = bool(msg.media)
        print(f"Received message: start='{start_text}', sender_id={sender_id}, has_media={has_media}")
        
        await bot.send_message(
            TARGET_GROUP,
            msg.text or "",
            file=msg.media,
            parse_mode="md"
        )
        print(f"Sent message to {TARGET_GROUP}")
    except FloodWaitError as e:
        print(f"FloodWaitError in handler: Waiting {e.seconds} seconds")
        await asyncio.sleep(e.seconds + 1)
        await bot.send_message(
            TARGET_GROUP,
            msg.text or "",
            file=msg.media,
            parse_mode="md"
        )
    except Exception as e:
        print(f"Error sending to {TARGET_GROUP}: {e}")

async def main():
    if await start_with_retry(bot, BOT_TOKEN):
        print(f"Listening to {SOURCE_GROUP}, sending to {TARGET_GROUP}")
        await bot.run_until_disconnected()
    else:
        print("Bot failed to start")

if __name__ == "__main__":
    asyncio.run(main())
