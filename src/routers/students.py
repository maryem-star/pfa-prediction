from fastapi import APIRouter, Depends, HTTPException, Query
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
from typing import Optional


router = APIRouter(prefix="/v2/students", tags=["Étudiants V2"])


def _build_prediction_object(prediction: Prediction, grades: list = None) -> dict:
    """Construit l'objet prediction complet attendu par le frontend."""
    if not prediction:
        return None

    # Générer facteurs de risque et recommandations à partir de la prédiction
    from src.ml_models.predict import top_facteurs_risque, recommandations

    # Reconstruire les features approximatives pour les facteurs de risque
    features_approx = {}
    if grades:
        notes_s1 = [g.note for g in grades if g.semestre == "S1"]
        notes_s2 = [g.note for g in grades if g.semestre == "S2"]
        if notes_s1:
            features_approx["Moyenne_S1"] = sum(notes_s1) / len(notes_s1)
        if notes_s2:
            features_approx["Moyenne_S2"] = sum(notes_s2) / len(notes_s2)
        if notes_s1 and notes_s2:
            features_approx["Moyenne_Annuelle"] = (
                features_approx["Moyenne_S1"] + features_approx["Moyenne_S2"]
            ) / 2

    # Si pas de notes, utiliser note_predite comme approximation
    if not features_approx and prediction.note_predite is not None:
        features_approx["Moyenne_Annuelle"] = prediction.note_predite

    facteurs = top_facteurs_risque(features_approx, prediction.statut_couleur)
    recs = recommandations(prediction.statut_couleur, facteurs)

    # Label basé sur la couleur
    label_map = {"VERT": "Réussi", "JAUNE": "À surveiller", "ROUGE": "Échec"}

    return {
        "label": label_map.get(prediction.statut_couleur, "Non évalué"),
        "probabilite": prediction.probabilite_reussite,
        "statut_couleur": prediction.statut_couleur,
        "note_predite": prediction.note_predite,
        "facteurs_risque": facteurs,
        "recommandations": recs,
        "modele_utilise": prediction.modele_utilise,
    }


def _auto_predict(student_id: int, db: Session) -> Optional[Prediction]:
    """Lance automatiquement une prédiction ML si l'étudiant n'en a aucune."""
    from src.ml_models.predict import predict as ml_predict
    import os

    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "models"
    )
    model_path = os.path.join(models_dir, "RandomForest.pkl")
    if not os.path.exists(model_path):
        return None

    # Récupérer les notes de l'étudiant pour les features
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    features = _grades_to_features(grades)

    try:
        result = ml_predict(features, modele="RandomForest")
    except Exception:
        return None

    prediction = Prediction(
        student_id=student_id,
        modele_utilise=result["modele_utilise"],
        probabilite_reussite=result["probabilite"],
        statut_couleur=result["statut_couleur"],
        note_predite=result["note_predite"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


def _grades_to_features(grades: list) -> dict:
    """Convertit les grades de la BDD en features pour le modèle ML."""
    features = {}

    notes_s1 = [g for g in grades if g.semestre == "S1"]
    notes_s2 = [g for g in grades if g.semestre == "S2"]

    # Mapper les notes par module pour S1
    for i, g in enumerate(notes_s1[:5], 1):
        features[f"Module_S1_{i}"] = g.note
    if notes_s1:
        features["Moyenne_S1"] = sum(g.note for g in notes_s1) / len(notes_s1)

    # Mapper les notes par module pour S2
    for i, g in enumerate(notes_s2[:5], 1):
        features[f"Module_S2_{i}"] = g.note
    if notes_s2:
        features["Moyenne_S2"] = sum(g.note for g in notes_s2) / len(notes_s2)

    # Moyenne annuelle
    all_notes = [g.note for g in grades]
    if all_notes:
        features["Moyenne_Annuelle"] = sum(all_notes) / len(all_notes)

    return features


@router.get("/")
def liste_etudiants(
    filiere: Optional[str] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    current_user=Depends(require_not_etudiant)
):
    """Liste des étudiants filtrée selon le rôle, avec dernière prédiction."""
    filieres = get_filieres_autorisees(current_user)

    query = db.query(Student)
    if filieres is not None:
        if not filieres:
            return []
        query = query.filter(Student.filiere.in_(filieres))

    # Filtre par filière si spécifié dans la requête
    if filiere:
        query = query.filter(Student.filiere == filiere)

    students = query.limit(limit).all()

    result = []
    for s in students:
        last_pred = (
            db.query(Prediction)
            .filter(Prediction.student_id == s.id)
            .order_by(Prediction.created_at.desc())
            .first()
        )
        result.append({
            "id": s.id,
            "nom": s.nom,
            "prenom": s.prenom,
            "cne": getattr(s, "cne", None) or getattr(s, "email", ""),
            "email": s.email,
            "filiere": s.filiere,
            "annee": s.annee,
            "prediction": {
                "statut_couleur": last_pred.statut_couleur,
                "probabilite": last_pred.probabilite_reussite,
            } if last_pred else None,
        })

    return result


@router.get("/{student_id}/stats")
def stats_etudiant(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Statistiques détaillées d'un étudiant avec prédiction ML complète."""
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
    grades = db.query(Grade).filter(Grade.student_id == student_id).all()
    predictions = (
        db.query(Prediction)
        .filter(Prediction.student_id == student_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )

    # Auto-predict si aucune prédiction
    last_prediction = predictions[0] if predictions else None
    if not last_prediction:
        last_prediction = _auto_predict(student_id, db)
        if last_prediction:
            predictions = [last_prediction]

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

    return {
        "etudiant": {
            "id":      student.id,
            "nom":     student.nom,
            "prenom":  student.prenom,
            "filiere": student.filiere,
            "annee":   student.annee,
            "cne":     getattr(student, "cne", None) or getattr(student, "email", ""),
            "email":   student.email,
        },
        "moyennes_par_semestre": stats_semestres,
        "nombre_modules": len(grades),
        "derniere_prediction": _build_prediction_object(last_prediction, grades),
        "historique_predictions": [
            {"date": p.created_at, "resultat": p.statut_couleur}
            for p in predictions
        ],
    }


@router.get("/{student_id}/grades")
def grades_etudiant(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Notes d'un étudiant structurées par semestre."""
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

    grades = db.query(Grade).filter(Grade.student_id == student_id).all()

    # Structurer par semestre: { "s1": { "Matière": note }, "s2": {...} }
    result = {}
    for g in grades:
        sem_key = (g.semestre or "?").lower().replace("s", "s")
        if sem_key not in result:
            result[sem_key] = {}
        result[sem_key][g.matiere] = g.note

    return result
