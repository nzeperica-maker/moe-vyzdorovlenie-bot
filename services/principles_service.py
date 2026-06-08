from services.database import supabase


def load_principles():
    result = (
        supabase.table("principles")
        .select("*")
        .order("source_number")
        .execute()
    )

    return result.data or []
