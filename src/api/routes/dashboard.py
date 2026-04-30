from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.student import Student
from src.models.intervention import Intervention
from src.models.notification import Notification
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total_etudiants = db.query(Student).count()
    par_filiere = {}
    for filiere in ["ISIC", "G2E", "GI", "2ITE", "Genie-Civil", "CCN"]:
        par_filiere[filiere] = db.query(Student).filter(Student.filiere == filiere).count()
    total_interventions = db.query(Intervention).count()
    interventions_ouvertes = db.query(Intervention).filter(Intervention.statut == "ouvert").count()
    notifications_non_lues = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.lu.is_(False)
    ).count()

    return {
        "total_etudiants": total_etudiants,
        "par_filiere": par_filiere,
        "total_interventions": total_interventions,
        "interventions_ouvertes": interventions_ouvertes,
        "notifications_non_lues": notifications_non_lues
    }