from database.db import get_connection
from datetime import datetime


# =========================================================
# 1. CREATE NEW ATTENDANCE SESSION
# =========================================================

# def create_session(
#     class_name,
#     section,
#     session_name,
#     teacher_name
# ):
def start_new_session(
    class_name,
    section,
    session_name,
    teacher_name
): 
    connection = get_connection()
    cursor = connection.cursor()

    try:
        now = datetime.now()

        date = now.strftime("%Y-%m-%d")
        start_time = now.strftime("%H:%M:%S")

        cursor.execute("""
            INSERT INTO attendance_sessions (
                class_name,
                section,
                date,
                start_time,
                teacher_name,
                session_name,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            class_name,
            section,
            date,
            start_time,
            teacher_name,
            session_name,
            "Active"
        ))

        session_id = cursor.lastrowid

        connection.commit()

        print("\n================================")
        print("✅ NEW ATTENDANCE SESSION CREATED")
        print("================================")
        print(f"Session ID : {session_id}")
        print(f"Class      : {class_name}")
        print(f"Section    : {section}")
        print(f"Session    : {session_name}")
        print(f"Teacher    : {teacher_name}")
        print(f"Date       : {date}")
        print(f"Start Time : {start_time}")
        print("================================")

        return session_id

    except Exception as e:
        connection.rollback()
        print(f"❌ Session creation error: {e}")
        return None

    finally:
        connection.close()

def get_classes():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT class_name
            FROM students
            WHERE class_name IS NOT NULL
            AND TRIM(class_name) != ''
        """)

        rows = cursor.fetchall()

        # Remove duplicate classes ignoring case
        classes = {}

        for row in rows:
            class_name = row[0].strip()
            key = class_name.lower()

            if key not in classes:
                classes[key] = class_name

        return sorted(classes.values(), key=str.lower)

    finally:
        connection.close()

def get_sections(class_name):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT DISTINCT section
            FROM students
            WHERE LOWER(TRIM(class_name))
                = LOWER(TRIM(?))
            AND section IS NOT NULL
            AND TRIM(section) != ''
            ORDER BY section
        """, (class_name,))

        return [row[0] for row in cursor.fetchall()]

    finally:
        connection.close()

def get_students_for_class(class_name, section=None):
    connection = get_connection()
    cursor = connection.cursor()

    try:

        if section:
            cursor.execute("""
                SELECT
                    id,
                    roll_number,
                    name,
                    class_name,
                    section
                FROM students
                WHERE LOWER(TRIM(class_name))
                    = LOWER(TRIM(?))
                AND LOWER(TRIM(COALESCE(section, '')))
                    = LOWER(TRIM(?))
                ORDER BY roll_number
            """, (
                class_name,
                section
            ))

        else:
            cursor.execute("""
                SELECT
                    id,
                    roll_number,
                    name,
                    class_name,
                    section
                FROM students
                WHERE LOWER(TRIM(class_name))
                    = LOWER(TRIM(?))
                ORDER BY roll_number
            """, (class_name,))

        return cursor.fetchall()

    finally:
        connection.close()

def get_sessions(class_name, section=None):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        if section:
            cursor.execute("""
                SELECT
                    id,
                    session_name,
                    date,
                    start_time,
                    end_time,
                    teacher_name,
                    status
                FROM attendance_sessions
                WHERE LOWER(TRIM(class_name))
                    = LOWER(TRIM(?))
                AND LOWER(TRIM(COALESCE(section, '')))
                    = LOWER(TRIM(?))
                ORDER BY id DESC
            """, (
                class_name,
                section
            ))

        else:
            cursor.execute("""
                SELECT
                    id,
                    session_name,
                    date,
                    start_time,
                    end_time,
                    teacher_name,
                    status
                FROM attendance_sessions
                WHERE LOWER(TRIM(class_name))
                    = LOWER(TRIM(?))
                ORDER BY id DESC
            """, (class_name,))

        return cursor.fetchall()

    finally:
        connection.close()
# =========================================================
# 2. MARK STUDENT PRESENT
# =========================================================

def mark_attendance_by_roll(
    roll_number,
    session_id
):
    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------
        # Check session
        # -----------------------------------------

        cursor.execute("""
            SELECT
                id,
                class_name,
                section,
                status
            FROM attendance_sessions
            WHERE id = ?
        """, (session_id,))

        session = cursor.fetchone()

        if session is None:
            print("❌ Attendance session not found.")
            return False, "Session not found"

        session_class = session[1]
        session_section = session[2]
        session_status = session[3]

        if session_status != "Active":
            print("⚠️ Attendance session is not active.")
            return False, "Session not active"

        # -----------------------------------------
        # Find student
        # -----------------------------------------

        cursor.execute("""
            SELECT
                id,
                roll_number,
                name,
                class_name,
                section
            FROM students
            WHERE roll_number = ?
        """, (str(roll_number),))

        student = cursor.fetchone()

        if student is None:
            print(
                f"❌ Student with roll number "
                f"{roll_number} not found."
            )

            return False, "Student not found"

        student_id = student[0]
        roll = student[1]
        name = student[2]
        class_name = student[3]
        section = student[4]

        # -----------------------------------------
        # Check class
        # -----------------------------------------

        if class_name.strip().lower() != session_class.strip().lower():
            print(
                f"⚠️ Student {roll} belongs to "
                f"class '{class_name}', not "
                f"'{session_class}'."
            )

            return False, "Wrong class"

        # -----------------------------------------
        # Check section
        # -----------------------------------------

        if (section or "").strip().lower() != (session_section or "").strip().lower():

          print(
              f"⚠️ Student {roll} belongs to "
              f"section '{section}', not "
              f"'{session_section}'."
            )

          return False, "Wrong section"

        # -----------------------------------------
        # Check if already present in THIS session
        # -----------------------------------------

        cursor.execute("""
            SELECT
                id,
                status
            FROM attendance
            WHERE session_id = ?
            AND student_id = ?
        """, (
            session_id,
            student_id
        ))

        existing = cursor.fetchone()

        if existing:

            if existing[1] == "Present":
                return True, "Already Present"

            # If record exists but status isn't Present,
            # update it to Present.
            cursor.execute("""
                UPDATE attendance
                SET
                    status = ?,
                    time = ?
                WHERE id = ?
            """, (
                "Present",
                datetime.now().strftime("%H:%M:%S"),
                existing[0]
            ))

            connection.commit()

            print(
                f"✅ Attendance updated: "
                f"{roll} - {name}"
            )

            return True, "Present"

        # -----------------------------------------
        # Create new attendance record
        # -----------------------------------------

        now = datetime.now()

        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        cursor.execute("""
            INSERT INTO attendance (
                session_id,
                student_id,
                roll_number,
                student_name,
                class_name,
                date,
                time,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            student_id,
            roll,
            name,
            class_name,
            date,
            time,
            "Present"
        ))

        connection.commit()

        print(
            f"✅ PRESENT: {roll} - {name}"
        )

        return True, "Present"

    except Exception as e:

        connection.rollback()

        print(
            f"❌ Attendance error: {e}"
        )

        return False, "Error"

    finally:
        connection.close()


# =========================================================
# 3. GET PENDING STUDENTS
# =========================================================

def get_pending_students(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                class_name,
                section
            FROM attendance_sessions
            WHERE id = ?
        """, (session_id,))

        session = cursor.fetchone()

        if session is None:
            return []

        session_class = session[0]
        session_section = session[1]

        cursor.execute("""
            SELECT
                s.id,
                s.roll_number,
                s.name,
                s.class_name,
                s.section
            FROM students s
            WHERE LOWER(TRIM(s.class_name))
                = LOWER(TRIM(?))
            AND LOWER(TRIM(COALESCE(s.section, '')))
                = LOWER(TRIM(COALESCE(?, '')))
            AND s.id NOT IN (
                SELECT student_id
                FROM attendance
                WHERE session_id = ?
                AND status = 'Present'
            )
            ORDER BY s.roll_number
        """, (
            session_class,
            session_section,
            session_id
        ))

        students = cursor.fetchall()

        return students

    finally:
        connection.close()

# =========================================================
# 4. SHOW SESSION ATTENDANCE
# =========================================================

def show_session_attendance(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                roll_number,
                student_name,
                class_name,
                time,
                status
            FROM attendance
            WHERE session_id = ?
            ORDER BY roll_number
        """, (session_id,))

        records = cursor.fetchall()

        print("\n================================")
        print("     SESSION ATTENDANCE")
        print("================================")

        if not records:
            print("No attendance records found.")
            return

        for record in records:

            print(
                f"Roll: {record[0]} | "
                f"Name: {record[1]} | "
                f"Class: {record[2]} | "
                f"Time: {record[3]} | "
                f"Status: {record[4]}"
            )

    finally:
        connection.close()


# =========================================================
# 5. GET SESSION SUMMARY
# =========================================================

def get_session_summary(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Get session class and section
        cursor.execute("""
            SELECT class_name, section
            FROM attendance_sessions
            WHERE id = ?
        """, (session_id,))

        session = cursor.fetchone()

        if session is None:
            return {
                "total": 0,
                "present": 0,
                "pending": 0,
                "absent": 0
            }

        session_class = session[0]
        session_section = session[1]

        # -----------------------------------------
        # TOTAL STUDENTS
        # -----------------------------------------

        if session_section:
            cursor.execute("""
                SELECT COUNT(*)
                FROM students
                WHERE LOWER(TRIM(class_name))
                    = LOWER(TRIM(?))
                AND LOWER(TRIM(COALESCE(section, '')))
                    = LOWER(TRIM(?))
            """, (
                session_class,
                session_section
            ))
        else:
            cursor.execute("""
                SELECT COUNT(*)
                FROM students
                WHERE LOWER(TRIM(class_name))
                    = LOWER(TRIM(?))
            """, (session_class,))

        total_students = cursor.fetchone()[0]

        # -----------------------------------------
        # PRESENT
        # -----------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE session_id = ?
            AND status = 'Present'
        """, (session_id,))

        present = cursor.fetchone()[0]

        # -----------------------------------------
        # ABSENT
        # -----------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM attendance
            WHERE session_id = ?
            AND status = 'Absent'
        """, (session_id,))

        absent = cursor.fetchone()[0]

        # -----------------------------------------
        # PENDING
        # -----------------------------------------

        pending = total_students - present - absent

        if pending < 0:
            pending = 0

        return {
            "total": total_students,
            "present": present,
            "pending": pending,
            "absent": absent
        }

    finally:
        connection.close()

# =========================================================
# 6. FINISH ATTENDANCE
# =========================================================

def finish_session(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # -----------------------------------------
        # Check session
        # -----------------------------------------

        cursor.execute("""
            SELECT
                class_name,
                section,
                status
            FROM attendance_sessions
            WHERE id = ?
        """, (session_id,))

        session = cursor.fetchone()

        if session is None:
            print("❌ Session not found.")
            return False

        session_class = session[0]
        session_section = session[1]
        session_status = session[2]

        if session_status == "Completed":
            print("⚠️ Session already completed.")
            return False

        # -----------------------------------------
        # Find students of THIS CLASS + SECTION
        # who are not Present in THIS SESSION
        # -----------------------------------------

        cursor.execute("""
            SELECT
                s.id,
                s.roll_number,
                s.name,
                s.class_name,
                s.section
            FROM students s
            WHERE LOWER(TRIM(s.class_name))
                = LOWER(TRIM(?))
            AND LOWER(TRIM(COALESCE(s.section, '')))
                = LOWER(TRIM(COALESCE(?, '')))
            AND s.id NOT IN (
                SELECT student_id
                FROM attendance
                WHERE session_id = ?
                AND status = 'Present'
            )
            ORDER BY s.roll_number
        """, (
            session_class,
            session_section,
            session_id
        ))

        pending_students = cursor.fetchall()

        now = datetime.now()

        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        # -----------------------------------------
        # Mark pending students as ABSENT
        # -----------------------------------------

        for student in pending_students:

            student_id = student[0]
            roll = student[1]
            name = student[2]
            student_class = student[3]
            student_section = student[4]

            cursor.execute("""
                INSERT INTO attendance (
                    session_id,
                    student_id,
                    roll_number,
                    student_name,
                    class_name,
                    date,
                    time,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                student_id,
                roll,
                name,
                student_class,
                date,
                time,
                "Absent"
            ))

        # -----------------------------------------
        # Complete session
        # -----------------------------------------

        cursor.execute("""
            UPDATE attendance_sessions
            SET
                end_time = ?,
                status = 'Completed'
            WHERE id = ?
        """, (
            time,
            session_id
        ))

        connection.commit()

        print("\n================================")
        print("✅ ATTENDANCE SESSION COMPLETED")
        print("================================")
        print(f"Session ID : {session_id}")
        print(f"Class      : {session_class}")
        print(f"Section    : {session_section}")
        print(f"Absent     : {len(pending_students)}")
        print(f"End Time   : {time}")
        print("================================")

        return True

    except Exception as e:

        connection.rollback()

        print(
            f"❌ Finish session error: {e}"
        )

        return False

    finally:
        connection.close()

# =========================================================
# 7. SHOW ALL SESSIONS
# =========================================================

def show_sessions():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                id,
                class_name,
                section,
                date,
                start_time,
                end_time,
                teacher_name,
                session_name,
                status
            FROM attendance_sessions
            ORDER BY id DESC
        """)

        sessions = cursor.fetchall()

        print("\n================================")
        print("       ATTENDANCE SESSIONS")
        print("================================")

        if not sessions:
            print("No sessions found.")
            return

        for session in sessions:

            print(
                f"ID: {session[0]} | "
                f"Class: {session[1]} | "
                f"Section: {session[2]} | "
                f"Date: {session[3]} | "
                f"Start: {session[4]} | "
                f"End: {session[5]} | "
                f"Teacher: {session[6]} | "
                f"Name: {session[7]} | "
                f"Status: {session[8]}"
            )

    finally:
        connection.close()