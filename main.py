from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)
import os

from handlers.morning import morning_checkin
from handlers.evening import evening_review

TOKEN = os.getenv("Bot_token")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🙏 Добро пожаловать в Моё выздоровление\n\n"
        "Доступные команды:\n\n"
        "/morning - Утренний настрой\n"
        "/evening - Вечерняя инвентаризация"
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("morning", morning_checkin))
    app.add_handler(CommandHandler("evening", evening_review))

    app.run_polling()


if __name__ == "__main__":
    main()
