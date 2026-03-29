import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolov8n.pt")

# Load video
video_path = "tools/library_video.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("❌ Could not open video.")
    exit()

print("▶ Running chair detection on video... Press Q to quit")

while True:
    ret, frame = cap.read()

    if not ret:
        print("✅ Video finished")
        break

    # Run YOLO detection
    results = model(frame)[0]

    # Draw results
    annotated = results.plot()

    cv2.imshow("Chair Detection", annotated)

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()