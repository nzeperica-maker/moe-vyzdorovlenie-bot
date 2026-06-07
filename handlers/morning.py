from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import json
import os

user_states = {}

DATA_FILE = "data/daily_reviews.json"


def save_morning_review(user_id, answers):
    os.makedirs("data", exist_ok=True)

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append({
        "telegram_id": user_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": "morning",
        "score": answers.get("score"),
        "mood": answers.get("mood"),
        "craving": answers.get("craving"),
        "plan": answers.get("plan"),
        "created_at": datetime.now().isoformat()
    })

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


async def morning_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "🌅 Утренний настрой\n\n"
        "1. Оцени своё состояние от 1 до 10"
    )


async def handle_morning_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in user_states:
        return False

    state = user_states[user_id]
    text = update.message.text

    if state["step"] == 1:
        state["answers"]["score"] = text
        state["step"] = 2
        await update.message.reply_text(
            "2. Опиши своё состояние подробнее.\n\n"
            "Что происходит внутри тебя сегодня утром?"
        )

    elif state["step"] == 2:
        state["answers"]["mood"] = text
        state["step"] = 3
        await update.message.reply_text(
            "3. Есть ли сегодня тяга?\n\n"
            "Напиши: нет / слабая / сильная"
        )

    elif state["step"] == 3:
        state["answers"]["craving"] = text
        state["step"] = 4
        await update.message.reply_text(
            "4. Что поможет тебе сохранить трезвость сегодня?"
        )

    elif state["step"] == 4:
        state["answers"]["plan"] = text

        save_morning_review(user_id, state["answers"])

        await update.message.reply_text(
            "✅ Утренний настрой сохранён.\n\n"
            "Пусть сегодняшний день будет трезвым, честным и спокойным."
        )

        del user_states[user_id]

    return True
