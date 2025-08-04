import os
import asyncio
import re
from telethon import TelegramClient, events
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
    text = msg.text or ""
    
    # Extract Phanes variables
    lines = text.splitlines()
    token_name = ""
    token_ticker = ""
    contract_address = ""
    chain = ""
    age = ""
    watchers = ""
    usd_price = ""
    price_change = ""
    market_cap = ""
    volume = ""
    liquidity = ""
    supply = ""
    one_hour_change = ""
    one_hour_buys = ""
    one_hour_sells = ""
    ath = ""
    freshies = ""
    top_10_holders = ""
    top_holders = []
    dev_sold = ""
    dev_sold_id = ""
    dex_paid = ""
    
    # Parse header
    if lines:
        header_match = re.match(r'🟣 \*\*(.*?)\*\*.*?\((.*?)\)', lines[0])
        if header_match:
            token_name = header_match.group(1)
            token_ticker = header_match.group(2)
    
    for line in lines:
        if line.startswith("├ ") and not contract_address:
            contract_address = line.split("├ ")[1].strip()
        elif line.startswith("└ "):
            parts = line.split(" | ")
            if len(parts) >= 3:
                chain = parts[0].split("└ ")[1].strip()
                age = parts[1].strip()
                watchers = parts[2].strip()
        elif line.startswith(" ├ USD:"):
            parts = line.split("(-")
            usd_price = parts[0].split("├ USD:")[1].strip()
            price_change = "-"+parts[1].strip() if len(parts) > 1 else ""
        elif line.startswith(" ├ MC:"):
            market_cap = line.split("├ MC:")[1].strip()
        elif line.startswith(" ├ Vol:"):
            volume = line.split("├ Vol:")[1].strip()
        elif line.startswith(" ├ LP:"):
            liquidity = line.split("├ LP:")[1].strip()
        elif line.startswith(" ├ Sup:"):
            supply = line.split("├ Sup:")[1].strip()
        elif line.startswith(" ├ 1H:"):
            parts = line.split(" 🅑 ")
            one_hour_change = parts[0].split("├ 1H:")[1].strip()
            if len(parts) > 1:
                one_hour_buys = parts[1].split(" Ⓢ ")[0].strip()
                one_hour_sells = parts[1].split(" Ⓢ ")[1].strip()
        elif line.startswith(" └ ATH:"):
            ath = line.split("└ ATH:")[1].strip()
        elif line.startswith(" ├ Freshies:"):
            freshies = line.split("├ Freshies:")[1].strip()
        elif line.startswith(" ├ Top 10:"):
            top_10_holders = line.split("├ Top 10:")[1].strip()
        elif line.startswith(" ├ TH:"):
            holders = line.split("├ TH:")[1].split("|")
            top_holders = [h.strip().split(" ")[0] for h in holders]
        elif line.startswith(" ├ Dev Sold:"):
            dev_sold = line.split("├ Dev Sold:")[1].strip().split(" ")[0]
            dev_sold_id = re.search(r'pfdev_([0-9a-zA-Z]+)', text)
            dev_sold_id = dev_sold_id.group(1) if dev_sold_id else ""
        elif line.startswith(" └ Dex Paid:"):
            dex_paid = line.split("└ Dex Paid:")[1].strip().split(" ")[0]

    # Format the message with manual hyperlinks
    formatted_message = (
        f"🟣 **[{token_name}](https://t.me/phanesgoldbot?start=price_{contract_address})** ({token_ticker})\n"
        f"├ {contract_address}\n"
        f"└ {chain} | {age} | {watchers}\n\n"
        f"📊 **Token Stats**\n"
        f"├ USD: {usd_price} ({price_change})\n"
        f"├ MC: {market_cap}\n"
        f"├ Vol: {volume}\n"
        f"├ LP: {liquidity}\n"
        f"├ Sup: {supply}\n"
        f"├ 1H: {one_hour_change} 🅑 {one_hour_buys} Ⓢ {one_hour_sells}\n"
        f"└ ATH: {ath}\n\n"
        f"🔒 **Security**\n"
        f"├ Freshies: {freshies}\n"
        f"├ Top 10: {top_10_holders}\n"
        f"├ TH: " + " | ".join([f"[{h}](https://solscan.io/account/{h})" for h in top_holders]) + "\n"
        f"├ Dev Sold: {dev_sold} [__stats__](https://t.me/phanes_bot?start=pfdev_{dev_sold_id})\n"
        f"└ Dex Paid: {dex_paid} [__info__](https://t.me/phanesgoldbot?start=dp_{contract_address})"
    )

    # Send the formatted message
    if isinstance(msg.media, MessageMediaWebPage):
        await bot.send_message(
            TARGET_GROUP,
            formatted_message,
            parse_mode="md"
        )
    else:
        await bot.send_message(
            TARGET_GROUP,
            formatted_message,
            file=msg.media,
            parse_mode="md"
        )

async def main():
    if await start_with_retry(bot, BOT_TOKEN):
        await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
