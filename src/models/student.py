from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from src.utils.database import Base
from datetime import datetime, timezone


class Student(Base):
    __tablename__ = "students"

    id        = Column(Integer, primary_key=True, index=True)
    nom       = Column(String(100), nullable=False)
    prenom    = Column(String(100), nullable=False)
    cne       = Column(String(50), unique=True, nullable=True, index=True)
    email     = Column(String(150), unique=True)
    filiere   = Column(String(100))
    annee     = Column(String(10))
    semestre  = Column(String(10))
    absences_s1 = Column(Float, default=0)
    absences_s2 = Column(Float, default=0)
    modules_non_valides = Column(Integer, default=0)
    redoublant = Column(Integer, default=0)
    photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    grades          = relationship("Grade", back_populates="student")
    predictions     = relationship("Prediction", back_populates="student")
    interventions   = relationship("Intervention", back_populates="student")
    recommendations = relationship("Recommendation", back_populates="etudiant")