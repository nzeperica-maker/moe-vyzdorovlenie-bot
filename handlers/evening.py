from telegram import Update
from telegram.ext import ContextTypes


async def evening_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Вечерняя инвентаризация\n\n"
        "Опиши ситуацию, которая вызвала эмоциональный отклик сегодня."
    )
