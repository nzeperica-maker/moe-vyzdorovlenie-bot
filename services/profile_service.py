from datetime import datetime, date
from services.storage import find_by_telegram_id, upsert_by_telegram_id, load_json, save_json

USERS_FILE = "data/users.json"


def get_user_profile(telegram_id):
    return find_by_telegram_id(USERS_FILE, telegram_id)


def save_user_profile(profile):
    upsert_by_telegram_id(USERS_FILE, profile)


def delete_user_profile(telegram_id):
    users = load_json(USERS_FILE, [])
    users = [
        item for item in users
        if item.get("telegram_id") != telegram_id
    ]
    save_json(USERS_FILE, users)


def parse_sobriety_date(text):
    cleaned = text.strip().replace("/", ".").replace("-", ".")

    for fmt in ("%d.%m.%Y", "%Y.%m.%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass

    return None


def sobriety_days(sobriety_date_text):
    parsed = parse_sobriety_date(sobriety_date_text)

    if not parsed:
        return None

    return (date.today() - parsed).days + 1
