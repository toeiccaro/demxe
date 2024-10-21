# app/main.py
from fastapi import FastAPI, BackgroundTasks
from .db import SessionLocal
from .models import VehicleCount
from .video_processing import VideoProcessor

app = FastAPI()
video_processor = VideoProcessor(source='https://www.youtube.com/watch?v=_TusTf0iZQU', model_path='yolo11s.pt', cam_path = '/home/admin-msi/Downloads/demxe/app/images/cam_truoc')

@app.get("/")
def read_root():
    return {"message": "Welcome to the vehicle counting API"}

@app.get("/process_frame")
def process_frame(background_tasks: BackgroundTasks):
    # Start processing frames in the background
    background_tasks.add_task(process_frames)
    return {"status": "processing started"}

def process_frames():
    while True:
        frame = video_processor.process_frame()
        if frame is not None:
            # Here you can add logic to handle the processed frame
            pass

@app.on_event("shutdown")
def shutdown_event():
    video_processor.stream.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
