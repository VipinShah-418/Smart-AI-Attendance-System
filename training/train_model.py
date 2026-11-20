import cv2
import numpy as np
from pathlib import Path
import sys
import traceback


# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = BASE_DIR / "dataset" / "students"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "face_model.yml"


# ==========================================
# TRAIN MODEL
# ==========================================

def train_model():

    print("\n================================")
    print("       FACE MODEL TRAINING")
    print("================================")

    # Check OpenCV face module
    if not hasattr(cv2, "face"):
        raise RuntimeError(
            "OpenCV face module is missing. "
            "Install opencv-contrib-python."
        )

    # Check dataset folder
    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATASET_DIR}"
        )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    faces = []
    labels = []
    student_count = 0
    image_count = 0

    # Get student folders in sorted order
    student_folders = sorted(
        folder for folder in DATASET_DIR.iterdir()
        if folder.is_dir()
    )

    if not student_folders:
        raise RuntimeError(
            f"No student folders found in: {DATASET_DIR}"
        )

    # ======================================
    # LOAD DATASET
    # ======================================

    for student_folder in student_folders:

        try:
            student_id = int(student_folder.name)
        except ValueError:
            print(f"Skipping non-numeric folder: {student_folder.name}")
            continue

        print(f"\nStudent ID: {student_id}")

        student_images = 0

        image_files = sorted(
            list(student_folder.glob("*.jpg"))
            + list(student_folder.glob("*.jpeg"))
            + list(student_folder.glob("*.png"))
        )

        for image_path in image_files:

            image = cv2.imread(
                str(image_path),
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                print(f"Warning: Cannot read {image_path.name}")
                continue

            image = cv2.resize(image, (200, 200))

            faces.append(image)
            labels.append(student_id)

            student_images += 1
            image_count += 1

        if student_images > 0:
            student_count += 1
            print(f"Images loaded: {student_images}")
        else:
            print("Warning: No valid images found.")

    # ======================================
    # VALIDATE DATASET
    # ======================================

    if not faces:
        raise RuntimeError(
            "No valid face images found. "
            "Check dataset/students folders."
        )

    if len(set(labels)) < 1:
        raise RuntimeError("No valid student labels found.")

    print("\n================================")
    print("Starting model training...")
    print(f"Students: {student_count}")
    print(f"Images: {image_count}")
    print("================================")

    # ======================================
    # TRAIN MODEL
    # ======================================

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    label_array = np.asarray(labels, dtype=np.int32)

    recognizer.train(faces, label_array)

    # ======================================
    # SAVE MODEL SAFELY
    # ======================================

    temp_model_path = MODEL_DIR / "face_model_temp.yml"

    try:
        recognizer.write(str(temp_model_path))

        if not temp_model_path.exists() or temp_model_path.stat().st_size == 0:
            raise RuntimeError("Temporary model file was not created.")

        # Replace the previous model only after successful training.
        temp_model_path.replace(MODEL_PATH)

    finally:
        if temp_model_path.exists():
            temp_model_path.unlink()

    print("\n================================")
    print("MODEL TRAINED SUCCESSFULLY")
    print("================================")
    print(f"Students: {student_count}")
    print(f"Images: {image_count}")
    print(f"Model: {MODEL_PATH}")
    print("================================")

    return True


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    try:
        train_model()
    except Exception as error:
        print("\nMODEL TRAINING FAILED")
        print(f"Reason: {error}")
        traceback.print_exc()
        sys.exit(1)