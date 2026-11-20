# import sqlite3
# from pathlib import Path


# # Database location
# BASE_DIR = Path(__file__).resolve().parent
# DB_PATH = BASE_DIR / "attendance.db"


# def get_connection():
#     """Create and return a database connection."""
#     return sqlite3.connect(DB_PATH)


# def create_tables():
#     """Create all required tables."""

#     connection = get_connection()
#     cursor = connection.cursor()

#     # Teachers table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS teachers (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             username TEXT UNIQUE NOT NULL,
#             password TEXT NOT NULL,
#             name TEXT NOT NULL
#         )
#     """)

#     # Students table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS students (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             roll_number TEXT UNIQUE NOT NULL,
#             name TEXT NOT NULL,
#             class_name TEXT NOT NULL,
#             section TEXT,
#             face_id INTEGER UNIQUE,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     # Attendance table
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS attendance (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             student_id INTEGER NOT NULL,
#             roll_number TEXT NOT NULL,
#             student_name TEXT NOT NULL,
#             class_name TEXT NOT NULL,
#             date TEXT NOT NULL,
#             time TEXT NOT NULL,
#             status TEXT NOT NULL,
#             teacher_name TEXT,
            
#             FOREIGN KEY (student_id)
#             REFERENCES students(id)
#         )
#     """)

#     connection.commit()
#     connection.close()

#     print("✅ Database and tables created successfully!")


# if __name__ == "__main__":
#     create_tables()



import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "attendance.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------
    # TEACHERS
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    """)

    # -------------------------
    # STUDENTS
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            section TEXT,
            face_id INTEGER UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -------------------------
    # ATTENDANCE SESSIONS
    # -------------------------
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

    # -------------------------
    # ATTENDANCE
    # -------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            roll_number TEXT NOT NULL,
            student_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            status TEXT NOT NULL,
            
            FOREIGN KEY (session_id)
                REFERENCES attendance_sessions(id),

            FOREIGN KEY (student_id)
                REFERENCES students(id),

            UNIQUE(session_id, student_id)
        )
    """)

    connection.commit()
    connection.close()

    print("✅ Database and tables created successfully!")


if __name__ == "__main__":
    create_tables()