from telegram import Update
from telegram.ext import ContextTypes

user_states = {}

async def morning_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "🌅 Утренний настрой\n\n"
        "1. Оцени своё состояние от 1 до 10"
    )
