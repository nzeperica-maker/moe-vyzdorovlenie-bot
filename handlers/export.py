from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import load_json


FIELD_NAMES = {
    "situation": "Ситуация",
    "thoughts": "Мысли",
    "feelings": "Чувства",
    "egoism": "Эгоизм",
    "selfishness": "Корысть",
    "dishonesty": "Нечестность",
    "fear": "Страх",
    "real_motive": "Истинный мотив",
    "responsibility": "Моя ответственность",
    "broken_principles": "Нарушенные принципы",
    "applied_principles": "Принципы для применения",
    "new_decision": "Новое решение",
    "action_plan": "Конкретное действие",
    "prayer": "Молитва",
    "gratitude": "Благодарность",
}


def format_value(value):
    if isinstance(value, list):
        if not value:
            return "—"
        return "\n".join([f"• {item}" for item in value])

    if value is None or value == "":
        return "—"

    return str(value)


def filter_today(records, user_id):
    today = datetime.now().strftime("%Y-%m-%d")

    return [
        item for item in records
        if item.get("telegram_id") == user_id
        and item.get("created_at", "").startswith(today)
    ]


def format_section(title, records):
    if not records:
        return f"\n\n{title}\nНет записей."

    text = f"\n\n{title}"

    for index, record in enumerate(records, start=1):
        text += f"\n\nЗапись {index}"

        for key, label in FIELD_NAMES.items():
            if key in record:
                text += f"\n\n{label}:\n{format_value(record.get(key))}"

    return text


async def export_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today_readable = datetime.now().strftime("%d.%m.%Y")

    daily_reviews = filter_today(
        load_json("data/daily_reviews.json", []),
        user_id
    )

    fears = filter_today(
        load_json("data/fears.json", []),
        user_id
    )

    resentments = filter_today(
        load_json("data/resentments.json", []),
        user_id
    )

    export_text = (
        f"📄 Полная выгрузка дня\n"
        f"Дата: {today_readable}\n\n"
        f"Этот отчёт можно переслать спонсору."
    )

    export_text += format_section("🌙 Вечерняя инвентаризация", daily_reviews)
    export_text += format_section("😨 Страхи", fears)
    export_text += format_section("💢 Обиды", resentments)

    if len(export_text) <= 3900:
        await update.message.reply_text(export_text)
    else:
        filename = "vygruzka_dnya.txt"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(export_text)

        await update.message.reply_document(
            document=open(filename, "rb"),
            filename=filename,
            caption="📄 Полная выгрузка дня"
        )
