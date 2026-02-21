from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.prediction import Prediction
from src.models.student import Student
from src.models.grade import Grade
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/predictions", tags=["Predictions"])

class PredictionCreate(BaseModel):
    student_id: int
    modele_utilise: Optional[str] = "RandomForest"
    probabilite_reussite: Optional[float] = None
    statut_couleur: Optional[str] = None
    note_predite: Optional[float] = None

def calculer_couleur(probabilite: float) -> str:
    if probabilite >= 0.85:
        return "VERT"
    elif probabilite >= 0.50:
        return "JAUNE"
    else:
        return "ROUGE"

@router.get("/")
def get_predictions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Prediction).all()

@router.get("/student/{student_id}")
def get_prediction_by_student(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    prediction = db.query(Prediction).filter(Prediction.student_id == student_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Aucune prédiction pour cet étudiant")
    return prediction

@router.post("/")
def create_prediction(data: PredictionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    couleur = calculer_couleur(data.probabilite_reussite) if data.probabilite_reussite else "JAUNE"

    prediction = Prediction(
        student_id=data.student_id,
        modele_utilise=data.modele_utilise,
        probabilite_reussite=data.probabilite_reussite,
        statut_couleur=couleur,
        note_predite=data.note_predite
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction

@router.get("/dashboard/couleurs")
def get_dashboard_couleurs(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verts = db.query(Prediction).filter(Prediction.statut_couleur == "VERT").count()
    jaunes = db.query(Prediction).filter(Prediction.statut_couleur == "JAUNE").count()
    rouges = db.query(Prediction).filter(Prediction.statut_couleur == "ROUGE").count()
    return {
        "VERT": verts,
        "JAUNE": jaunes,
        "ROUGE": rouges,
        "total": verts + jaunes + rouges
    } 
