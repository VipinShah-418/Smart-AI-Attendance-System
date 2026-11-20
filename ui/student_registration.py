
# import cv2
# import sqlite3
# import subprocess
# import sys
# import customtkinter as ctk

# from pathlib import Path
# from tkinter import messagebox

# from camera.camera import Camera
# from face.detector import FaceDetector


# # ==========================================
# # PATHS
# # ==========================================

# BASE_DIR = Path(__file__).resolve().parent.parent

# DB_PATH = BASE_DIR / "database" / "attendance.db"

# DATASET_DIR = BASE_DIR / "dataset" / "students"


# # ==========================================
# # CAPTURE POSES
# # ==========================================

# POSES = [
#     "1/10 - Look straight",
#     "2/10 - Look slightly up",
#     "3/10 - Look slightly down",
#     "4/10 - Turn slightly left",
#     "5/10 - Turn more left",
#     "6/10 - Left profile",
#     "7/10 - Turn slightly right",
#     "8/10 - Turn more right",
#     "9/10 - Right profile",
#     "10/10 - Slight head tilt",
# ]


# # ==========================================
# # DATABASE: REGISTER STUDENT
# # ==========================================

# def save_student_to_database(
#     roll_number,
#     name,
#     class_name,
#     section
# ):
#     connection = sqlite3.connect(DB_PATH)

#     try:
#         cursor = connection.cursor()

#         cursor.execute("""
#             INSERT INTO students (
#                 roll_number,
#                 name,
#                 class_name,
#                 section
#             )
#             VALUES (?, ?, ?, ?)
#         """, (
#             roll_number,
#             name,
#             class_name,
#             section
#         ))

#         connection.commit()

#         return True, "Student registered successfully."

#     except sqlite3.IntegrityError:
#         return False, "This roll number already exists."

#     except sqlite3.Error as error:
#         return False, str(error)

#     finally:
#         connection.close()


# # ==========================================
# # FACE IMAGE CAPTURE
# # ==========================================

# def capture_student_faces(roll_number):
#     student_dir = DATASET_DIR / roll_number

#     # Create the dataset directory.
#     student_dir.mkdir(parents=True, exist_ok=True)

#     # Check for previously captured images.
#     existing_images = list(student_dir.glob("*.jpg"))

#     if existing_images:
#         overwrite = messagebox.askyesno(
#             "Existing Face Images",
#             f"{len(existing_images)} image(s) already exist "
#             f"for roll number {roll_number}.\n\n"
#             "Replace the existing images?"
#         )

#         if not overwrite:
#             return

#         for image_path in existing_images:
#             image_path.unlink()

#     camera = Camera(source=0)

#     if not camera.start():
#         messagebox.showerror(
#             "Camera Error",
#             "Camera could not be opened."
#         )
#         return

#     try:
#         detector = FaceDetector()
#     except Exception as error:
#         camera.release()

#         messagebox.showerror(
#             "Face Detector Error",
#             str(error)
#         )
#         return

#     saved_count = 0
#     cancelled = False

#     try:
#         while saved_count < len(POSES):

#             success, frame = camera.read()

#             if not success:
#                 print("Could not read camera frame.")
#                 break

#             faces = detector.detect(frame)

#             # Show detected face rectangles.
#             for x, y, w, h in faces:
#                 cv2.rectangle(
#                     frame,
#                     (x, y),
#                     (x + w, y + h),
#                     (0, 255, 0),
#                     2
#                 )

#             # Display instructions.
#             cv2.putText(
#                 frame,
#                 f"Roll: {roll_number}",
#                 (20, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (255, 255, 255),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 POSES[saved_count],
#                 (20, 65),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.65,
#                 (0, 255, 255),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 f"Saved: {saved_count}/10",
#                 (20, 100),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 255, 0),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 "SPACE = Capture | Q = Cancel",
#                 (20, 135),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2
#             )

#             cv2.imshow(
#                 "Student Face Registration",
#                 frame
#             )

#             key = cv2.waitKey(1) & 0xFF

#             # Cancel capture.
#             if key == ord("q"):
#                 cancelled = True
#                 break

#             # Capture only when SPACE is pressed.
#             if key == 32:

#                 # Exactly one face must be visible.
#                 if len(faces) != 1:
#                     print(
#                         "Capture rejected: "
#                         "Keep exactly one face in the frame."
#                     )
#                     continue

#                 x, y, w, h = faces[0]

#                 face_image = frame[
#                     y:y + h,
#                     x:x + w
#                 ]

#                 if face_image.size == 0:
#                     print("Invalid face image. Try again.")
#                     continue

#                 # Convert face to grayscale.
#                 gray_face = cv2.cvtColor(
#                     face_image,
#                     cv2.COLOR_BGR2GRAY
#                 )

#                 # Save a consistent image size.
#                 gray_face = cv2.resize(
#                     gray_face,
#                     (200, 200)
#                 )

#                 image_number = saved_count + 1

#                 image_path = (
#                     student_dir / f"{image_number}.jpg"
#                 )

#                 if cv2.imwrite(
#                     str(image_path),
#                     gray_face
#                 ):
#                     saved_count += 1

#                     print(
#                         f"Saved {saved_count}/10: "
#                         f"{image_path.name}"
#                     )

#         cv2.destroyAllWindows()

#     except Exception as error:
#         messagebox.showerror(
#             "Capture Error",
#             str(error)
#         )

#     finally:
#         camera.release()
#         cv2.destroyAllWindows()

#     # After all 10 images are saved, automatically retrain the model.
#     if saved_count == len(POSES):
#         messagebox.showinfo(
#             "Capture Complete",
#             f"Successfully captured 10 face images.\n\n"
#             f"Roll Number: {roll_number}\n"
#             "The face recognition model will now train automatically.",
#             parent=None
#         )

#         try:
#             result = subprocess.run(
#                 [sys.executable, "-m", "training.train_model"],
#                 cwd=str(BASE_DIR),
#                 capture_output=True,
#                 text=True,
#                 timeout=300
#             )

#             if result.returncode == 0:
#                 messagebox.showinfo(
#                     "Training Successful",
#                     "Student face images saved and model training completed.\n\n"
#                     "The new student is ready for live attendance.\n\n"
#                     + (result.stdout[-1800:] if result.stdout.strip() else "Training completed."),
#                 )
#             else:
#                 details = (result.stderr or result.stdout or "No details available.")[-2500:]
#                 messagebox.showerror(
#                     "Training Failed",
#                     "Face images were saved, but model training failed.\n\n"
#                     "Please check the training script and terminal output.\n\n"
#                     + details
#                 )

#         except subprocess.TimeoutExpired:
#             messagebox.showerror(
#                 "Training Timed Out",
#                 "Model training took longer than 5 minutes.\n"
#                 "The images are saved; please check training/train_model.py."
#             )
#         except Exception as error:
#             messagebox.showerror(
#                 "Training Error",
#                 f"Images are saved, but automatic training could not start:\n{error}"
#             )

#     elif cancelled:

#         messagebox.showwarning(
#             "Capture Cancelled",
#             f"Capture cancelled after {saved_count} images.\n\n"
#             "Complete all 10 images before training the model."
#         )

#     else:

#         messagebox.showwarning(
#             "Capture Incomplete",
#             f"Only {saved_count}/10 images were saved.\n"
#             "Please try capturing again."
#         )


# # ==========================================
# # STUDENT REGISTRATION WINDOW
# # ==========================================

# def open_student_registration(parent):

#     window = ctk.CTkToplevel(parent)

#     window.title("Student Registration")
#     window.geometry("650x650")
#     window.resizable(False, False)

#     window.transient(parent)
#     window.grab_set()

#     registered_roll = {"value": None}

#     # Main frame.
#     main_frame = ctk.CTkFrame(
#         window,
#         corner_radius=20
#     )

#     main_frame.pack(
#         fill="both",
#         expand=True,
#         padx=25,
#         pady=25
#     )

#     # Heading.
#     ctk.CTkLabel(
#         main_frame,
#         text="Student Registration",
#         font=ctk.CTkFont(
#             size=28,
#             weight="bold"
#         )
#     ).pack(pady=(25, 5))

#     ctk.CTkLabel(
#         main_frame,
#         text="Register a student and capture face images",
#         font=ctk.CTkFont(size=14)
#     ).pack(pady=(0, 20))

#     # Form.
#     form_frame = ctk.CTkFrame(
#         main_frame,
#         fg_color="transparent"
#     )

#     form_frame.pack(padx=40, fill="x")

#     def create_field(label_text, placeholder):
#         ctk.CTkLabel(
#             form_frame,
#             text=label_text,
#             font=ctk.CTkFont(size=14, weight="bold")
#         ).pack(anchor="w", pady=(8, 3))

#         entry = ctk.CTkEntry(
#             form_frame,
#             height=40,
#             placeholder_text=placeholder
#         )

#         entry.pack(fill="x")

#         return entry

#     roll_entry = create_field(
#         "Roll Number",
#         "Enter numeric roll number"
#     )

#     name_entry = create_field(
#         "Student Name",
#         "Enter full name"
#     )

#     class_entry = create_field(
#         "Class",
#         "e.g. B.Tech CSE"
#     )

#     section_entry = create_field(
#         "Section",
#         "e.g. A"
#     )

#     # Capture button starts disabled.
#     capture_button = ctk.CTkButton(
#         main_frame,
#         text="Capture 10 Face Images",
#         width=350,
#         height=45,
#         state="disabled"
#     )

#     capture_button.pack(pady=(20, 10))

#     # ======================================
#     # SAVE STUDENT
#     # ======================================

#     def register_student():

#         roll = roll_entry.get().strip()
#         name = name_entry.get().strip()
#         class_name = class_entry.get().strip()
#         section = section_entry.get().strip()

#         if not all([
#             roll,
#             name,
#             class_name,
#             section
#         ]):
#             messagebox.showwarning(
#                 "Missing Information",
#                 "Please fill all fields.",
#                 parent=window
#             )
#             return

#         # Face recognition uses numeric folder labels.
#         if not roll.isdigit():
#             messagebox.showwarning(
#                 "Invalid Roll Number",
#                 "For this version, use a numeric roll number."
#                 ,
#                 parent=window
#             )
#             return

#         success, message = save_student_to_database(
#             roll,
#             name,
#             class_name,
#             section
#         )

#         if not success:
#             messagebox.showerror(
#                 "Registration Failed",
#                 message,
#                 parent=window
#             )
#             return

#         registered_roll["value"] = roll

#         # Lock registration fields after successful save.
#         for entry in [
#             roll_entry,
#             name_entry,
#             class_entry,
#             section_entry
#         ]:
#             entry.configure(state="disabled")

#         save_button.configure(state="disabled")

#         capture_button.configure(
#             state="normal",
#             command=lambda: capture_student_faces(
#                 registered_roll["value"]
#             )
#         )

#         messagebox.showinfo(
#             "Registration Successful",
#             f"Student registered successfully!\n\n"
#             f"Name: {name}\n"
#             f"Roll Number: {roll}\n"
#             f"Class: {class_name}\n"
#             f"Section: {section}\n\n"
#             "Now capture 10 face images.",
#             parent=window
#         )

#     save_button = ctk.CTkButton(
#         main_frame,
#         text="Save Student",
#         width=350,
#         height=45,
#         command=register_student
#     )

#     save_button.pack(pady=5)

#     ctk.CTkLabel(
#         main_frame,
#         text="Use good lighting and keep your full face visible.",
#         font=ctk.CTkFont(size=12)
#     ).pack(pady=(5, 15))

#     return window





# import cv2
# import sqlite3
# import customtkinter as ctk

# from pathlib import Path
# from tkinter import messagebox

# from camera.camera import Camera
# from face.detector import FaceDetector


# # ==========================================
# # PATHS
# # ==========================================

# BASE_DIR = Path(__file__).resolve().parent.parent

# DB_PATH = BASE_DIR / "database" / "attendance.db"

# DATASET_DIR = BASE_DIR / "dataset" / "students"


# # ==========================================
# # CAPTURE POSES
# # ==========================================

# POSES = [
#     "1/10 - Look straight",
#     "2/10 - Look slightly up",
#     "3/10 - Look slightly down",
#     "4/10 - Turn slightly left",
#     "5/10 - Turn more left",
#     "6/10 - Left profile",
#     "7/10 - Turn slightly right",
#     "8/10 - Turn more right",
#     "9/10 - Right profile",
#     "10/10 - Slight head tilt",
# ]


# # ==========================================
# # DATABASE: REGISTER STUDENT
# # ==========================================

# def save_student_to_database(
#     roll_number,
#     name,
#     class_name,
#     section
# ):
#     connection = sqlite3.connect(DB_PATH)

#     try:
#         cursor = connection.cursor()

#         cursor.execute("""
#             INSERT INTO students (
#                 roll_number,
#                 name,
#                 class_name,
#                 section
#             )
#             VALUES (?, ?, ?, ?)
#         """, (
#             roll_number,
#             name,
#             class_name,
#             section
#         ))

#         connection.commit()

#         return True, "Student registered successfully."

#     except sqlite3.IntegrityError:
#         return False, "This roll number already exists."

#     except sqlite3.Error as error:
#         return False, str(error)

#     finally:
#         connection.close()


# # ==========================================
# # FACE IMAGE CAPTURE
# # ==========================================

# def capture_student_faces(roll_number):
#     student_dir = DATASET_DIR / roll_number

#     # Create the dataset directory.
#     student_dir.mkdir(parents=True, exist_ok=True)

#     # Check for previously captured images.
#     existing_images = list(student_dir.glob("*.jpg"))

#     if existing_images:
#         overwrite = messagebox.askyesno(
#             "Existing Face Images",
#             f"{len(existing_images)} image(s) already exist "
#             f"for roll number {roll_number}.\n\n"
#             "Replace the existing images?"
#         )

#         if not overwrite:
#             return

#         for image_path in existing_images:
#             image_path.unlink()

#     camera = Camera(source=0)

#     if not camera.start():
#         messagebox.showerror(
#             "Camera Error",
#             "Camera could not be opened."
#         )
#         return

#     try:
#         detector = FaceDetector()
#     except Exception as error:
#         camera.release()

#         messagebox.showerror(
#             "Face Detector Error",
#             str(error)
#         )
#         return

#     saved_count = 0
#     cancelled = False

#     try:
#         while saved_count < len(POSES):

#             success, frame = camera.read()

#             if not success:
#                 print("Could not read camera frame.")
#                 break

#             faces = detector.detect(frame)

#             # Show detected face rectangles.
#             for x, y, w, h in faces:
#                 cv2.rectangle(
#                     frame,
#                     (x, y),
#                     (x + w, y + h),
#                     (0, 255, 0),
#                     2
#                 )

#             # Display instructions.
#             cv2.putText(
#                 frame,
#                 f"Roll: {roll_number}",
#                 (20, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (255, 255, 255),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 POSES[saved_count],
#                 (20, 65),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.65,
#                 (0, 255, 255),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 f"Saved: {saved_count}/10",
#                 (20, 100),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 (0, 255, 0),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 "SPACE = Capture | Q = Cancel",
#                 (20, 135),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 255),
#                 2
#             )

#             cv2.imshow(
#                 "Student Face Registration",
#                 frame
#             )

#             key = cv2.waitKey(1) & 0xFF

#             # Cancel capture.
#             if key == ord("q"):
#                 cancelled = True
#                 break

#             # Capture only when SPACE is pressed.
#             if key == 32:

#                 # Exactly one face must be visible.
#                 if len(faces) != 1:
#                     print(
#                         "Capture rejected: "
#                         "Keep exactly one face in the frame."
#                     )
#                     continue

#                 x, y, w, h = faces[0]

#                 face_image = frame[
#                     y:y + h,
#                     x:x + w
#                 ]

#                 if face_image.size == 0:
#                     print("Invalid face image. Try again.")
#                     continue

#                 # Convert face to grayscale.
#                 gray_face = cv2.cvtColor(
#                     face_image,
#                     cv2.COLOR_BGR2GRAY
#                 )

#                 # Save a consistent image size.
#                 gray_face = cv2.resize(
#                     gray_face,
#                     (200, 200)
#                 )

#                 image_number = saved_count + 1

#                 image_path = (
#                     student_dir / f"{image_number}.jpg"
#                 )

#                 if cv2.imwrite(
#                     str(image_path),
#                     gray_face
#                 ):
#                     saved_count += 1

#                     print(
#                         f"Saved {saved_count}/10: "
#                         f"{image_path.name}"
#                     )

#         cv2.destroyAllWindows()

#     except Exception as error:
#         messagebox.showerror(
#             "Capture Error",
#             str(error)
#         )

#     finally:
#         camera.release()
#         cv2.destroyAllWindows()

#     # Handle completion or cancellation.
#     if saved_count == len(POSES):

#         messagebox.showinfo(
#             "Capture Complete",
#             f"Successfully captured 10 face images.\n\n"
#             f"Roll Number: {roll_number}\n"
#             f"Folder: {student_dir}\n\n"
#             "Next step: Retrain the face recognition model."
#         )

#     elif cancelled:

#         messagebox.showwarning(
#             "Capture Cancelled",
#             f"Capture cancelled after {saved_count} images.\n\n"
#             "Complete all 10 images before training the model."
#         )

#     else:

#         messagebox.showwarning(
#             "Capture Incomplete",
#             f"Only {saved_count}/10 images were saved.\n"
#             "Please try capturing again."
#         )


# # ==========================================
# # STUDENT REGISTRATION WINDOW
# # ==========================================

# def open_student_registration(parent):

#     window = ctk.CTkToplevel(parent)

#     window.title("Student Registration")
#     window.geometry("650x650")
#     window.resizable(False, False)

#     window.transient(parent)
#     window.grab_set()

#     registered_roll = {"value": None}

#     # Main frame.
#     main_frame = ctk.CTkFrame(
#         window,
#         corner_radius=20
#     )

#     main_frame.pack(
#         fill="both",
#         expand=True,
#         padx=25,
#         pady=25
#     )

#     # Heading.
#     ctk.CTkLabel(
#         main_frame,
#         text="Student Registration",
#         font=ctk.CTkFont(
#             size=28,
#             weight="bold"
#         )
#     ).pack(pady=(25, 5))

#     ctk.CTkLabel(
#         main_frame,
#         text="Register a student and capture face images",
#         font=ctk.CTkFont(size=14)
#     ).pack(pady=(0, 20))

#     # Form.
#     form_frame = ctk.CTkFrame(
#         main_frame,
#         fg_color="transparent"
#     )

#     form_frame.pack(padx=40, fill="x")

#     def create_field(label_text, placeholder):
#         ctk.CTkLabel(
#             form_frame,
#             text=label_text,
#             font=ctk.CTkFont(size=14, weight="bold")
#         ).pack(anchor="w", pady=(8, 3))

#         entry = ctk.CTkEntry(
#             form_frame,
#             height=40,
#             placeholder_text=placeholder
#         )

#         entry.pack(fill="x")

#         return entry

#     roll_entry = create_field(
#         "Roll Number",
#         "Enter numeric roll number"
#     )

#     name_entry = create_field(
#         "Student Name",
#         "Enter full name"
#     )

#     class_entry = create_field(
#         "Class",
#         "e.g. B.Tech CSE"
#     )

#     section_entry = create_field(
#         "Section",
#         "e.g. A"
#     )

#     # Capture button starts disabled.
#     capture_button = ctk.CTkButton(
#         main_frame,
#         text="Capture 10 Face Images",
#         width=350,
#         height=45,
#         state="disabled"
#     )

#     capture_button.pack(pady=(20, 10))

#     # ======================================
#     # SAVE STUDENT
#     # ======================================

#     def register_student():

#         roll = roll_entry.get().strip()
#         name = name_entry.get().strip()
#         class_name = class_entry.get().strip()
#         section = section_entry.get().strip()

#         if not all([
#             roll,
#             name,
#             class_name,
#             section
#         ]):
#             messagebox.showwarning(
#                 "Missing Information",
#                 "Please fill all fields.",
#                 parent=window
#             )
#             return

#         # Face recognition uses numeric folder labels.
#         if not roll.isdigit():
#             messagebox.showwarning(
#                 "Invalid Roll Number",
#                 "For this version, use a numeric roll number."
#                 ,
#                 parent=window
#             )
#             return

#         success, message = save_student_to_database(
#             roll,
#             name,
#             class_name,
#             section
#         )

#         if not success:
#             messagebox.showerror(
#                 "Registration Failed",
#                 message,
#                 parent=window
#             )
#             return

#         registered_roll["value"] = roll

#         # Lock registration fields after successful save.
#         for entry in [
#             roll_entry,
#             name_entry,
#             class_entry,
#             section_entry
#         ]:
#             entry.configure(state="disabled")

#         save_button.configure(state="disabled")

#         capture_button.configure(
#             state="normal",
#             command=lambda: capture_student_faces(
#                 registered_roll["value"]
#             )
#         )

#         messagebox.showinfo(
#             "Registration Successful",
#             f"Student registered successfully!\n\n"
#             f"Name: {name}\n"
#             f"Roll Number: {roll}\n"
#             f"Class: {class_name}\n"
#             f"Section: {section}\n\n"
#             "Now capture 10 face images.",
#             parent=window
#         )

#     save_button = ctk.CTkButton(
#         main_frame,
#         text="Save Student",
#         width=350,
#         height=45,
#         command=register_student
#     )

#     save_button.pack(pady=5)

#     ctk.CTkLabel(
#         main_frame,
#         text="Use good lighting and keep your full face visible.",
#         font=ctk.CTkFont(size=12)
#     ).pack(pady=(5, 15))

#     return window






import cv2
import sqlite3
import subprocess
import sys
import customtkinter as ctk

from pathlib import Path
from tkinter import messagebox

from camera.camera import Camera
from face.detector import FaceDetector


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "attendance.db"

DATASET_DIR = BASE_DIR / "dataset" / "students"

DEFAULT_CLASSES = [
    "B.Tech CSE",
    "B.Tech IT",
    "B.Tech AI & ML",
    "B.Tech Data Science",
    "B.Tech ECE",
    "B.Tech Mechanical",
    "B.Tech Civil",
    "BCA",
    "MCA",
    "Other",
]


def ensure_classes_table():
    """Create a shared class list and preserve classes already used by students."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_name TEXT NOT NULL UNIQUE COLLATE NOCASE
            )
        """)
        for item in DEFAULT_CLASSES:
            connection.execute(
                "INSERT OR IGNORE INTO classes (class_name) VALUES (?)",
                (item,)
            )
        connection.execute("""
            INSERT OR IGNORE INTO classes (class_name)
            SELECT DISTINCT TRIM(class_name)
            FROM students
            WHERE class_name IS NOT NULL AND TRIM(class_name) != ''
        """)


def get_class_options():
    ensure_classes_table()
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            "SELECT class_name FROM classes ORDER BY class_name COLLATE NOCASE"
        ).fetchall()
    return [row[0] for row in rows]


def add_class_to_database(class_name):
    cleaned = " ".join(class_name.strip().split())
    if not cleaned:
        return False, "Please enter a class name."

    ensure_classes_table()
    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute(
                "INSERT INTO classes (class_name) VALUES (?)", (cleaned,)
            )
        return True, cleaned
    except sqlite3.IntegrityError:
        with sqlite3.connect(DB_PATH) as connection:
            row = connection.execute(
                "SELECT class_name FROM classes WHERE class_name = ? COLLATE NOCASE",
                (cleaned,)
            ).fetchone()
        return False, f"Class already exists: {row[0] if row else cleaned}"


# ==========================================
# CAPTURE POSES
# ==========================================

POSES = [
    "1/10 - Look straight",
    "2/10 - Look slightly up",
    "3/10 - Look slightly down",
    "4/10 - Turn slightly left",
    "5/10 - Turn more left",
    "6/10 - Left profile",
    "7/10 - Turn slightly right",
    "8/10 - Turn more right",
    "9/10 - Right profile",
    "10/10 - Slight head tilt",
]


# ==========================================
# DATABASE: REGISTER STUDENT
# ==========================================

def save_student_to_database(
    roll_number,
    name,
    class_name,
    section
):
    ensure_classes_table()
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO students (
                roll_number,
                name,
                class_name,
                section
            )
            VALUES (?, ?, ?, ?)
        """, (
            roll_number,
            name,
            class_name,
            section
        ))

        connection.commit()

        return True, "Student registered successfully."

    except sqlite3.IntegrityError:
        return False, "This roll number already exists."

    except sqlite3.Error as error:
        return False, str(error)

    finally:
        connection.close()


# ==========================================
# FACE IMAGE CAPTURE
# ==========================================

def capture_student_faces(roll_number):
    student_dir = DATASET_DIR / roll_number

    # Create the dataset directory.
    student_dir.mkdir(parents=True, exist_ok=True)

    # Check for previously captured images.
    existing_images = list(student_dir.glob("*.jpg"))

    if existing_images:
        overwrite = messagebox.askyesno(
            "Existing Face Images",
            f"{len(existing_images)} image(s) already exist "
            f"for roll number {roll_number}.\n\n"
            "Replace the existing images?"
        )

        if not overwrite:
            return

        for image_path in existing_images:
            image_path.unlink()

    camera = Camera(source=0)

    if not camera.start():
        messagebox.showerror(
            "Camera Error",
            "Camera could not be opened."
        )
        return

    try:
        detector = FaceDetector()
    except Exception as error:
        camera.release()

        messagebox.showerror(
            "Face Detector Error",
            str(error)
        )
        return

    saved_count = 0
    cancelled = False

    try:
        while saved_count < len(POSES):

            success, frame = camera.read()

            if not success:
                print("Could not read camera frame.")
                break

            faces = detector.detect(frame)

            # Show detected face rectangles.
            for x, y, w, h in faces:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            # Display instructions.
            cv2.putText(
                frame,
                f"Roll: {roll_number}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                POSES[saved_count],
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"Saved: {saved_count}/10",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "SPACE = Capture | Q = Cancel",
                (20, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Student Face Registration",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            # Cancel capture.
            if key == ord("q"):
                cancelled = True
                break

            # Capture only when SPACE is pressed.
            if key == 32:

                # Exactly one face must be visible.
                if len(faces) != 1:
                    print(
                        "Capture rejected: "
                        "Keep exactly one face in the frame."
                    )
                    continue

                x, y, w, h = faces[0]

                face_image = frame[
                    y:y + h,
                    x:x + w
                ]

                if face_image.size == 0:
                    print("Invalid face image. Try again.")
                    continue

                # Convert face to grayscale.
                gray_face = cv2.cvtColor(
                    face_image,
                    cv2.COLOR_BGR2GRAY
                )

                # Save a consistent image size.
                gray_face = cv2.resize(
                    gray_face,
                    (200, 200)
                )

                image_number = saved_count + 1

                image_path = (
                    student_dir / f"{image_number}.jpg"
                )

                if cv2.imwrite(
                    str(image_path),
                    gray_face
                ):
                    saved_count += 1

                    print(
                        f"Saved {saved_count}/10: "
                        f"{image_path.name}"
                    )

        cv2.destroyAllWindows()

    except Exception as error:
        messagebox.showerror(
            "Capture Error",
            str(error)
        )

    finally:
        camera.release()
        cv2.destroyAllWindows()

    # After all 10 images are saved, automatically retrain the model.
    if saved_count == len(POSES):
        messagebox.showinfo(
            "Capture Complete",
            f"Successfully captured 10 face images.\n\n"
            f"Roll Number: {roll_number}\n"
            "The face recognition model will now train automatically.",
            parent=None
        )

        try:
            result = subprocess.run(
                [sys.executable, "-m", "training.train_model"],
                cwd=str(BASE_DIR),
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                messagebox.showinfo(
                    "Training Successful",
                    "Student face images saved and model training completed.\n\n"
                    "The new student is ready for live attendance.\n\n"
                    + (result.stdout[-1800:] if result.stdout.strip() else "Training completed."),
                )
            else:
                details = (result.stderr or result.stdout or "No details available.")[-2500:]
                messagebox.showerror(
                    "Training Failed",
                    "Face images were saved, but model training failed.\n\n"
                    "Please check the training script and terminal output.\n\n"
                    + details
                )

        except subprocess.TimeoutExpired:
            messagebox.showerror(
                "Training Timed Out",
                "Model training took longer than 5 minutes.\n"
                "The images are saved; please check training/train_model.py."
            )
        except Exception as error:
            messagebox.showerror(
                "Training Error",
                f"Images are saved, but automatic training could not start:\n{error}"
            )

    elif cancelled:

        messagebox.showwarning(
            "Capture Cancelled",
            f"Capture cancelled after {saved_count} images.\n\n"
            "Complete all 10 images before training the model."
        )

    else:

        messagebox.showwarning(
            "Capture Incomplete",
            f"Only {saved_count}/10 images were saved.\n"
            "Please try capturing again."
        )


# ==========================================
# STUDENT REGISTRATION WINDOW
# ==========================================

def open_student_registration(parent):

    window = ctk.CTkToplevel(parent)

    window.title("Student Registration")
    window.geometry("650x650")
    window.resizable(False, False)

    window.transient(parent)
    window.grab_set()

    registered_roll = {"value": None}

    # Main frame.
    main_frame = ctk.CTkFrame(
        window,
        corner_radius=20
    )

    main_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=25
    )

    # Heading.
    ctk.CTkLabel(
        main_frame,
        text="Student Registration",
        font=ctk.CTkFont(
            size=28,
            weight="bold"
        )
    ).pack(pady=(25, 5))

    ctk.CTkLabel(
        main_frame,
        text="Register a student and capture face images",
        font=ctk.CTkFont(size=14)
    ).pack(pady=(0, 20))

    # Form.
    form_frame = ctk.CTkFrame(
        main_frame,
        fg_color="transparent"
    )

    form_frame.pack(padx=40, fill="x")

    def create_field(label_text, placeholder):
        ctk.CTkLabel(
            form_frame,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(8, 3))

        entry = ctk.CTkEntry(
            form_frame,
            height=40,
            placeholder_text=placeholder
        )

        entry.pack(fill="x")

        return entry

    roll_entry = create_field(
        "Roll Number",
        "Enter numeric roll number"
    )

    name_entry = create_field(
        "Student Name",
        "Enter full name"
    )

    ctk.CTkLabel(
        form_frame,
        text="Class",
        font=ctk.CTkFont(size=14, weight="bold")
    ).pack(anchor="w", pady=(8, 3))

    class_options = get_class_options()
    class_entry = ctk.CTkComboBox(
        form_frame,
        values=class_options,
        height=40,
        state="readonly"
    )
    class_entry.pack(fill="x")
    class_entry.set(
        "B.Tech CSE" if "B.Tech CSE" in class_options else class_options[0]
    )

    def add_new_class():
        dialog = ctk.CTkToplevel(window)
        dialog.title("Add New Class")
        dialog.geometry("360x190")
        dialog.resizable(False, False)
        dialog.transient(window)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Enter new class name",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 8))

        new_class_entry = ctk.CTkEntry(
            dialog,
            width=280,
            placeholder_text="e.g. B.Tech Cyber Security"
        )
        new_class_entry.pack(pady=5)
        new_class_entry.focus()

        def save_new_class():
            success, result = add_class_to_database(new_class_entry.get())
            if success:
                updated_options = get_class_options()
                class_entry.configure(values=updated_options)
                class_entry.set(result)
                messagebox.showinfo(
                    "Class Added",
                    f"{result} added to the class list.",
                    parent=dialog
                )
                dialog.destroy()
            else:
                messagebox.showwarning(
                    "Class Not Added", result, parent=dialog
                )

        ctk.CTkButton(
            dialog, text="Save Class", command=save_new_class
        ).pack(pady=12)

    ctk.CTkButton(
        form_frame,
        text="+ Add New Class",
        height=32,
        command=add_new_class
    ).pack(fill="x", pady=(5, 2))

    section_entry = create_field(
        "Section",
        "e.g. A"
    )

    # Capture button starts disabled.
    capture_button = ctk.CTkButton(
        main_frame,
        text="Capture 10 Face Images",
        width=350,
        height=45,
        state="disabled"
    )

    capture_button.pack(pady=(20, 10))

    # ======================================
    # SAVE STUDENT
    # ======================================

    def register_student():

        roll = roll_entry.get().strip()
        name = name_entry.get().strip()
        class_name = class_entry.get().strip()
        section = section_entry.get().strip()

        if not all([
            roll,
            name,
            class_name,
            section
        ]):
            messagebox.showwarning(
                "Missing Information",
                "Please fill all fields.",
                parent=window
            )
            return

        # Face recognition uses numeric folder labels.
        if not roll.isdigit():
            messagebox.showwarning(
                "Invalid Roll Number",
                "For this version, use a numeric roll number."
                ,
                parent=window
            )
            return

        success, message = save_student_to_database(
            roll,
            name,
            class_name,
            section
        )

        if not success:
            messagebox.showerror(
                "Registration Failed",
                message,
                parent=window
            )
            return

        registered_roll["value"] = roll

        # Lock registration fields after successful save.
        for entry in [
            roll_entry,
            name_entry,
            class_entry,
            section_entry
        ]:
            entry.configure(state="disabled")

        save_button.configure(state="disabled")

        capture_button.configure(
            state="normal",
            command=lambda: capture_student_faces(
                registered_roll["value"]
            )
        )

        messagebox.showinfo(
            "Registration Successful",
            f"Student registered successfully!\n\n"
            f"Name: {name}\n"
            f"Roll Number: {roll}\n"
            f"Class: {class_name}\n"
            f"Section: {section}\n\n"
            "Now capture 10 face images.",
            parent=window
        )

    save_button = ctk.CTkButton(
        main_frame,
        text="Save Student",
        width=350,
        height=45,
        command=register_student
    )

    save_button.pack(pady=5)

    ctk.CTkLabel(
        main_frame,
        text="Use good lighting and keep your full face visible.",
        font=ctk.CTkFont(size=12)
    ).pack(pady=(5, 15))

    return window