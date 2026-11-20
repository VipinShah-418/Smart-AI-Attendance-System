import cv2

from camera.camera import Camera
from face.detector import FaceDetector


camera = Camera(source=0)

if not camera.start():
    exit()


detector = FaceDetector()


while True:

    success, frame = camera.read()

    if not success:
        print("❌ Frame read nahi hua.")
        break

    faces = detector.detect(frame)

    for (x, y, w, h) in faces:

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Face Detected",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.putText(
        frame,
        f"Faces: {len(faces)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "AI Attendance - Face Detection",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()