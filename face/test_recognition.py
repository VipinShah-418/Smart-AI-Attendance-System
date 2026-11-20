import cv2

from camera.camera import Camera
from face.detector import FaceDetector
from face.recognizer import FaceRecognizer


# --------------------------------------------------
# CAMERA
# --------------------------------------------------

camera = Camera(source=0)

if not camera.start():
    exit()


# --------------------------------------------------
# FACE DETECTOR
# --------------------------------------------------

detector = FaceDetector()


# --------------------------------------------------
# FACE RECOGNIZER
# --------------------------------------------------

recognizer = FaceRecognizer()


print("\n================================")
print("      FACE RECOGNITION")
print("================================")
print("Press Q to exit.")
print("================================")


while True:

    success, frame = camera.read()

    if not success:
        print("❌ Frame not received.")
        break

    # Detect faces
    faces = detector.detect(frame)

    for (x, y, w, h) in faces:

        # Crop face
        face = frame[
            y:y + h,
            x:x + w
        ]

        try:

            student_id, confidence = (
                recognizer.recognize(face)
            )

            # LBPH confidence:
            # lower = better match
            #
            # We start with 70 as our threshold.
            if confidence < 70:

                label = (
                    f"ID: {student_id} "
                    f"Confidence: {confidence:.1f}"
                )

                box_color = (0, 255, 0)

            else:

                label = (
                    f"Unknown "
                    f"Confidence: {confidence:.1f}"
                )

                box_color = (0, 0, 255)

            # Draw box
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                box_color,
                2
            )

            # Draw label
            cv2.putText(
                frame,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                box_color,
                2
            )

        except Exception as e:

            print(
                f"⚠️ Recognition error: {e}"
            )

    cv2.imshow(
        "AI Attendance - Face Recognition",
        frame
    )

    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()