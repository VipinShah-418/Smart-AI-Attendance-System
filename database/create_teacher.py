import sqlite3
from pathlib import Path
import getpass

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "attendance.db"


def create_teacher():
    username = input("Enter teacher username: ").strip()
    name = input("Enter teacher full name: ").strip()
    password = getpass.getpass("Enter teacher password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if not username or not name or not password:
        print("❌ All fields are required.")
        return

    if password != confirm_password:
        print("❌ Passwords do not match.")
        return

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO teachers (username, password, name)
            VALUES (?, ?, ?)
        """, (username, password, name))

        connection.commit()
        print("\n✅ Teacher account created successfully!")
        print(f"Username: {username}")
        print(f"Name: {name}")

    except sqlite3.IntegrityError:
        print("❌ This username already exists.")

    except sqlite3.Error as error:
        print(f"❌ Database error: {error}")

    finally:
        connection.close()


if __name__ == "__main__":
    create_teacher()