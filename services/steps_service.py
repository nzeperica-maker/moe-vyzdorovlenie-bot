from services.database import supabase


def load_steps():
    result = (
        supabase.table("steps")
        .select("*")
        .order("step_number")
        .execute()
    )

    return result.data or []


def get_step(step_number):
    result = (
        supabase.table("steps")
        .select("*")
        .eq("step_number", step_number)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]


def get_user_step_progress(user_id, step_number):
    result = (
        supabase.table("user_step_progress")
        .select("*")
        .eq("telegram_id", user_id)
        .eq("step_number", step_number)
        .limit(1)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]


def set_user_step_status(user_id, step_number, status):
    supabase.table("user_step_progress").upsert(
        {
            "telegram_id": user_id,
            "step_number": step_number,
            "status": status,
        },
        on_conflict="telegram_id,step_number"
    ).execute()


def load_user_progress(user_id):
    result = (
        supabase.table("user_step_progress")
        .select("*")
        .eq("telegram_id", user_id)
        .order("step_number")
        .execute()
    )

    return result.data or []


def save_step_answer(user_id, step_number, question_index, question_text, answer_text):
    supabase.table("user_step_answers").insert({
        "telegram_id": user_id,
        "step_number": step_number,
        "question_index": question_index,
        "question_text": question_text,
        "answer_text": answer_text,
    }).execute()


def load_step_answers(user_id, step_number=None):
    query = (
        supabase.table("user_step_answers")
        .select("*")
        .eq("telegram_id", user_id)
    )

    if step_number is not None:
        query = query.eq("step_number", step_number)

    result = query.order("created_at").execute()

    return result.data or []
