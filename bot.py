import os
import re
import json
import instaloader
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6593129349
DB_FILE = "users.json"

L = instaloader.Instaloader(dirname_pattern="downloads")

# ---------------- USER DATABASE ---------------- #

def load_users():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f)

def add_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        save_users(users)

# ---------------- START COMMAND ---------------- #

def start(update: Update, context: CallbackContext):

    user_id = update.effective_user.id
    add_user(user_id)

    text = """
👋 *Welcome to Instagram Reel Downloader Bot*

Send any Instagram Reel link and I will download it instantly.

*Features*
⚡ Fast download
📥 HD quality
🚀 No watermark
"""

    buttons = [
        [InlineKeyboardButton("📥 How To Use", callback_data="help")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]

    update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- BUTTON HANDLER ---------------- #

def button(update: Update, context: CallbackContext):

    query = update.callback_query
    query.answer()

    if query.data == "help":
        query.edit_message_text(
            "📥 *How to Use*\n\nSend any Instagram Reel link.\nThe bot will download and send the video.",
            parse_mode="Markdown"
        )

    elif query.data == "about":
        query.edit_message_text(
            "ℹ️ Instagram Reel Downloader Bot\nFast and simple reel downloader.",
            parse_mode="Markdown"
        )

    elif query.data == "stats":
        users = load_users()
        query.edit_message_text(f"📊 Total Users: {len(users)}")

# ---------------- REEL DOWNLOAD ---------------- #

def download_reel(update: Update, context: CallbackContext):

    text = update.message.text

    if "instagram.com" not in text or "/reel/" not in text:
        update.message.reply_text("❌ Please send a valid Instagram Reel link.")
        return

    msg = update.message.reply_text("⏳ Downloading your reel...")

    try:
        shortcode = re.search(r"reel\/([^\/]+)", text).group(1)

        post = instaloader.Post.from_shortcode(L.context, shortcode)

        L.download_post(post, target="downloads")

        for file in os.listdir("downloads"):
            if file.endswith(".mp4"):
                path = f"downloads/{file}"

                update.message.reply_video(open(path, "rb"))

                os.remove(path)

        msg.delete()

    except Exception as e:
        msg.edit_text("❌ Failed to download reel.")

# ---------------- ADMIN PANEL ---------------- #

def admin(update: Update, context: CallbackContext):

    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not authorized.")
        return

    buttons = [
        [InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]

    update.message.reply_text(
        "👑 *Admin Panel*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- STATS ---------------- #

def stats(update: Update, context: CallbackContext):

    if update.effective_user.id != ADMIN_ID:
        return

    users = load_users()

    update.message.reply_text(f"📊 Total Users: {len(users)}")

# ---------------- BROADCAST ---------------- #

def broadcast(update: Update, context: CallbackContext):

    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        update.message.reply_text("Usage:\n/broadcast message")
        return

    message = " ".join(context.args)

    users = load_users()

    sent = 0

    for user in users:
        try:
            context.bot.send_message(chat_id=user, text=message)
            sent += 1
        except:
            pass

    update.message.reply_text(f"✅ Broadcast sent to {sent} users.")

# ---------------- MAIN ---------------- #

def main():

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin))
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("broadcast", broadcast))

    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_reel))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
