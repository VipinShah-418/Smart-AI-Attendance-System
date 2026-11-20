import cv2


class Camera:

    def __init__(self, source=0):
        self.source = source
        self.cap = None

    def start(self):
        print("Testing Windows Camera with MSMF...")

        self.cap = cv2.VideoCapture(
            self.source,
            cv2.CAP_MSMF
        )

        if not self.cap.isOpened():
            print(f"❌ Unable to open camera: {self.source}")
            return False

        print(f"✅ Camera opened successfully: {self.source}")
        return True

    def read(self):
        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()

        if not ret:
            print("❌ Frame not received")
            return False, None

        return True, frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

        cv2.destroyAllWindows()

        print("📷 Camera released.")