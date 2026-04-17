from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from src.utils.database import Base
from datetime import datetime


class Student(Base):
    __tablename__ = "students"

    id        = Column(Integer, primary_key=True, index=True)
    nom       = Column(String(100), nullable=False)
    prenom    = Column(String(100), nullable=False)
    email     = Column(String(150), unique=True)
    filiere   = Column(String(100))
    annee     = Column(String(10))
    semestre  = Column(String(10))
    photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    grades          = relationship("Grade", back_populates="student")
    predictions     = relationship("Prediction", back_populates="student")
    interventions   = relationship("Intervention", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="etudiant")