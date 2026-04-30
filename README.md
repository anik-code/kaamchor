# kaamchor
import json
import os
import random
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# ================= CONFIG =================
BOT_TOKEN = "8696804914:AAGV9OYGHfwVfDxgprDL7_cqMmBwhQvsMYo"
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
    elif balance >= 1000: return "💎 Ameer Kaamchor"
    elif balance >= 500: return "🔥 Pro Kaamchor"
    elif balance >= 200: return "🙂 Thoda Kaamchor"
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
        return await update.message.reply_text(f"⏳ Abhi rest karo 😴\n{hours} ghante baad aana")

    user["wallet"] += 100
    user["last_daily"] = now
    save()

    await update.message.reply_text("🎁 Free ka paisa mil gaya! +100 💰")

async def work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)
    earn = random.randint(20, 80)

    user["wallet"] += earn
    save()

    await update.message.reply_text(f"💼 Thoda kaam kiya... {earn} kama liye 😅")

# ================= BANK =================
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if not context.args:
        return await update.message.reply_text("Usage: /deposit amount")

    amount = int(context.args[0])

    if amount <= 0 or amount > user["wallet"]:
        return await update.message.reply_text("❌ Galat amount")

    user["wallet"] -= amount
    user["bank"] += amount
    save()

    await update.message.reply_text(f"🏦 {amount} bank me daal diye")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if not context.args:
        return await update.message.reply_text("Usage: /withdraw amount")

    amount = int(context.args[0])

    if amount <= 0 or amount > user["bank"]:
        return await update.message.reply_text("❌ Galat amount")

    user["bank"] -= amount
    user["wallet"] += amount
    save()

    await update.message.reply_text(f"💰 {amount} nikaal liye")

# ================= PAY =================
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /pay user_id amount")

    sender = get_user(update.effective_user.id)
    receiver_id = context.args[0]
    amount = int(context.args[1])

    if amount <= 0 or amount > sender["wallet"]:
        return await update.message.reply_text("❌ Galat amount")

    receiver = get_user(receiver_id)

    sender["wallet"] -= amount
    receiver["wallet"] += amount
    save()

    await update.message.reply_text(f"💸 {amount} transfer ho gaye!")

# ================= SHOP =================
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update.effective_user.id)

    if not context.args:
        return await update.message.reply_text("Usage: /buy item")

    item = context.args[0].lower()

    if item not in SHOP_ITEMS:
        return await update.message.reply_text("❌ Item nahi mila")

    price = SHOP_ITEMS[item]

    if user["wallet"] < price:
        return await update.message.reply_text("💸 Paise kam hain")

    user["wallet"] -= price
    user["inventory"].append(item)
    save()

    await update.message.reply_text(f"🛒 {item} kharid liya!")

# ================= LEADERBOARD =================
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top = sorted(ECO.items(), key=lambda x: x[1]["wallet"] + x[1]["bank"], reverse=True)

    text = "🏆 Top Kaamchor:\n\n"
    for i, (uid, data) in enumerate(top[:10], start=1):
        text += f"{i}. {uid} → 💰 {data['wallet'] + data['bank']}\n"

    await update.message.reply_text(text)

# ================= BUTTON =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "eco":
        await query.edit_message_text("💰 Commands:\n/balance /daily /work /pay")
    elif query.data == "bank":
        await query.edit_message_text("🏦 Commands:\n/deposit /withdraw")
    elif query.data == "shop":
        text = "🛒 Dukaan:\n"
        for i, p in SHOP_ITEMS.items():
            text += f"{i} → {p}\n"
        await query.edit_message_text(text)
    elif query.data == "lb":
        top = sorted(ECO.items(), key=lambda x: x[1]["wallet"] + x[1]["bank"], reverse=True)
        text = "🏆 Top Kaamchor:\n\n"
        for i, (uid, data) in enumerate(top[:10], start=1):
            text += f"{i}. {uid} → 💰 {data['wallet'] + data['bank']}\n"
        await query.edit_message_text(text)

# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("daily", daily))
    app.add_handler(CommandHandler("work", work))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    app.add_handler(CallbackQueryHandler(button_handler))

    print("🔥 KAAMCHOR BOT ONLINE 😎")
    app.run_polling()

if __name__ == "__main__":
    main()
