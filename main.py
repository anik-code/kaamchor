import os, json, random, time, threading, http.server, socketserver
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render Port Fix
def run_dummy():
    port = int(os.environ.get("PORT", 10000))
    httpd = socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler)
    print(f"✅ Dummy server running on port {port}")
    httpd.serve_forever()
threading.Thread(target=run_dummy, daemon=True).start()

# Configuration
TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

# Identity
IDENTITY = "Aapka naam Kaamchor Bot hai. Owner @Kaamchor_hu. Yadav Brand. Swag mein bolo."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Yadav Brand Bot Zinda hai! Kuch pucho bhai.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GEMINI_KEY:
        await update.message.reply_text("❌ Render mein 'GEMINI_API_KEY' nahi mil rahi!")
        return
    
    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"{IDENTITY}\nUser: {update.message.text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        # Ye line batayegi ki asal problem kya hai
        error_msg = str(e)
        if "API_KEY_INVALID" in error_msg:
            await update.message.reply_text("❌ Bhai, teri Gemini API Key galat hai. Nayi nikaal kar dalo.")
        elif "User location is not supported" in error_msg:
            await update.message.reply_text("❌ Google AI Studio aapki location support nahi kar raha. VPN try karo key lete waqt.")
        else:
            await update.message.reply_text(f"⚠️ Error: {error_msg}")

if TOKEN:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    print("🚀 Bot Polling Started...")
    app.run_polling()
    
