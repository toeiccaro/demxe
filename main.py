import cv2 
import numpy as np
from ultralytics import YOLO
from vidgear.gears import CamGear
import cvzone

# Initialize the video stream
stream = CamGear(source='https://www.youtube.com/watch?v=_TusTf0iZQU', stream_mode=True, logging=True).start()

# Load COCO class names
with open("coco.txt", "r") as f:
    class_names = f.read().splitlines()

# Load the YOLOv8 model
model = YOLO("yolo11s.pt")

# Hardcoded polyline coordinates (replace this with your actual coordinates)
hardcoded_polylines = {
    'area1': [(200, 100), (600, 100), (600, 200), (200, 200)],
    'area2': [(300, 300), (800, 300), (1000, 400), (300, 400)]
}

# Function to draw the hardcoded polylines on the frame
def draw_hardcoded_polylines(frame):
    for name, polyline in hardcoded_polylines.items():
        polyline_array = np.array(polyline, dtype=np.int32)
        cv2.polylines(frame, [polyline_array], isClosed=True, color=(255, 0, 0), thickness=2)
    return frame

count = 0
going_up = {}
going_down = {}
gnu = []
gnd = []

while True:
    # Read a frame from the video stream
    frame = stream.read()
    count += 1
    if count % 3 != 0:
        continue

    frame = cv2.resize(frame, (1020, 500))

    # Run YOLOv8 tracking on the frame
    results = model.track(frame, persist=True, classes=[2])

    # Check if there are any boxes in the results
    if results[0].boxes is not None and results[0].boxes.id is not None:
        # Get the boxes (x, y, w, h), class IDs, track IDs, and confidences
        boxes = results[0].boxes.xyxy.int().cpu().tolist()  # Bounding boxes
        class_ids = results[0].boxes.cls.int().cpu().tolist()  # Class IDs
        track_ids = results[0].boxes.id.int().cpu().tolist()  # Track IDs
        confidences = results[0].boxes.conf.cpu().tolist()  # Confidence score

        # Draw boxes and labels on the frame
        for box, class_id, track_id, conf in zip(boxes, class_ids, track_ids, confidences):
            c = class_names[class_id]
            x1, y1, x2, y2 = box
            
            # Calculate the center of the bounding box
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Check points against hardcoded polylines (area1 and area2)
            if cv2.pointPolygonTest(np.array(hardcoded_polylines['area1'], dtype=np.int32), (cx, cy), False) >= 0:
                going_up[track_id] = (cx, cy)
            if track_id in going_up:
                if cv2.pointPolygonTest(np.array(hardcoded_polylines['area2'], dtype=np.int32), (cx, cy), False) >= 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
                    cvzone.putTextRect(frame, f'{c}', (x1, y1), 1, 1)
                    if gnu.count(track_id) == 0:
                        gnu.append(track_id)
            if cv2.pointPolygonTest(np.array(hardcoded_polylines['area2'], dtype=np.int32), (cx, cy), False) >= 0:
                going_down[track_id] = (cx, cy)
            if track_id in going_down:
                if cv2.pointPolygonTest(np.array(hardcoded_polylines['area1'], dtype=np.int32), (cx, cy), False) >= 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
                    cvzone.putTextRect(frame, f'{c}', (x1, y1), 1, 1)
                    if gnd.count(track_id) == 0:
                        gnd.append(track_id)
    
    godown = len(gnd)
    goup = len(gnu)
    cvzone.putTextRect(frame, f'Xe vao:-{godown}', (50, 60), 2, 2)
    cvzone.putTextRect(frame, f'Xe ra:-{goup}', (50, 160), 2, 2)

    # Draw hardcoded polylines
    frame = draw_hardcoded_polylines(frame)

    # Display the frame
    cv2.imshow("RGB", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the video capture object and close the display window
stream.stop()
cv2.destroyAllWindows()
