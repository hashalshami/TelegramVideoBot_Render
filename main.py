
import os
import yt_dlp
import logging
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "7987575935:AAEX002b88rCHix2ebprBGg9qlAKJOdRO34"

logging.basicConfig(level=logging.INFO)

async def download_video(url: str):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best[ext=mp4]/best',
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

    await update.message.reply_text("⏳ جاري تحميل الفيديو، انتظر لحظة...")

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
        await update.message.reply_text("❌ حدث خطأ أثناء تحميل الفيديو.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 البوت يعمل الآن...")
    app.run_polling()
