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
            "Перед началом давай создадим твой профиль.\n\n"
            "Напиши команду /profile"
        )
        return

    days = sobriety_days(profile.get("sobriety_date"))

    days_text = ""
    if days:
        days_text = f"\nСегодня твой {days}-й день трезвости.\n"

    await update.message.reply_text(
        f"🙏 Добро пожаловать, {profile.get('nickname')}.\n"
        f"{days_text}\n"
        "Выбери раздел или используй команду:\n\n"
        "/morning — утренний настрой\n"
        "/evening — вечерняя инвентаризация\n"
        "/fear — инвентаризация страхов\n"
        "/resentment — инвентаризация обид\n"
        "/principles — духовные принципы\n"
        "/recovery — моё выздоровление",
        reply_markup=main_menu_keyboard()
    )
