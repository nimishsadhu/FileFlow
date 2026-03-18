import sqlite3
from datetime import datetime
from pathlib import Path

from ..config import REPORTS_DIR


def get_db_path():
    return Path(REPORTS_DIR) / "history.db"


def _create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            folder_path   TEXT,
            total_files   INTEGER,
            total_size_mb REAL,
            categories    TEXT,
            run_date      TEXT
        )
    """)


def save_to_database(stats, folder_path):
    db_path = get_db_path()
    db_path.parent.mkdir(exist_ok=True)

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        _create_table(cursor)
        cursor.execute(
            """
            INSERT INTO runs (folder_path, total_files, total_size_mb, categories, run_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                folder_path,
                stats["total_files"],
                stats["total_size_mb"],
                str(stats["category_counts"]),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()


def load_history():
    db_path = get_db_path()
    if not db_path.exists():
        return []

    with sqlite3.connect(str(db_path)) as conn:
        cursor = conn.cursor()
        _create_table(cursor)
        cursor.execute("""
            SELECT id, folder_path, total_files, total_size_mb, categories, run_date
            FROM runs
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()

    return [
        {
            "id":            row[0],
            "folder_path":   row[1],
            "total_files":   row[2],
            "total_size_mb": row[3],
            "categories":    row[4],
            "run_date":      row[5],
        }
        for row in rows
    ]


def delete_run(run_id):
    db_path = get_db_path()
    if not db_path.exists():
        return False

    with sqlite3.connect(str(db_path)) as conn:
        conn.cursor().execute("DELETE FROM runs WHERE id = ?", (run_id,))
        conn.commit()
    return True


def clear_all_history():
    db_path = get_db_path()
    if not db_path.exists():
        return False

    with sqlite3.connect(str(db_path)) as conn:
        conn.cursor().execute("DELETE FROM runs")
        conn.commit()
    return True
