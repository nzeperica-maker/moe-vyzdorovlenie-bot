from services.database import supabase


def append_record(path, record):
    try:
        if path == "data/daily_reviews.json":
            supabase.table("daily_reviews").insert({
                "telegram_id": record.get("telegram_id"),
                "review_type": record.get("type", "review"),
                "data": record
            }).execute()
            return True

        if path == "data/fears.json":
            supabase.table("fears").insert({
                "telegram_id": record.get("telegram_id"),
                "data": record
            }).execute()
            return True

        if path == "data/resentments.json":
            supabase.table("resentments").insert({
                "telegram_id": record.get("telegram_id"),
                "data": record
            }).execute()
            return True

        return False

    except Exception as error:
        print("SUPABASE SAVE ERROR:", error)
        return False


def load_json(path, default=None):
    if default is None:
        default = []

    try:
        if path == "data/daily_reviews.json":
            rows = supabase.table("daily_reviews").select("*").execute().data
            return [row["data"] for row in rows]

        if path == "data/fears.json":
            rows = supabase.table("fears").select("*").execute().data
            return [row["data"] for row in rows]

        if path == "data/resentments.json":
            rows = supabase.table("resentments").select("*").execute().data
            return [row["data"] for row in rows]

        return default

    except Exception as error:
        print("SUPABASE LOAD ERROR:", error)
        return default


def save_json(path, data):
    return False
