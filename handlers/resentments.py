from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import append_record
from services.profile_service import get_user_profile

resentment_states = {}


async def resentment_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)

    if not profile:
        await update.message.reply_text(
            "Сначала нужно создать профиль.\n\n"
            "Напиши /profile"
        )
        return

    resentment_states[user_id] = {
        "step": 1,
        "answers": {}
    }

    await update.message.reply_text(
        "💢 Инвентаризация обид\n\n"
        "1. На кого или на что есть обида?"
    )


async def handle_resentment_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in resentment_states:
        return False

    state = resentment_states[user_id]
    text = update.message.text.strip()

    if state["step"] == 1:
        state["answers"]["target"] = text
        state["step"] = 2
        await update.message.reply_text("2. Что именно произошло?")

    elif state["step"] == 2:
        state["answers"]["event"] = text
        state["step"] = 3
        await update.message.reply_text("3. Какие мои ожидания не оправдались?")

    elif state["step"] == 3:
        state["answers"]["expectations"] = text
        state["step"] = 4
        await update.message.reply_text("4. Какая моя часть была задета?")

    elif state["step"] == 4:
        state["answers"]["affected_part"] = text
        state["step"] = 5
        await update.message.reply_text("5. Где моя ответственность в этой ситуации?")

    elif state["step"] == 5:
        state["answers"]["responsibility"] = text
        state["step"] = 6
        await update.message.reply_text("6. Какой новый взгляд я могу применить?")

    elif state["step"] == 6:
        state["answers"]["new_view"] = text
        state["step"] = 7
        await update.message.reply_text("7. Какой духовный принцип поможет?")

    elif state["step"] == 7:
        state["answers"]["principle"] = text

        record = {
            "telegram_id": user_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "type": "resentment",
            "created_at": datetime.now().isoformat(),
            **state["answers"]
        }

        append_record("data/resentments.json", record)

        await update.message.reply_text(
            "✅ Инвентаризация обиды сохранена."
        )

        del resentment_states[user_id]

    return True
