from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import load_json


def get_today_records(user_id):
    today = datetime.now().strftime("%Y-%m-%d")

    daily_reviews = load_json("data/daily_reviews.json", [])
    fears = load_json("data/fears.json", [])
    resentments = load_json("data/resentments.json", [])

    today_daily = [
        item for item in daily_reviews
        if item.get("telegram_id") == user_id
        and item.get("created_at", "").startswith(today)
    ]

    today_fears = [
        item for item in fears
        if item.get("telegram_id") == user_id
        and item.get("created_at", "").startswith(today)
    ]

    today_resentments = [
        item for item in resentments
        if item.get("telegram_id") == user_id
        and item.get("created_at", "").startswith(today)
    ]

    return today_daily, today_fears, today_resentments


def format_record(title, records):
    if not records:
        return f"\n\n{title}\nНет записей."

    text = f"\n\n{title}"

    for index, record in enumerate(records, start=1):
        text += f"\n\nЗапись {index}:"

        for key, value in record.items():
            if key in ["telegram_id", "created_at", "type"]:
                continue

            text += f"\n{key}: {value}"

    return text


async def export_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.now().strftime("%d.%m.%Y")

    daily, fears, resentments = get_today_records(user_id)

    export_text = f"📄 Полная выгрузка дня\nДата: {today}"

    export_text += format_record("🌅 / 🌙 Настрои и инвентаризации", daily)
    export_text += format_record("😨 Страхи", fears)
    export_text += format_record("💢 Обиды", resentments)

    if len(export_text) < 4000:
        await update.message.reply_text(export_text)
    else:
        filename = "export_today.txt"

        with open(filename, "w", encoding="utf-8") as file:
            file.write(export_text)

        await update.message.reply_document(
            document=open(filename, "rb"),
            filename=filename,
            caption="📄 Полная выгрузка дня"
        )
