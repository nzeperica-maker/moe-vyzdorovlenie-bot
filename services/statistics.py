import json
import os

DATA_FILE = "data/daily_reviews.json"


def get_morning_stats(user_id):
    if not os.path.exists(DATA_FILE):
        return "Пока нет сохранённых утренних настроев."

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            data = []

    records = [
        item for item in data
        if item.get("telegram_id") == user_id and item.get("type") == "morning"
    ]

    if not records:
        return "Пока нет сохранённых утренних настроев."

    scores = []
    for item in records:
        try:
            scores.append(int(item.get("score")))
        except (TypeError, ValueError):
            pass

    total = len(records)
    average = round(sum(scores) / len(scores), 1) if scores else "нет данных"

    last = records[-1]

    return (
        "📈 Моё выздоровление\n\n"
        f"Утренних настроев сохранено: {total}\n"
        f"Средняя оценка состояния: {average}\n\n"
        "Последний утренний настрой:\n"
        f"Дата: {last.get('date')}\n"
        f"Оценка: {last.get('score')}\n"
        f"Состояние: {last.get('mood')}\n"
        f"Тяга: {last.get('craving')}\n"
        f"План на трезвость: {last.get('plan')}"
    )
