from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import os

from handlers.start import start
from handlers.profile import profile, handle_profile_message, reset_profile
from handlers.morning import morning_checkin, handle_morning_message, handle_morning_callback
from handlers.evening import evening_review, handle_evening_message, handle_evening_callback
from handlers.fears import fear_inventory, handle_fear_message, handle_fear_callback
from handlers.resentments import resentment_inventory, handle_resentment_message, handle_resentment_callback
from handlers.principles import show_principles, handle_principles_callback
from handlers.defects import show_defects, handle_defects_callback
from handlers.recovery import recovery_stats
from handlers.export import export_today
from keyboards.main_menu import main_menu_keyboard


TOKEN = os.getenv("Bot_token")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "👤 Профиль":
        await profile(update, context)
        return

    if text == "🌅 Утренний настрой":
        await morning_checkin(update, context)
        return

    if text == "🌙 Вечерняя инвентаризация":
        await evening_review(update, context)
        return

    if text == "😨 Страхи":
        await fear_inventory(update, context)
        return

    if text == "💢 Обиды":
        await resentment_inventory(update, context)
        return

    if text == "📚 Принципы":
        await show_principles(update, context)
        return

    if text == "🧩 Дефекты":
        await show_defects(update, context)
        return

    if text == "📈 Моё выздоровление":
        await recovery_stats(update, context)
        return

    if text == "📄 Выгрузка дня":
        await export_today(update, context)
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
        "Выбери раздел кнопкой ниже.",
        reply_markup=main_menu_keyboard()
    )


def main():
    if not TOKEN:
        raise RuntimeError("Не найдена переменная окружения Bot_token")

    app = Application.builder().token(TOKEN).build()

    # Команды оставлены как запасной вариант, но основной интерфейс — кнопки.
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CommandHandler("reset_profile", reset_profile))
    app.add_handler(CommandHandler("morning", morning_checkin))
    app.add_handler(CommandHandler("evening", evening_review))
    app.add_handler(CommandHandler("fear", fear_inventory))
    app.add_handler(CommandHandler("resentment", resentment_inventory))
    app.add_handler(CommandHandler("principles", show_principles))
    app.add_handler(CommandHandler("defects", show_defects))
    app.add_handler(CommandHandler("recovery", recovery_stats))
    app.add_handler(CommandHandler("export_today", export_today))

    app.add_handler(CallbackQueryHandler(handle_morning_callback, pattern="^morning:"))
    app.add_handler(CallbackQueryHandler(handle_evening_callback, pattern="^evening:"))
    app.add_handler(CallbackQueryHandler(handle_fear_callback, pattern="^fear:"))
    app.add_handler(CallbackQueryHandler(handle_resentment_callback, pattern="^resentment:"))
    app.add_handler(CallbackQueryHandler(handle_principles_callback, pattern="^principles:"))
    app.add_handler(CallbackQueryHandler(handle_defects_callback, pattern="^defects:"))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
