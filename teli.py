import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# CONFIG
# ==============================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Set in Render Dashboard
COOKIES_FILE_PATH = "cookies.txt"  # Must be in the same folder as this script

logging.basicConfig(level=logging.INFO)

# ==============================
# Start Command
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send me an Instagram Reel link, and I'll fetch the download link for you!")

# ==============================
# Handle Instagram Link
# ==============================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram link.")
        return

    await update.message.reply_text("⏳ Downloading your video... please wait.")

    try:
        # Run yt-dlp to get direct download link using cookies.txt
        cmd = [
            "yt-dlp",
            "--cookies", COOKIES_FILE_PATH,
            "-g", url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            logging.error(result.stderr)
            await update.message.reply_text(f"❌ yt-dlp error:\n{result.stderr}")
            return

        direct_link = result.stdout.strip()

        if not direct_link:
            await update.message.reply_text("❌ Could not get download link. Maybe the reel is private or age-restricted.")
            return

        await update.message.reply_text(f"✅ Here’s your download link:\n{direct_link}")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Error: Download process timed out.")

# ==============================
# Main
# ==============================
if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is not set!")
        exit(1)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Bot is running...")
    app.run_polling()





