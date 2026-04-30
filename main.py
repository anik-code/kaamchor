import json, os, random, time, http.server, socketserver, threading
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# ================= RENDER PORT FIX =================
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# ================= CONFIG & IDENTITY =================
BOT_TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
OWNER_USERNAME = "Kaamchor_hu"
GC_LINK = "https://t.me/+5hMWodyI8z5hMTBl"

PERSONAL_INFO = """
Aapka naam 'Kaamchor Bot' hai (Male AI).
Aapke Malik: Kaamchor (@Kaamchor_hu)
Malik ka Birthday: 2 November 2009
Malik ki Caste: Yadav (Yadav Brand 👑)
Status: Malik aur tu dono Single ho.
Style: Desi aur Yadav swag mein reply dena.
"""

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    ai_model = genai.GenerativeModel('gemini-pro')

ECONOMY_FILE = "economy.json"

# ================= DATA FUNCTIONS =================
def load_data():
    if os.path.exists(ECONOMY_FILE):
        try:
            with open(ECONOMY_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

ECO = load_data()

def save():
    with open(ECONOMY_FILE, "w") as f: json.dump(ECO, f, indent=4)

def get_user(uid):
    uid = str(uid)
    if uid not in ECO:
        ECO[uid] = {"wallet": 100, "bank": 0, "last_work": 0}
    return ECO[uid]

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Paisa System", callback_data="eco"), InlineKeyboardButton("🏦 Bank", callback_data="bank")],
        [InlineKeyboardButton("🚨 Criminal Society", url=GC_LINK)],
        [InlineKeyboardButton("👑 Owner", url=f"https://t.me/{@kaamchor_hu}")]
    ]
    await update.message.reply_text(
        f"👋 Welcome {update.effective_user.first_name}!\nMain hoon *Kaamchor Bot*.  ! 😎\n\nCommands:\n/work - Paise kamao\n/bal - Balance dekho",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    earn = random.randint(50, 150)
    u["wallet"] += earn
    save()
    await update.message.reply_text(f"💼 Tune kaam kiya aur {earn} coins kamaye! 😅")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = get_user(update.effective_user.id)
    await update.message.reply_text(f"💰 Wallet: {u['wallet']}\n🏦 Bank: {u['bank']}")

# ================= AI CHAT =================
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    if not GEMINI_KEY:
        await update.message.reply_text("❌ Render mein GEMINI_API_KEY check karo bhai!")
        return
    try:
        prompt = f"SYSTEM: {PERSONAL_INFO}\nUser: {update.message.text}"
        response = ai_model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except:
        await update.message.reply_text("⚠️ AI thoda bimar hai, key check kar le.")

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("bal", balance))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_chat))
    app.run_polling()

if __name__ == "__main__":
    main()
    
            
