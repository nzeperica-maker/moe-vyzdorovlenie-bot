from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def nav_keyboard(prefix):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ Назад", callback_data=f"{prefix}:back"),
            InlineKeyboardButton("❌ Отменить", callback_data=f"{prefix}:cancel"),
        ]
    ])
