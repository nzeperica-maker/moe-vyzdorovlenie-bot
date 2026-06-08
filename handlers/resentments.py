from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile
from keyboards.navigation import nav_keyboard
from keyboards.main_menu import main_menu_keyboard

resentment_states = {}

QUESTIONS = {
    1: '1. На кого или на что есть обида?',
    2: '2. Что именно произошло?',
    3: '3. Какие мои ожидания не оправдались?',
    4: '4. Какая моя часть была задета?',
    5: '5. Где моя ответственность в этой ситуации?',
    6: '6. Какой дефект характера проявился?',
    7: '7. Какой новый взгляд я могу применить?',
    8: '8. Какой духовный принцип поможет?',
    9: '9. Какое конкретное действие нужно?',
}

ANSWER_KEYS = {
    1: 'target',
    2: 'event',
    3: 'expectations',
    4: 'affected_part',
    5: 'responsibility',
    6: 'defect',
    7: 'new_view',
    8: 'principle',
    9: 'action',
}


async def resentment_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Нажми кнопку «👤 Профиль».",
            reply_markup=main_menu_keyboard()
        )
        return

    resentment_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "💢 Инвентаризация обид"
    )
    await update.message.reply_text(
        QUESTIONS[1],
        reply_markup=nav_keyboard("resentment")
    )


async def handle_resentment_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in resentment_states:
        return False

    state = resentment_states[user_id]
    step = state["step"]
    text = update.message.text.strip()

    state["answers"][ANSWER_KEYS[step]] = text

    if step < 9:
        state["step"] = step + 1
        await update.message.reply_text(
            QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("resentment")
        )
    else:
        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "resentment",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/resentments.json", record)

        await update.message.reply_text(
            "✅ Инвентаризация обиды сохранена.",
            reply_markup=main_menu_keyboard()
        )

        del resentment_states[user_id]

    return True


async def handle_resentment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in resentment_states:
        await query.edit_message_text("Этот опрос уже не активен.")
        return

    action = query.data.split(":")[1]

    if action == "cancel":
        del resentment_states[user_id]
        await query.edit_message_text("❌ Опрос отменён.")
        return

    if action == "back":
        state = resentment_states[user_id]
        current_step = state["step"]

        if current_step <= 1:
            await query.edit_message_text(
                "Это первый вопрос. Назад вернуться нельзя.",
                reply_markup=nav_keyboard("resentment")
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
            reply_markup=nav_keyboard("resentment")
        )
