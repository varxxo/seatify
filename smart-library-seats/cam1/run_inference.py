import cv2
import json
import numpy as np
import requests
from ultralytics import YOLO
import os
import time

# Use environment variable to enable UI if needed
SHOW_UI = os.getenv("SHOW_UI", "false").lower() == "true"

# Static configs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
SERVER_URL = "http://127.0.0.1:8000/update"
CONFIG_URL = "http://127.0.0.1:8000/config"

# Load YOLO model
print(f"⌛ Loading YOLO model from {MODEL_PATH}...")
model = YOLO(MODEL_PATH)
print("✅ Model loaded.")

SEAT_HISTORY = {}

def get_overlap(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    minArea = min(boxAArea, boxBArea)
    if minArea == 0: return 0
    return interArea / float(minArea)

def process_frame(frame, floor_id, mode):
    results = model(frame, verbose=False)[0]
    dets = results.boxes.data.cpu().numpy()

    # Classes: 0 (person), 56 (chair)
    # Reservation classes: backpack(24), handbag(26), bottle(39), cup(41), laptop(63), cell phone(67), book(73)
    reserved_classes = [24, 26, 39, 41, 63, 67, 73]
    persons = [b[:4] for b in dets if int(b[5]) == 0 and b[4] > 0.40]
    bags = [b[:4] for b in dets if int(b[5]) in reserved_classes and b[4] > 0.35]
    
    if mode == 'video':
        chairs = [b[:4] for b in dets if int(b[5]) == 56]
    else:
        chairs = [b[:4] for b in dets if int(b[5]) == 56 and b[4] > 0.45]

    seat_states = {}
    
    # If no chairs detected, we can't report accurate seat-level data
    # Fallback: if we see people but no chairs, maybe tell dashboard?
    # For MVP, we'll assign unique IDs to each detected chair dynamically
    for i, cbox in enumerate(chairs):
        sid = f"Seat-{i+1}"
        
        # Check if any person is sitting on this chair (high overlap)
        is_occupied = any(get_overlap(cbox, pbox) > 0.2 for pbox in persons)
        is_reserved = any(get_overlap(cbox, bbox) > 0.2 for bbox in bags)

        if is_occupied: current_state = "OCCUPIED"
        elif is_reserved: current_state = "RESERVED"
        else: current_state = "EMPTY"

        if mode == 'video':
            SEAT_HISTORY.setdefault(sid, []).append(current_state)
            if len(SEAT_HISTORY[sid]) > 5:
                SEAT_HISTORY[sid].pop(0)
            
            final_state = max(set(SEAT_HISTORY[sid]), key=SEAT_HISTORY[sid].count)
            seat_states[sid] = final_state
        else:
            seat_states[sid] = current_state

    available = list(seat_states.values()).count("EMPTY")
    occupied = list(seat_states.values()).count("OCCUPIED")
    reserved = list(seat_states.values()).count("RESERVED")
    
    # Generate relative UI Bounding Boxes
    img_h, img_w = frame.shape[:2]
    boxes_payload = []
    for i, cbox in enumerate(chairs):
        sid = f"Seat-{i+1}"
        boxes_payload.append({
            "id": sid,
            "status": seat_states.get(sid, "EMPTY"),
            "x": float(cbox[0]) / img_w * 100,
            "y": float(cbox[1]) / img_h * 100,
            "width": float(cbox[2] - cbox[0]) / img_w * 100,
            "height": float(cbox[3] - cbox[1]) / img_h * 100
        })

    print("STABLE SEAT STATES:", len(seat_states), "chairs found")
    print("AVAILABLE:", available)

    return {
        "floor_id": floor_id,
        "available": available,
        "occupied": occupied,
        "reserved": reserved,
        "seats": seat_states,
        "boxes": boxes_payload,
        "raw_detections": {"chairs": len(chairs), "persons": len(persons)}
    }, seat_states, chairs

def run():
    print("🚀 Auto-Sense Inference Started. No polygons required!")
    last_config = {}
    cap = None
    frame_count = 0

    while True:
        try:
            resp = requests.get(CONFIG_URL, timeout=3)
            config = resp.json()
        except:
            time.sleep(2)
            continue

        mode = config.get("mode", "image")
        source = config.get("source", "tools/library_video.mp4")
        floor_id = config.get("floor_id", 1)

        if config != last_config:
            print(f"🔄 Source: {source} | Floor {floor_id}")
            last_config = config
            if cap: 
                cap.release()
                cap = None
            
            # Check if source is a local image
            if source.endswith(('.jpg', '.jpeg', '.png')):
                static_img = cv2.imread(source)
            else:
                static_img = None
                cap = cv2.VideoCapture(source)

        if static_img is not None:
            frame = static_img.copy()
            time.sleep(0.5)
            frame_count = 10 # Force instant processing
        elif cap:
            ret, frame = cap.read()
            if not ret:
                if not source.startswith("http"):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            frame_count += 1
        
        if frame is not None and frame_count % 10 == 0: # Higher frequency for auto-sense
                payload, seat_states, chairs = process_frame(frame, floor_id, mode)
                try:
                    requests.post(SERVER_URL, json=payload)
                    print(f"Update: {payload['available']}/{len(chairs)} seats free.")
                except: pass

                if SHOW_UI:
                    for i, cbox in enumerate(chairs):
                        st = seat_states.get(f"Seat-{i+1}", "EMPTY")
                        col = (0, 255, 0) if st == "EMPTY" else (0, 0, 255) if st == "OCCUPIED" else (0, 255, 255)
                        cv2.rectangle(frame, (int(cbox[0]), int(cbox[1])), (int(cbox[2]), int(cbox[3])), col, 2)
                    cv2.imshow("Smart Library Feed", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): break

if __name__ == "__main__":
    run()

