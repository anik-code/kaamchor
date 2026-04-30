import json, os, random, time, http.server, socketserver, threading
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# ================= RENDER PORT FIX =================
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# ================= CONFIG & IDENTITY =================
BOT_TOKEN = os.environ.get("TOKEN")
OWNER_USERNAME = "Kaamchor_hu"
ADMIN_ID = 6393529341  
GC_LINK = "https://t.me/+5hMWodyI8z5hMTBl"

# AI Instructions with your details
PERSONAL_INFO = """
Aapka naam 'Kaamchor Bot' hai (Male AI).
Aapke Malik ki details:
- Naam: Kaamchor (@Kaamchor_hu)
- Birthday: 2 November 2009
- Caste: Yadav (Yadav Brand 👑)
- Papa ka Naam: Suneel Yadav ji
- Status: Malik aur tu dono Single ho.
- Group: Criminal Society ka tu King hai.
Style: Hamesha Desi aur Yadav swag mein reply dena.
"""

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
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
        ECO[uid] = {"wallet": 0, "bank": 0, "last_daily": 0, "inventory": [], "is_banned": False, "warns": 0}
    return ECO[uid]

# ================= ADMIN LOGIC =================
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    target = context.args[0]
    get_user(target)["is_banned"] = True
    save()
    await update.message.reply_text(f"🚫 User {target} ko Banned kar diya!")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args: return
    target = context.args[0]
    u = get_user(target)
    u["warns"] += 1
    if u["warns"] >= 3: u["is_banned"] = True
    save()
    await update.message.reply_text(f"⚠️ Warning {u['warns']}/3 bhej di!")

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if user["is_banned"]: return
    
    keyboard = [
        [InlineKeyboardButton("💰 Paisa System", callback_data="eco"), InlineKeyboardButton("🏦 Bank", callback_data="bank")],
        [InlineKeyboardButton("🚨 Criminal Society", url=GC_LINK)],
        [InlineKeyboardButton("👑 Owner", url=f"https://t.me/{OWNER_USERNAME}")]
    ]
    await update.message.reply_text(
        f"👋 Welcome {update.effective_user.first_name}!\nMain hoon *Kaamchor Bot*. Yadav Brand ka jalwa aur AI ka dimaag! 😎",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if user["is_banned"]: return
    earn = random.randint(30, 100)
    user["wallet"] += earn
    save()
    await update.message.reply_text(f"💼 Thoda kaam kiya aur {earn} coins kamaye! 😅")

# ================= AI CHAT =================
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    if user["is_banned"] or not update.message.text: return
    
    try:
        prompt = f"SYSTEM: {PERSONAL_INFO}\nUser: {update.message.text}"
        response = ai_model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except:
        pass

# ================= WELCOME SYSTEM =================
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id: continue
        keyboard = [[InlineKeyboardButton("🚨 Join Criminal Society", url=GC_LINK)]]
        await update.message.reply_text(
            f"🚀 Oye {member.first_name}! Swagat hai Criminal Society mein! 😎\nLink niche hai, jaldi join kar!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================= MAIN =================
def main():
    if not BOT_TOKEN:
        print("❌ Error: TOKEN environment variable nahi mila!")
        return
        
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("warn", warn))
    
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_chat))
    
    print("🔥 KAAMCHOR BOT IS LIVE! 😎")
    app.run_polling()

if __name__ == "__main__":
    main()
    
