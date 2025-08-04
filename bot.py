from telethon import events, errors
import asyncio, re

SOURCE_GROUP  = "BACKENDZEROPINGxc_vy"   # where scraper forwards raw pings
TARGET_GROUP  = "ZeroPingX"              # final public group or channel

bot = TelegramClient("zeroping_bot", api_id, api_hash)

def extract_fields(text: str):
    """Return dict with all the values we care about."""
    lines   = text.splitlines()
    fields  = {
        "token": "N/A", "name": "N/A", "usd": "N/A", "mc": "N/A",
        "vol": "N/A",  "seen": "N/A", "dex": "N/A", "dex_paid": "N/A",
        "holder": "N/A", "th": "N/A"
    }

    for ln in lines:
        ln = ln.strip()
        if ln.startswith("💊"):
            fields["token"] = ln[2:].strip()
        elif ln.startswith("┌"):
            fields["name"]  = ln[1:].strip()
        elif ln.startswith("├USD:"):
            fields["usd"]   = ln.split("USD:")[1].strip()
        elif ln.startswith("├MC:"):
            fields["mc"]    = ln.split("MC:")[1].strip()
        elif ln.startswith("├Vol:"):
            fields["vol"]   = ln.split("Vol:")[1].strip()
        elif ln.startswith("├Seen:"):
            fields["seen"]  = ln.split("Seen:")[1].strip()
        elif ln.startswith("├Dex:"):
            fields["dex"]   = ln.split("Dex:")[1].strip()
        elif ln.startswith("├Dex Paid:"):
            fields["dex_paid"] = ln.split("Dex Paid:")[1].strip()
        elif ln.startswith("├Holder:"):
            fields["holder"] = ln.split("Holder:")[1].strip()
        elif ln.startswith("└TH:"):
            fields["th"]     = ln.split("TH:")[1].strip()

    return fields


@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay_and_format(event):
    """Read raw ping, format summary, forward to frontend group."""
    try:
        txt = event.message.raw_text or ""

        f = extract_fields(txt)

        formatted = (
            f"{f['name']}\n"
            f"Token: {f['token']}\n"
            f"USD: {f['usd']}\n"
            f"MC: {f['mc']}\n"
            f"Volume: {f['vol']}\n"
            f"Seen: {f['seen']}\n"
            f"Dex: {f['dex']} | Paid: {f['dex_paid']}\n"
            f"Holder: {f['holder']}\n"
            f"Top Holders: {f['th']}"
        )

        await bot.send_message(
            entity=TARGET_GROUP,
            message=formatted,          # plain text; no extra formatting
            link_preview=False
        )

    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await relay_and_format(event)
    except Exception as err:
        print("❌ formatting bot error:", err)

