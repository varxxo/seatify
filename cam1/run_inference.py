import cv2
import json
import numpy as np
import os
from ultralytics import YOLO

# === CONFIG ===
MODEL_PATH = "yolov8n.pt"           # lightweight YOLO model
SEATS_PATH = "cam1/seats_cam1.json"
SOURCE_PATH = "tools/library_zone.jpg"   # can be image OR video OR 0 for webcam

# === Load seat map ===
with open(SEATS_PATH, "r") as f:
    SEATS = json.load(f)

# === Load model ===
model = YOLO(MODEL_PATH)

# === Try opening as video ===
cap = cv2.VideoCapture(SOURCE_PATH if isinstance(SOURCE_PATH, int) else str(SOURCE_PATH))
is_video = cap.isOpened()

def poly_overlap_ratio(poly, bbox, frame_shape):
    """Calculate overlap ratio between polygon (seat) and bbox (detected object)."""
    h, w = frame_shape[:2]
    x1, y1, x2, y2 = map(int, bbox)
    seat_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.fillPoly(seat_mask, [np.array(poly, np.int32)], 255)
    box_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.rectangle(box_mask, (x1, y1), (x2, y2), 255, -1)
    inter = cv2.bitwise_and(seat_mask, box_mask)
    return cv2.countNonZero(inter) / max(cv2.countNonZero(seat_mask), 1)

print("✅ Running detection... Press Q to quit.")

def process_frame(frame):
    results = model(frame)[0]
    dets = results.boxes.data.cpu().numpy() if results.boxes is not None else []
    persons = [b for b in dets if int(b[5]) == 0]
    bags = [b for b in dets if int(b[5]) == 24]

    seat_status = {}

    for seat in SEATS:
        seat_id = seat["id"]
        poly = seat["polygon"]
        occupied = any(poly_overlap_ratio(poly, p[:4], frame.shape) > 0.1 for p in persons)
        reserved = any(poly_overlap_ratio(poly, b[:4], frame.shape) > 0.1 for b in bags)

        if occupied:
            seat_status[seat_id] = "OCCUPIED"
        elif reserved:
            seat_status[seat_id] = "RESERVED"
        else:
            seat_status[seat_id] = "EMPTY"

    for seat in SEATS:
        pts = np.array(seat["polygon"], np.int32)
        color = (0, 255, 0) if seat_status[seat["id"]] == "EMPTY" else \
                (0, 255, 255) if seat_status[seat["id"]] == "RESERVED" else (0, 0, 255)
        cv2.polylines(frame, [pts], True, color, 2)
        cv2.putText(frame, seat["id"], tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return frame


if not is_video:
    # If SOURCE_PATH is an image file
    frame = cv2.imread(SOURCE_PATH)
    if frame is None:
        print("❌ Could not load image. Check path.")
        exit()
    frame = process_frame(frame)
    cv2.imshow("Seat Detection (Image)", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    # If SOURCE_PATH is a video or webcam
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = process_frame(frame)
        cv2.imshow("Seat Detection (Video)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

# --- Save output image for both image & video modes ---
import os

save_dir = os.path.join("D:", "seatify", "smart-library-seats", "tools")
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, "output_preview.jpg")

success = cv2.imwrite(save_path, frame)

if success:
    print(f"✅ Image saved successfully at: {save_path}")
else:
    print("❌ Save failed! Double-check file path or permissions.")
