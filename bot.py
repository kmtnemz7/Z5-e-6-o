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
@bot.on(events.NewMessage(chats=SOURCE_GROUP))
async def relay_and_format(event):
    try:
        raw = event.message.raw_text or ""
        if not raw:
            return

        f = extract_fields(raw)
for k in f:                          # HTML-escape dynamic text
    f[k] = h(f[k])

msg = (
    # Header (DexScreener link)
    f"💊&nbsp;&nbsp;<b><a href='https://dexscreener.com/solana/{f['token']}'>{f['name']}</a></b>\n"

    # Contract
    f"╰─🧬&nbsp;CA&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;"
    f"<code><a href='https://solscan.io/token/{f['token']}'>{f['token']}</a></code>\n"
    f"&nbsp;&nbsp;&nbsp;│\n"

    # Core stats (one per line, vertically aligned via non-breaking spaces)
    f"&nbsp;&nbsp;&nbsp;💵&nbsp;Price&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;{f['usd']}\n"
    f"&nbsp;&nbsp;&nbsp;📈&nbsp;MC&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;{f['mc']}\n"
    f"&nbsp;&nbsp;&nbsp;💧&nbsp;Volume&nbsp;&nbsp;&nbsp;→&nbsp;{f['vol']}\n"
    f"&nbsp;&nbsp;&nbsp;⏱️&nbsp;&nbsp;Last&nbsp;Seen&nbsp;→&nbsp;{f['seen']}\n"
    f"&nbsp;&nbsp;&nbsp;│\n"

    # Liquidity / holders
    f"&nbsp;&nbsp;&nbsp;⚖️&nbsp;DEX&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;"
    f"<a href='https://raydium.io'>{f['dex']}</a>&nbsp;&nbsp;|&nbsp;Paid&nbsp;{f['dex_paid']}\n"
    f"&nbsp;&nbsp;&nbsp;👥&nbsp;Holders&nbsp;&nbsp;&nbsp;→&nbsp;{f['holder']}\n"
    f"&nbsp;&nbsp;&nbsp;🔝&nbsp;TH&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→&nbsp;{f['th']}\n"

    "────────────────────────────────────────────────────────\n"

    # Brand line & CTA
    "🔬&nbsp;&nbsp;Deep&nbsp;analysis&nbsp;by&nbsp;"
    "<b><a href='https://t.me/ZeroPingX_bot'>ZeroPing</a></b>"
    "&nbsp;—&nbsp;our&nbsp;AI-powered&nbsp;pattern-recognition&nbsp;bot\n"
    "🔼&nbsp;&nbsp;<b><a href='https://axiom.trade/@kmtz'>Quick&nbsp;trade&nbsp;on&nbsp;AXIOM!</a></b>&nbsp;🚀"
)

await bot.send_message(
    TARGET_GROUP,
    msg,
    parse_mode="HTML",
    link_preview=False
)
        )

    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds + 1)
        await relay_and_format(event)      # retry once
    except Exception as err:
        print("❌ BOT FORWARD ERROR:", err)

# ── 6. Run ─────────────────────────────────────
async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print(f"Listening in {SOURCE_GROUP} → posting to {TARGET_GROUP}")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())








