import json
from services.database import supabase


def seed_defects():
    with open("data/defects.json", "r", encoding="utf-8") as file:
        defects = json.load(file)

    count = 0

    for item in defects:
        supabase.table("defects").upsert(
            {
                "source_number": item.get("source_number"),
                "name": item.get("name"),
                "category": item.get("category", ""),
                "description": item.get("description", ""),
                "related_principles": item.get("related_principles", []),
                "tags": item.get("tags", []),
            },
            on_conflict="source_number"
        ).execute()

        count += 1

    return count
