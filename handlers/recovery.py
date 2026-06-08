from telegram import Update
from telegram.ext import ContextTypes
from services.statistics import build_recovery_summary


async def recovery_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = build_recovery_summary(user_id)
    await update.message.reply_text(message)
