import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "attendance.db"


def migrate_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("================================")
    print("     DATABASE MIGRATION")
    print("================================")

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # --------------------------------
    # 1. Create attendance_sessions
    # --------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL,
            section TEXT,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            teacher_name TEXT NOT NULL,
            session_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active'
        )
    """)

    print("✅ attendance_sessions table ready.")

    # --------------------------------
    # 2. Check current attendance table
    # --------------------------------
    cursor.execute("PRAGMA table_info(attendance)")
    columns = cursor.fetchall()

    column_names = [column[1] for column in columns]

    print("Existing attendance columns:")
    print(column_names)

    # --------------------------------
    # 3. If session_id doesn't exist,
    #    add it
    # --------------------------------
    if "session_id" not in column_names:

        cursor.execute("""
            ALTER TABLE attendance
            ADD COLUMN session_id INTEGER
        """)

        print("✅ session_id column added.")

    else:
        print("ℹ️ session_id already exists.")

    connection.commit()

    # --------------------------------
    # 4. Show students
    # --------------------------------
    cursor.execute("""
        SELECT id, roll_number, name, class_name
        FROM students
        ORDER BY id
    """)

    students = cursor.fetchall()

    print("\n================================")
    print("       STUDENTS CHECK")
    print("================================")

    if students:
        for student in students:
            print(
                f"ID: {student[0]} | "
                f"Roll: {student[1]} | "
                f"Name: {student[2]} | "
                f"Class: {student[3]}"
            )
    else:
        print("⚠️ No students found.")

    # --------------------------------
    # 5. Show attendance records
    # --------------------------------
    cursor.execute("""
        SELECT id, student_id, roll_number, student_name,
               date, status, session_id
        FROM attendance
        ORDER BY id
    """)

    attendance_records = cursor.fetchall()

    print("\n================================")
    print("     ATTENDANCE CHECK")
    print("================================")

    if attendance_records:
        for record in attendance_records:
            print(
                f"ID: {record[0]} | "
                f"Student ID: {record[1]} | "
                f"Roll: {record[2]} | "
                f"Name: {record[3]} | "
                f"Date: {record[4]} | "
                f"Status: {record[5]} | "
                f"Session: {record[6]}"
            )
    else:
        print("No attendance records found.")

    connection.close()

    print("\n================================")
    print("✅ DATABASE MIGRATION COMPLETE")
    print("================================")


if __name__ == "__main__":
    migrate_database()