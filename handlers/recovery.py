Замени **`handlers/recovery.py` целиком** на этот код:

```python
from telegram import Update
from telegram.ext import ContextTypes
from collections import Counter
from services.storage import load_json
from services.profile_service import get_user_profile, sobriety_days


def only_user(records, user_id):
    return [record for record in records if record.get("telegram_id") == user_id]


def detect_type(record):
    if record.get("type") == "morning" or "score" in record:
        return "morning"

    if record.get("type") == "evening" or "situation" in record:
        return "evening"

    return record.get("type", "unknown")


def normalize_list(value):
    if not value:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        if value.startswith("[") and value.endswith("]"):
            value = value.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            return [item.strip() for item in value.split(",") if item.strip()]

        return [value.strip()]

    return []


def count_values(records, keys):
    counter = Counter()

    for record in records:
        for key in keys:
            counter.update(normalize_list(record.get(key)))

    return counter


def format_counter(counter, empty_text="Нет данных", limit=5):
    if not counter:
        return empty_text

    lines = []

    for index, (name, count) in enumerate(counter.most_common(limit), start=1):
        lines.append(f"{index}. {name} — {count}")

    return "\n".join(lines)


def get_scores(records):
    scores = []

    for record in records:
        try:
            scores.append(int(record.get("score")))
        except (TypeError, ValueError):
            pass

    return scores


def average(values):
    if not values:
        return "нет данных"

    return round(sum(values) / len(values), 1)


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

    scores = get_scores(morning_records)

    used_principles = count_values(
        daily_records + fear_records + resentment_records,
        ["principle", "applied_principles"]
    )

    broken_principles = count_values(
        daily_records,
        ["broken_principles"]
    )

    fears = count_values(
        daily_records + fear_records,
        ["fear"]
    )

    defects = count_values(
        fear_records + resentment_records,
        ["defect"]
    )

    name = profile.get("nickname") if profile else "Пользователь"
    days = sobriety_days(profile.get("sobriety_date")) if profile else None

    text = "📈 <b>Моё выздоровление</b>\n\n"

    text += "👤 <b>Профиль</b>\n"
    text += f"Имя: {name}\n"

    if days:
        text += f"Дней трезвости: {days}\n"

    text += "\n📊 <b>Активность за весь период</b>\n"
    text += f"• Утренних настроев: {len(morning_records)}\n"
    text += f"• Вечерних инвентаризаций: {len(evening_records)}\n"
    text += f"• Инвентаризаций страхов: {len(fear_records)}\n"
    text += f"• Инвентаризаций обид: {len(resentment_records)}\n"

    text += "\n🌅 <b>Утреннее состояние</b>\n"
    text += f"• Средняя оценка утра: {average(scores)}\n"

    if scores:
        text += f"• Лучший день: {max(scores)}\n"
        text += f"• Самый сложный день: {min(scores)}\n"

    text += "\n😨 <b>Частые страхи</b>\n"
    text += format_counter(fears, "Нет данных")

    text += "\n\n📚 <b>Наиболее используемые принципы</b>\n"
    text += format_counter(used_principles, "Нет данных")

    text += "\n\n⚠️ <b>Часто нарушаемые принципы</b>\n"
    text += format_counter(broken_principles, "Нет данных")

    text += "\n\n🧩 <b>Частые дефекты</b>\n"
    text += format_counter(defects, "Нет данных")

    text += "\n\n📄 Подробные записи смотри в разделе «Выгрузка дня»."

    await update.message.reply_text(text, parse_mode="HTML")
