
import os
import yt_dlp
import logging
from flask import Flask, request
from telegram import Update, InputFile, Bot
from telegram.ext import Application, MessageHandler, ContextTypes, filters
from telegram.ext import Dispatcher

BOT_TOKEN = "7987575935:AAEX002b88rCHix2ebprBGg9qlAKJOdRO34"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-service.onrender.com")

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()
dispatcher = application.dispatcher

async def download_video(url: str):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'writethumbnail': True,
        'writeinfojson': True,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        ext = filename.split('.')[-1]
        video_file = f"video.{ext}"
        title = info.get('title', 'No title')
        thumbnail = info.get('thumbnail')

    return video_file, title, thumbnail

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    await context.bot.send_message(chat_id, "⏳ جاري تحميل الفيديو، انتظر لحظة...")

    try:
        video_file, title, thumb_url = await download_video(url)

        caption = f"🎬 {title}\n🔗 {url}"

        await context.bot.send_video(
            chat_id=chat_id,
            video=InputFile(video_file),
            caption=caption
        )

        os.remove(video_file)

    except Exception as e:
        logging.error(f"خطأ: {e}")
        await context.bot.send_message(chat_id, "❌ حدث خطأ أثناء تحميل الفيديو.")

dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "🤖 Telegram Webhook Bot is running!"

if __name__ == "__main__":
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
