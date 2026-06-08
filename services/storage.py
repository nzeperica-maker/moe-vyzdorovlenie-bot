import json
import os


def load_json(path, default=None):
    if default is None:
        default = []

    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return default


def save_json(path, data):
    folder = os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def append_record(path, record):
    data = load_json(path, [])
    data.append(record)
    save_json(path, data)


def find_by_telegram_id(path, telegram_id):
    data = load_json(path, [])

    for item in data:
        if item.get("telegram_id") == telegram_id:
            return item

    return None


def upsert_by_telegram_id(path, record):
    data = load_json(path, [])
    updated = False

    for index, item in enumerate(data):
        if item.get("telegram_id") == record.get("telegram_id"):
            data[index] = record
            updated = True
            break

    if not updated:
        data.append(record)

    save_json(path, data)
