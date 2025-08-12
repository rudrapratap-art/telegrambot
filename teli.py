import os
import telebot
import yt_dlp
import tempfile
import shutil

# Get Bot Token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables!")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)

# Handle /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hi! Send me an Instagram reel link and I'll download it for you!")

# Handle incoming Instagram URLs
@bot.message_handler(func=lambda message: "instagram.com" in message.text.lower())
def download_instagram(message):
    url = message.text.strip()
    bot.reply_to(message, "⏳ Downloading your video... please wait!")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "video.mp4")

            ydl_opts = {
                'outtmpl': output_file,
                'format': 'best',
                'cookiesfrombrowser': ('chrome',),  # Will only work if cookies are available (Render won't have them for 18+)
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            bot.send_video(message.chat.id, open(output_file, 'rb'))

    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# Run bot
if __name__ == "__main__":
    print("🚀 Bot is running on Render...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)

