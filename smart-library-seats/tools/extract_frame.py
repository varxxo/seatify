import cv2

video_path = "tools/library_video.mp4"

cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()

if ret:
    cv2.imwrite("tools/camera_reference.jpg", frame)
    print("Frame extracted as tools/camera_reference.jpg")
else:
    print("Could not extract frame")

cap.release()