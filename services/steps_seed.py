import json
from services.database import supabase


def seed_steps():
    with open("data/steps.json", "r", encoding="utf-8") as file:
        steps = json.load(file)

    count = 0

    for item in steps:
        supabase.table("steps").upsert(
            {
                "step_number": item.get("step_number"),
                "title": item.get("title"),
                "short_description": item.get("short_description", ""),
                "full_description": item.get("full_description", ""),
                "practice": item.get("practice", []),
                "questions": item.get("questions", []),
                "literature": item.get("literature", []),
                "prayer": item.get("prayer", ""),
                "related_principles": item.get("related_principles", []),
                "related_tools": item.get("related_tools", []),
            },
            on_conflict="step_number"
        ).execute()

        count += 1

    return count
