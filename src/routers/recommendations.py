from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.utils.database import get_db
from src.auth.dependencies import get_current_user
from src.utils.permissions import verifier_acces_filiere
from src.models.recommendation import Recommendation, RecommendationStatut
from src.models.student import Student
from src.models.user import RoleEnum

router = APIRouter(prefix="/recommendations", tags=["Recommandations"])

CHEFS_AUTORISES = [
    RoleEnum.chef_departement_STIN,
    RoleEnum.chef_departement_TRI,
    RoleEnum.chef_filiere_G2E,
    RoleEnum.chef_filiere_GC,
    RoleEnum.chef_filiere_GI,
    RoleEnum.chef_filiere_ISIC,
    RoleEnum.chef_filiere_2ITE,
    RoleEnum.chef_filiere_CCN,
    RoleEnum.directeur_adjoint,
    RoleEnum.super_admin,
]


class RecommendationCreate(BaseModel):
    etudiant_id: int
    message: str


@router.post("/")
def envoyer_recommendation(
    data: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Un chef envoie une recommandation à un étudiant de sa filière."""
    if current_user.role not in CHEFS_AUTORISES:
        raise HTTPException(
            status_code=403,
            detail="Seuls les chefs peuvent envoyer des recommandations"
        )

    student = db.query(Student).filter(Student.id == data.etudiant_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if not verifier_acces_filiere(student.filiere, current_user):
        raise HTTPException(
            status_code=403,
            detail="Cet étudiant n'est pas dans votre filière/département"
        )

    reco = Recommendation(
        etudiant_id=data.etudiant_id,
        envoyeur_id=current_user.id,
        message=data.message,
    )
    db.add(reco)
    db.commit()
    db.refresh(reco)
    return {"message": "Recommandation envoyée", "id": reco.id}


@router.get("/mes-recommendations")
def mes_recommendations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Un étudiant récupère toutes ses recommandations."""
    if current_user.role != RoleEnum.etudiant:
        raise HTTPException(status_code=403, detail="Réservé aux étudiants")

    if not current_user.student_id:
        raise HTTPException(status_code=404, detail="Profil étudiant non lié")

    student = db.query(Student).filter(Student.id == current_user.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Profil étudiant introuvable")

    recos = (
        db.query(Recommendation)
        .filter(Recommendation.etudiant_id == student.id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    # Marquer comme lues
    for r in recos:
        if r.statut == RecommendationStatut.non_lu:
            r.statut = RecommendationStatut.lu
    db.commit()

    return [
        {
            "id":       r.id,
            "message":  r.message,
            "envoyeur": f"{r.envoyeur.prenom} {r.envoyeur.nom}",
            "role":     r.envoyeur.role,
            "date":     r.created_at,
            "statut":   r.statut,
        }
        for r in recos
    ]