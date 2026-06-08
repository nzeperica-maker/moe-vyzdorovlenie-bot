from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile

evening_states = {}


async def evening_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Напиши /profile"
        )
        return

    evening_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        f"🌙 Вечерняя инвентаризация, {profile.get('nickname')}.\n\n"
        "1. Опиши ситуацию, которая сегодня вызвала эмоциональный отклик."
    )


async def handle_evening_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in evening_states:
        return False

    state = evening_states[user_id]
    text = update.message.text.strip()

    if state["step"] == 1:
        state["answers"]["situation"] = text
        state["step"] = 2
        await update.message.reply_text("2. Какие мысли появились в этой ситуации?")

    elif state["step"] == 2:
        state["answers"]["thoughts"] = text
        state["step"] = 3
        await update.message.reply_text("3. Что ты чувствовал(а)?")

    elif state["step"] == 3:
        state["answers"]["feelings"] = text
        state["step"] = 4
        await update.message.reply_text(
            "4. В чём проявлялся мой эгоизм?\n\n"
            "Опиши подробно: чего я хотел(а), что защищал(а), "
            "как хотел(а), чтобы всё было по-моему?"
        )

    elif state["step"] == 4:
        state["answers"]["egoism"] = text
        state["step"] = 5
        await update.message.reply_text(
            "5. В чём проявлялась моя корысть?\n\n"
            "Что я пытался(лась) получить: одобрение, внимание, контроль, "
            "выгоду, безопасность, признание?"
        )

    elif state["step"] == 5:
        state["answers"]["selfishness"] = text
        state["step"] = 6
        await update.message.reply_text(
            "6. В чём проявлялась моя нечестность?\n\n"
            "Что я не хотел(а) признавать? Где был самообман?"
        )

    elif state["step"] == 6:
        state["answers"]["dishonesty"] = text
        state["step"] = 7
        await update.message.reply_text(
            "7. Чего я боялся(лась)?\n\n"
            "Что я мог(ла) потерять? Что пытался(лась) контролировать?"
        )

    elif state["step"] == 7:
        state["answers"]["fear"] = text
        state["step"] = 8
        await update.message.reply_text(
            "8. Какие духовные принципы я использовал(а) "
            "или хочу применить в этой ситуации?\n\n"
            "Подсказка: список принципов можно посмотреть через /principles"
        )

    elif state["step"] == 8:
        state["answers"]["principles"] = text
        state["step"] = 9
        await update.message.reply_text(
            "9. Какое новое решение необходимо в этой ситуации?"
        )

    elif state["step"] == 9:
        state["answers"]["new_decision"] = text
        state["step"] = 10
        await update.message.reply_text(
            "10. Молитва.\n\n"
            "Поговори с Богом / Высшей Силой искренне своими словами."
        )

    elif state["step"] == 10:
        state["answers"]["prayer"] = text
        state["step"] = 11
        await update.message.reply_text(
            "11. За что ты благодарен(на) сегодня?\n\n"
            "Напиши минимум 3 пункта."
        )

    elif state["step"] == 11:
        state["answers"]["gratitude"] = text

        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "evening",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/daily_reviews.json", record)

        await update.message.reply_text(
            "✅ Вечерняя инвентаризация сохранена.\n\n"
            "Спасибо за честность сегодня."
        )

        del evening_states[user_id]

    return True
