"""
valuation des modles ML: mtriques, matrices de confusion, courbes ROC.
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")   # pas de fentre GUI
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, auc, classification_report
)
import joblib

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_PATH = os.path.join(BASE_DIR, "models")
DOCS_PATH   = os.path.join(BASE_DIR, "docs")
os.makedirs(DOCS_PATH, exist_ok=True)

COLORS = {
    "LogisticRegression": "#4e79a7",
    "RandomForest":       "#59a14f",
    "SVM":                "#e15759",
}


def compute_metrics(model, X_test, y_test, name: str) -> dict:
    """Calcule toutes les mtriques pour un modle."""
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc      = auc(fpr, tpr)

    return {
        "name":      name,
        "accuracy":  round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc":   round(roc_auc, 4),
        "y_pred":    y_pred,
        "y_proba":   y_proba,
        "fpr":       fpr,
        "tpr":       tpr,
    }


def plot_confusion_matrices(results: list, y_test, output_path: str):
    """Affiche les matrices de confusion cte  cte."""
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, res in zip(axes, results):
        cm = confusion_matrix(y_test, res["y_pred"])
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["chec", "Russi"],
                    yticklabels=["chec", "Russi"])
        ax.set_title(res["name"], fontsize=12, fontweight="bold")
        ax.set_xlabel("Prdit")
        ax.set_ylabel("Rel")

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   Matrices de confusion  {output_path}")


def plot_roc_curves(results: list, output_path: str):
    """Trace les courbes ROC de tous les modles."""
    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot([0, 1], [0, 1], "k--", linewidth=1.5, label="Alatoire (AUC = 0.50)")
    for res in results:
        color = COLORS.get(res["name"], "#888888")
        ax.plot(res["fpr"], res["tpr"], color=color, linewidth=2.5,
                label=f"{res['name']} (AUC = {res['roc_auc']:.2f})")

    ax.set_xlabel("Taux de Faux Positifs (FPR)", fontsize=12)
    ax.set_ylabel("Taux de Vrais Positifs (TPR)", fontsize=12)
    ax.set_title("Courbes ROC  Comparaison des Modles ML", fontsize=14, fontweight="bold")
    ax.legend(loc="lower right", fontsize=10)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])
    ax.grid(alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   Courbes ROC  {output_path}")


def plot_metrics_comparison(results: list, output_path: str):
    """Graphique en barres comparant toutes les mtriques."""
    metrics_names = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    labels        = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 5))

    for i, res in enumerate(results):
        vals = [res[m] for m in metrics_names]
        color = COLORS.get(res["name"], "#888888")
        bars = ax.bar(x + i * width, vals, width, label=res["name"], color=color, alpha=0.85)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01,
                    f"{b.get_height():.2f}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x + width)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim([0, 1.15])
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Comparaison des Mtriques  3 Modles ML", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"   Comparaison mtriques  {output_path}")


def evaluate_all(models: dict, X_test, y_test) -> list:
    """
    value tous les modles et gnre les graphiques.

    Args:
        models: dict {nom: estimateur}
        X_test, y_test: donnes de test

    Returns:
        liste de dicts de mtriques
    """
    print("\n" + "=" * 60)
    print("  VALUATION DES MODLES")
    print("=" * 60)

    results = []
    for name, model in models.items():
        res = compute_metrics(model, X_test, y_test, name)
        results.append(res)
        print(f"\n {name}:")
        print(f"   Accuracy : {res['accuracy']:.4f}")
        print(f"   Precision: {res['precision']:.4f}")
        print(f"   Recall   : {res['recall']:.4f}")
        print(f"   F1-Score : {res['f1']:.4f}")
        print(f"   ROC-AUC  : {res['roc_auc']:.4f}")

    # Gnrer les graphiques
    plot_confusion_matrices(results, y_test,
        os.path.join(DOCS_PATH, "confusion_matrices.png"))
    plot_roc_curves(results,
        os.path.join(DOCS_PATH, "roc_curves.png"))
    plot_metrics_comparison(results,
        os.path.join(DOCS_PATH, "metrics_comparison.png"))

    # Sauvegarder les mtriques
    metrics_clean = [{k: v for k, v in r.items()
                      if k not in ("y_pred", "y_proba", "fpr", "tpr")}
                     for r in results]
    joblib.dump(metrics_clean, os.path.join(MODELS_PATH, "metrics.pkl"))

    # Meilleur modle
    best = max(results, key=lambda r: r["f1"])
    print(f"\n Meilleur modle (F1): {best['name']} (F1={best['f1']:.4f})")

    return results


if __name__ == "__main__":
    import joblib
    models = joblib.load(os.path.join(MODELS_PATH, "all_models.pkl"))
    from src.preprocessing.data_pipeline import run_pipeline
    _, X_test, _, y_test, _ = run_pipeline()
    evaluate_all(models, X_test, y_test)
