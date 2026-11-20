from database.db import get_connection

connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT id, roll_number, name, class_name, section
    FROM students
""")

students = cursor.fetchall()

print("\n===== STUDENTS =====")

if not students:
    print("No students found.")
else:
    for student in students:
        print(
            f"ID: {student[0]} | "
            f"Roll: {student[1]} | "
            f"Name: {student[2]} | "
            f"Class: {student[3]} | "
            f"Section: {student[4]}"
        )

connection.close()