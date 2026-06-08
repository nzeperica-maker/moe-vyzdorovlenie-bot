from datetime import datetime
from services.database import supabase


def parse_sobriety_date(text):
    try:
        return datetime.strptime(text.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def sobriety_days(date_text):
    if not date_text:
        return None

    try:
        if "-" in date_text:
            sobriety_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        else:
            sobriety_date = datetime.strptime(date_text, "%d.%m.%Y").date()

        return (datetime.now().date() - sobriety_date).days + 1
    except ValueError:
        return None


def get_user_profile(telegram_id):
    result = (
        supabase.table("users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]


def save_user_profile(profile_data):
    sobriety_date = parse_sobriety_date(profile_data["sobriety_date"])

    supabase.table("users").upsert({
        "telegram_id": profile_data["telegram_id"],
        "nickname": profile_data["nickname"],
        "sobriety_date": sobriety_date.isoformat(),
        "timezone": profile_data.get("timezone", "Europe/Stockholm"),
    }, on_conflict="telegram_id").execute()


def delete_user_profile(telegram_id):
    supabase.table("users").delete().eq("telegram_id", telegram_id).execute()
