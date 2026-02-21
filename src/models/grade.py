from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.utils.database import Base
from datetime import datetime

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    matiere = Column(String(100))
    note = Column(Float)
    semestre = Column(String(10))
    annee_academique = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="grades")