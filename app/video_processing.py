import cv2
import numpy as np
from ultralytics import YOLO
from vidgear.gears import CamGear
import os
from datetime import datetime

class VideoProcessor:
    def __init__(self, source, model_path, cam_path):
        # Khởi tạo camera stream và model YOLO
        self.stream = CamGear(source=source, stream_mode=True, logging=True).start()
        self.model = YOLO(model_path)  # Load mô hình YOLO
        
        # Khởi tạo các khu vực và lưu trữ phương tiện
        self.area1 = [(200, 100), (600, 100), (600, 200), (200, 200)]  # Khu vực 1
        self.area2 = [(300, 300), (800, 300), (1000, 400), (300, 400)]  # Khu vực 2
        self.vehicle_in_area1 = {}  # Lưu thông tin xe trong area1
        self.vehicle_in_area2 = {}  # Lưu thông tin xe trong area2
        self.save_dir = cam_path  # Thư mục để lưu ảnh
        os.makedirs(self.save_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại
        self.vehicle_count = 0  # Đếm số lượng xe

    def is_in_area(self, point, area):
        # Hàm kiểm tra một điểm có nằm trong khu vực không
        return cv2.pointPolygonTest(np.array(area, dtype=np.int32), point, False) >= 0

    def process_frame(self):
        # Đọc một khung hình từ camera stream
        frame = self.stream.read()
        frame = cv2.resize(frame, (1020, 500))  # Resize khung hình

        # Nhận diện xe trong khung hình bằng YOLO
        results = self.model(frame)
        boxes = results[0].boxes.xyxy.int().cpu().tolist()  # Lấy bounding boxes
        if results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu().tolist()  # Lấy track ID của xe
        else:
            track_ids = []  # Hoặc xử lý theo cách khác nếu không có ID
        # Xử lý từng bounding box và track ID
        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = box
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  # Tính trung tâm bounding box

            # Kiểm tra xem xe có đang ở trong area1 không
            if self.is_in_area((cx, cy), self.area1):
                if track_id not in self.vehicle_in_area1:
                    self.vehicle_in_area1[track_id] = (cx, cy)
                    self.vehicle_count += 1  # Đếm số xe vào
                    self.record_vehicle(frame, box, track_id, "into area1")
            
            # Kiểm tra xem xe có đang ở trong area2 không
            if self.is_in_area((cx, cy), self.area2):
                if track_id not in self.vehicle_in_area2:
                    self.vehicle_in_area2[track_id] = (cx, cy)
                    self.record_vehicle(frame, box, track_id, "into area2")

        # Vẽ khu vực trên khung hình
        self.draw_areas(frame)
        return frame

    def draw_areas(self, frame):
        # Vẽ khu vực area1 và area2
        cv2.polylines(frame, [np.array(self.area1, dtype=np.int32)], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.polylines(frame, [np.array(self.area2, dtype=np.int32)], isClosed=True, color=(0, 255, 0), thickness=2)

    def record_vehicle(self, frame, box, track_id, direction):
        # Vẽ bounding box và lưu ảnh phương tiện
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(frame, f'Track ID: {track_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f'{direction}', (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Lưu ảnh phương tiện
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_path = os.path.join(self.save_dir, f'vehicle_{track_id}_{timestamp}.jpg')
        cv2.imwrite(image_path, frame)

    def get_vehicle_count(self):
        # Trả về số lượng xe đã đếm được
        return self.vehicle_count
