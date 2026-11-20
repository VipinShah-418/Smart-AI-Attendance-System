import cv2
from pathlib import Path


class FaceRecognizer:

    def __init__(self):

        base_dir = Path(__file__).resolve().parent.parent

        model_path = (
            base_dir
            / "models"
            / "face_model.yml"
        )

        if not model_path.exists():
            raise FileNotFoundError(
                f"❌ Face model not found:\n{model_path}"
            )

        self.recognizer = (
            cv2.face.LBPHFaceRecognizer_create()
        )

        self.recognizer.read(
            str(model_path)
        )

        print("✅ Face recognition model loaded.")

    def recognize(self, face):

        gray_face = cv2.cvtColor(
            face,
            cv2.COLOR_BGR2GRAY
        )

        gray_face = cv2.resize(
            gray_face,
            (200, 200)
        )

        student_id, confidence = (
            self.recognizer.predict(gray_face)
        )

        return student_id, confidence