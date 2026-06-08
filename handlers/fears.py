from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile
from keyboards.navigation import nav_keyboard
from keyboards.main_menu import main_menu_keyboard

fear_states = {}

QUESTIONS = {
    1: '1. Опиши страх или тревожную ситуацию.',
    2: '2. Чего именно ты боишься?',
    3: '3. Что ты боишься потерять?',
    4: '4. Что ты пытаешься контролировать?',
    5: '5. Какой дефект характера проявился?',
    6: '6. Какой духовный принцип может помочь?',
    7: '7. Какое действие ты можешь сделать на духовной основе?',
}

ANSWER_KEYS = {
    1: 'situation',
    2: 'fear',
    3: 'loss',
    4: 'control',
    5: 'defect',
    6: 'principle',
    7: 'action',
}


async def fear_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Нажми кнопку «👤 Профиль».",
            reply_markup=main_menu_keyboard()
        )
        return

    fear_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "😨 Инвентаризация страхов"
    )
    await update.message.reply_text(
        QUESTIONS[1],
        reply_markup=nav_keyboard("fear")
    )


async def handle_fear_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in fear_states:
        return False

    state = fear_states[user_id]
    step = state["step"]
    text = update.message.text.strip()

    state["answers"][ANSWER_KEYS[step]] = text

    if step < 7:
        state["step"] = step + 1
        await update.message.reply_text(
            QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("fear")
        )
    else:
        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "fear",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/fears.json", record)

        await update.message.reply_text(
            "✅ Инвентаризация страха сохранена.",
            reply_markup=main_menu_keyboard()
        )

        del fear_states[user_id]

    return True


async def handle_fear_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in fear_states:
        await query.edit_message_text("Этот опрос уже не активен.")
        return

    action = query.data.split(":")[1]

    if action == "cancel":
        del fear_states[user_id]
        await query.edit_message_text("❌ Опрос отменён.")
        return

    if action == "back":
        state = fear_states[user_id]
        current_step = state["step"]

        if current_step <= 1:
            await query.edit_message_text(
                "Это первый вопрос. Назад вернуться нельзя.",
                reply_markup=nav_keyboard("fear")
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
            reply_markup=nav_keyboard("fear")
        )
