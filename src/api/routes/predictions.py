from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.prediction import Prediction
from src.models.student import Student
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional, List
import os

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# ─── Schémas ──────────────────────────────────────────────────────────────────
class PredictionCreate(BaseModel):
    student_id: int
    modele_utilise: Optional[str] = "RandomForest"
    probabilite_reussite: Optional[float] = None
    statut_couleur: Optional[str] = None
    note_predite: Optional[float] = None

# ─── Schéma commun: notes réelles par position (Module_SX_Y) ─────────────────
class StudentFeaturesBase(BaseModel):
    """Features communes à tous les schémas de prédiction — alignées sur le pipeline ML."""
    # 1ère Année — Semestre 1
    Absences_S1:    Optional[float] = 0.0
    Module_S1_1:    Optional[float] = None   # Maths 1 / équivalent
    Module_S1_2:    Optional[float] = None   # Algo/Physique / équivalent
    Module_S1_3:    Optional[float] = None   # Architecture / équivalent
    Module_S1_4:    Optional[float] = None   # Electronique / équivalent
    Module_S1_5:    Optional[float] = None   # Systèmes / équivalent
    Anglais_Tech_1: Optional[float] = None
    Francais_Pro_1: Optional[float] = None
    Moyenne_S1:     Optional[float] = None
    # 1ère Année — Semestre 2
    Absences_S2:    Optional[float] = 0.0
    Module_S2_1:    Optional[float] = None   # Maths 2 / équivalent
    Module_S2_2:    Optional[float] = None   # Structures/Physique2
    Module_S2_3:    Optional[float] = None   # POO/Electronique2
    Module_S2_4:    Optional[float] = None   # BDD/Thermo
    Module_S2_5:    Optional[float] = None   # Réseaux/Matériaux
    Anglais_Tech_2: Optional[float] = None
    Francais_Pro_2: Optional[float] = None
    PFA_2:          Optional[float] = None
    Moyenne_S2:     Optional[float] = None
    Moyenne_Annuelle: Optional[float] = None
    # Bilan
    Modules_Non_Valides: Optional[int] = 0
    Redoublant:          Optional[int] = 0
    Redoublant_1A:       Optional[int] = 0
    Participation:       Optional[float] = None
    Filiere_Code:        Optional[int] = 0

class PredictionMLRequest(StudentFeaturesBase):
    student_id: int
    modele_utilise: Optional[str] = "RandomForest"

class Prediction3ARequest(StudentFeaturesBase):
    student_id: int
    filiere: str  # ex: "ite", "isic", "ccn", "gee", "civil", "industriel"
    modele_utilise: Optional[str] = "RandomForest"
    # 2ème Année (optionnel — améliore la précision)
    Absences_S3:    Optional[float] = None
    Module_S3_1:    Optional[float] = None
    Module_S3_2:    Optional[float] = None
    Module_S3_3:    Optional[float] = None
    Module_S3_4:    Optional[float] = None
    Module_S3_5:    Optional[float] = None
    Anglais_Tech_S3: Optional[float] = None
    Francais_Pro_S3: Optional[float] = None
    Absences_S4:    Optional[float] = None
    Module_S4_1:    Optional[float] = None
    Module_S4_2:    Optional[float] = None
    Module_S4_3:    Optional[float] = None
    Module_S4_4:    Optional[float] = None
    Module_S4_5:    Optional[float] = None
    Anglais_Tech_S4: Optional[float] = None
    Francais_Pro_S4: Optional[float] = None
    PFA_4:          Optional[float] = None
    Redoublant_2A:  Optional[int] = 0

# ─── Endpoint: Prédiction ML réelle ──────────────────────────────────────────
@router.post("/ml/predict")
def predict_ml(
    data: PredictionMLRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lance une prédiction ML réelle et sauvegarde dans la base de données."""
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    # Vérifier que les modèles sont disponibles
    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))), "models"
    )
    model_path = os.path.join(models_dir, f"{data.modele_utilise}.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=503,
            detail=f"Modèle '{data.modele_utilise}' non disponible. Exécutez d'abord train.py."
        )

    # Appel du module ML
    from src.ml_models.predict import predict as ml_predict
    features = data.model_dump(exclude={"student_id", "modele_utilise"})
    result = ml_predict(features, modele=data.modele_utilise)

    # Sauvegarde en base
    prediction = Prediction(
        student_id=data.student_id,
        modele_utilise=result["modele_utilise"],
        probabilite_reussite=result["probabilite"],
        statut_couleur=result["statut_couleur"],
        note_predite=result["note_predite"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        **result,
        "prediction_id": prediction.id,
    }

# ─── Endpoint: Prédiction ML 3ème Année (Modules & PFE) ──────────────────────
@router.post("/ml/predict-3a")
def predict_ml_3a(
    data: Prediction3ARequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Lance une prédiction experte pour la 3ème année (validation S5 et PFE)."""
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    # Appel du module ML expert 3A
    from src.ml_models.predict import predict_modules_3A

    # Extraire toutes les features
    all_data = data.model_dump(exclude={"student_id", "filiere", "modele_utilise"})

    # Séparer 1A et 2A
    champs_2A = {"Absences_S3", "Module_S3_1", "Module_S3_2", "Module_S3_3", "Module_S3_4",
                 "Module_S3_5", "Anglais_Tech_S3", "Francais_Pro_S3",
                 "Absences_S4", "Module_S4_1", "Module_S4_2", "Module_S4_3", "Module_S4_4",
                 "Module_S4_5", "Anglais_Tech_S4", "Francais_Pro_S4", "PFA_4", "Redoublant_2A"}
    features_1A = {k: v for k, v in all_data.items() if k not in champs_2A and v is not None}
    features_2A = {k: v for k, v in all_data.items() if k in champs_2A and v is not None}

    # Mapper S3/S4 vers les clés attendues par le système 2A
    if features_2A:
        mapping_2a = {
            "Absences_S3": "Absences_S1", "Absences_S4": "Absences_S2",
            "Module_S3_1": "Module_S1_1", "Module_S3_2": "Module_S1_2",
            "Module_S3_3": "Module_S1_3", "Module_S3_4": "Module_S1_4",
            "Module_S3_5": "Module_S1_5",
            "Module_S4_1": "Module_S2_1", "Module_S4_2": "Module_S2_2",
            "Module_S4_3": "Module_S2_3", "Module_S4_4": "Module_S2_4",
            "Module_S4_5": "Module_S2_5",
            "Anglais_Tech_S3": "Anglais_Tech_1", "Francais_Pro_S3": "Francais_Pro_1",
            "Anglais_Tech_S4": "Anglais_Tech_2", "Francais_Pro_S4": "Francais_Pro_2",
            "PFA_4": "PFA_2", "Redoublant_2A": "Redoublant",
        }
        features_2A = {mapping_2a.get(k, k): v for k, v in features_2A.items()}

    # Exécuter la prédiction globale
    resultats_3A = predict_modules_3A(
        etudiant_1A=features_1A,
        filiere=data.filiere,
        etudiant_2A=features_2A if features_2A else None,
        modele=data.modele_utilise
    )

    return resultats_3A

# ─── Endpoint: Prédiction par lot ────────────────────────────────────────────
class BatchRequest(BaseModel):
    students: List[PredictionMLRequest]

@router.post("/ml/batch")
def predict_ml_batch(
    data: BatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Prédiction pour plusieurs étudiants en une seule requête."""
    from src.ml_models.predict import predict as ml_predict
    resultats = []
    for s in data.students:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        if not student:
            resultats.append({"student_id": s.student_id, "error": "Etudiant non trouve"})
            continue
        features = s.model_dump(exclude={"student_id", "modele_utilise"})
        result = ml_predict(features, modele=s.modele_utilise or "RandomForest")
        prediction = Prediction(
            student_id=s.student_id,
            modele_utilise=result["modele_utilise"],
            probabilite_reussite=result["probabilite"],
            statut_couleur=result["statut_couleur"],
            note_predite=result["note_predite"],
        )
        db.add(prediction)
        resultats.append({"student_id": s.student_id, **result})
    db.commit()
    return {"resultats": resultats, "total": len(resultats)}

# --- Endpoint: Prediction Tolerante (avec facteurs humains) ---
class PredictionTolerantRequest(StudentFeaturesBase):
    student_id: int
    modele_utilise: Optional[str] = "RandomForest"
    # Facteurs humains (peuvent être ignorés — l'IA détecte automatiquement)
    Maladie_Chronique:     Optional[int] = 0
    Probleme_Familial:     Optional[int] = 0
    Etudiant_Travailleur:  Optional[int] = 0
    Handicap:              Optional[int] = 0
    Cas_Force_Majeure:     Optional[int] = 0
    Engagement_Associatif: Optional[int] = 0
    Progression_Notable:   Optional[int] = 0

@router.post("/ml/predict-tolerant")
def predict_ml_tolerant(
    data: PredictionTolerantRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Prediction tolerante: prend en compte les facteurs humains
    (maladie, handicap, problemes familiaux, etc.) pour ajuster la prediction.

    Ajoute le statut ORANGE = "passage possible par tolerance".
    """
    import json
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Etudiant non trouve")

    # Verifier que les modeles sont disponibles
    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))), "models"
    )
    model_path = os.path.join(models_dir, f"{data.modele_utilise}.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(
            status_code=503,
            detail=f"Modele '{data.modele_utilise}' non disponible. Executez d'abord train.py."
        )

    # Appel du module ML tolerant
    from src.ml_models.predict import predict_tolerant
    features = data.model_dump(exclude={"student_id", "modele_utilise"})
    result = predict_tolerant(features, modele=data.modele_utilise)

    # Sauvegarde en base avec les donnees de tolerance
    tolerance = result.get("tolerance", {})
    prediction = Prediction(
        student_id=data.student_id,
        modele_utilise=result["modele_utilise"],
        probabilite_reussite=result["probabilite"],
        statut_couleur=result["statut_couleur_strict"],
        note_predite=result["note_predite"],
        tolerance_score=tolerance.get("score_tolerance", 0),
        facteurs_attenuants=json.dumps(tolerance.get("facteurs_actifs", [])),
        passage_tolerant=result.get("statut_couleur_tolerant") == "ORANGE",
        statut_couleur_tolerant=result.get("statut_couleur_tolerant"),
        decision_probable=result.get("decision_probable"),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return {
        **result,
        "prediction_id": prediction.id,
    }

# ─── Endpoints existants (inchangés) ─────────────────────────────────────────
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
    from src.ml_models.predict import classifier_couleur
    couleur = classifier_couleur(data.probabilite_reussite, None) if data.probabilite_reussite else "JAUNE"
    prediction = Prediction(
        student_id=data.student_id,
        modele_utilise=data.modele_utilise,
        probabilite_reussite=data.probabilite_reussite,
        statut_couleur=couleur,
        note_predite=data.note_predite,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction

@router.get("/dashboard/couleurs")
def get_dashboard_couleurs(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    verts  = db.query(Prediction).filter(Prediction.statut_couleur == "VERT").count()
    jaunes = db.query(Prediction).filter(Prediction.statut_couleur == "JAUNE").count()
    rouges = db.query(Prediction).filter(Prediction.statut_couleur == "ROUGE").count()
    return {
        "VERT": verts, "JAUNE": jaunes, "ROUGE": rouges,
        "total": verts + jaunes + rouges
    }

@router.get("/ml/metriques")
def get_model_metrics(current_user=Depends(get_current_user)):
    """Retourne les métriques des modèles ML (pour Interface 6)."""
    import joblib, os
    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))), "models"
    )
    path = os.path.join(models_dir, "metrics.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=503,
            detail="Métriques non disponibles. Exécutez evaluate.py d'abord.")
    metrics = joblib.load(path)
    return {"modeles": metrics}
