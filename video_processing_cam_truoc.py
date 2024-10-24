import cv2
import numpy as np
from ultralytics import YOLO
from vidgear.gears import CamGear
import cvzone
import os
from datetime import datetime

class VideoProcessor:
    def __init__(self, source, model_path, cam_path):
        self.stream = CamGear(source=source, stream_mode=True, logging=True).start()
        self.model = YOLO(model_path)
        self.class_names = self.load_class_names("coco.txt")
        self.hardcoded_polylines = {
            'area1': [(200, 100), (600, 100), (600, 200), (200, 200)],
            'area2': [(300, 300), (800, 300), (1000, 400), (300, 400)]
        }
        self.count = 0
        self.going_up = {}
        self.going_down = {}
        self.gnu = []
        self.gnd = []
        self.vehicle_status = {}

        # Directory to save images
        self.save_dir = cam_path
        os.makedirs(self.save_dir, exist_ok=True)

    def load_class_names(self, filepath):
        with open(filepath, "r") as f:
            return f.read().splitlines()

    def draw_hardcoded_polylines(self, frame):
        for name, polyline in self.hardcoded_polylines.items():
            polyline_array = np.array(polyline, dtype=np.int32)
            cv2.polylines(frame, [polyline_array], isClosed=True, color=(255, 0, 0), thickness=2)
        return frame

    def process_frame(self):
        frame = self.stream.read()
        self.count += 1
        if self.count % 3 != 0:
            return None

        frame = cv2.resize(frame, (1020, 500))
        results = self.model.track(frame, persist=True, classes=[2])

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            print("track_idstrack_ids", track_ids)

            for box, class_id, track_id in zip(boxes, class_ids, track_ids):
                self.process_box(frame, box, class_id, track_id)

        frame = self.draw_hardcoded_polylines(frame)
        return frame

    def process_box(self, frame, box, class_id, track_id):
        c = self.class_names[class_id]
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        if cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area1'], dtype=np.int32), (cx, cy), False) >= 0:
            self.going_up[track_id] = (cx, cy)
            self.vehicle_status[track_id] = "up"  # Cập nhật trạng thái phương tiện

        if track_id in self.going_up:
            if cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area2'], dtype=np.int32), (cx, cy), False) >= 0:
                if track_id not in self.vehicle_status or self.vehicle_status[track_id] != "up":
                    self.record_vehicle(frame, x1, y1, x2, y2, track_id, c, "up")
                    self.vehicle_status[track_id] = "up"  # Cập nhật trạng thái sau khi lưu

        if cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area2'], dtype=np.int32), (cx, cy), False) >= 0:
            self.going_down[track_id] = (cx, cy)
            self.vehicle_status[track_id] = "down"  # Cập nhật trạng thái phương tiện

        if track_id in self.going_down:
            if cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area1'], dtype=np.int32), (cx, cy), False) >= 0:
                if track_id not in self.vehicle_status or self.vehicle_status[track_id] != "down":
                    self.record_vehicle(frame, x1, y1, x2, y2, track_id, c, "down")
                    self.vehicle_status[track_id] = "down"  # Cập nhật trạng thái sau khi lưu

    def record_vehicle(self, frame, x1, y1, x2, y2, track_id, class_name, direction):
        # Draw rectangle and text
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
        cvzone.putTextRect(frame, f'{class_name}', (x1, y1), 1, 1)

        # Create a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(self.save_dir, f'vehicle_{track_id}_{timestamp}.jpg')
        cv2.imwrite(image_path, frame)





if __name__ == "__main__":
    # Example usage
    
    video_processor = VideoProcessor(source='https://www.youtube.com/watch?v=ByED80IKdIU', model_path='yolo11s.pt', cam_path = '/home/admin-msi/Downloads/demxe/app/images/cam_truoc')
    
    while True:
        processed_frame = video_processor.process_frame()
        if processed_frame is not None:
            cv2.imshow("Processed Frame", processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()