import os
import asyncio
import re
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaWebPage

# Environment variables
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphane")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

# Initialize the bot
bot = TelegramClient("zeroping_bot", api_id, api_hash)

# Function to parse Phanes message
def parse_phanes_message(text):
    lines = text.splitlines()
    header_lines = []
    stats_lines = []
    security_lines = []
    in_stats = False
    in_security = False

    # Split message into sections
    for line in lines:
        if line.startswith("🟣"):
            header_lines.append(line)
        elif "📊 Token Stats" in line:
            in_stats = True
            in_security = False
        elif "🔒 Security" in line:
            in_stats = False
            in_security = True
        elif in_stats and line.strip():
            stats_lines.append(line)
        elif in_security and line.strip():
            security_lines.append(line)

    # Initialize variables with defaults
    token_name = ""
    token_ticker = ""
    contract_address = ""
    chain = ""
    age = ""
    watchers = ""

    # Parse header section
    if header_lines:
        header_line = header_lines[0]
        match = re.match(r'🟣 \*\*(.*?)\*\*.*?\((.*?)\)', header_line)
        if match:
            token_name = match.group(1)
            token_ticker = match.group(2)
        if len(header_lines) > 1:
            contract_line = header_lines[1]
            contract_address = contract_line.split("├ ")[1].strip()
        if len(header_lines) > 2:
            info_line = header_lines[2]
            parts = info_line.split(" | ")
            chain = parts[0].split("└ ")[1].strip()
            age = parts[1].strip()
            watchers = parts[2].strip()

    # Parse stats section
    stats = {}
    for line in stats_lines:
        if line.startswith(" ├ ") or line.startswith(" └ "):
            parts = line.split(": ", 1)
            if len(parts) == 2:
                key = parts[0].strip()[2:].strip()
                value = parts[1].strip()
                stats[key] = value

    # Extract specific stats
    usd_price = ""
    price_change = ""
    if "USD" in stats:
        usd_part = stats["USD"]
        if "(" in usd_part:
            usd_price, price_change = usd_part.split(" (")
            price_change = price_change.rstrip(")")
        else:
            usd_price = usd_part

    market_cap = stats.get("MC", "")
    volume = stats.get("Vol", "")
    liquidity = stats.get("LP", "")
    supply = stats.get("Sup", "")
    one_hour_change = ""
    one_hour_buys = ""
    one_hour_sells = ""
    if "1H" in stats:
        one_hour = stats["1H"]
        parts = one_hour.split(" 🅑 ")
        if len(parts) > 1:
            one_hour_change = parts[0].strip()
            buys_sells = parts[1].split(" Ⓢ ")
            if len(buys_sells) > 1:
                one_hour_buys = buys_sells[0].strip()
                one_hour_sells = buys_sells[1].strip()
    ath = stats.get("ATH", "")

    # Parse security section
    security = {}
    for line in security_lines:
        if line.startswith(" ├ ") or line.startswith(" └ "):
            parts = line.split(": ", 1)
            if len(parts) == 2:
                key = parts[0].strip()[2:].strip()
                value = parts[1].strip()
                security[key] = value

    freshies = security.get("Freshies", "")
    top_10_holders = security.get("Top 10", "")
    th_line = security.get("TH", "")
    dev_sold = security.get("Dev Sold", "").split(" ")[0] if "Dev Sold" in security else ""
    dex_paid = security.get("Dex Paid", "").split(" ")[0] if "Dex Paid" in security else ""

    # Extract top holders
    top_holders = []
    if th_line:
        holders = th_line.split("|")
        for holder in holders:
            match = re.match(r'(\d+\.\d+)\s*\((https://solscan.io/account/[a-zA-Z0-9]+)\)', holder.strip())
            if match:
                percentage = match.group(1)
                address = match.group(2).split("/")[-1]
                top_holders.append((percentage, address))

    # Extract dev_sold_id
    dev_sold_id = ""
    id_match = re.search(r'pfdev_([0-9a-zA-Z]+)', text)
    if id_match:
        dev_sold_id = id_match.group(1)

    # Build the formatted message with hyperlinks
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
        f"├ TH: " + " | ".join([f"[{p}](https://solscan.io/account/{a})" for p, a in top_holders]) + "\n"
        f"├ Dev Sold: {dev_sold} [__stats__](https://t.me/phanes_bot?start=pfdev_{dev_sold_id})\n"
        f"└ Dex Paid: {dex_paid} [__info__](https://t.me/phanesgoldbot?start=dp_{contract_address})"
    )

    return formatted_message

# Event handler
@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def handle(event):
    msg = event.message
    text = msg.text or ""
    formatted_message = parse_phanes_message(text)
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

# Main function
async def main():
    if await start_with_retry(bot, BOT_TOKEN):
        await bot.run_until_disconnected()

# Helper function for bot startup
async def start_with_retry(client, bot_token, retries=3, base_delay=60):
    for attempt in range(retries):
        try:
            await client.start(bot_token=bot_token)
            return True
        except Exception:
            if attempt < retries - 1:
                await asyncio.sleep(base_delay)
    return False

if __name__ == "__main__":
    asyncio.run(main())
