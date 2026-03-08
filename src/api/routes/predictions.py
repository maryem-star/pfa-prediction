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

class PredictionMLRequest(BaseModel):
    student_id: int
    modele_utilise: Optional[str] = "RandomForest"
    # Features de l'étudiant
    Absences_S1:           Optional[float] = 0
    Mathematiques_1:       Optional[float] = None
    Algorithmique_Prog:    Optional[float] = None
    Architecture_Ord:      Optional[float] = None
    Electronique_Num:      Optional[float] = None
    Reseaux_Info_1:        Optional[float] = None
    Anglais_Tech_1:        Optional[float] = None
    Francais_Pro_1:        Optional[float] = None
    Moyenne_S1:            Optional[float] = None
    Absences_S2:           Optional[float] = 0
    Mathematiques_2:       Optional[float] = None
    Structures_Donnees:    Optional[float] = None
    Systemes_Exploitation: Optional[float] = None
    Bases_Donnees:         Optional[float] = None
    Reseaux_Info_2:        Optional[float] = None
    Anglais_Tech_2:        Optional[float] = None
    Francais_Pro_2:        Optional[float] = None
    PFA_2:                 Optional[float] = None
    Modules_Non_Valides:   Optional[int]   = 0
    Redoublant:            Optional[int]   = 0

class Prediction3ARequest(BaseModel):
    student_id: int
    filiere: str  # ex: "ite", "isic", "mecanique", etc.
    modele_utilise: Optional[str] = "RandomForest"
    # Les notes S1/S2 (comme PredictionMLRequest)
    Absences_S1:           Optional[float] = 0
    Mathematiques_1:       Optional[float] = None
    Algorithmique_Prog:    Optional[float] = None
    Architecture_Ord:      Optional[float] = None
    Electronique_Num:      Optional[float] = None
    Reseaux_Info_1:        Optional[float] = None
    Anglais_Tech_1:        Optional[float] = None
    Francais_Pro_1:        Optional[float] = None
    Moyenne_S1:            Optional[float] = None
    Absences_S2:           Optional[float] = 0
    Mathematiques_2:       Optional[float] = None
    Structures_Donnees:    Optional[float] = None
    Systemes_Exploitation: Optional[float] = None
    Bases_Donnees:         Optional[float] = None
    Reseaux_Info_2:        Optional[float] = None
    Anglais_Tech_2:        Optional[float] = None
    Francais_Pro_2:        Optional[float] = None
    PFA_2:                 Optional[float] = None
    Modules_Non_Valides:   Optional[int]   = 0
    Redoublant:            Optional[int]   = 0

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
    
    # Extraire les features
    features_1A = data.model_dump(exclude={"student_id", "filiere", "modele_utilise"})
    
    # Exécuter la prédiction globale
    resultats_3A = predict_modules_3A(
        etudiant_1A=features_1A,
        filiere=data.filiere,
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
            resultats.append({"student_id": s.student_id, "error": "Étudiant non trouvé"})
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
