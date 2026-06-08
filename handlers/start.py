from telegram import Update
from telegram.ext import ContextTypes

from keyboards.main_menu import main_menu_keyboard
from services.profile_service import get_user_profile, sobriety_days


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "🙏 Добро пожаловать в «Моё выздоровление»\n\n"
            "Сначала создай профиль.",
            reply_markup=main_menu_keyboard()
        )
        return

    days = sobriety_days(profile.get("sobriety_date"))

    await update.message.reply_text(
        f"🙏 Добро пожаловать, {profile.get('nickname')}.\n\n"
        f"Сегодня твой {days}-й день трезвости.\n\n"
        "Выбери раздел кнопкой ниже:",
        reply_markup=main_menu_keyboard()
    )
