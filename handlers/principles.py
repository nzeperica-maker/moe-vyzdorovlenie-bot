from telegram import Update
from telegram.ext import ContextTypes
from services.principles_service import load_principles


async def show_principles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    principles = load_principles()

    if not principles:
        await update.message.reply_text("Справочник принципов пока пуст.")
        return

    lines = ["📚 Духовные принципы\n"]

    for item in principles[:30]:
        lines.append(
            f"{item.get('id')}. {item.get('name')}"
        )

    lines.append(
        "\nПока показаны первые 30 принципов. "
        "Позже добавим поиск и выбор кнопками."
    )

    await update.message.reply_text("\n".join(lines))
