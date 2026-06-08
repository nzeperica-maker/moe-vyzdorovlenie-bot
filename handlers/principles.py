from telegram import Update
from telegram.ext import ContextTypes
from services.principles_service import load_principles


async def show_principles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    principles = load_principles()

    if not principles:
        await update.message.reply_text("Справочник принципов пока пуст.")
        return

    lines = ["📚 Духовные принципы\n"]

    for item in principles[:80]:
        lines.append(
            f"{item.get('id')}. {item.get('name')}"
        )

    lines.append(
        f"\nВсего в справочнике: {len(principles)} принципов.\n"
        "Пока показаны первые 80, чтобы сообщение помещалось в Telegram.\n"
        "В этой версии можно выбрать принцип текстом в утреннем настрое или вечерней инвентаризации."
    )

    await update.message.reply_text("\n".join(lines))
