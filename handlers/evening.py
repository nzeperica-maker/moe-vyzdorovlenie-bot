from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime

from services.storage import append_record
from keyboards.navigation import nav_keyboard
from keyboards.main_menu import main_menu_keyboard

evening_states = {}

PRINCIPLES = [
    "Честность",
    "Смирение",
    "Любовь",
    "Терпимость",
    "Благодарность",
    "Принятие",
    "Прощение",
    "Служение",
    "Готовность",
    "Осознанность",
    "Ответственность",
    "Терпение",
    "Искренность",
    "Сострадание",
    "Не спорить",
    "Ничего не ожидать",
    "Живи и давай жить другим",
    "Подметать свою сторону улицы",
    "Доверие Богу / ВС",
    "Делай, что должен и будь что будет",
]

QUESTIONS = {
    1: "1. Опиши ситуацию, которая сегодня вызвала эмоциональный отклик.",
    2: "2. Какие мысли появились в этой ситуации?",
    3: "3. Что ты чувствовал(а)?",
    4: "4. В чём проявлялся мой эгоизм?\n\nОпиши подробно, не односложно.",
    5: "5. В чём проявлялась моя корысть?\n\nЧто я пытался(лась) получить?",
    6: "6. В чём проявлялась моя нечестность?\n\nГде был самообман или недоговорённость?",
    7: "7. Чего я боялся(лась)?\n\nЧто я мог(ла) потерять?",
    8: "8. Какой был мой истинный мотив?",
    9: "9. Где моя ответственность в этой ситуации?",
    10: "10. Какие духовные принципы были нарушены?",
    11: "11. Какие духовные принципы нужно применить?",
    12: "12. Какое новое решение необходимо?",
    13: "13. Какое конкретное действие я сделаю?",
    14: "14. Молитва.",
    15: "15. За что ты благодарен(на) сегодня?",
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
    11: "applied_principles",
    12: "new_decision",
    13: "action_plan",
    14: "prayer",
    15: "gratitude",
}


def principles_keyboard(selected, mode):
    buttons = []

    for i in range(0, len(PRINCIPLES), 2):
        row = []

        for principle in PRINCIPLES[i:i + 2]:
            mark = "☑️" if principle in selected else "☐"
            row.append(
                InlineKeyboardButton(
                    f"{mark} {principle}",
                    callback_data=f"evening:toggle:{mode}:{principle}"
                )
            )

        buttons.append(row)

    buttons.append([
        InlineKeyboardButton("✅ Готово", callback_data=f"evening:done:{mode}")
    ])

    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data="evening:back"),
        InlineKeyboardButton("❌ Отменить", callback_data="evening:cancel"),
    ])

    return InlineKeyboardMarkup(buttons)


async def evening_review(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    evening_states[user_id] = {
        "step": 1,
        "answers": {},
        "broken_selected": [],
        "applied_selected": [],
    }

    await update.message.reply_text("🌙 Вечерняя инвентаризация")
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
    text = update.message.text

    if step in [10, 11]:
        await update.message.reply_text(
            "Здесь нужно выбрать принципы кнопками с галочками."
        )
        return True

    state["answers"][ANSWER_KEYS[step]] = text

    if step == 9:
        state["step"] = 10
        await update.message.reply_text(
            QUESTIONS[10],
            reply_markup=principles_keyboard(state["broken_selected"], "broken")
        )
        return True

    if step < 15:
        state["step"] = step + 1
        await update.message.reply_text(
            QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("evening")
        )
        return True

    append_record(
        "data/daily_reviews.json",
        {
            "telegram_id": user_id,
            "type": "evening",
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
        await query.edit_message_text("Этот опрос уже не активен.")
        return

    state = evening_states[user_id]
    parts = query.data.split(":", 3)
    action = parts[1]

    if action == "cancel":
        del evening_states[user_id]
        await query.edit_message_text("❌ Вечерняя инвентаризация отменена.")
        return

    if action == "back":
        if state["step"] > 1:
            state["step"] -= 1

        await query.edit_message_text(
            "⬅️ Вернулись назад.\n\n" + QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("evening")
        )
        return

    if action == "toggle":
        mode = parts[2]
        principle = parts[3]

        key = "broken_selected" if mode == "broken" else "applied_selected"

        if principle in state[key]:
            state[key].remove(principle)
        else:
            state[key].append(principle)

        await query.edit_message_text(
            QUESTIONS[state["step"]],
            reply_markup=principles_keyboard(state[key], mode)
        )
        return

    if action == "done":
        mode = parts[2]

        if mode == "broken":
            state["answers"]["broken_principles"] = state["broken_selected"]
            state["step"] = 11

            await query.edit_message_text(
                QUESTIONS[11],
                reply_markup=principles_keyboard(state["applied_selected"], "applied")
            )
            return

        if mode == "applied":
            state["answers"]["applied_principles"] = state["applied_selected"]
            state["step"] = 12

            await query.edit_message_text(
                QUESTIONS[12],
                reply_markup=nav_keyboard("evening")
            )
            return
