from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from src.utils.database import Base
from datetime import datetime, timezone

class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    type_intervention = Column(String(100))    # ex: Convocation, Entretien
    description = Column(Text)
    statut = Column(String(50), default="ouvert")  # ouvert, en_cours, fermé
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="interventions")
