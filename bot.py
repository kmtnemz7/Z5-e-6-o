import os, asyncio, re
from telethon import TelegramClient, events, errors

# ── 1.  Settings ──────────────────────────────────────────
api_id     = int(os.getenv("API_ID"))
api_hash   = os.getenv("API_HASH")
BOT_TOKEN  = os.getenv("BOT_TOKEN")

SOURCE_GROUP = "BACKENDZEROPINGxc_vy"    # scraper posts here
TARGET_GROUP = "ZeroPingX"               # bot forwards summary here

# ── 2.  Create bot client *before* decorators ─────────────
bot = TelegramClient("zeroping_bot", api_id, api_hash)

# ── 3.  Helper to parse Bitfoot ping text ─────────────────
def extract_fields(text: str):
    fields = {
        "token":"N/A","name":"N/A","usd":"N/A","mc":"N/A",
        "vol":"N/A","seen":"N/A","dex":"N/A","dex_paid":"N/A",
        "holder":"N/A","th":"N/A"
    }
    for ln in text.splitlines():
        ln = ln.strip()
        if ln.startswith("💊"):           fields["token"] = ln[2:].strip()
        elif ln.startswith("┌"):         fields["name"]  = ln[1:].strip()
        elif ln.startswith("├USD:"):     fields["usd"]   = ln.split("USD:")[1].strip()
        elif ln.startswith("├MC:"):      fields["mc"]    = ln.split("MC:")[1].strip()
        elif ln.startswith("├Vol:"):     fields["vol"]   = ln.split("Vol:")[1].strip()
        elif ln.startswith("├Seen:"):    fields["seen"]  = ln.split("Seen:")[1].strip()
        elif ln.startswith("├Dex:"):     fields["dex"]   = ln.split("Dex:")[1].strip()
        elif ln.startswith("├Dex Paid:"):fields["dex_paid"]=ln.split("Dex Paid:")[1].strip()
        elif ln.startswith("├Holder:"):  fields["holder"]= ln.split("Holder:")[1].strip()
        elif ln.startswith("└TH:"):      fields["th"]    = ln.split("TH:")[1].strip()
    return fields

# ── 4.  Handler (runs after bot exists) ───────────────────
@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay_and_format(event):
    try:
        txt = event.message.raw_text or ""
        if not txt:
            return

        f = extract_fields(txt)
        summary = (
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
            TARGET_GROUP,
            summary,
            link_preview=False
        )

    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await relay_and_format(event)
    except Exception as err:
        print("❌ BOT FORWARD ERROR:", err)

# ── 5.  Start the bot ─────────────────────────────────────
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print(f"Listening in {SOURCE_GROUP} → posting to {TARGET_GROUP}")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
