import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "gumasta.db"

print("Database path:", DB_PATH)

with sqlite3.connect(DB_PATH) as conn:
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    print(tables)