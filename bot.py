import os, asyncio, re
from telethon import TelegramClient, events, errors
from html import escape as h

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
from html import escape as h  # std-lib

@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay_and_format(event):
    try:
        raw = event.message.raw_text or ""
        if not raw:
            return

        f = extract_fields(raw)          # dict of values

        # HTML-escape dynamic fields
        for k in f:
            f[k] = h(f[k])

        msg = (
    f"💊 <b><a href='https://dexscreener.com/solana/{f['token']}'>{f['name']}</a></b>     🔽\n"
    f"└ CA: <code><a href='https://solscan.io/token/{f['token']}'>{f['token']}</a></code>\n\n"

    # ── vertically aligned stats block ────────────
    f""
    f"💵 Price: {f['usd']}\n"
    f"📈 MC: {f['mc']}\n"
    f"💧 Vol: {f['vol']}\n"
    f"⏱️ Seen: {f['seen']}"
    f"\n  |\n"
    # ──────────────────────────────────────────────

    f"⚖️ <b>DEX:</b> <a href='https://raydium.io'>{f['dex']}</a> | Paid: {f['dex_paid']}\n"
    f"👥 <b>Holder:</b> {f['holder']}\n"
    f"🔝 <b>TH:</b> {f['th']}\n\n"
    f"🔬 Deep analysis by <a href='https://t.me/ZeroPingX_bot'>ZeroPing</a> — our AI powered pattern recognition bot.\n\n"
    f"<b><a href='https://axiom.trade/@kmtz'>🔼 Quick trade on AXIOM!</a></b>"
)
        await bot.send_message(
            TARGET_GROUP,
            msg,
            parse_mode="HTML",
            link_preview=False
        )

    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await relay_and_format(event)   # retry
    except Exception as err:
        print("❌ BOT FORWARD ERROR:", err)


# ── 6. Run ─────────────────────────────────────
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print(f"Listening in {SOURCE_GROUP} → posting to {TARGET_GROUP}")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())













