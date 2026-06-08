from services.database import supabase


def load_defects():
    result = (
        supabase.table("defects")
        .select("*")
        .order("source_number")
        .execute()
    )

    return result.data or []


def get_defect_by_id(defect_id):
    result = (
        supabase.table("defects")
        .select("*")
        .eq("id", defect_id)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]
