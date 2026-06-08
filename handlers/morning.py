from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile, sobriety_days
from keyboards.navigation import nav_keyboard
from keyboards.main_menu import main_menu_keyboard

morning_states = {}

QUESTIONS = {
    1: "1. Оцени своё состояние от 1 до 10.",
    2: "2. Опиши своё состояние подробнее.\n\nЧто происходит внутри тебя сегодня утром?",
    3: "3. Что сегодня вызывает наибольшее беспокойство?",
    4: "4. Есть ли сегодня тяга?\n\nНапиши: нет / слабая / сильная.",
    5: "5. Какие 3 важных действия ты хочешь сделать сегодня?",
    6: "6. Какой духовный принцип ты хочешь практиковать сегодня?\n\nПодсказка: список принципов можно посмотреть через /principles",
    7: "7. Как ты можешь применить этот принцип сегодня на практике?",
    8: "8. О чём ты хочешь попросить Бога / Высшую Силу сегодня?",
}

ANSWER_KEYS = {
    1: "score",
    2: "state_description",
    3: "worry",
    4: "craving",
    5: "daily_actions",
    6: "principle",
    7: "principle_practice",
    8: "prayer",
}


def morning_score_description(score_text: str) -> str:
    try:
        score = int(score_text)
    except ValueError:
        return "Спасибо. Теперь опиши состояние подробнее."

    if score <= 3:
        return (
            "Похоже, утро даётся непросто. Сегодня особенно важно быть бережным(ой) "
            "к себе, не оставаться одному/одной и обращаться за помощью."
        )
    if score <= 6:
        return (
            "Состояние среднее. Это хороший момент, чтобы честно заметить тревоги, "
            "страхи и заранее выбрать духовный принцип на день."
        )
    if score <= 8:
        return (
            "Есть ресурс. Можно использовать этот день для спокойных действий, "
            "служения и укрепления трезвости."
        )
    return (
        "Высокий ресурс. Важно сохранить благодарность, смирение и помнить: "
        "трезвость поддерживается ежедневными действиями."
    )


async def ask_morning_question(update_or_query, step):
    text = QUESTIONS[step]

    if hasattr(update_or_query, "message") and update_or_query.message:
        await update_or_query.message.reply_text(text, reply_markup=nav_keyboard("morning"))
    else:
        await update_or_query.edit_message_text(text, reply_markup=nav_keyboard("morning"))


async def morning_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Нажми кнопку «👤 Профиль».",
            reply_markup=main_menu_keyboard()
        )
        return

    days = sobriety_days(profile.get("sobriety_date"))

    morning_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        f"🌅 Доброе утро, {profile.get('nickname')}.\n"
        f"Сегодня твой {days}-й день трезвости."
    )
    await update.message.reply_text(QUESTIONS[1], reply_markup=nav_keyboard("morning"))


async def handle_morning_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in morning_states:
        return False

    state = morning_states[user_id]
    step = state["step"]
    text = update.message.text.strip()

    state["answers"][ANSWER_KEYS[step]] = text

    if step == 1:
        await update.message.reply_text(morning_score_description(text))

    if step < 8:
        state["step"] = step + 1
        await update.message.reply_text(
            QUESTIONS[state["step"]],
            reply_markup=nav_keyboard("morning")
        )
    else:
        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "morning",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/daily_reviews.json", record)

        await update.message.reply_text(
            "✅ Утренний настрой сохранён.\n\n"
            "Пусть сегодняшний день будет трезвым, честным и спокойным.",
            reply_markup=main_menu_keyboard()
        )

        del morning_states[user_id]

    return True


async def handle_morning_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in morning_states:
        await query.edit_message_text("Утренний настрой уже не активен.")
        return

    action = query.data.split(":")[1]

    if action == "cancel":
        del morning_states[user_id]
        await query.edit_message_text("❌ Утренний настрой отменён.")
        return

    if action == "back":
        state = morning_states[user_id]
        current_step = state["step"]

        if current_step <= 1:
            await query.edit_message_text(
                "Это первый вопрос. Назад вернуться нельзя.",
                reply_markup=nav_keyboard("morning")
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
            reply_markup=nav_keyboard("morning")
        )
