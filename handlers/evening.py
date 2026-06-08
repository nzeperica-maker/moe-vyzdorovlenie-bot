from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

from services.storage import append_record
from keyboards.navigation import nav_keyboard
from keyboards.main_menu import main_menu_keyboard

evening_states = {}

QUESTIONS = {
    1: "1. Опиши ситуацию, которая сегодня вызвала эмоциональный отклик.",
    2: "2. Какие мысли появились в этой ситуации?",
    3: "3. Что ты чувствовал(а)?",
    4: "4. В чём проявлялся мой эгоизм?",
    5: "5. В чём проявлялась моя корысть?",
    6: "6. В чём проявлялась моя нечестность?",
    7: "7. Чего я боялся(лась)?",
    8: "8. Какой был мой истинный мотив?",
    9: "9. Где моя ответственность в этой ситуации?",
    10: "10. Какие духовные принципы я нарушил(а)?",
    11: "11. Какие духовные принципы помогут мне?",
    12: "12. Какое новое решение необходимо?",
    13: "13. Какое конкретное действие я сделаю?",
    14: "14. Молитва.",
    15: "15. За что ты благодарен(на) сегодня?"
}

ANSWER_KEYS = {
    1: "situation",
    2: "thoughts",
    3: "feelings",
    4: "egoism",
    5: "selfishness",
    6: "dishonesty",
    7: "fear",
    8: "real_motive",
    9: "responsibility",
    10: "broken_principles",
    11: "helpful_principles",
    12: "new_decision",
    13: "action_plan",
    14: "prayer",
    15: "gratitude"
}


async def evening_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    evening_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "🌙 Вечерняя инвентаризация",
        reply_markup=nav_keyboard("evening")
    )

    await update.message.reply_text(QUESTIONS[1])


async def handle_evening_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in evening_states:
        return False

    state = evening_states[user_id]
    step = state["step"]

    state["answers"][ANSWER_KEYS[step]] = update.message.text

    if step < len(QUESTIONS):
        state["step"] += 1

        await update.message.reply_text(
            QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("evening")
        )

    else:
        append_record(
            "data/daily_reviews.json",
            {
                "telegram_id": user_id,
                "created_at": datetime.now().isoformat(),
                **state["answers"]
            }
        )

        await update.message.reply_text(
            "✅ Вечерняя инвентаризация сохранена.",
            reply_markup=main_menu_keyboard()
        )

        del evening_states[user_id]

    return True


async def handle_evening_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in evening_states:
        return

    action = query.data.split(":")[1]

    if action == "cancel":
        del evening_states[user_id]

        await query.edit_message_text(
            "❌ Инвентаризация отменена."
        )

        return

    if action == "back":
        state = evening_states[user_id]

        if state["step"] > 1:
            state["step"] -= 1

        await query.edit_message_text(
            f"⬅️ Возврат к вопросу №{state['step']}"
        )
