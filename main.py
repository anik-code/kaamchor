import os, threading, http.server, socketserver, json
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- RENDER PORT FIX ---
def run_dummy():
    port = int(os.environ.get("PORT", 10000))
    httpd = socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler)
    httpd.serve_forever()
threading.Thread(target=run_dummy, daemon=True).start()

# --- CONFIG ---
# Yahan check karo: Render settings mein name 'TOKEN' aur 'GEMINI_API_KEY' hi hona chahiye
BOT_TOKEN = os.environ.get("TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Oye! Kaamchor Bot zinda ho gaya! 😎\nBatao Yadav Brand ke liye kya seva karein?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    
    # Agar AI Key sahi hai toh AI reply dega
    if GEMINI_KEY:
        try:
            prompt = f"Reply like Kaamchor Bot (Owner @Kaamchor_hu, Yadav Brand): {update.message.text}"
            res = model.generate_content(prompt)
            await update.message.reply_text(res.text)
        except Exception as e:
            await update.message.reply_text(f"❌ AI Error: API Key check karo bhai!")
    else:
        await update.message.reply_text("⚠️ API Key nahi mili! Render Settings check karo.")

# --- MAIN ---
def main():
    if not BOT_TOKEN:
        print("❌ Error: TOKEN variable nahi mila!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    print("🚀 BOT IS RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
    0
