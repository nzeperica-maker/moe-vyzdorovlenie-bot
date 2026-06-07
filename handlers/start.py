from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🌅 Утренний настрой"],
        ["🌙 Вечерняя инвентаризация"],
        ["😨 Инвентаризация страхов"],
        ["💢 Инвентаризация обид"],
        ["📚 Духовные принципы"],
        ["📈 Моё выздоровление"],
        ["📊 Карточка духовного роста"],
        ["⚙️ Настройки"]
    ]

    await update.message.reply_text(
        "Добро пожаловать в Моё Выздоровление 🙏",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )
