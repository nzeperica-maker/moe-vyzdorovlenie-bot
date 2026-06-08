from telegram import ReplyKeyboardMarkup


def main_menu_keyboard():
    keyboard = [
        ["👤 Профиль"],
        ["🌅 Утренний настрой"],
        ["🌙 Вечерняя инвентаризация"],
        ["😨 Страхи", "💢 Обиды"],
        ["📚 Принципы", "🧩 Дефекты"],
        ["📈 Моё выздоровление"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True
    )
