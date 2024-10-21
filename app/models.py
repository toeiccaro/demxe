# app/models.py
from sqlalchemy import Column, Integer, String
from .db import Base

class VehicleCount(Base):
    __tablename__ = "vehicle_count"

    id = Column(Integer, primary_key=True, index=True)
    direction = Column(String, index=True)
    count = Column(Integer)
