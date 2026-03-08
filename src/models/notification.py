from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from src.utils.database import Base
from datetime import datetime, timezone

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    titre = Column(String(200))
    message = Column(Text)
    lu = Column(Boolean, default=False)
    niveau = Column(String(50), default="info")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))