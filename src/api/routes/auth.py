from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from src.utils.database import get_db
from src.models.user import User
from src.auth.jwt import create_access_token
from src.auth.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    nom: str
    prenom: str
    email: str
    password: str
    role: str = "etudiant"

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    user = User(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    return {"message": "Compte créé avec succès"}

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_access_token({
        "sub": user.email,
        "role": user.role.value,
        "id": user.id,
        "nom": user.nom,
        "prenom": user.prenom,
        "filiere": user.filiere if hasattr(user, "filiere") else None,
        "student_id": user.student_id if hasattr(user, "student_id") else None,
    })
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "role": user.role.value,
            "filiere": user.filiere if hasattr(user, "filiere") else None,
            "student_id": user.student_id if hasattr(user, "student_id") else None,
        }
    }

@router.get("/me")
def get_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "role": current_user.role.value,
        "filiere": current_user.filiere,
        "student_id": current_user.student_id,
    }