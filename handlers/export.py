from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from services.storage import load_json


MORNING_FIELDS = [
    ("score", "Оценка состояния"),
    ("state_description", "Описание состояния"),
    ("worry", "Что тревожит"),
    ("craving", "Тяга"),
    ("prayer", "Молитва / просьба к Богу"),
    ("principle", "Духовный принцип дня"),
    ("principle_practice", "Как я буду применять принцип"),
    ("daily_actions", "Действия на сегодня"),
]

EVENING_FIELDS = [
    ("situation", "Ситуация"),
    ("thoughts", "Мысли"),
    ("feelings", "Чувства"),
    ("egoism", "Эгоизм"),
    ("selfishness", "Корысть"),
    ("dishonesty", "Нечестность"),
    ("fear", "Страхи"),
    ("real_motive", "Истинный мотив"),
    ("responsibility", "Моя ответственность"),
    ("broken_principles", "Нарушенные духовные принципы"),
    ("applied_principles", "Духовные принципы для применения"),
    ("new_decision", "Новое решение"),
    ("action_plan", "Конкретное действие"),
    ("prayer", "Молитва"),
    ("gratitude", "Благодарность"),
]

FEAR_FIELDS = [
    ("situation", "Ситуация"),
    ("fear", "Страх"),
    ("loss", "Что боюсь потерять"),
    ("control", "Что пытаюсь контролировать"),
    ("defect", "Дефект характера"),
    ("principle", "Духовный принцип"),
    ("action", "Действие"),
]

RESENTMENT_FIELDS = [
    ("target", "На кого / на что обида"),
    ("event", "Что произошло"),
    ("expectations", "Какие ожидания не оправдались"),
    ("affected_part", "Что было задето"),
    ("responsibility", "Моя ответственность"),
    ("defect", "Дефект характера"),
    ("new_view", "Новый взгляд"),
    ("principle", "Духовный принцип"),
    ("action", "Действие"),
]


def clean_value(value):
    if value is None or value == "":
        return "—"

    if isinstance(value, list):
        if not value:
            return "—"
        return "\n".join(f"• {item}" for item in value)

    text = str(value)

    if text.startswith("[") and text.endswith("]"):
        text = (
            text.replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace('"', "")
        )
        items = [item.strip() for item in text.split(",") if item.strip()]
        if items:
            return "\n".join(f"• {item}" for item in items)

    return text.strip()


def filter_today(records, user_id):
    today = datetime.now().strftime("%Y-%m-%d")

    return [
        item for item in records
        if item.get("telegram_id") == user_id
        and item.get("created_at", item.get("date", "")).startswith(today)
    ]


def detect_record_type(record):
    if "score" in record or "state_description" in record:
        return "morning"

    if "broken_principles" in record or "applied_principles" in record:
        return "evening"

    return record.get("type", "unknown")


def format_fields(record, fields):
    text = ""

    for key, label in fields:
        if key in record:
            text += f"\n<b>{label}</b>\n"
            text += f"{clean_value(record.get(key))}\n"

    return text


def format_morning(records):
    morning_records = [
        record for record in records
        if detect_record_type(record) == "morning"
    ]

    if not morning_records:
        return "\n🌅 <b>Утренний настрой</b>\nНет записей.\n"

    text = "\n🌅 <b>Утренний настрой</b>\n"

    for index, record in enumerate(morning_records, start=1):
        text += f"\n<b>Запись {index}</b>\n"
        text += format_fields(record, MORNING_FIELDS)

    return text


def format_evening(records):
    evening_records = [
        record for record in records
        if detect_record_type(record) == "evening"
    ]

    if not evening_records:
        return "\n🌙 <b>Вечерняя инвентаризация</b>\nНет записей.\n"

    text = "\n🌙 <b>Вечерняя инвентаризация</b>\n"

    for index, record in enumerate(evening_records, start=1):
        text += f"\n<b>Ситуация {index}</b>\n"
        text += format_fields(record, EVENING_FIELDS)

    return text


def format_extra_section(title, records, fields):
    if not records:
        return f"\n{title}\nНет записей.\n"

    text = f"\n{title}\n"

    for index, record in enumerate(records, start=1):
        text += f"\n<b>Запись {index}</b>\n"
        text += format_fields(record, fields)

    return text


def split_message(text, limit=3900):
    parts = []

    while len(text) > limit:
        cut = text.rfind("\n\n", 0, limit)
        if cut == -1:
            cut = limit

        parts.append(text[:cut])
        text = text[cut:].strip()

    if text:
        parts.append(text)

    return parts


async def export_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today_readable = datetime.now().strftime("%d.%m.%Y")

    daily_records = filter_today(
        load_json("data/daily_reviews.json", []),
        user_id
    )

    fear_records = filter_today(
        load_json("data/fears.json", []),
        user_id
    )

    resentment_records = filter_today(
        load_json("data/resentments.json", []),
        user_id
    )

    export_text = (
        f"📄 <b>Полная выгрузка дня</b>\n"
        f"Дата: <b>{today_readable}</b>\n\n"
        f"Отчёт для личного анализа или отправки спонсору.\n"
        f"────────────────────\n"
    )

    export_text += format_morning(daily_records)
    export_text += "\n────────────────────\n"
    export_text += format_evening(daily_records)
    export_text += "\n────────────────────\n"
    export_text += format_extra_section("😨 <b>Инвентаризация страхов</b>", fear_records, FEAR_FIELDS)
    export_text += "\n────────────────────\n"
    export_text += format_extra_section("💢 <b>Инвентаризация обид</b>", resentment_records, RESENTMENT_FIELDS)

    for part in split_message(export_text):
        await update.message.reply_text(part, parse_mode="HTML")
