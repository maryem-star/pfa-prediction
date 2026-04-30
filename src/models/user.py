from sqlalchemy import Column, Integer, String, Enum, DateTime
from src.utils.database import Base
from datetime import datetime
import enum

class RoleEnum(str, enum.Enum):
    super_admin           = "super_admin"
    directeur_adjoint     = "directeur_adjoint"
    chef_departement_STIN = "chef_departement_STIN"
    chef_departement_TRI  = "chef_departement_TRI"
    chef_filiere_G2E      = "chef_filiere_G2E"
    chef_filiere_GC       = "chef_filiere_GC"
    chef_filiere_GI       = "chef_filiere_GI"
    chef_filiere_ISIC     = "chef_filiere_ISIC"
    chef_filiere_2ITE     = "chef_filiere_2ITE"
    chef_filiere_CCN      = "chef_filiere_CCN"
    etudiant              = "etudiant"

ROLE_FILIERES = {
    RoleEnum.super_admin:           None,
    RoleEnum.directeur_adjoint:     None,
    RoleEnum.chef_departement_STIN: ["G2E", "GC", "GI"],
    RoleEnum.chef_departement_TRI:  ["ISIC", "2ITE", "CCN"],
    RoleEnum.chef_filiere_G2E:      ["G2E"],
    RoleEnum.chef_filiere_GC:       ["GC"],
    RoleEnum.chef_filiere_GI:       ["GI"],
    RoleEnum.chef_filiere_ISIC:     ["ISIC"],
    RoleEnum.chef_filiere_2ITE:     ["2ITE"],
    RoleEnum.chef_filiere_CCN:      ["CCN"],
    RoleEnum.etudiant:              [],
}

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    nom             = Column(String(100), nullable=False)
    prenom          = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum(RoleEnum), default=RoleEnum.etudiant)
    filiere         = Column(String(20), nullable=True)
    student_id      = Column(Integer, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)