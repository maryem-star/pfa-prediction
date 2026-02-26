"""
Tests unitaires — Pipeline ML avec vraies conditions de reussite
Conditions: Moyenne >= 12, Modules_NV <= 3, PFA >= 12
Zones de danger: Absences > 10h, Redoublant = 1
pytest tests/test_ml.py -v
"""

import os, sys
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ─── Test 1: Data Pipeline ────────────────────────────────────────────────────
def test_data_pipeline_runs():
    """Le pipeline doit charger les 6 filieres et retourner des donnees valides."""
    from src.preprocessing.data_pipeline import run_pipeline
    X_train, X_test, y_train, y_test, features = run_pipeline()

    assert X_train.shape[0] > 0,            "X_train est vide"
    assert X_test.shape[0] > 0,             "X_test est vide"
    assert len(features) >= 20,             "Trop peu de features"
    assert not np.isnan(X_train).any(),     "X_train contient des NaN"
    assert set(np.unique(y_train)) <= {0,1},"La cible doit etre 0 ou 1"
    # Verifier la presence des features danger/comportement
    assert "Danger_Absences"    in features, "Feature Danger_Absences manquante"
    assert "Profil_Comportement" in features,"Feature Profil_Comportement manquante"


# ─── Test 2: Conditions de reussite multi-criteres ───────────────────────────
def test_conditions_reussite():
    """Verifier les 3 conditions de reussite sur un DataFrame de test."""
    import pandas as pd
    from src.preprocessing.data_pipeline import create_target_binary

    # Etudiant qui reussit: Moy=14, Modules_NV=1, PFA=15
    df = pd.DataFrame([{
        "Moyenne_Annuelle": 14.0, "Modules_Non_Valides": 1, "PFA_2":15.0,
        "Absences_S1": 3, "Absences_S2": 2, "Redoublant": 0,
    }])
    df = create_target_binary(df)
    assert df["Reussite"].iloc[0] == 1, "Doit reussir: Moy>=12, Modules<=3, PFA>=12"

    # Echec par moyenne insuffisante
    df2 = pd.DataFrame([{
        "Moyenne_Annuelle": 11.5, "Modules_Non_Valides": 1, "PFA_2": 15.0,
        "Absences_S1": 3, "Absences_S2": 2, "Redoublant": 0,
    }])
    df2 = create_target_binary(df2)
    assert df2["Reussite"].iloc[0] == 0, "Doit echouer: Moy < 12"

    # Echec par modules non valides
    df3 = pd.DataFrame([{
        "Moyenne_Annuelle": 13.0, "Modules_Non_Valides": 4, "PFA_2": 15.0,
        "Absences_S1": 3, "Absences_S2": 2, "Redoublant": 0,
    }])
    df3 = create_target_binary(df3)
    assert df3["Reussite"].iloc[0] == 0, "Doit echouer: Modules_NV > 3"

    # Echec par PFA insuffisante
    df4 = pd.DataFrame([{
        "Moyenne_Annuelle": 13.0, "Modules_Non_Valides": 2, "PFA_2": 10.0,
        "Absences_S1": 3, "Absences_S2": 2, "Redoublant": 0,
    }])
    df4 = create_target_binary(df4)
    assert df4["Reussite"].iloc[0] == 0, "Doit echouer: PFA < 12"


# ─── Test 3: Profil comportemental (absences) ─────────────────────────────────
def test_profil_comportement():
    """Verifier les 4 profils comportementaux."""
    import pandas as pd
    from src.preprocessing.data_pipeline import create_target_binary

    cas = [
        (2, 2, 0),    # Tres assidu: total=4h -> profil 0
        (8, 5, 1),    # Assidu: total=13h -> profil 1
        (14, 12, 2),  # Preoccupant: total=26h -> profil 2
        (20, 15, 3),  # Absenteiste: total=35h -> profil 3
    ]
    for abs1, abs2, expected_profil in cas:
        df = pd.DataFrame([{
            "Moyenne_Annuelle": 13.0, "Modules_Non_Valides": 1, "PFA_2": 14.0,
            "Absences_S1": abs1, "Absences_S2": abs2, "Redoublant": 0,
        }])
        df = create_target_binary(df)
        got = df["Profil_Comportement"].iloc[0]
        assert got == expected_profil, \
            f"Abs({abs1}+{abs2}={abs1+abs2}h): attendu profil {expected_profil}, obtenu {got}"


# ─── Test 4: Classification Couleur (vraies conditions) ──────────────────────
def test_classifier_couleur():
    """VERT si note>=12 et proba>=70%, ROUGE si note<12 ou proba<40%."""
    from src.ml_models.predict import classifier_couleur

    assert classifier_couleur(0.80, 14.0) == "VERT",  "0.80 + note=14 -> VERT"
    assert classifier_couleur(0.75, 13.0) == "VERT",  "0.75 + note=13 -> VERT"
    assert classifier_couleur(0.60, 12.5) == "JAUNE", "0.60 + note=12.5 -> JAUNE"
    assert classifier_couleur(0.55, 11.0) == "ROUGE", "note < 12 -> ROUGE"
    assert classifier_couleur(0.30, 14.0) == "ROUGE", "proba < 40% -> ROUGE"


# ─── Test 5: Entraînement des 3 Modèles ─────────────────────────────────────
def test_model_training():
    """Les 3 modeles doivent s'entrainer et atteindre Accuracy > 0.60."""
    from src.preprocessing.data_pipeline import run_pipeline
    from src.ml_models.train import train_all
    from sklearn.metrics import accuracy_score

    X_train, X_test, y_train, y_test, _ = run_pipeline()
    models = train_all(X_train, y_train)

    assert len(models) == 3, "Il doit y avoir exactement 3 modeles"
    for name, model in models.items():
        acc = accuracy_score(y_test, model.predict(X_test))
        assert acc >= 0.60, f"{name}: Accuracy trop faible ({acc:.2f})"


# ─── Test 6: Structure de sortie de predict() ────────────────────────────────
def test_predict_output_structure():
    """predict() doit retourner tous les champs requis incluant le profil comportemental."""
    from src.ml_models.predict import predict

    etudiant = {
        "Absences_S1": 5, "Absences_S2": 4,
        "Module_S1_1": 13.0, "Module_S1_2": 12.0, "Module_S1_3": 13.0,
        "Module_S1_4": 12.5, "Module_S1_5": 12.0,
        "Anglais_Tech_1": 14.0, "Francais_Pro_1": 13.0,
        "Moyenne_S1": 12.8,
        "Module_S2_1": 13.0, "Module_S2_2": 12.5, "Module_S2_3": 13.0,
        "Module_S2_4": 12.0, "Module_S2_5": 13.0,
        "Anglais_Tech_2": 14.0, "Francais_Pro_2": 13.0,
        "PFA_2": 14.0, "Moyenne_S2": 13.1,
        "Modules_Non_Valides": 0, "Redoublant": 0,
        "Filiere_Code": 1, "Moyenne_Annuelle": 12.95,
        "Progression": 0.3, "Total_Absences": 9, "Moy_Module1": 13.0,
    }
    result = predict(etudiant)

    required = ["label", "probabilite", "note_predite", "statut_couleur",
                "conditions", "profil_comportement", "facteurs_risque",
                "recommandations", "modele_utilise"]
    for key in required:
        assert key in result, f"Cle manquante: {key}"

    assert result["label"] in ["Reussi", "Echec"]
    assert 0.0 <= result["probabilite"] <= 1.0
    assert result["statut_couleur"] in ["VERT", "JAUNE", "ROUGE"]

    # Verifier les 3 conditions dans le resultat
    conds = result["conditions"]
    assert "moy_ok"  in conds, "Condition moy_ok manquante"
    assert "mod_ok"  in conds, "Condition mod_ok manquante"
    assert "pfa_ok"  in conds, "Condition pfa_ok manquante"

    # Verifier le profil comportemental
    prof = result["profil_comportement"]
    assert "score"   in prof, "Score profil manquant"
    assert "label"   in prof, "Label profil manquant"
    assert "remarques" in prof, "Remarques manquantes"
    assert len(prof["remarques"]) > 0, "Au moins une remarque attendue"


# ─── Test 7: Prédiction batch ─────────────────────────────────────────────────
def test_predict_batch():
    """predict_batch doit retourner autant de resultats que d'entrees."""
    from src.ml_models.predict import predict_batch

    inputs = [
        {"Moyenne_S1":13.0,"Absences_S1":3,"PFA_2":14.0,"Redoublant":0,"Modules_Non_Valides":0},
        {"Moyenne_S1":8.0, "Absences_S1":20,"PFA_2":9.0, "Redoublant":1,"Modules_Non_Valides":5},
    ]
    results = predict_batch(inputs)
    assert len(results) == 2
    for r in results:
        assert "statut_couleur" in r
        assert "profil_comportement" in r
