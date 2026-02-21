from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.intervention import Intervention
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/interventions", tags=["Interventions"])

class InterventionCreate(BaseModel):
    student_id: int
    type_intervention: str
    description: Optional[str] = None
    statut: Optional[str] = "ouvert"

@router.get("/")
def get_interventions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Intervention).all()

@router.get("/student/{student_id}")
def get_interventions_by_student(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Intervention).filter(Intervention.student_id == student_id).all()

@router.post("/")
def create_intervention(data: InterventionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    intervention = Intervention(**data.model_dump())
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    return intervention

@router.put("/{intervention_id}/statut")
def update_statut(intervention_id: int, statut: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")
    intervention.statut = statut
    db.commit()
    return {"message": f"Statut mis à jour : {statut}"}

@router.delete("/{intervention_id}")
def delete_intervention(intervention_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention non trouvée")
    db.delete(intervention)
    db.commit()
    return {"message": "Intervention supprimée"} 
