from telegram import Update
from telegram.ext import ContextTypes

async def morning_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌅 Утренний настрой\n\n"
        "Оцени своё состояние от 1 до 10."
    )
