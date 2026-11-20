# import cv2
# from pathlib import Path

# from camera.camera import Camera
# from face.detector import FaceDetector


# # --------------------------------------------------
# # SETTINGS
# # --------------------------------------------------

# TOTAL_IMAGES = 10

# POSES = [
#     "Front - Normal",
#     "Front - Look Slightly Up",
#     "Front - Look Slightly Down",
#     "Turn Slightly Left",
#     "Turn More Left",
#     "Left Profile",
#     "Turn Slightly Right",
#     "Turn More Right",
#     "Right Profile",
#     "Front - Slight Head Tilt"
# ]


# # --------------------------------------------------
# # CAPTURE FUNCTION
# # --------------------------------------------------

# def capture_dataset(roll_number):

#     # Dataset folder
#     dataset_dir = (
#         Path(__file__).resolve().parent.parent
#         / "dataset"
#         / "students"
#         / str(roll_number)
#     )

#     dataset_dir.mkdir(
#         parents=True,
#         exist_ok=True
#     )

#     print("\n================================")
#     print("      FACE DATA COLLECTION")
    
#     print("================================")
#     print(f"Roll Number : {roll_number}")
#     print(f"Images      : {TOTAL_IMAGES}")
#     print("================================")

#     camera = Camera(source=0)

#     if not camera.start():
#         return

#     detector = FaceDetector()

#     image_count = 0

#     while image_count < TOTAL_IMAGES:

#         success, frame = camera.read()

#         if not success:
#             print("❌ Could not read camera frame.")
#             break

#         faces = detector.detect(frame)

#         # ------------------------------------------
#         # Draw detected faces
#         # ------------------------------------------

#         for (x, y, w, h) in faces:

#             cv2.rectangle(
#                 frame,
#                 (x, y),
#                 (x + w, y + h),
#                 (0, 255, 0),
#                 2
#             )

#         # ------------------------------------------
#         # Current pose
#         # ------------------------------------------

#         pose = POSES[image_count]

#         cv2.putText(
#             frame,
#             f"Image: {image_count + 1}/{TOTAL_IMAGES}",
#             (20, 35),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.8,
#             (0, 255, 0),
#             2
#         )

#         cv2.putText(
#             frame,
#             pose,
#             (20, 70),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.65,
#             (0, 255, 255),
#             2
#         )

#         cv2.putText(
#             frame,
#             "Press SPACE to capture",
#             (20, 105),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.65,
#             (255, 255, 255),
#             2
#         )

#         cv2.putText(
#             frame,
#             "Press Q to cancel",
#             (20, 140),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.65,
#             (0, 0, 255),
#             2
#         )

#         cv2.putText(
#             frame,
#             f"Faces detected: {len(faces)}",
#             (20, 175),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.65,
#             (0, 255, 0),
#             2
#         )

#         cv2.imshow(
#             "AI Attendance - Face Dataset",
#             frame
#         )

#         key = cv2.waitKey(1) & 0xFF

#         # ------------------------------------------
#         # Cancel
#         # ------------------------------------------

#         if key == ord("q"):
#             print("\n❌ Dataset collection cancelled.")
#             break

#         # ------------------------------------------
#         # Capture
#         # ------------------------------------------

#         if key == 32:  # SPACE

#             # Exactly one face required
#             if len(faces) != 1:

#                 print(
#                     f"⚠️ Cannot capture. "
#                     f"Detected {len(faces)} faces."
#                 )

#                 continue

#             x, y, w, h = faces[0]

#             # Face must be reasonably large
#             if w < 100 or h < 100:

#                 print(
#                     "⚠️ Face is too far from camera. "
#                     "Move closer."
#                 )

#                 continue

#             # Crop face
#             face_image = frame[
#                 y:y + h,
#                 x:x + w
#             ]

#             image_count += 1

#             filename = (
#                 dataset_dir
#                 / f"{image_count}.jpg"
#             )

#             cv2.imwrite(
#                 str(filename),
#                 face_image
#             )

#             print(
#                 f"✅ Image {image_count}/"
#                 f"{TOTAL_IMAGES} saved: {filename}"
#             )

#     camera.release()

#     if image_count == TOTAL_IMAGES:

#         print("\n================================")
#         print("✅ DATASET COLLECTION COMPLETE")
#         print("================================")
#         print(f"Roll Number : {roll_number}")
#         print(f"Images      : {image_count}")
#         print(f"Location    : {dataset_dir}")
#         print("================================")

#     else:

#         print(
#             f"\n⚠️ Collection stopped at "
#             f"{image_count}/{TOTAL_IMAGES} images."
#         )


# # --------------------------------------------------
# # MAIN
# # --------------------------------------------------

# if __name__ == "__main__":

#     roll_number = input(
#         "Enter student roll number: "
#     ).strip()

#     if not roll_number:

#         print("❌ Roll number cannot be empty.")

#     else:

#         capture_dataset(roll_number)
import cv2
from pathlib import Path

from camera.camera import Camera
from face.detector import FaceDetector


# ==========================================
# SETTINGS
# ==========================================

TOTAL_IMAGES = 10

# Face crop margins
SIDE_MARGIN = 0.35
TOP_MARGIN = 0.55
BOTTOM_MARGIN = 0.35

POSES = [
    "Front - Normal",
    "Front - Look Slightly Up",
    "Front - Look Slightly Down",
    "Turn Slightly Left",
    "Turn More Left",
    "Left Profile",
    "Turn Slightly Right",
    "Turn More Right",
    "Right Profile",
    "Front - Slight Head Tilt"
]


# ==========================================
# FACE CROP FUNCTION
# ==========================================

def crop_full_face(frame, face):

    x, y, w, h = face

    height, width = frame.shape[:2]

    # Add margins around detected face
    extra_x = int(w * SIDE_MARGIN)
    extra_top = int(h * TOP_MARGIN)
    extra_bottom = int(h * BOTTOM_MARGIN)

    # Expanded coordinates
    x1 = max(0, x - extra_x)
    y1 = max(0, y - extra_top)

    x2 = min(width, x + w + extra_x)
    y2 = min(height, y + h + extra_bottom)

    # Crop original color frame
    face_image = frame[y1:y2, x1:x2].copy()

    if face_image.size == 0:
        return None

    return face_image


# ==========================================
# CAPTURE FUNCTION
# ==========================================

def capture_dataset(roll_number):

    dataset_dir = (
        Path(__file__).resolve().parent.parent
        / "dataset"
        / "students"
        / str(roll_number)
    )

    dataset_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\n================================")
    print("      FACE DATA COLLECTION")
    print("================================")
    print(f"Roll Number : {roll_number}")
    print(f"Images      : {TOTAL_IMAGES}")
    print("================================")

    camera = Camera(source=0)

    if not camera.start():
        return

    detector = FaceDetector()

    image_count = 0

    try:

        while image_count < TOTAL_IMAGES:

            success, frame = camera.read()

            if not success or frame is None:
                print("❌ Could not read camera frame.")
                break

            # Preserve original color image
            original_frame = frame.copy()

            faces = detector.detect(frame)

            # Draw detection rectangles only on display frame
            display_frame = frame.copy()

            for (x, y, w, h) in faces:

                cv2.rectangle(
                    display_frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            pose = POSES[image_count]

            cv2.putText(
                display_frame,
                f"Image: {image_count + 1}/{TOTAL_IMAGES}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                display_frame,
                pose,
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            cv2.putText(
                display_frame,
                "SPACE: Capture",
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.putText(
                display_frame,
                "Q: Cancel",
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 0, 255),
                2
            )

            cv2.putText(
                display_frame,
                f"Faces detected: {len(faces)}",
                (20, 175),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "AI Attendance - Face Dataset",
                display_frame
            )

            key = cv2.waitKey(1) & 0xFF

            # Cancel
            if key == ord("q"):

                print("\n❌ Dataset collection cancelled.")
                break

            # Capture
            if key == 32:

                if len(faces) != 1:

                    print(
                        f"⚠️ Cannot capture. "
                        f"Detected {len(faces)} faces."
                    )

                    continue

                x, y, w, h = faces[0]

                if w < 120 or h < 120:

                    print(
                        "⚠️ Face is too small. "
                        "Move closer to camera."
                    )

                    continue

                # Crop with extra margins
                face_image = crop_full_face(
                    original_frame,
                    faces[0]
                )

                if face_image is None:
                    print("❌ Invalid face crop.")
                    continue

                crop_height, crop_width = face_image.shape[:2]

                if crop_width < 100 or crop_height < 100:
                    print("❌ Cropped image is too small.")
                    continue

                image_count += 1

                filename = (
                    dataset_dir
                    / f"{image_count}.jpg"
                )

                # Save COLOR image
                saved = cv2.imwrite(
                    str(filename),
                    face_image
                )

                if not saved:

                    image_count -= 1
                    print("❌ Image could not be saved.")
                    continue

                print(
                    f"✅ Image {image_count}/{TOTAL_IMAGES} saved"
                )

                print(
                    f"   Size: {crop_width} x {crop_height}"
                )

    finally:

        camera.release()
        cv2.destroyAllWindows()

    if image_count == TOTAL_IMAGES:

        print("\n================================")
        print("✅ DATASET COLLECTION COMPLETE")
        print("================================")
        print(f"Roll Number : {roll_number}")
        print(f"Images      : {image_count}")
        print(f"Location    : {dataset_dir}")
        print("================================")

    else:

        print(
            f"\n⚠️ Collection stopped at "
            f"{image_count}/{TOTAL_IMAGES} images."
        )


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    roll_number = input(
        "Enter student roll number: "
    ).strip()

    if not roll_number:

        print("❌ Roll number cannot be empty.")

    else:

        capture_dataset(roll_number)