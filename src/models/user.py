from sqlalchemy import Column, Integer, String, Enum, DateTime
from src.utils.database import Base
from datetime import datetime
import enum

class RoleEnum(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    enseignant = "enseignant"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.enseignant)
    created_at = Column(DateTime, default=datetime.utcnow) 
