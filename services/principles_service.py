from services.database import supabase


def load_principles():
    result = (
        supabase.table("principles")
        .select("*")
        .order("source_number")
        .execute()
    )

    return result.data or []


def get_principle_by_id(principle_id):
    result = (
        supabase.table("principles")
        .select("*")
        .eq("id", principle_id)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]
