from services.storage import load_json


def load_defects():
    return load_json("data/defects.json", [])
