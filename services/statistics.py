from collections import Counter
from services.storage import load_json
from services.profile_service import get_user_profile, sobriety_days


def _records_for_user(path, user_id):
    return [
        item for item in load_json(path, [])
        if item.get("telegram_id") == user_id
    ]


def build_recovery_summary(user_id):
    profile = get_user_profile(user_id)
    daily = _records_for_user("data/daily_reviews.json", user_id)
    fears = _records_for_user("data/fears.json", user_id)
    resentments = _records_for_user("data/resentments.json", user_id)

    morning = [item for item in daily if item.get("type") == "morning"]
    evening = [item for item in daily if item.get("type") == "evening"]

    scores = []
    for item in morning:
        try:
            scores.append(int(item.get("score")))
        except (TypeError, ValueError):
            pass

    average_score = round(sum(scores) / len(scores), 1) if scores else "нет данных"

    principles = []
    for item in daily:
        value = item.get("principle") or item.get("principles")
        if value:
            principles.append(value)

    common_principles = Counter(principles).most_common(5)

    name = profile.get("nickname") if profile else "друг"
    days = sobriety_days(profile.get("sobriety_date")) if profile else None

    message = "📈 Моё выздоровление\n\n"
    message += f"Пользователь: {name}\n"

    if days:
        message += f"Дней трезвости: {days}\n"

    message += (
        f"\nУтренних настроев: {len(morning)}\n"
        f"Вечерних инвентаризаций: {len(evening)}\n"
        f"Инвентаризаций страхов: {len(fears)}\n"
        f"Инвентаризаций обид: {len(resentments)}\n"
        f"Средняя оценка утра: {average_score}\n"
    )

    if common_principles:
        message += "\nЧасто выбранные принципы:\n"
        for principle, count in common_principles:
            message += f"• {principle}: {count}\n"

    last_morning = morning[-1] if morning else None
    last_evening = evening[-1] if evening else None

    if last_morning:
        message += (
            "\nПоследний утренний настрой:\n"
            f"Дата: {last_morning.get('date')}\n"
            f"Оценка: {last_morning.get('score')}\n"
            f"Состояние: {last_morning.get('state_description')}\n"
            f"Принцип дня: {last_morning.get('principle')}\n"
        )

    if last_evening:
        message += (
            "\nПоследняя вечерняя инвентаризация:\n"
            f"Дата: {last_evening.get('date')}\n"
            f"Ситуация: {last_evening.get('situation')}\n"
            f"Новое решение: {last_evening.get('new_decision')}\n"
        )

    return message
