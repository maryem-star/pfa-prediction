from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.student import Student
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/students", tags=["Students"])

class StudentCreate(BaseModel):
    nom: str
    prenom: str
    email: Optional[str] = None
    filiere: Optional[str] = None
    annee: Optional[str] = None
    semestre: Optional[str] = None

@router.get("/")
def get_students(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Student).all()

@router.post("/")
def create_student(data: StudentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    return student

@router.put("/{student_id}")
def update_student(student_id: int, data: StudentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    for key, value in data.model_dump().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    db.delete(student)
    db.commit()
    return {"message": "Étudiant supprimé"}