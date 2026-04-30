from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.prediction import Prediction
from src.models.student import Student
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional, List
import os

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# --- Schemas ---
class PredictionCreate(BaseModel):
    student_id: int
    modele_utilise: Optional[str] = "RandomForest"
    probabilite_reussite: Optional[float] = None
    statut_couleur: Optional[str] = None
    note_predite: Optional[float] = None

class StudentFeaturesBase(BaseModel):
    Absences_S1:    Optional[float] = 0.0
    Module_S1_1:    Optional[float] = None
    Module_S1_2:    Optional[float] = None
    Module_S1_3:    Optional[float] = None
    Module_S1_4:    Optional[float] = None
    Module_S1_5:    Optional[float] = None
    Anglais_Tech_1: Optional[float] = None
    Francais_Pro_1: Optional[float] = None
    Moyenne_S1:     Optional[float] = None
    Absences_S2:    Optional[float] = 0.0
    Module_S2_1:    Optional[float] = None
    Module_S2_2:    Optional[float] = None
    Module_S2_3:    Optional[float] = None
    Module_S2_4:    Optional[float] = None
    Module_S2_5:    Optional[float] = None
    Anglais_Tech_2: Optional[float] = None
    Francais_Pro_2: Optional[float] = None
    PFA_2:          Optional[float] = None
    Moyenne_S2:     Optional[float] = None
    Moyenne_Annuelle: Optional[float] = None
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
    filiere: str
    modele_utilise: Optional[str] = "RandomForest"
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


# --- Prediction ML ---
@router.post("/ml/predict")
def predict_ml(
    data: PredictionMLRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Etudiant non trouve")

    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))), "models"
    )
    model_path = os.path.join(models_dir, f"{data.modele_utilise}.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=503, detail=f"Modele '{data.modele_utilise}' non disponible")

    from src.ml_models.predict import predict as ml_predict
    features = data.model_dump(exclude={"student_id", "modele_utilise"})
    features = {k: (v if v is not None else 0.0) for k, v in features.items()}
    result = ml_predict(features, modele=data.modele_utilise)

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

    return {**result, "prediction_id": prediction.id}


# --- Prediction 3A ---
@router.post("/ml/predict-3a")
def predict_ml_3a(
    data: Prediction3ARequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Etudiant non trouve")

    from src.ml_models.predict import predict_modules_3A

    all_data = data.model_dump(exclude={"student_id", "filiere", "modele_utilise"})

    champs_2A = {"Absences_S3", "Module_S3_1", "Module_S3_2", "Module_S3_3", "Module_S3_4",
                 "Module_S3_5", "Anglais_Tech_S3", "Francais_Pro_S3",
                 "Absences_S4", "Module_S4_1", "Module_S4_2", "Module_S4_3", "Module_S4_4",
                 "Module_S4_5", "Anglais_Tech_S4", "Francais_Pro_S4", "PFA_4", "Redoublant_2A"}
    features_1A = {k: v for k, v in all_data.items() if k not in champs_2A and v is not None}
    features_2A = {k: v for k, v in all_data.items() if k in champs_2A and v is not None}

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

    resultats_3A = predict_modules_3A(
        etudiant_1A=features_1A,
        filiere=data.filiere,
        etudiant_2A=features_2A if features_2A else None,
        modele=data.modele_utilise
    )

    return resultats_3A


# --- Batch prediction (JSON) ---
class BatchRequest(BaseModel):
    students: List[PredictionMLRequest]

@router.post("/ml/batch")
def predict_ml_batch(
    data: BatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    from src.ml_models.predict import predict as ml_predict
    resultats = []
    for s in data.students:
        student = db.query(Student).filter(Student.id == s.student_id).first()
        if not student:
            resultats.append({"student_id": s.student_id, "error": "Etudiant non trouve"})
            continue
        features = s.model_dump(exclude={"student_id", "modele_utilise"})
        features = {k: (v if v is not None else 0.0) for k, v in features.items()}
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


# --- Batch prediction via CSV file upload (BatchPredictionPage) ---
@router.post("/batch")
async def predict_batch_csv(
    file: UploadFile = File(...),
    modele: str = Form("RandomForest"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    import pandas as pd
    import io as iomod
    from src.ml_models.predict import predict as ml_predict

    contents = await file.read()
    try:
        df = pd.read_csv(iomod.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Format CSV invalide")

    results = []
    for _, row in df.iterrows():
        features = {}
        for col in row.index:
            if col == "student_id":
                continue
            try:
                val = float(row[col])
                features[col] = val if pd.notna(val) else 0.0
            except (ValueError, TypeError):
                features[col] = 0.0

        try:
            result = ml_predict(features, modele=modele)
            result["student_id"] = row.get("student_id", "")
            results.append(result)
        except Exception as e:
            results.append({
                "student_id": row.get("student_id", ""),
                "error": str(e),
                "statut_couleur": "ROUGE",
                "label": "Erreur",
                "probabilite": 0,
            })

    return {"predictions": results, "total": len(results)}


# --- Existing endpoints ---
@router.get("/")
def get_predictions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Prediction).all()

@router.get("/student/{student_id}")
def get_prediction_by_student(student_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    prediction = db.query(Prediction).filter(Prediction.student_id == student_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Aucune prediction pour cet etudiant")
    return prediction

@router.post("/")
def create_prediction(data: PredictionCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Etudiant non trouve")
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
    import joblib
    models_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))), "models"
    )
    path = os.path.join(models_dir, "metrics.pkl")
    if not os.path.exists(path):
        raise HTTPException(status_code=503, detail="Metriques non disponibles")
    metrics = joblib.load(path)
    return {"modeles": metrics}
