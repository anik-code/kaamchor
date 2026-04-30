import http.server
import socketserver
import threading
import os

# Render port error fix karne ke liye chhota server
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Dummy server running on port {port}")
        httpd.serve_forever()

# Isse alag se chalne do
threading.Thread(target=run_dummy_server, daemon=True).start()
import json
import os
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ================= CONFIG =================
BOT_TOKEN = os.environ.get("TOKEN")
ECONOMY_FILE = "economy.json"

SHOP_ITEMS = {
    "vip": 500,
    "shield": 300,
    "boost": 200
}

# ================= DATA =================
def load_data():
    if os.path.exists(ECONOMY_FILE):
        with open(ECONOMY_FILE, "r") as f:
            return json.load(f)
    return {}

ECO = load_data()

def save():
    with open(ECONOMY_FILE, "w") as f:
        json.dump(ECO, f, indent=4)

def get_user(uid):
    uid = str(uid)
    if uid not in ECO:
        ECO[uid] = {
            "wallet": 0,
            "bank": 0,
            "last_daily": 0,
            "inventory": []
        }
    return ECO[uid]

# ================= RANK =================
def get_rank(balance):
    if balance >= 2000: return "👑 Boss Kaamchor"
    elif balance >= 1000: return "💎 Ameer"
    elif balance >= 500: return "🔥 Pro"
    elif balance >= 200: return "🙂 Thoda Ameer"
    else: return "🐣 Naya Kaamchor"

# ================= COMMANDS =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Paisa System", callback_data="eco"), InlineKeyboardButton("🏦 Bank", callback_data="bank")],
        [InlineKeyboardButton("🛒 Dukaan", callback_data="shop"), InlineKeyboardButton("🏆 Top Kaamchor", callback_data="lb")]
    ]
    await update.message.reply_text(
        "👋 Welcome to *KAAMCHOR BOT* 😎\nKaam kam, paisa zyada!\nButtons use karo 👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    total = user["wallet"] + user["bank"]
    rank = get_rank(total)

    await update.message.reply_text(
        f"👤 {update.effective_user.first_name}\n"
        f"💰 Wallet: {user['wallet']}\n"
        f"🏦 Bank: {user['bank']}\n"
        f"🎖 Rank: {rank}"
    )

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    now = time.time()

    if now - user["last_daily"] < 86400:
        rem = int(86400 - (now - user["last_daily"]))
        hours = rem // 3600
        
