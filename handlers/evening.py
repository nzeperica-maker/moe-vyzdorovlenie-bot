from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile
from keyboards.navigation import nav_keyboard
from keyboards.main_menu import main_menu_keyboard

evening_states = {}

QUESTIONS = {
    1: '1. Опиши ситуацию, которая сегодня вызвала эмоциональный отклик.',
    2: '2. Какие мысли появились в этой ситуации?',
    3: '3. Что ты чувствовал(а)?',
    4: '4. В чём проявлялся мой эгоизм?\n\nОпиши подробно: чего я хотел(а), что защищал(а), как хотел(а), чтобы всё было по-моему?',
    5: '5. В чём проявлялась моя корысть?\n\nЧто я пытался(лась) получить: одобрение, внимание, контроль, выгоду, безопасность, признание?',
    6: '6. В чём проявлялась моя нечестность?\n\nЧто я не хотел(а) признавать? Где был самообман?',
    7: '7. Чего я боялся(лась)?\n\nЧто я мог(ла) потерять? Что пытался(лась) контролировать?',
    8: '8. Какой был мой истинный мотив?',
    9: '9. Где моя ответственность в этой ситуации?',
    10: '10. Какие духовные принципы я нарушил(а)?',
    11: '11. Какие духовные принципы помогут мне в этой ситуации?',
    12: '12. Какое новое решение необходимо?',
    13: '13. Какое конкретное действие я сделаю?',
    14: '14. Молитва.\n\nПоговори с Богом / Высшей Силой искренне своими словами.',
    15: '15. За что ты благодарен(на) сегодня?\n\nНапиши минимум 3 пункта.',
}

ANSWER_KEYS = {
    1: 'situation',
    2: 'thoughts',
    3: 'feelings',
    4: 'egoism',
    5: 'selfishness',
    6: 'dishonesty',
    7: 'fear',
    8: 'real_motive',
    9: 'responsibility',
    10: 'broken_principles',
    11: 'helpful_principles',
    12: 'new_decision',
    13: 'action_plan',
    14: 'prayer',
    15: 'gratitude',
}


async def evening_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Нажми кнопку «👤 Профиль».",
            reply_markup=main_menu_keyboard()
        )
        return

    evening_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "🌙 Вечерняя инвентаризация"
    )
    await update.message.reply_text(
        QUESTIONS[1],
        reply_markup=nav_keyboard("evening")
    )


async def handle_evening_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in evening_states:
        return False

    state = evening_states[user_id]
    step = state["step"]
    text = update.message.text.strip()

    state["answers"][ANSWER_KEYS[step]] = text

    if step < 15:
        state["step"] = step + 1
        await update.message.reply_text(
            QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("evening")
        )
    else:
        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "evening",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/daily_reviews.json", record)

        await update.message.reply_text(
            "✅ Вечерняя инвентаризация сохранена.

Спасибо за честность сегодня."
        )

        del evening_states[user_id]

    return True


async def handle_evening_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in evening_states:
        await query.edit_message_text("Этот опрос уже не активен.")
        return

    action = query.data.split(":")[1]

    if action == "cancel":
        del evening_states[user_id]
        await query.edit_message_text("❌ Опрос отменён.")
        return

    if action == "back":
        state = evening_states[user_id]
        current_step = state["step"]

        if current_step <= 1:
            await query.edit_message_text(
                "Это первый вопрос. Назад вернуться нельзя.",
                reply_markup=nav_keyboard("evening")
            )
            return

        previous_step = current_step - 1
        key = ANSWER_KEYS.get(previous_step)
        if key in state["answers"]:
            del state["answers"][key]

        state["step"] = previous_step

        await query.edit_message_text(
            "⬅️ Вернулись назад. Напиши ответ заново.\n\n"
            + QUESTIONS[previous_step],
            reply_markup=nav_keyboard("evening")
        )
