# app/models.py
from sqlalchemy import Column, Integer, String, DateTime
from .db import Base
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # Chú ý: Nên mã hóa mật khẩu trước khi lưu trữ!

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    trackId = Column(String, index=True)
    direction = Column(String)
    image_path = Column(String)
