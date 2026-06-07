from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters

)
import os

from handlers.morning import morning_checkin, user_states
from handlers.evening import evening_review

TOKEN = os.getenv("Bot_token")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 Добро пожаловать в Моё выздоровление\n\n"
        "Доступные команды:\n\n"
        "/morning - Утренний настрой\n"
        "/evening - Вечерняя инвентаризация"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_states:
        return

    state = user_states[user_id]
    text = update.message.text

    if state["step"] == 1:
        state["answers"]["score"] = text
        state["step"] = 2

        await update.message.reply_text(
            "2. Какое у тебя сейчас настроение?"
        )

    elif state["step"] == 2:
        state["answers"]["mood"] = text
        state["step"] = 3

        await update.message.reply_text(
            "3. Есть ли сегодня тяга?\n"
            "(нет / слабая / сильная)"
        )

    elif state["step"] == 3:
        state["answers"]["craving"] = text
        state["step"] = 4

        await update.message.reply_text(
            "4. Что поможет тебе сохранить трезвость сегодня?"
        )

    elif state["step"] == 4:
        state["answers"]["plan"] = text

        await update.message.reply_text(
            "✅ Утренний настрой завершён!"
        )

        del user_states[user_id]
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("morning", morning_checkin))
    app.add_handler(CommandHandler("evening", evening_review))
app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)
    app.run_polling()


if __name__ == "__main__":
    main()


from telegram.ext import MessageHandler, filters
