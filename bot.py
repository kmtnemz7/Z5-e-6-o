import os
import re
from telethon import TelegramClient, events

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SOURCE_GROUP = os.getenv("BACKEND_GROUP", "zeropingphane")
TARGET_GROUP = os.getenv("FRONTEND_GROUP", "ZeroPingX")

bot = TelegramClient("zeroping_bot", api_id, api_hash).start(bot_token=BOT_TOKEN)

def parse_phanes_message(text):
    if not text:
        return None, []
    # Extract variables with regex
    token_match = re.search(r'\*\*(.*?)\*\* \((.*?)\) \((.*?)\)', text)
    contract_match = re.search(r'├ ([1-9A-HJ-NP-Za-km-z]{42,44})', text)  # Any Solana address
    chain_match = re.search(r'└ #(\w+)', text)
    platform_match = re.search(r'\((Raydium)\)', text)
    age_match = re.search(r'🌱(\d+h)', text)
    views_match = re.search(r'👁️([\d.]+K|\d+)', text)
    usd_match = re.search(r'USD:\s+\$([\d.₄]+)\s*\((.*?)\)', text)
    mc_match = re.search(r'MC:\s+\$(.*?)\n', text)
    vol_match = re.search(r'Vol:\s+\$(.*?)\n', text)
    lp_match = re.search(r'LP:\s+\$(.*?)\n', text)
    supply_match = re.search(r'Sup:\s+([\d.MB/]+)', text)
    one_hour_match = re.search(r'1H:\s+([-+]?[\d.]+)%.*?🅑 (\d+) Ⓢ (\d+)', text)
    ath_match = re.search(r'ATH:\s+\$(.*?)\s*\((.*?)\)', text)
    x_link_match = re.search(r'𝕏 \((.*?)\)', text)
    freshies_match = re.search(r'Freshies:\s+([\d.]+%)\s+1D\s*\|\s*([\d.]+%)\s+7D', text)
    top10_match = re.search(r'Top 10:\s+([\d.]+%)\s*\|\s*(\d+)', text)
    dex_paid_match = re.search(r'Dex Paid:\s+🟢', text)

    # Assign variables
    token_name = token_match.group(1) if token_match else "Unknown"
    ticker = token_match.group(3) if token_match else "Unknown"
    contract = contract_match.group(1) if contract_match else "Unknown"
    chain = chain_match.group(1) if chain_match else "Unknown"
    platform = platform_match.group(1) if platform_match else "Unknown"
    age = age_match.group(1) if age_match else "Unknown"
    views = views_match.group(1) if views_match else "Unknown"
    usd_price = usd_match.group(1) if usd_match else "Unknown"
    price_change = usd_match.group(2) if usd_match else "Unknown"
    mc = mc_match.group(1) if mc_match else "Unknown"
    vol = vol_match.group(1) if vol_match else "Unknown"
    lp = lp_match.group(1) if lp_match else "Unknown"
    supply = supply_match.group(1) if supply_match else "Unknown"
    one_hour = one_hour_match.group(1) if one_hour_match else "Unknown"
    buys = one_hour_match.group(2) if one_hour_match else "Unknown"
    sells = one_hour_match.group(3) if one_hour_match else "Unknown"
    ath = ath_match.group(1) if ath_match else "Unknown"
    x_link = x_link_match.group(1) if x_link_match else ""
    freshies = f"{freshies_match.group(1)} (1D), {freshies_match.group(2)} (7D)" if freshies_match else "Unknown"
    top10 = f"{top10_match.group(1)}, {top10_match.group(2)} holders" if top10_match else "Unknown"
    dex_paid = "✅" if dex_paid_match else "❌"

    # Custom format
    message = (
        f"🌟 **{token_name}** ({ticker}) on {chain} ({platform})\n"
        f"Contract: {contract}\n"
        f"Market Cap: ${mc} | Price: ${usd_price} ({price_change}) | Volume: ${vol}\n"
        f"Liquidity: ${lp} | Supply: {supply} | Age: {age}\n"
        f"1H Change: {one_hour}% ({buys} Buys, {sells} Sells) | ATH: ${ath}\n"
        f"Links: [X]({x_link})\n"
        f"Security: Freshies {freshies}, Top 10 Holders {top10}, Dex Paid {dex_paid}"
    )
    return message, []

@bot.on(events.NewMessage(chats="zeropingphane"))
async def handle(event):
    try:
        msg = event.message
        # Detect Phanes messages
        if msg.text and ("**" in msg.text or "📊 Token Stats" in msg.text):
            custom_message, entities = parse_phanes_message(msg.text)
            await bot.send_message(
                "ZeroPingX",
                custom_message,
                file=msg.media,  # Include image
                parse_mode="md"
            )
        else:
            # Copy other messages as-is
            await bot.send_message(
                "ZeroPingX",
                msg.text or "",
                file=msg.media,
                parse_mode="md"
            )
        print(f"Sent message to ZeroPingX")
    except Exception as e:
        print(f"Error sending to ZeroPingX: {e}")

bot.run_until_disconnected()
