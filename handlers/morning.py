from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile, sobriety_days

morning_states = {}


async def morning_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Напиши /profile"
        )
        return

    days = sobriety_days(profile.get("sobriety_date"))

    morning_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        f"🌅 Доброе утро, {profile.get('nickname')}.\n"
        f"Сегодня твой {days}-й день трезвости.\n\n"
        "1. Оцени своё состояние от 1 до 10."
    )


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


async def handle_morning_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in morning_states:
        return False

    state = morning_states[user_id]
    text = update.message.text.strip()

    if state["step"] == 1:
        state["answers"]["score"] = text
        state["step"] = 2

        await update.message.reply_text(
            morning_score_description(text) + "\n\n"
            "2. Опиши своё состояние подробнее.\n\n"
            "Что происходит внутри тебя сегодня утром?"
        )

    elif state["step"] == 2:
        state["answers"]["state_description"] = text
        state["step"] = 3

        await update.message.reply_text(
            "3. Что сегодня вызывает наибольшее беспокойство?"
        )

    elif state["step"] == 3:
        state["answers"]["worry"] = text
        state["step"] = 4

        await update.message.reply_text(
            "4. Есть ли сегодня тяга?\n\n"
            "Напиши: нет / слабая / сильная."
        )

    elif state["step"] == 4:
        state["answers"]["craving"] = text
        state["step"] = 5

        await update.message.reply_text(
            "5. Какие 3 важных действия ты хочешь сделать сегодня?"
        )

    elif state["step"] == 5:
        state["answers"]["daily_actions"] = text
        state["step"] = 6

        await update.message.reply_text(
            "6. Какой духовный принцип ты хочешь практиковать сегодня?\n\n"
            "Подсказка: список принципов можно посмотреть через /principles"
        )

    elif state["step"] == 6:
        state["answers"]["principle"] = text
        state["step"] = 7

        await update.message.reply_text(
            "7. Как ты можешь применить этот принцип сегодня на практике?"
        )

    elif state["step"] == 7:
        state["answers"]["principle_practice"] = text
        state["step"] = 8

        await update.message.reply_text(
            "8. О чём ты хочешь попросить Бога / Высшую Силу сегодня?"
        )

    elif state["step"] == 8:
        state["answers"]["prayer"] = text

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
            "Пусть сегодняшний день будет трезвым, честным и спокойным."
        )

        del morning_states[user_id]

    return True
