# history.py - Diagnosis history stored in a local SQLite database.
# Uses only Python's built-in sqlite3 - single file: data/iai.db
# Tables:
#   diagnoses(id, saved_at, complaint, risk, risk_level, answers_json,
#             report_json, causes_json, report_text)
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'iai.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Create the table once; safe to call every time
    with _conn() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS diagnoses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            saved_at TEXT NOT NULL,
            complaint TEXT,
            risk INTEGER,
            risk_level TEXT,
            answers_json TEXT,
            report_json TEXT,
            causes_json TEXT,
            report_text TEXT
        )''')


def save_diagnosis(rec):
    # rec keys: complaint, risk, risk_level, answers, report_values, causes, report_text
    init_db()
    with _conn() as conn:
        cur = conn.execute(
            'INSERT INTO diagnoses (saved_at, complaint, risk, risk_level, answers_json, report_json, causes_json, report_text) '
            'VALUES (?,?,?,?,?,?,?,?)',
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             rec.get('complaint', ''), int(rec.get('risk', 0)), rec.get('risk_level', ''),
             json.dumps(rec.get('answers', {}), ensure_ascii=False),
             json.dumps(rec.get('report_values', {}), ensure_ascii=False),
             json.dumps(rec.get('causes', []), ensure_ascii=False),
             rec.get('report_text', '')))
        return cur.lastrowid


def list_diagnoses():
    init_db()
    with _conn() as conn:
        rows = conn.execute('SELECT id, saved_at, complaint, risk, risk_level FROM diagnoses ORDER BY id DESC').fetchall()
    return [dict(r) for r in rows]


def get_diagnosis(did):
    init_db()
    with _conn() as conn:
        row = conn.execute('SELECT * FROM diagnoses WHERE id=?', (did,)).fetchone()
    if not row:
        return None
    d = dict(row)
    for k in ('answers_json', 'report_json', 'causes_json'):
        try:
            d[k.replace('_json', '')] = json.loads(d[k] or '{}')
        except Exception:
            d[k.replace('_json', '')] = {}
    return d


def delete_diagnosis(did):
    init_db()
    with _conn() as conn:
        conn.execute('DELETE FROM diagnoses WHERE id=?', (did,))
    return True
