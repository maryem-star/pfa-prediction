"""
Tests unitaires — Pipeline ML
pytest tests/test_ml.py -v
"""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Test 1: Data Pipeline ────────────────────────────────────────────────────
def test_data_pipeline_runs():
    """Le pipeline doit charger, nettoyer et retourner des données valides."""
    from src.preprocessing.data_pipeline import run_pipeline
    X_train, X_test, y_train, y_test, features = run_pipeline()

    assert X_train.shape[0] > 0,      "X_train est vide"
    assert X_test.shape[0] > 0,       "X_test est vide"
    assert len(features) > 0,         "Aucune feature"
    assert len(y_train) > 0,          "y_train est vide"
    assert set(np.unique(y_train)) <= {0, 1}, "La cible doit être 0 ou 1"
    assert not np.isnan(X_train).any(), "X_train contient des NaN"


# ─── Test 2: Classification Couleur ──────────────────────────────────────────
def test_classifier_couleur():
    """Vérifier les seuils VERT/JAUNE/ROUGE."""
    from src.ml_models.predict import classifier_couleur

    assert classifier_couleur(0.90) == "VERT",  "0.90 → VERT"
    assert classifier_couleur(0.85) == "VERT",  "0.85 → VERT"
    assert classifier_couleur(0.70) == "JAUNE", "0.70 → JAUNE"
    assert classifier_couleur(0.50) == "JAUNE", "0.50 → JAUNE"
    assert classifier_couleur(0.30) == "ROUGE", "0.30 → ROUGE"
    assert classifier_couleur(0.00) == "ROUGE", "0.00 → ROUGE"

    # Avec note prédite
    assert classifier_couleur(0.40, 15.0) == "VERT",  "prob=0.40, note=15 → VERT"
    assert classifier_couleur(0.30, 11.0) == "JAUNE", "prob=0.30, note=11 → JAUNE"
    assert classifier_couleur(0.20,  8.0) == "ROUGE", "prob=0.20, note=8  → ROUGE"


# ─── Test 3: Entraînement des Modèles ────────────────────────────────────────
def test_model_training():
    """Les 3 modèles doivent s'entraîner et atteindre Accuracy > 0.60."""
    from src.preprocessing.data_pipeline import run_pipeline
    from src.ml_models.train import train_all
    from sklearn.metrics import accuracy_score

    X_train, X_test, y_train, y_test, _ = run_pipeline()
    models = train_all(X_train, y_train)

    assert len(models) == 3, "Il doit y avoir 3 modèles"

    for name, model in models.items():
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        assert acc >= 0.60, f"{name}: Accuracy trop faible ({acc:.2f})"


# ─── Test 4: Sortie de Prédiction ────────────────────────────────────────────
def test_predict_output_structure():
    """La fonction predict() doit retourner tous les champs requis."""
    from src.ml_models.predict import predict

    input_exemple = {
        "Absences_S1": 3, "Mathematiques_1": 12.0, "Algorithmique_Prog": 11.0,
        "Architecture_Ord": 13.0, "Electronique_Num": 10.0, "Reseaux_Info_1": 12.0,
        "Anglais_Tech_1": 14.0, "Francais_Pro_1": 13.0, "Moyenne_S1": 12.0,
        "Absences_S2": 2, "Mathematiques_2": 13.0, "Structures_Donnees": 11.0,
        "Systemes_Exploitation": 12.0, "Bases_Donnees": 14.0, "Reseaux_Info_2": 13.0,
        "Anglais_Tech_2": 14.0, "Francais_Pro_2": 13.0, "PFA_2": 16.0,
        "Modules_Non_Valides": 0, "Redoublant": 0,
    }

    result = predict(input_exemple)

    required_keys = ["label", "probabilite", "note_predite",
                     "statut_couleur", "facteurs_risque",
                     "recommandations", "modele_utilise"]
    for key in required_keys:
        assert key in result, f"Clé manquante: {key}"

    assert result["label"] in ["Réussi", "Échec"]
    assert 0.0 <= result["probabilite"] <= 1.0
    assert result["statut_couleur"] in ["VERT", "JAUNE", "ROUGE"]
    assert isinstance(result["facteurs_risque"], list)
    assert isinstance(result["recommandations"], list)


# ─── Test 5: Prédiction par Lot ──────────────────────────────────────────────
def test_predict_batch():
    """predict_batch doit retourner autant de résultats que d'entrées."""
    from src.ml_models.predict import predict_batch

    inputs = [
        {"Moyenne_S1": 12.0, "Absences_S1": 2, "Redoublant": 0},
        {"Moyenne_S1": 7.0,  "Absences_S1": 20, "Redoublant": 1},
    ]
    results = predict_batch(inputs)

    assert len(results) == 2
    for r in results:
        assert "statut_couleur" in r
