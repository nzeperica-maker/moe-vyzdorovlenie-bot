from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import os

from handlers.start import start
from handlers.profile import profile, handle_profile_message, reset_profile
from handlers.morning import morning_checkin, handle_morning_message
from handlers.evening import evening_review, handle_evening_message
from handlers.fears import fear_inventory, handle_fear_message
from handlers.resentments import resentment_inventory, handle_resentment_message
from handlers.principles import show_principles
from handlers.recovery import recovery_stats


TOKEN = os.getenv("Bot_token")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌅 Утренний настрой":
        await morning_checkin(update, context)
        return

    if text == "🌙 Вечерняя инвентаризация":
        await evening_review(update, context)
        return

    if text == "😨 Инвентаризация страхов":
        await fear_inventory(update, context)
        return

    if text == "💢 Инвентаризация обид":
        await resentment_inventory(update, context)
        return

    if text == "📚 Духовные принципы":
        await show_principles(update, context)
        return

    if text == "📈 Моё выздоровление":
        await recovery_stats(update, context)
        return

    if await handle_profile_message(update, context):
        return

    if await handle_morning_message(update, context):
        return

    if await handle_evening_message(update, context):
        return

    if await handle_fear_message(update, context):
        return

    if await handle_resentment_message(update, context):
        return

    await update.message.reply_text(
        "Я пока не понял(а) сообщение.\n\n"
        "Используй команды:\n"
        "/start — главное меню\n"
        "/profile — мой профиль\n"
        "/morning — утренний настрой\n"
        "/evening — вечерняя инвентаризация\n"
        "/fear — инвентаризация страхов\n"
        "/resentment — инвентаризация обид\n"
        "/principles — духовные принципы\n"
        "/recovery — моё выздоровление"
    )


def main():
    if not TOKEN:
        raise RuntimeError("Не найдена переменная окружения Bot_token")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("reset_profile", reset_profile))
    app.add_handler(CommandHandler("morning", morning_checkin))
    app.add_handler(CommandHandler("evening", evening_review))
    app.add_handler(CommandHandler("fear", fear_inventory))
    app.add_handler(CommandHandler("resentment", resentment_inventory))
    app.add_handler(CommandHandler("principles", show_principles))
    app.add_handler(CommandHandler("recovery", recovery_stats))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
