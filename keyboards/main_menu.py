from telegram import ReplyKeyboardMarkup


def main_menu_keyboard():
    keyboard = [
        ["🌅 Утренний настрой"],
        ["🌙 Вечерняя инвентаризация"],
        ["😨 Инвентаризация страхов"],
        ["💢 Инвентаризация обид"],
        ["📚 Духовные принципы"],
        ["📈 Моё выздоровление"],
    ]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
