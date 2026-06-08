import json
from services.database import supabase


def seed_principles():
    with open("data/principles.json", "r", encoding="utf-8") as file:
        principles = json.load(file)

    inserted = 0

    for item in principles:
        supabase.table("principles").upsert(
            {
                "source_number": item.get("source_number") or item.get("id"),
                "name": item.get("name"),
                "description": item.get("description", ""),
                "tags": item.get("tags", []),
            },
            on_conflict="source_number"
        ).execute()

        inserted += 1

    return inserted
