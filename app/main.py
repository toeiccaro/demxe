import logging
from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# Import video processor và các mô hình
from .video_processing import VideoProcessor
from .db import SessionLocal  # Đảm bảo có file db.py định nghĩa SessionLocal
from .models import User, Vehicle  # Đảm bảo có file models.py định nghĩa User và Vehicle

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Khởi tạo VideoProcessor
video_processor = VideoProcessor(
    source='https://www.youtube.com/watch?v=ByED80IKdIU', 
    model_path='yolo11s.pt', 
    cam_path='/home/admin-msi/Downloads/demxe/app/images/cam_truoc'
)

# Cấu hình logging
logging.basicConfig(level=logging.DEBUG)

@app.on_event("startup")
def startup_event():
    logging.debug("Starting up the app...")

@app.get("/")
def read_root():
    return {"message": "Welcome to the vehicle counting API"}

@app.get("/process_frame")
def process_frame(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_frames)
    return {"status": "processing started"}

def process_frames():
    while True:
        frame = video_processor.process_frame()
        if frame is not None:
            pass  # Xử lý frame đã được xử lý ở đây

# Định nghĩa các mô hình người dùng
class UserCreate(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: str = None
    password: str = None

class UserResponse(BaseModel):
    id: int
    username: str
    password: str

# Định nghĩa các mô hình phương tiện
class VehicleCreate(BaseModel):
    trackId: str
    direction: str
    image_path: str

class VehicleResponse(BaseModel):
    id: int
    createdAt: datetime
    updatedAt: datetime
    trackId: str
    direction: str
    image_path: str

# Dependency để lấy phiên làm việc với cơ sở dữ liệu
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint cho người dùng
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password=user.password)  # Lưu mật khẩu trực tiếp
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

# API lấy thông tin người dùng theo ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    print("db_user:", db_user.__dict__)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# API đăng nhập
@app.post("/login/")
def login(username: str, password: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user and db_user.password == password:  # So sánh mật khẩu trực tiếp
        return {"success": True}
    return {"success": False}

# Endpoint cho phương tiện
@app.post("/vehicles/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@app.get("/vehicles/", response_model=List[VehicleResponse])
def get_vehicles(skip: int = 0, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Session = Depends(get_db)):
    query = db.query(Vehicle)
    if start_date and end_date:
        query = query.filter(Vehicle.createdAt.between(start_date, end_date))
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles

@app.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.on_event("shutdown")
def shutdown_event():
    logging.debug("Shutting down the app...")
    video_processor.stream.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
