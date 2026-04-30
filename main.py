import json, os, random, time, http.server, socketserver, threading
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# --- RENDER PORT FIX ---
def run_dummy():
    port = int(os.environ.get("PORT", 10000))
    httpd = socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()
threading.Thread(target=run_dummy, daemon=True).start()

# --- CONFIG ---
TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
GC_LINK = "https://t.me/+5hMWodyI8z5hMTBl" # Aapka Group Link

# AI Identity
IDENTITY = """
Aapka naam Kaamchor Bot hai. Malik: @Kaamchor_hu (Yadav Brand).
Details: DOB 2 Nov 2009, Papa: Suneel Yadav .
Style: Hamesha Desi, haryanvi/hindi mix swag mein reply do. 
Tu Criminal Society ka king hai aur ek number ka badmash bot hai.
"""

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

# --- DATA SYSTEM ---
ECO_FILE = "economy.json"
def load_data():
    if os.path.exists(ECO_FILE):
        try:
            with open(ECO_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

ECO = load_data()

def save():
    with open(ECO_FILE, "w") as f: json.dump(ECO, f, indent=4)

def get_user(uid):
    uid = str(uid)
    if uid not in ECO:
        ECO[uid] = {"wallet": 100, "bank": 0, "last_work": 0}
    return ECO[uid]

# --- COMMANDS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Paisa System", callback_data="eco"), InlineKeyboardButton("🏦 Bank", callback_data="bank")],
        [InlineKeyboardButton("🚨 Join Criminal Society", url=GC_LINK)]
    ]
    await update.message.reply_text(
        f"🔥 Oye {update.effective_user.first_name}!\n\nMain hoon **Kaamchor Bot**. !\n\n"
        "👉 `/work` karke paise kamao.\n"
        "👉 `/bal` se apna paisa dekho.\n"
        "👉 Kuch bhi pucho, AI reply dega!",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 **Wallet:** {u['wallet']} coins\n🏦 **Bank:** {u['bank']} coins")

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    now = time.time()
    if now - u["last_work"] < 60:
        await update.message.reply_text("🛑 Itna kaam mat kar thak jayega! 1 minute rukh ja.")
        return
    
    earn = random.randint(50, 200)
    u["wallet"] += earn
    u["last_work"] = now
    save()
    jobs = ["Gadi saaf ki", "Yadav Brand ka parcha banta", "Badmashi ki", "Chai pilayi"]
    await update.message.reply_text(f"✅ Tune **{random.choice(jobs)}** aur tujhe mile {earn} coins! 🔥")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    try:
        amt = int(context.args[0])
        if u["wallet"] >= amt:
            u["wallet"] -= amt
            u["bank"] += amt
            save()
            await update.message.reply_text(f"🏦 {amt} coins Bank mein jama kar diye!")
        else: await update.message.reply_text("❌ Itne paise nahi hain tere paas!")
    except: await update.message.reply_text("👉 `/dep [amount]` likho.")

# --- AI CHAT ---
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    try:
        prompt = f"{IDENTITY}\nUser: {update.message.text}"
        res = model.generate_content(prompt)
        await update.message.reply_text(res.text)
    except: pass

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("bal", balance))
    app.add_handler(CommandHandler("dep", deposit))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_chat))
    
    print("🚀 PRO KAAMCHOR BOT IS LIVE!")
    app.run_polling()

if __name__ == "__main__":
    main()
            
