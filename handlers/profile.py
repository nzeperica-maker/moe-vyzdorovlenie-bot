from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.profile_service import (
    get_user_profile,
    save_user_profile,
    delete_user_profile,
    parse_sobriety_date,
    sobriety_days,
)

profile_states = {}


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current = get_user_profile(user_id)

    if current:
        days = sobriety_days(current.get("sobriety_date"))
        days_text = f"{days}" if days else "не удалось посчитать"

        await update.message.reply_text(
            "👤 Твой профиль\n\n"
            f"Псевдоним: {current.get('nickname')}\n"
            f"Дата трезвости: {current.get('sobriety_date')}\n"
            f"Дней трезвости: {days_text}\n"
            f"Часовой пояс: {current.get('timezone')}\n\n"
            "Чтобы создать профиль заново, используй /reset_profile"
        )
        return

    profile_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "👤 Создание профиля\n\n"
        "1. Как к тебе обращаться?\n\n"
        "Напиши псевдоним."
    )


async def reset_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    delete_user_profile(user_id)

    await update.message.reply_text(
        "Профиль удалён.\n\n"
        "Чтобы создать новый профиль, напиши /profile"
    )


async def handle_profile_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in profile_states:
        return False

    state = profile_states[user_id]
    text = update.message.text.strip()

    if state["step"] == 1:
        state["answers"]["nickname"] = text
        state["step"] = 2

        await update.message.reply_text(
            "2. Укажи дату трезвости.\n\n"
            "Формат: ДД.ММ.ГГГГ\n"
            "Например: 14.03.2024"
        )

    elif state["step"] == 2:
        parsed = parse_sobriety_date(text)

        if not parsed:
            await update.message.reply_text(
                "Не получилось распознать дату.\n\n"
                "Пожалуйста, введи в формате ДД.ММ.ГГГГ.\n"
                "Например: 14.03.2024"
            )
            return True

        state["answers"]["sobriety_date"] = parsed.strftime("%d.%m.%Y")
        state["step"] = 3

        await update.message.reply_text(
            "3. Укажи часовой пояс.\n\n"
            "Например: Europe/Stockholm или Europe/Moscow.\n"
            "Если не знаешь, напиши: Europe/Stockholm"
        )

    elif state["step"] == 3:
        state["answers"]["timezone"] = text

        profile_data = {
            "telegram_id": user_id,
            "nickname": state["answers"]["nickname"],
            "sobriety_date": state["answers"]["sobriety_date"],
            "timezone": state["answers"]["timezone"],
            "created_at": datetime.now().isoformat()
        }

        save_user_profile(profile_data)
        days = sobriety_days(profile_data["sobriety_date"])

        await update.message.reply_text(
            "✅ Профиль сохранён.\n\n"
            f"Псевдоним: {profile_data['nickname']}\n"
            f"Дата трезвости: {profile_data['sobriety_date']}\n"
            f"Сегодня твой {days}-й день трезвости.\n\n"
            "Теперь можешь использовать /morning или /evening."
        )

        del profile_states[user_id]

    return True
