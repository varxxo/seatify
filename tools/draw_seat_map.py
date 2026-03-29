import cv2
import json

# === Global lists ===
seat_map = []
temp_points = []

def click_event(event, x, y, flags, params):
    global temp_points
    if event == cv2.EVENT_LBUTTONDOWN:
        temp_points.append((x, y))
        cv2.circle(img, (x, y), 4, (0, 255, 0), -1)
        cv2.imshow("Define Seats", img)

        # When 4 points are selected, treat it as one seat
        if len(temp_points) == 4:
            seat_id = f"S-{len(seat_map) + 1}"
            seat_map.append({"id": seat_id, "polygon": temp_points.copy()})
            print(f"✅ Seat {seat_id} saved with points {temp_points}")
            temp_points.clear()

# === Load an image of your library zone ===
img = cv2.imread("tools/library_zone.jpg")
 # Replace with your test image name
if img is None:
    print("❌ Could not load image. Place a test image (library_zone.jpg) in tools/ folder.")
    exit()

cv2.startWindowThread()
cv2.namedWindow("Define Seats", cv2.WINDOW_NORMAL)
cv2.imshow("Define Seats", img)
cv2.waitKey(1)  # helps force window refresh
cv2.setMouseCallback("Define Seats", click_event)


cv2.waitKey(0)
cv2.destroyAllWindows()

# === Save polygons to cam1 folder ===
json.dump(seat_map, open("cam1/seats_cam1.json", "w"), indent=2)
print(f"✅ Saved {len(seat_map)} seats to ../cam1/seats_cam1.json")
