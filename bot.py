import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError
from telethon.tl.types import MessageMediaWebPage

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphane")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

async def start_with_retry(client, bot_token, retries=3, base_delay=60):
    for attempt in range(retries):
        try:
            await client.start(bot_token=bot_token)
            return True
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(base_delay)
    return False

bot = TelegramClient("zeroping_bot", api_id, api_hash)

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def handle(event):
    msg = event.message
    if isinstance(msg.media, MessageMediaWebPage):
        await bot.send_message(
            TARGET_GROUP,
            msg.text or "",
            parse_mode="md"
        )
    else:
        await bot.send_message(
            TARGET_GROUP,
            msg.text or "",
            file=msg.media,
            parse_mode="md"
        )

async def main():
    if await start_with_retry(bot, BOT_TOKEN):
        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
