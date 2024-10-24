# app/api/vehicle.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import SessionLocal
from ..models import Vehicle
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

router = APIRouter()

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

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=VehicleResponse)
def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

@router.get("/", response_model=List[VehicleResponse])
def get_vehicles(skip: int = 0, limit: int = 10, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, db: Session = Depends(get_db)):
    query = db.query(Vehicle)
    if start_date and end_date:
        query = query.filter(Vehicle.createdAt.between(start_date, end_date))
    vehicles = query.offset(skip).limit(limit).all()
    return vehicles

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle
