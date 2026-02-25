"""
Entranement des 3 modles ML avec Hyperparameter Tuning.
Modles: Logistic Regression, Random Forest, SVM
"""

import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

# Imports internes
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.preprocessing.data_pipeline import run_pipeline

MODELS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "models"
)
os.makedirs(MODELS_PATH, exist_ok=True)

#  Grilles de paramtres 
PARAM_GRIDS = {
    "LogisticRegression": {
        "model": LogisticRegression(max_iter=1000, random_state=42),
        "params": {
            "C":      [0.01, 0.1, 1, 10, 100],
            "solver": ["lbfgs", "liblinear"],
        },
    },
    "RandomForest": {
        "model": RandomForestClassifier(random_state=42),
        "params": {
            "n_estimators":  [50, 100, 200],
            "max_depth":     [None, 3, 5, 7],
            "min_samples_split": [2, 5],
        },
    },
    "SVM": {
        "model": SVC(probability=True, random_state=42),
        "params": {
            "C":      [0.1, 1, 10],
            "kernel": ["rbf", "linear"],
            "gamma":  ["scale", "auto"],
        },
    },
}


def train_all(X_train, y_train, cv: int = 5):
    """
    Entrane les 3 modles avec GridSearchCV et sauvegarde les meilleurs.

    Args:
        X_train: donnes d'entranement (dj normalises)
        y_train: tiquettes d'entranement
        cv: nombre de folds pour la validation croise

    Returns:
        dict {nom_modele: meilleur_estimateur}
    """
    # Avec peu de donnes, on limite cv au nombre de classes min prsentes
    unique_classes = len(set(y_train))
    if unique_classes < 2:
        print("  [Attention] Une seule classe dans y_train - utilisation de KFold standard")
        from sklearn.model_selection import KFold
        skf = KFold(n_splits=min(cv, len(y_train)), shuffle=True, random_state=42)
    else:
        min_class_count = int(np.bincount(y_train).min())
        n_splits = max(2, min(cv, min_class_count))
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)


    results = {}

    for name, config in PARAM_GRIDS.items():
        print(f"\n Entranement: {name}")
        grid = GridSearchCV(
            estimator=config["model"],
            param_grid=config["params"],
            cv=skf,
            scoring="f1",
            n_jobs=-1,
            verbose=0,
        )
        grid.fit(X_train, y_train)

        best = grid.best_estimator_
        results[name] = best

        # Sauvegarde
        path = os.path.join(MODELS_PATH, f"{name}.pkl")
        joblib.dump(best, path)
        print(f"   Meilleurs params: {grid.best_params_}")
        print(f"   Modle sauvegard: {path}")

    # Sauvegarder aussi le rsum des rsultats
    joblib.dump(results, os.path.join(MODELS_PATH, "all_models.pkl"))
    print("\n Tous les modles sauvegards dans models/")
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("  PFA  Entranement des modles ML")
    print("=" * 60)

    X_train, X_test, y_train, y_test, features = run_pipeline()
    models = train_all(X_train, y_train)

    print("\n Modles entrans:")
    for name in models:
        print(f"   {name}")

    # valuation rapide
    from src.ml_models.evaluate import evaluate_all
    evaluate_all(models, X_test, y_test)
