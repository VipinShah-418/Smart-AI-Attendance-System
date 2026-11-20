
from database.db import get_connection

def add_student(roll_number, name, class_name, section):

    # Basic validation
    if not roll_number:
        print("❌ Roll number cannot be empty.")
        return False

    if not name:
        print("❌ Student name cannot be empty.")
        return False

    if not class_name:
        print("❌ Class cannot be empty.")
        return False

    if not section:
        print("❌ Section cannot be empty.")
        return False

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check whether roll number already exists
        cursor.execute("""
            SELECT id, name
            FROM students
            WHERE roll_number = ?
        """, (roll_number,))

        existing_student = cursor.fetchone()

        if existing_student:
            print(
                f"⚠️ Roll number {roll_number} already exists "
                f"for student '{existing_student[1]}'."
            )
            return False

        # Insert student
        cursor.execute("""
            INSERT INTO students
            (roll_number, name, class_name, section)
            VALUES (?, ?, ?, ?)
        """, (
            roll_number,
            name,
            class_name,
            section
        ))

        connection.commit()

        print("\n✅ Student added successfully!")
        print("--------------------------------")
        print(f"Roll Number : {roll_number}")
        print(f"Name        : {name}")
        print(f"Class       : {class_name}")
        print(f"Section     : {section}")
        print("--------------------------------")

        return True

    except Exception as e:

        connection.rollback()

        print(f"❌ Database error: {e}")

        return False

    finally:
        connection.close()


if __name__ == "__main__":

    print("\n===== STUDENT REGISTRATION =====")

    roll_number = input("Enter Roll Number: ").strip()
    name = input("Enter Student Name: ").strip()
    class_name = input("Enter Class: ").strip()
    section = input("Enter Section: ").strip()

    add_student(
        roll_number,
        name,
        class_name,
        section
    )