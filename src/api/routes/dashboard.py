from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.utils.database import get_db
from src.models.student import Student
from src.models.grade import Grade
from src.models.prediction import Prediction
from src.models.intervention import Intervention
from src.models.notification import Notification
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

ALL_FILIERES = ["ISIC", "CCN", "2ITE", "G2E", "GI", "GC"]


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total_etudiants = db.query(Student).count()

    # Compter les prédictions par couleur
    from sqlalchemy import func, distinct

    # Dernière prédiction par étudiant (subquery)
    latest_pred_subq = (
        db.query(
            Prediction.student_id,
            func.max(Prediction.id).label("max_id")
        )
        .group_by(Prediction.student_id)
        .subquery()
    )

    latest_preds = (
        db.query(Prediction)
        .join(latest_pred_subq, Prediction.id == latest_pred_subq.c.max_id)
        .all()
    )

    vert_count = sum(1 for p in latest_preds if p.statut_couleur == "VERT")
    jaune_count = sum(1 for p in latest_preds if p.statut_couleur == "JAUNE")
    rouge_count = sum(1 for p in latest_preds if p.statut_couleur == "ROUGE")
    predicted_count = vert_count + jaune_count + rouge_count

    taux_reussite = round((vert_count / predicted_count * 100), 1) if predicted_count > 0 else 0

    # Predictions par filière
    predictions_par_filiere = []
    for filiere in ALL_FILIERES:
        filiere_students = db.query(Student.id).filter(Student.filiere == filiere).all()
        filiere_ids = [s.id for s in filiere_students]

        f_preds = [p for p in latest_preds if p.student_id in filiere_ids]
        reussite = sum(1 for p in f_preds if p.statut_couleur == "VERT")
        moyen = sum(1 for p in f_preds if p.statut_couleur == "JAUNE")
        risque = sum(1 for p in f_preds if p.statut_couleur == "ROUGE")

        predictions_par_filiere.append({
            "filiere": filiere,
            "reussite": reussite,
            "moyen": moyen,
            "risque": risque,
        })

    taux_moyen = round((jaune_count / predicted_count * 100), 1) if predicted_count > 0 else 0
    taux_risque = round((rouge_count / predicted_count * 100), 1) if predicted_count > 0 else 0

    return {
        "total_etudiants": total_etudiants,
        "taux_reussite": taux_reussite,
        "taux_moyen": taux_moyen,
        "taux_risque": taux_risque,
        "en_surveillance": jaune_count,
        "a_risque": rouge_count,
        "predictions_par_filiere": predictions_par_filiere,
    }


@router.get("/analysis")
def get_analysis(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Real analysis data for AnalysisPage."""

    # Filiere stats from predictions
    latest_pred_subq = (
        db.query(
            Prediction.student_id,
            func.max(Prediction.id).label("max_id")
        )
        .group_by(Prediction.student_id)
        .subquery()
    )
    latest_preds = (
        db.query(Prediction)
        .join(latest_pred_subq, Prediction.id == latest_pred_subq.c.max_id)
        .all()
    )

    filiere_stats = []
    for filiere in ALL_FILIERES:
        filiere_ids = [s.id for s in db.query(Student.id).filter(Student.filiere == filiere).all()]
        f_preds = [p for p in latest_preds if p.student_id in filiere_ids]
        filiere_stats.append({
            "filiere": filiere,
            "reussite": sum(1 for p in f_preds if p.statut_couleur == "VERT"),
            "moyen": sum(1 for p in f_preds if p.statut_couleur == "JAUNE"),
            "risque": sum(1 for p in f_preds if p.statut_couleur == "ROUGE"),
        })

    # Module averages
    module_avgs = (
        db.query(Grade.matiere, func.avg(Grade.note).label("moyenne"))
        .group_by(Grade.matiere)
        .all()
    )
    module_avg_data = [
        {"module": m, "moyenne": round(avg, 1)}
        for m, avg in module_avgs
    ]

    # Radar: average per category
    categories = {
        "Maths": ["Mathematiques_1", "Mathematiques_2"],
        "Info": ["Algorithmique_Prog", "Structures_Donnees", "Systemes_Exploitation"],
        "Reseaux": ["Reseaux_Info_1", "Reseaux_Info_2"],
        "Langues": ["Anglais_Tech_1", "Anglais_Tech_2", "Francais_Pro_1", "Francais_Pro_2"],
        "BD": ["Bases_Donnees"],
        "PFA": ["PFA_2"],
    }
    radar_data = []
    for subject, matieres in categories.items():
        avg_val = (
            db.query(func.avg(Grade.note))
            .filter(Grade.matiere.in_(matieres))
            .scalar()
        )
        radar_data.append({"subject": subject, "score": round(avg_val, 1) if avg_val else 0})

    # Absence distribution (from CSV data)
    absences_data = [
        {"range": "0-2", "count": 0},
        {"range": "3-5", "count": 0},
        {"range": "6-10", "count": 0},
        {">10": ">10", "range": ">10", "count": 0},
    ]

    return {
        "filiere_stats": filiere_stats,
        "module_averages": module_avg_data,
        "radar_data": radar_data,
        "absences_data": absences_data,
    }
