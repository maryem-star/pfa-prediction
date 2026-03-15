
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.utils.database import Base
from datetime import datetime, timezone

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    modele_utilise = Column(String(100))        # ex: RandomForest
    probabilite_reussite = Column(Float)   # ex: 0.87
    statut_couleur = Column(String(20))        # VERT, JAUNE, ROUGE
    note_predite = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="predictions")