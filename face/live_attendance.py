import cv2
import time

from camera.camera import Camera
from face.detector import FaceDetector
from face.recognizer import FaceRecognizer

from database.attendance import (
    mark_attendance_by_roll,
    get_session_summary,
    get_pending_students,
    finish_session,
    get_classes,
    get_sections,
    get_sessions,
    start_new_session,
)


CONFIDENCE_THRESHOLD = 70


# Prevent repeated database calls
last_marked = set()
def select_session():
    print("\n================================")
    print("     ATTENDANCE SESSION")
    print("================================")

    # 1. Select Class
    classes = get_classes()

    if not classes:
        print("❌ No classes found.")
        return None

    print("\nAvailable Classes:")

    for i, class_name in enumerate(classes, start=1):
        print(f"{i}. {class_name}")

    try:
        choice = int(input("\nSelect Class: "))
        class_name = classes[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid class selection.")
        return None

    # 2. Select Section
    sections = get_sections(class_name)

    if not sections:
        print("❌ No sections found.")
        return None

    print("\nAvailable Sections:")

    for i, section in enumerate(sections, start=1):
        print(f"{i}. {section}")

    try:
        choice = int(input("\nSelect Section: "))
        section = sections[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid section selection.")
        return None

    # 3. Get sessions
    sessions = get_sessions(class_name, section)

    print("\n================================")
    print("Available Sessions")
    print("================================")

    if sessions:
        for i, session in enumerate(sessions, start=1):
            session_id = session[0]
            session_name = session[1]
            date = session[2]
            start_time = session[3]
            status = session[6]

            print(
                f"{i}. {session_name} | "
                f"{date} {start_time} | "
                f"{status}"
            )

    print(f"{len(sessions) + 1}. Start New Attendance Session")

    try:
        choice = int(input("\nSelect Session: "))
    except ValueError:
        print("❌ Invalid selection.")
        return None

    # 4. New session
    if choice == len(sessions) + 1:

        session_name = input(
            "Enter Session Name: "
        ).strip()

        if not session_name:
            print("❌ Session name cannot be empty.")
            return None

        teacher_name = input(
            "Enter Teacher Name: "
        ).strip()

        if not teacher_name:
            print("❌ Teacher name cannot be empty.")
            return None

        session_id = start_new_session(
            class_name,
            section,
            session_name,
            teacher_name
        )

        return session_id

    # 5. Existing session
    if choice < 1 or choice > len(sessions):
        print("❌ Invalid session selection.")
        return None

    selected_session = sessions[choice - 1]

    session_id = selected_session[0]
    session_name = selected_session[1]
    status = selected_session[6]

    print("\n================================")
    print("Selected Session")
    print("================================")
    print(f"Session ID : {session_id}")
    print(f"Session    : {session_name}")
    print(f"Status     : {status}")
    print("================================")

    if status != "Active":
        print("⚠️ This session is already completed.")
        print("❌ Cannot take attendance in this session.")
        return None

    return session_id

def run_live_attendance(session_id):

    print("\n==========================================")
    print("       AI SMART ATTENDANCE SYSTEM")
    print("==========================================")
    print(f"Session ID : {session_id}")
    # print(f"Teacher    : {TEACHER_NAME}")
    print("Teacher    : Selected Session")
    print("------------------------------------------")
    print("SPACE = Pause camera")
    print("Q     = Exit camera")
    print("==========================================")

    camera = Camera(source=0)

    if not camera.start():
        print("❌ Camera could not start.")
        return

    try:

        detector = FaceDetector()
        recognizer = FaceRecognizer()

        while True:

            success, frame = camera.read()

            if not success:
                print("❌ Could not read camera frame.")
                break

            faces = detector.detect(frame)

            # =========================================
            # FACE PROCESSING
            # =========================================

            for (x, y, w, h) in faces:

                face = frame[y:y + h, x:x + w]

                try:
                    student_id, confidence = recognizer.recognize(face)

                except Exception as e:
                    print(f"❌ Recognition error: {e}")
                    continue

                # =====================================
                # RECOGNIZED
                # =====================================

                if confidence < CONFIDENCE_THRESHOLD:

                    roll_number = str(student_id)

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"Roll: {roll_number}",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )

                    cv2.putText(
                        frame,
                        f"Confidence: {confidence:.1f}",
                        (x, y + h + 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 255, 255),
                        2
                    )

                    # =================================
                    # MARK ONLY ONCE PER CAMERA RUN
                    # =================================

                    if roll_number not in last_marked:

                        success_mark, status = mark_attendance_by_roll(
                            roll_number,
                            session_id
                        )

                        if success_mark:

                            if status == "Present":
                                print(
                                    f"✅ PRESENT: {roll_number}"
                                )

                            elif status == "Already Present":
                                print(
                                    f"⚠️ ALREADY PRESENT: "
                                    f"{roll_number}"
                                )

                            last_marked.add(roll_number)

                    cv2.putText(
                        frame,
                        "RECOGNIZED",
                        (x, y + h + 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

                # =====================================
                # UNKNOWN
                # =====================================

                else:

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 0, 255),
                        2
                    )

                    cv2.putText(
                        frame,
                        "UNKNOWN",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2
                    )

            # =========================================
            # SESSION SUMMARY
            # =========================================

            try:

                summary = get_session_summary(session_id)

                total = summary["total"]
                present = summary["present"]
                pending = summary["pending"]
                absent = summary["absent"]

                cv2.putText(
                    frame,
                    f"Total   : {total}",
                    (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Present : {present}",
                    (20, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Pending : {pending}",
                    (20, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Absent  : {absent}",
                    (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 0, 255),
                    2
                )

                cv2.putText(
                    frame,
                    "Q = Exit",
                    (20, 155),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2
                )

            except Exception as e:

                print(f"❌ Summary error: {e}")

            cv2.imshow(
                "AI Attendance - Live Session",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            # =========================================
            # EXIT
            # =========================================

            if key == ord("q"):

                print("\n🛑 Camera stopped.")
                print("ℹ️ Session is still ACTIVE.")
                break

    except KeyboardInterrupt:

        print("\n⚠️ Camera interrupted by user.")
        print("ℹ️ Session is still ACTIVE.")

    except Exception as e:

        print(f"\n❌ Live attendance error: {e}")

    finally:

        camera.release()

        print("📷 Attendance camera released.")

        cv2.destroyAllWindows()

    # =============================================
    # FINAL CURRENT SUMMARY
    # =============================================

    try:

        summary = get_session_summary(session_id)

        print("\n================================")
        print("       CURRENT SESSION")
        print("================================")
        print(f"Total   : {summary['total']}")
        print(f"Present : {summary['present']}")
        print(f"Pending : {summary['pending']}")
        print(f"Absent  : {summary['absent']}")
        print("================================")

    except Exception as e:

        print(f"❌ Could not get summary: {e}")


# =================================================
# SHOW PENDING STUDENTS
# =================================================

def show_pending(session_id):

    pending = get_pending_students(session_id)

    print("\n================================")
    print("       PENDING STUDENTS")
    print("================================")

    if not pending:
        print("✅ No pending students.")
        return

    for student in pending:

        print(
            f"Roll: {student[1]} | "
            f"Name: {student[2]} | "
            f"Class: {student[3]} | "
            f"Section: {student[4]}"
        )

    print("================================")


# =================================================
# MAIN
# =================================================

# =================================================
# MAIN
# =================================================

if __name__ == "__main__":

    # Select class → section → session
    SESSION_ID = select_session()

    if SESSION_ID is None:
        print("\n❌ No valid attendance session selected.")
        exit()

    while True:

        print("\n================================")
        print("       ATTENDANCE OPTIONS")
        print("================================")
        print("1. Start / Resume Attendance")
        print("2. Show Pending Students")
        print("3. Finish Attendance")
        print("4. Show Session Summary")
        print("5. Exit")
        print("================================")

        choice = input("Enter choice: ").strip()

        # =========================================
        # 1. START / RESUME
        # =========================================

        if choice == "1":

            last_marked.clear()

            run_live_attendance(SESSION_ID)

        # =========================================
        # 2. SHOW PENDING
        # =========================================

        elif choice == "2":

            show_pending(SESSION_ID)

        # =========================================
        # 3. FINISH ATTENDANCE
        # =========================================

        elif choice == "3":

            print("\n================================")
            print("       FINISH ATTENDANCE")
            print("================================")

            summary = get_session_summary(SESSION_ID)

            print(f"Total   : {summary['total']}")
            print(f"Present : {summary['present']}")
            print(f"Pending : {summary['pending']}")
            print(f"Absent  : {summary['absent']}")

            if summary["pending"] > 0:

                print(
                    "\n⚠️ Pending students will be "
                    "marked ABSENT."
                )

                confirm = input(
                    "Are you sure? (yes/no): "
                ).strip().lower()

                if confirm != "yes":

                    print("❌ Finish cancelled.")
                    continue

            success = finish_session(SESSION_ID)

            if success:

                print(
                    "\n✅ Attendance finished successfully."
                )

                final_summary = get_session_summary(
                    SESSION_ID
                )

                print("\n================================")
                print("       FINAL ATTENDANCE")
                print("================================")
                print(
                    f"Total   : {final_summary['total']}"
                )
                print(
                    f"Present : {final_summary['present']}"
                )
                print(
                    f"Pending : {final_summary['pending']}"
                )
                print(
                    f"Absent  : {final_summary['absent']}"
                )
                print("================================")

                break

        # =========================================
        # 4. SESSION SUMMARY
        # =========================================

        elif choice == "4":

            summary = get_session_summary(
                SESSION_ID
            )

            print("\n================================")
            print("       SESSION SUMMARY")
            print("================================")
            print(
                f"Total   : {summary['total']}"
            )
            print(
                f"Present : {summary['present']}"
            )
            print(
                f"Pending : {summary['pending']}"
            )
            print(
                f"Absent  : {summary['absent']}"
            )
            print("================================")

        # =========================================
        # 5. EXIT
        # =========================================

        elif choice == "5":

            print("\n👋 Attendance program closed.")
            break

        else:

            print("❌ Invalid choice.")