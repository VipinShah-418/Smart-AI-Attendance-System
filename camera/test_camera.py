import cv2

print("Testing Windows Camera with MSMF...")

cap = cv2.VideoCapture(0, cv2.CAP_MSMF)

if not cap.isOpened():
    print("❌ MSMF could not open camera")
    exit()

print("✅ Camera opened")

while True:
    ret, frame = cap.read()

    if not ret:
        print("❌ Frame not received")
        break

    cv2.imshow("Windows Camera - AI Attendance", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()