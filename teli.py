import os
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8005176399:AAFrGl9EMzOlh7xblow0vfiNb_aALl35gtw"  # Replace with your bot token
COOKIES_FILE = "cookies.txt"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send me an Instagram reel link and I’ll get you the download link.")

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "instagram.com" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram link.")
        return

    await update.message.reply_text("⏳ Fetching download link... please wait.")

    try:
        # Run yt-dlp to get direct video link
        cmd = [
            "yt-dlp",
            "--cookies", COOKIES_FILE,
            "-g",  # Get direct link
            "-f", "mp4",
            url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            download_link = result.stdout.strip()
            await update.message.reply_text(f"✅ Download Link:\n{download_link}")
        else:
            await update.message.reply_text(f"❌ yt-dlp error:\n{result.stderr}")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Error: Timed out while fetching the link.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))

    print("🚀 Bot is running...")
    app.run_polling()




