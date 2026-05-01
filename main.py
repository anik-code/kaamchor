import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.constants import ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================

BOT_TOKEN = "8644388934:AAG2zsGF8CEmUhMFuqW_CQC68ZxDY75k3qw"
OWNER_USERNAME = "@kaamchor_hu"

RULES_TEXT = """
🤖 Group Rules

1. No Spam:
No flood, repetitive stickers, or link-scams.

2. Respect:
No insults, racism, or harassment.

3. No Ads:
No self-promo or referral links without permission.

4. No NSFW:
Keep the content clean and professional.

5. No DMs:
Don't message members privately without asking.
"""

BAD_WORDS = ["badword", "spamword1", "spamword2"]

WARN_LIMIT = 3
WARNS = {}

# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================= COMMANDS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello!\n"
        "I am Combo Group Bot.\n"
        "Use /help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/help\n"
        "/rules\n"
        "/owner\n"
        "/ping\n"
        "/warn (reply)\n"
        "/mute (reply)\n"
        "/unmute (reply)\n"
        "/ban (reply)\n"
        "/unban user_id"
    )

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RULES_TEXT)

async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👑 Owner: {@Kaamchor_hu}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏓 Pong! Bot Online")

# ================= BUTTONS =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "rules":
        await query.message.reply_text(RULES_TEXT)

# ================= WELCOME IMAGE =================

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member

    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    if old_status in ["left", "kicked"] and new_status in ["member", "administrator"]:
        user = result.new_chat_member.user

        keyboard = [
            [
                InlineKeyboardButton("👑 Owner", url="https://t.me/kaamchor_hu"),
                InlineKeyboardButton("📜 Rules", callback_data="rules")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            with open("welcome.jpg", "rb") as photo:
                msg = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=photo,
                    caption=f"🎉 Welcome {user.mention_html()}\n\nFollow rules and enjoy.\nOwner: {OWNER_USERNAME}",
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
        except:
            msg = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🎉 Welcome {user.mention_html()}\nOwner: {OWNER_USERNAME}",
                parse_mode="HTML",
                reply_markup=reply_markup
            )

        await asyncio.sleep(60)

        try:
            await context.bot.delete_message(
                chat_id=update.effective_chat.id,
                message_id=msg.message_id
            )
        except:
            pass

# ================= FILTERS =================

async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    for word in BAD_WORDS:
        if word in text:
            try:
                await update.message.delete()
                await update.effective_chat.send_message("⚠️ Bad words not allowed.")
            except:
                pass
            return

    if "http://" in text or "https://" in text or "t.me/" in text:
        try:
            await update.message.delete()
            await update.effective_chat.send_message("🚫 Links are not allowed.")
        except:
            pass

# ================= WARN SYSTEM =================

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply user's message with /warn")
        return

    user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    user_id = user.id

    if chat_id not in WARNS:
        WARNS[chat_id] = {}

    if user_id not in WARNS[chat_id]:
        WARNS[chat_id][user_id] = 0

    WARNS[chat_id][user_id] += 1
    count = WARNS[chat_id][user_id]

    if count >= WARN_LIMIT:
        try:
            await context.bot.ban_chat_member(chat_id, user_id)
            await update.message.reply_text(
                f"🚫 {user.mention_html()} banned after {WARN_LIMIT} warns.",
                parse_mode="HTML"
            )
            WARNS[chat_id][user_id] = 0
        except:
            await update.message.reply_text("Need admin permission.")
    else:
        await update.message.reply_text(
            f"⚠️ {user.mention_html()} warned ({count}/{WARN_LIMIT})",
            parse_mode="HTML"
        )

# ================= MUTE =================

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply user with /mute")
        return

    user = update.message.reply_to_message.from_user

    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )

        await update.message.reply_text(
            f"🔇 {user.mention_html()} muted.",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text("Need admin permission.")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply user with /unmute")
        return

    user = update.message.reply_to_message.from_user

    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )

        await update.message.reply_text(
            f"🔊 {user.mention_html()} unmuted.",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text("Need admin permission.")

# ================= BAN =================

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply user with /ban")
        return

    user = update.message.reply_to_message.from_user

    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user.id)
        await update.message.reply_text(
            f"🚫 {user.mention_html()} banned.",
            parse_mode="HTML"
        )
    except:
        await update.message.reply_text("Need admin permission.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use /unban user_id")
        return

    try:
        user_id = int(context.args[0])
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ User unbanned.")
    except:
        await update.message.reply_text("Invalid user id.")

# ================= BASIC AI =================

async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    if update.effective_chat.type != "private":
        return

    text = update.message.text.lower()

    if "hello" in text:
        await update.message.reply_text("Hello 👋")
    elif "how are you" in text:
        await update.message.reply_text("I'm fine 🤖")
    else:
        await update.message.reply_text("AI mode placeholder 🤖")

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules))
    app.add_handler(CommandHandler("owner", owner))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))

    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderate), group=0)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat), group=1)

    print("Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
