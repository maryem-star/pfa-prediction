from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.grade import Grade
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/grades", tags=["Grades"])

class GradeCreate(BaseModel):
    student_id: int
    matiere: str
    note: float
    semestre: Optional[str] = None
    annee_academique: Optional[str] = None

@router.get("/")
def get_grades(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Grade).all()

@router.get("/student/{student_id}")
def get_grades_by_student(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Grade).filter(Grade.student_id == student_id).all()

@router.post("/")
def create_grade(data: GradeCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    grade = Grade(**data.model_dump())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

@router.delete("/{grade_id}")
def delete_grade(grade_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Note non trouvée")
    db.delete(grade)
    db.commit()
    return {"message": "Note supprimée"}