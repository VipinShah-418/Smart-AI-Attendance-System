import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "attendance.db"

print("AI SMART ATTENDANCE SYSTEM - DATABASE RESET")
print("--------------------------------------------")

confirm = input(
    "WARNING: All students, attendance, sessions and "
    "teacher accounts will be deleted.\n"
    "Type RESET to continue: "
).strip()

if confirm != "RESET":
    print("Reset cancelled. No data deleted.")
    raise SystemExit

if not DB_PATH.exists():
    print("Database file not found:", DB_PATH)
    raise SystemExit(1)

try:
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        existing_tables = {
            row[0]
            for row in connection.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
            """).fetchall()
        }

        tables_to_clear = [
            "attendance",
            "attendance_sessions",
            "students",
            "classes",
            "teachers",
        ]

        for table in tables_to_clear:
            if table in existing_tables:
                connection.execute(f'DELETE FROM "{table}"')
                print(f"Cleared: {table}")

        # Reset auto-increment counters when available.
        sequence_exists = connection.execute("""
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
            AND name = 'sqlite_sequence'
        """).fetchone()

        if sequence_exists:
            for table in tables_to_clear:
                connection.execute(
                    "DELETE FROM sqlite_sequence WHERE name = ?",
                    (table,)
                )

    print("\nDatabase reset successfully!")

except sqlite3.Error as error:
    print("Database reset failed:", error)