from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record

fear_states = {}


async def fear_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    fear_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "😨 Инвентаризация страхов\n\n"
        "1. Опиши страх или тревожную ситуацию."
    )


async def handle_fear_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in fear_states:
        return False

    state = fear_states[user_id]
    text = update.message.text.strip()

    if state["step"] == 1:
        state["answers"]["situation"] = text
        state["step"] = 2
        await update.message.reply_text("2. Чего именно ты боишься?")

    elif state["step"] == 2:
        state["answers"]["fear"] = text
        state["step"] = 3
        await update.message.reply_text("3. Что ты боишься потерять?")

    elif state["step"] == 3:
        state["answers"]["loss"] = text
        state["step"] = 4
        await update.message.reply_text("4. Что ты пытаешься контролировать?")

    elif state["step"] == 4:
        state["answers"]["control"] = text
        state["step"] = 5
        await update.message.reply_text("5. Какой духовный принцип может помочь?")

    elif state["step"] == 5:
        state["answers"]["principle"] = text

        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "fear",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/fears.json", record)

        await update.message.reply_text(
            "✅ Инвентаризация страха сохранена."
        )

        del fear_states[user_id]

    return True
