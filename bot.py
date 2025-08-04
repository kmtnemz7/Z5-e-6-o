import os, asyncio, re
from telethon import TelegramClient, events, errors

# ── 1. Settings ────────────────────────────────
api_id     = int(os.getenv("API_ID"))
api_hash   = os.getenv("API_HASH")
BOT_TOKEN  = os.getenv("BOT_TOKEN")

SOURCE_GROUP = "BACKENDZEROPINGxc_vy"
TARGET_GROUP = "ZeroPingX"

# ── 2. Bot client (must be before decorators) ──
bot = TelegramClient("zeroping_bot", api_id, api_hash)

# ── 3. Markdown-V2 escape helper ───────────────
def mdv2_escape(t: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+=|{}.!\\\-])', r'\\\1', str(t))

# ── 4. Parse Bitfoot ping text ─────────────────
def extract_fields(text: str):
    f = {
        "token":"N/A","name":"N/A","usd":"N/A","mc":"N/A",
        "vol":"N/A","seen":"N/A","dex":"N/A","dex_paid":"N/A",
        "holder":"N/A","th":"N/A"
    }
    for ln in text.splitlines():
        ln = ln.strip()
        if ln.startswith("💊"):            f["token"]     = ln[2:].strip()
        elif ln.startswith("┌"):          f["name"]      = ln[1:].strip()
        elif ln.startswith("├USD:"):      f["usd"]       = ln.split("USD:")[1].strip()
        elif ln.startswith("├MC:"):       f["mc"]        = ln.split("MC:")[1].strip()
        elif ln.startswith("├Vol:"):      f["vol"]       = ln.split("Vol:")[1].strip()
        elif ln.startswith("├Seen:"):     f["seen"]      = ln.split("Seen:")[1].strip()
        elif ln.startswith("├Dex:"):      f["dex"]       = ln.split("Dex:")[1].strip()
        elif ln.startswith("├Dex Paid:"): f["dex_paid"]  = ln.split("Dex Paid:")[1].strip()
        elif ln.startswith("├Holder:"):   f["holder"]    = ln.split("Holder:")[1].strip()
        elif ln.startswith("└TH:"):       f["th"]        = ln.split("TH:")[1].strip()
    return f

# ── 5. Handler ────────────────────────────────
@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay_and_format(event):
    try:
        raw = event.message.raw_text or ""
        if not raw:
            return

        f = extract_fields(raw)

        # escape every dynamic value for MarkdownV2
        for k in f:
            f[k] = mdv2_escape(f[k])

        # hyperlinked, bold, emoji-rich summary
        msg = (
            f"💊 *[{f['name']}](https://dexscreener.com/solana/{f['token']})*\n"
            f"📬 CA: [`{f['token']}`](https://solscan.io/token/{f['token']})\n\n"
            f"💵 *Price:* {f['usd']}\n"
            f"📈 *MC:* {f['mc']}\n"
            f"💧 *Vol:* {f['vol']}\n"
            f"⏱️ *Seen:* {f['seen']}\n\n"
            f"⚖️ *DEX:* [{f['dex']}](https://raydium.io) | Paid: {f['dex_paid']}\n"
            f"👥 *Holder:* {f['holder']}\n"
            f"🔝 *Top Holders:* {f['th']}\n\n"
            f"*[🔼 Quick trade on AXIOM\\!](https://axiom.trade/@kmtz)*"
        )

        await bot.send_message(
            TARGET_GROUP,
            msg,
            parse_mode="MarkdownV2",
            link_preview=False
        )

    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await relay_and_format(event)
    except Exception as err:
        print("❌ BOT FORWARD ERROR:", err)

# ── 6. Run ─────────────────────────────────────
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print(f"Listening in {SOURCE_GROUP} → posting to {TARGET_GROUP}")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

