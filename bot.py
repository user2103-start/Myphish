import os
import re
import json
import logging
import asyncio
import tempfile
from pathlib import Path
from typing import Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ParseMode
import instaloader

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID  = 6593129349
DB_FILE   = "users.json"

# ─── Simple JSON database ──────────────────────────────────────────────────────
def load_users() -> dict:
    if not Path(DB_FILE).exists():
        return {}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(data: dict) -> None:
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def register_user(user_id: int, username: Optional[str], full_name: str) -> None:
    data = load_users()
    uid  = str(user_id)
    if uid not in data:
        data[uid] = {
            "username":  username or "",
            "full_name": full_name,
            "user_id":   user_id,
        }
        save_users(data)


def user_count() -> int:
    return len(load_users())


# ─── Instagram URL helpers ─────────────────────────────────────────────────────
REEL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?instagram\.com/(?:reel|reels)/([A-Za-z0-9_\-]+)"
)


def extract_shortcode(url: str) -> Optional[str]:
    m = REEL_PATTERN.search(url)
    return m.group(1) if m else None


def is_reel_url(url: str) -> bool:
    return bool(extract_shortcode(url))


# ─── Download helper ───────────────────────────────────────────────────────────
async def download_reel(shortcode: str, dest_dir: str) -> str:
    """
    Downloads an Instagram reel by shortcode into dest_dir.
    Returns path to the .mp4 file. Raises RuntimeError on failure.
    """
    loop = asyncio.get_event_loop()

    def _do_download() -> str:
        L = instaloader.Instaloader(
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            dirname_pattern=dest_dir,
            filename_pattern="{shortcode}",
            quiet=True,
        )
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        if not post.is_video:
            raise RuntimeError("This post does not contain a video.")
        L.download_post(post, target=dest_dir)

        mp4_files = list(Path(dest_dir).rglob("*.mp4"))
        if not mp4_files:
            raise RuntimeError("Video file not found after download.")
        return str(mp4_files[0])

    try:
        path = await loop.run_in_executor(None, _do_download)
        return path
    except instaloader.exceptions.LoginRequiredException:
        raise RuntimeError(
            "This reel requires login. Please try a public reel."
        )
    except instaloader.exceptions.InstaloaderException as e:
        raise RuntimeError(f"Instaloader error: {e}")


# ─── /start ────────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    register_user(user.id, user.username, user.full_name)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📥 How To Use", callback_data="how_to_use"),
            InlineKeyboardButton("ℹ️ About",       callback_data="about"),
        ]
    ])

    text = (
        "👋 *Welcome to Instagram Reel Downloader Bot*\n\n"
        "Send any Instagram Reel link and I will download the reel video for you instantly\\.\n\n"
        "*Features:*\n"
        "⚡ Fast download\n"
        "📥 HD quality\n"
        "🚀 No watermark"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=keyboard,
    )


# ─── Callback query handler ────────────────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data  = query.data

    # ── User buttons ──────────────────────────────────────────────────────────
    if data == "how_to_use":
        text = (
            "📖 *How To Use*\n\n"
            "1\\. Open Instagram and find a Reel\\.\n"
            "2\\. Tap the *Share* button \\(paper plane icon\\)\\.\n"
            "3\\. Tap *Copy Link*\\.\n"
            "4\\. Paste the link here in this chat\\.\n"
            "5\\. Bot will download and send the video\\! ✅\n\n"
            "_Example link:_\n"
            "`https://www\\.instagram\\.com/reel/ABC123xyz/`"
        )
        back_kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_home")]]
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=back_kb
        )

    elif data == "about":
        text = (
            "ℹ️ *About This Bot*\n\n"
            "This bot lets you download Instagram Reels quickly\\.\n\n"
            "🔹 *Platform:* Instagram Reels only\n"
            "🔹 *Quality:* Best available \\(HD\\)\n"
            "🔹 *Watermark:* None\n"
            "🔹 *Cost:* Free\n\n"
            "Built with ❤️ using python\\-telegram\\-bot \\+ Instaloader\\."
        )
        back_kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_home")]]
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=back_kb
        )

    elif data == "back_home":
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📥 How To Use", callback_data="how_to_use"),
                InlineKeyboardButton("ℹ️ About",       callback_data="about"),
            ]
        ])
        text = (
            "👋 *Welcome to Instagram Reel Downloader Bot*\n\n"
            "Send any Instagram Reel link and I will download the reel video for you instantly\\.\n\n"
            "*Features:*\n"
            "⚡ Fast download\n"
            "📥 HD quality\n"
            "🚀 No watermark"
        )
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=keyboard
        )

    # ── Admin panel buttons ───────────────────────────────────────────────────
    elif data == "admin_stats":
        if query.from_user.id != ADMIN_ID:
            await query.answer("⛔ Unauthorized", show_alert=True)
            return
        count = user_count()
        await query.edit_message_text(
            f"📊 *Bot Statistics*\n\n👥 Total Users: `{count}`",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Back to Panel", callback_data="admin_back")]]
            ),
        )

    elif data == "admin_broadcast_prompt":
        if query.from_user.id != ADMIN_ID:
            await query.answer("⛔ Unauthorized", show_alert=True)
            return
        context.user_data["awaiting_broadcast"] = True
        await query.edit_message_text(
            "📢 *Broadcast Mode*\n\nSend your broadcast message now\\.\nIt will be forwarded to all users\\.",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Cancel", callback_data="admin_back")]]
            ),
        )

    elif data == "admin_back":
        if query.from_user.id != ADMIN_ID:
            await query.answer("⛔ Unauthorized", show_alert=True)
            return
        context.user_data.pop("awaiting_broadcast", None)
        await query.edit_message_text(
            "🛠️ *Admin Panel*\n\nWelcome, Admin\\! Choose an option:",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=admin_keyboard(),
        )

    elif data == "admin_close":
        if query.from_user.id != ADMIN_ID:
            await query.answer("⛔ Unauthorized", show_alert=True)
            return
        await query.delete_message()


# ─── Admin keyboard ────────────────────────────────────────────────────────────
def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Stats",     callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast_prompt"),
        ],
        [InlineKeyboardButton("❌ Close", callback_data="admin_close")],
    ])


# ─── /admin ────────────────────────────────────────────────────────────────────
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    await update.message.reply_text(
        "🛠️ *Admin Panel*\n\nWelcome, Admin\\! Choose an option:",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=admin_keyboard(),
    )


# ─── /stats ────────────────────────────────────────────────────────────────────
async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    count = user_count()
    await update.message.reply_text(
        f"📊 *Bot Statistics*\n\n👥 Total Users: `{count}`",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


# ─── /broadcast ────────────────────────────────────────────────────────────────
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Unauthorized.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /broadcast <your message>\n\nOr use the Admin Panel → 📢 Broadcast"
        )
        return

    text       = " ".join(context.args)
    users      = load_users()
    sent       = 0
    failed     = 0
    status_msg = await update.message.reply_text(
        f"📢 Broadcasting to {len(users)} users…"
    )

    for uid_str in users:
        try:
            await context.bot.send_message(chat_id=int(uid_str), text=text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await status_msg.edit_text(
        f"✅ Broadcast complete\\!\n\n"
        f"✔️ Sent: `{sent}`\n"
        f"❌ Failed: `{failed}`",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


# ─── Message handler ───────────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text.strip()

    # ── Admin broadcast via chat ──────────────────────────────────────────────
    if user.id == ADMIN_ID and context.user_data.get("awaiting_broadcast"):
        context.user_data.pop("awaiting_broadcast", None)
        users  = load_users()
        sent   = 0
        failed = 0
        status = await update.message.reply_text(
            f"📢 Broadcasting to {len(users)} users…"
        )
        for uid_str in users:
            try:
                await context.bot.send_message(chat_id=int(uid_str), text=text)
                sent += 1
            except Exception:
                failed += 1
            await asyncio.sleep(0.05)

        await status.edit_text(
            f"✅ Broadcast complete\\!\n\n"
            f"✔️ Sent: `{sent}`\n"
            f"❌ Failed: `{failed}`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # ── Validate URL ──────────────────────────────────────────────────────────
    if not is_reel_url(text):
        await update.message.reply_text(
            "❌ Please send a valid Instagram Reel link\\.\n\n"
            "Example:\n"
            "`https://www\\.instagram\\.com/reel/ABC123xyz/`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    shortcode = extract_shortcode(text)
    wait_msg  = await update.message.reply_text("⏳ Downloading your reel…")

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            video_path = await download_reel(shortcode, tmp_dir)

            with open(video_path, "rb") as vf:
                await update.message.reply_video(
                    video=vf,
                    caption="✅ Here is your Instagram Reel\\!",
                    parse_mode=ParseMode.MARKDOWN_V2,
                    supports_streaming=True,
                )

        except RuntimeError as e:
            logger.error("Download failed for %s: %s", shortcode, e)
            await update.message.reply_text(
                f"❌ *Download failed*\n\n"
                f"{str(e)}\n\n"
                "Please make sure the Reel is *public* and the link is correct\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except Exception:
            logger.exception("Unexpected error for %s", shortcode)
            await update.message.reply_text(
                "❌ An unexpected error occurred\\. Please try again later\\.",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        finally:
            try:
                await wait_msg.delete()
            except Exception:
                pass


# ─── Error handler ─────────────────────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Update caused error: %s", context.error, exc_info=context.error)


# ─── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError("BOT_TOKEN environment variable is not set.")

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(30)
        .pool_timeout(60)
        .build()
    )

    app.add_handler(CommandHandler("start",     cmd_start))
    app.add_handler(CommandHandler("admin",     cmd_admin))
    app.add_handler(CommandHandler("stats",     cmd_stats))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot started. Polling…")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
