import os
import tempfile
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token from environment
IG_COOKIES = os.getenv("IG_COOKIES")  # Instagram cookies.txt content from environment

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment variables")
if not IG_COOKIES:
    raise ValueError("❌ IG_COOKIES is not set in environment variables")

# Save cookies to a temporary file
def save_cookies():
    cookies_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    cookies_file.write(IG_COOKIES.encode())
    cookies_file.close()
    return cookies_file.name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send me any Instagram Reel link and I'll give you a direct download link.")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "instagram.com/reel" not in url:
        await update.message.reply_text("❌ Please send a valid Instagram Reel link.")
        return

    await update.message.reply_text("⏳ Downloading your reel... please wait.")

    cookies_path = save_cookies()
    try:
        # Run yt-dlp to get direct link (no full file download)
        result = subprocess.run(
            ["yt-dlp", "--cookies", cookies_path, "-g", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60
        )

        if result.returncode == 0 and result.stdout.strip():
            download_url = result.stdout.strip().split("\n")[0]
            await update.message.reply_text(f"✅ Here is your download link:\n{download_url}")
        else:
            await update.message.reply_text("❌ Failed to fetch reel. It may be private or restricted.")
    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Timed out while processing the reel.")
    finally:
        os.remove(cookies_path)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()




