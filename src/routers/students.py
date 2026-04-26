from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.auth.dependencies import get_current_user
from src.utils.permissions import (
    get_filieres_autorisees,
    verifier_acces_filiere,
    require_not_etudiant
)
from src.models.student import Student
from src.models.grade import Grade
from src.models.prediction import Prediction
from src.models.user import RoleEnum

router = APIRouter(prefix="/v2/students", tags=["Étudiants V2"])


@router.get("/")
def liste_etudiants(
    db: Session = Depends(get_db),
    current_user=Depends(require_not_etudiant)
):
    """Liste des étudiants filtrée selon le rôle de l'utilisateur connecté."""
    filieres = get_filieres_autorisees(current_user)

    query = db.query(Student)
    if filieres is not None:
        if not filieres:
            return []
        query = query.filter(Student.filiere.in_(filieres))

    return query.all()


@router.get("/{student_id}/stats")
def stats_etudiant(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Statistiques détaillées d'un étudiant spécifique."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    # Vérification des droits
    if current_user.role == RoleEnum.etudiant:
        if current_user.student_id != student_id:
            raise HTTPException(status_code=403, detail="Accès refusé")
    else:
        if not verifier_acces_filiere(student.filiere, current_user):
            raise HTTPException(
                status_code=403,
                detail="Cet étudiant n'est pas dans votre filière/département"
            )

    # Récupération des données
    grades      = db.query(Grade).filter(Grade.student_id == student_id).all()
    predictions = db.query(Prediction).filter(Prediction.student_id == student_id).all()

    # Calcul des moyennes par semestre
    moyennes_par_semestre = {}
    for g in grades:
        sem = g.semestre or "?"
        if sem not in moyennes_par_semestre:
            moyennes_par_semestre[sem] = []
        moyennes_par_semestre[sem].append(g.note)

    stats_semestres = {
        sem: round(sum(notes) / len(notes), 2)
        for sem, notes in moyennes_par_semestre.items()
    }

    derniere_prediction = predictions[-1].statut_couleur if predictions else None

    return {
        "etudiant": {
            "id":      student.id,
            "nom":     student.nom,
            "prenom":  student.prenom,
            "filiere": student.filiere,
            "annee":   student.annee,
        },
        "moyennes_par_semestre":  stats_semestres,
        "nombre_modules":         len(grades),
        "derniere_prediction":    derniere_prediction,
        "historique_predictions": [
            {"date": p.created_at, "resultat": p.statut_couleur}
            for p in predictions
        ],
    }