import cv2
from pathlib import Path


class FaceDetector:

    def __init__(self):

        model_path = (
            Path(__file__).resolve().parent.parent
            / "models"
            / "haarcascade_frontalface_default.xml"
        )

        self.face_cascade = cv2.CascadeClassifier(
            str(model_path)
        )

        if self.face_cascade.empty():
            raise RuntimeError(
                f"❌ Haar Cascade load nahi hua:\n{model_path}"
            )

        print("✅ Face detector loaded successfully.")

    def detect(self, frame):

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        return faces