from telegram import Update
from telegram.ext import ContextTypes
from collections import Counter
from services.storage import load_json
from services.profile_service import get_user_profile, sobriety_days


MORNING_FIELDS = [
    ("score", "Оценка состояния"),
    ("state_description", "Описание состояния"),
    ("worry", "Что тревожит"),
    ("craving", "Тяга"),
    ("principle", "Принцип дня"),
    ("principle_practice", "Применение принципа"),
    ("daily_actions", "Действия"),
    ("prayer", "Молитва"),
]

EVENING_FIELDS = [
    ("situation", "Ситуация"),
    ("thoughts", "Мысли"),
    ("feelings", "Чувства"),
    ("egoism", "Эгоизм"),
    ("selfishness", "Корысть"),
    ("dishonesty", "Нечестность"),
    ("fear", "Страх"),
    ("real_motive", "Истинный мотив"),
    ("responsibility", "Ответственность"),
    ("broken_principles", "Нарушенные принципы"),
    ("applied_principles", "Принципы для применения"),
    ("new_decision", "Новое решение"),
    ("action_plan", "Действие"),
    ("prayer", "Молитва"),
    ("gratitude", "Благодарность"),
]


def clean_value(value):
    if value is None or value == "":
        return "—"

    if isinstance(value, list):
        return "\n".join(f"• {item}" for item in value) if value else "—"

    text = str(value)

    if text.startswith("[") and text.endswith("]"):
        text = text.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
        items = [item.strip() for item in text.split(",") if item.strip()]
        return "\n".join(f"• {item}" for item in items)

    return text.strip()


def only_user(records, user_id):
    return [record for record in records if record.get("telegram_id") == user_id]


def detect_type(record):
    if record.get("type") == "morning" or "score" in record:
        return "morning"

    if record.get("type") == "evening" or "situation" in record:
        return "evening"

    return record.get("type", "unknown")


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


def count_values(records, keys):
    counter = Counter()

    for record in records:
        for key in keys:
            value = record.get(key)

            if isinstance(value, list):
                counter.update(value)

            elif isinstance(value, str) and value:
                if value.startswith("[") and value.endswith("]"):
                    value = value.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
                    items = [item.strip() for item in value.split(",") if item.strip()]
                    counter.update(items)
                else:
                    counter.update([value])

    return counter


def format_counter(title, counter):
    if not counter:
        return f"\n\n<b>{title}</b>\nНет данных."

    text = f"\n\n<b>{title}</b>"

    for name, count in counter.most_common(10):
        text += f"\n• {name} — {count}"

    return text


def format_record(title, record, fields):
    text = f"\n\n<b>{title}</b>"

    for key, label in fields:
        if key in record:
            text += f"\n\n<b>{label}</b>\n{clean_value(record.get(key))}"

    return text


async def recovery_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    profile = get_user_profile(user_id)
    daily_records = only_user(load_json("data/daily_reviews.json", []), user_id)
    fear_records = only_user(load_json("data/fears.json", []), user_id)
    resentment_records = only_user(load_json("data/resentments.json", []), user_id)

    morning_records = [
        record for record in daily_records
        if detect_type(record) == "morning"
    ]

    evening_records = [
        record for record in daily_records
        if detect_type(record) == "evening"
    ]

    name = profile.get("nickname") if profile else "Пользователь"
    days = sobriety_days(profile.get("sobriety_date")) if profile else None

    scores = []
    for record in morning_records:
        try:
            scores.append(int(record.get("score")))
        except (TypeError, ValueError):
            pass

    average_score = round(sum(scores) / len(scores), 1) if scores else "нет данных"

    principles_counter = count_values(
        daily_records,
        ["principle", "broken_principles", "applied_principles"]
    )

    fears_counter = count_values(
        daily_records + fear_records,
        ["fear"]
    )

    export_text = (
        "📈 <b>Моё выздоровление</b>\n\n"
        f"<b>Профиль</b>\n"
        f"Имя: {name}\n"
    )

    if days:
        export_text += f"Дней трезвости: {days}\n"

    export_text += (
        "\n<b>Общая статистика за весь период</b>\n"
        f"Утренних настроев: {len(morning_records)}\n"
        f"Вечерних инвентаризаций: {len(evening_records)}\n"
        f"Инвентаризаций страхов: {len(fear_records)}\n"
        f"Инвентаризаций обид: {len(resentment_records)}\n"
        f"Средняя оценка утра: {average_score}"
    )

    export_text += format_counter(
        "Часто встречающиеся духовные принципы",
        principles_counter
    )

    export_text += format_counter(
        "Часто встречающиеся страхи",
        fears_counter
    )

    if morning_records:
        export_text += format_record(
            "Последний утренний настрой",
            morning_records[-1],
            MORNING_FIELDS
        )

    if evening_records:
        export_text += format_record(
            "Последняя вечерняя инвентаризация",
            evening_records[-1],
            EVENING_FIELDS
        )

    export_text += (
        "\n\n<b>Все записи за период</b>\n"
        "Ниже перечислены все сохранённые утренние и вечерние записи."
    )

    for index, record in enumerate(morning_records, start=1):
        export_text += format_record(
            f"🌅 Утренний настрой {index}",
            record,
            MORNING_FIELDS
        )

    for index, record in enumerate(evening_records, start=1):
        export_text += format_record(
            f"🌙 Вечерняя инвентаризация {index}",
            record,
            EVENING_FIELDS
        )

    for part in split_message(export_text):
        await update.message.reply_text(part, parse_mode="HTML")
