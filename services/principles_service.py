from services.storage import load_json


def load_principles():
    return load_json("data/principles.json", [])


def get_principle_by_id(principle_id):
    principles = load_principles()

    for item in principles:
        if item.get("id") == principle_id:
            return item

    return None
