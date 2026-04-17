from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.utils.database import Base
from datetime import datetime
import enum


class RecommendationStatut(str, enum.Enum):
    non_lu = "non_lu"
    lu     = "lu"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id          = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    envoyeur_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message     = Column(Text, nullable=False)
    statut      = Column(Enum(RecommendationStatut), default=RecommendationStatut.non_lu)
    created_at  = Column(DateTime, default=datetime.utcnow)

    etudiant = relationship("Student", back_populates="recommendations")
    envoyeur = relationship("User")