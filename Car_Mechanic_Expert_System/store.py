# store.py - tiny JSON-file "database" for the expert system.
# The project has no external database; records are kept in the data/
# folder next to this file so they survive app restarts.
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def _path(name):
    return os.path.join(DATA_DIR, name + '.json')


def load_records(name):
    # Read a whole record list (returns [] if missing or corrupted)
    p = _path(name)
    if not os.path.exists(p):
        return []
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_dict(name):
    # Read a whole dict record (vehicle profile etc.)
    p = _path(name)
    if not os.path.exists(p):
        return {}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_records(name, records):
    # Overwrite a record list (used after edits / deletes)
    try:
        with open(_path(name), 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def save_dict(name, data):
    # Overwrite a dict record (vehicle profile etc.)
    try:
        with open(_path(name), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def append_record(name, record):
    # Append one record and return the new total count
    records = load_records(name)
    record['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    records.append(record)
    if save_records(name, records):
        return len(records)
    return -1


def delete_record(name, index):
    records = load_records(name)
    if 0 <= index < len(records):
        records.pop(index)
        return save_records(name, records)
    return False
