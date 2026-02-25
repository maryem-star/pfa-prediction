"""
Module de prédiction avec classification VERT / JAUNE / ROUGE.
Expose la fonction predict() utilisée par l'API FastAPI.
"""

import os
import numpy as np
import joblib
from typing import Optional

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_PATH = os.path.join(BASE_DIR, "models")

# ─── Seuils ───────────────────────────────────────────────────────────────────
SEUIL_VERT   = 0.85   # Probabilité ≥ 85% → VERT
SEUIL_JAUNE  = 0.50   # Probabilité ≥ 50% → JAUNE (sinon ROUGE)
NOTE_VERT    = 14.0   # Note ≥ 14 → VERT (si disponible)
NOTE_JAUNE   = 10.0   # Note ≥ 10 → JAUNE


def charger_modele(nom_modele: str = "RandomForest"):
    """Charge un modèle sauvegardé depuis models/."""
    path = os.path.join(MODELS_PATH, f"{nom_modele}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Modèle '{nom_modele}' introuvable. Exécutez train.py d'abord."
        )
    return joblib.load(path)


def charger_scaler():
    """Charge le StandardScaler sauvegardé."""
    path = os.path.join(MODELS_PATH, "scaler.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError("Scaler introuvable. Exécutez data_pipeline.py d'abord.")
    return joblib.load(path)


def charger_feature_names() -> list:
    """Charge la liste des features attendues par le modèle."""
    path = os.path.join(MODELS_PATH, "feature_names.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError("feature_names.pkl introuvable.")
    return joblib.load(path)


# ─── Algorithme de classification VERT / JAUNE / ROUGE ───────────────────────
def classifier_couleur(probabilite: float, note_predite: Optional[float] = None) -> str:
    """
    Classifie un étudiant en VERT, JAUNE ou ROUGE.

    Règles (conformes au cahier des charges):
      VERT   → note ≥ 14  OU  probabilité ≥ 85%
      JAUNE  → note ≥ 10  OU  probabilité ≥ 50%
      ROUGE  → sinon (note < 10 ET probabilité < 50%)

    Args:
        probabilite:  probabilité de réussite [0, 1]
        note_predite: note annuelle prédite sur 20 (optionnel)

    Returns:
        "VERT", "JAUNE" ou "ROUGE"
    """
    if note_predite is not None:
        if note_predite >= NOTE_VERT or probabilite >= SEUIL_VERT:
            return "VERT"
        elif note_predite >= NOTE_JAUNE or probabilite >= SEUIL_JAUNE:
            return "JAUNE"
        else:
            return "ROUGE"
    else:
        if probabilite >= SEUIL_VERT:
            return "VERT"
        elif probabilite >= SEUIL_JAUNE:
            return "JAUNE"
        else:
            return "ROUGE"


def top_facteurs_risque(feature_values: dict, feature_names: list,
                        couleur: str) -> list:
    """
    Retourne les 5 principaux facteurs de risque selon les valeurs de l'étudiant.

    Logique simple basée sur les seuils métier:
      - Absences élevées → risque
      - Notes faibles dans matières à fort coefficient → risque
      - Modules non validés → risque
    """
    facteurs = []

    seuils_risque = {
        "Absences_S1":           ("Absences élevées S1",       15, True),
        "Absences_S2":           ("Absences élevées S2",        15, True),
        "Total_Absences":        ("Total absences élevé",       30, True),
        "Mathematiques_1":       ("Mathématiques 1 faible",     10, False),
        "Mathematiques_2":       ("Mathématiques 2 faible",     10, False),
        "Algorithmique_Prog":    ("Algorithmique faible",       10, False),
        "Structures_Donnees":    ("Structures de données faible", 10, False),
        "Systemes_Exploitation": ("Systèmes d'exploitation faible", 10, False),
        "Bases_Donnees":         ("Bases de données faible",    10, False),
        "Moyenne_S1":            ("Moyenne S1 insuffisante",    10, False),
        "Modules_Non_Valides":   ("Modules non validés",         1, True),
        "Redoublant":            ("Étudiant redoublant",         1, True),
        "Progression":           ("Régression entre S1 et S2",  0, False),
    }

    for feat, (label, seuil, plus_grand) in seuils_risque.items():
        if feat in feature_values:
            val = feature_values[feat]
            triggered = (val > seuil) if plus_grand else (val < seuil)
            if triggered:
                # Impact estimé: écart normalisé par rapport au seuil
                if seuil != 0:
                    impact = abs(val - seuil) / max(abs(seuil), 1)
                else:
                    impact = abs(val)
                facteurs.append({
                    "facteur": label,
                    "valeur":  round(float(val), 2),
                    "impact":  round(min(impact * 100, 99), 1),
                })

    # Trier par impact décroissant, garder les 5 premiers
    facteurs.sort(key=lambda x: x["impact"], reverse=True)
    return facteurs[:5]


def recommandations(couleur: str, facteurs: list) -> list:
    """Retourne des recommandations automatiques selon le profil."""
    recs = {
        "ROUGE": [
            "⚠️ Convoquer l'étudiant immédiatement pour un entretien individuel.",
            "📚 Orienter vers le tutorat et les séances de soutien.",
            "📞 Informer la famille de la situation académique.",
            "🗓️ Planifier un suivi hebdomadaire avec un encadrant.",
        ],
        "JAUNE": [
            "📋 Planifier un suivi régulier (bi-mensuel).",
            "📖 Encourager la participation aux groupes de travail.",
            "🧑‍🏫 Recommander des ressources pédagogiques supplémentaires.",
        ],
        "VERT": [
            "🏆 Féliciter l'étudiant pour ses résultats.",
            "🚀 Proposer des projets et activités enrichissantes.",
            "📈 Encourager à aider ses camarades en difficulté.",
        ],
    }
    base = recs.get(couleur, [])

    # Recommendations spécifiques aux facteurs
    for f in facteurs:
        if "Absence" in f["facteur"]:
            base.insert(0, "🔔 Surveiller assidûment l'assiduité de l'étudiant.")
            break
        if "Mathématiques" in f["facteur"] or "Algorithmique" in f["facteur"]:
            base.insert(0, "➕ Inscrire l'étudiant en TD renforcé de Maths/Info.")
            break

    return list(dict.fromkeys(base))[:4]  # dédupliquer, garder 4 max


# ─── Fonction principale ──────────────────────────────────────────────────────
def predict(features_dict: dict, modele: str = "RandomForest") -> dict:
    """
    Prédit la réussite d'un étudiant et retourne toutes les informations.

    Args:
        features_dict: dictionnaire {nom_feature: valeur}
                       Exemple: {"Moyenne_S1": 12.5, "Absences_S1": 3, ...}
        modele: nom du modèle à utiliser (RandomForest, LogisticRegression, SVM)

    Returns:
        dict avec:
          - label         : "Réussi" ou "Échec"
          - probabilite   : float [0, 1]
          - statut_couleur: "VERT", "JAUNE" ou "ROUGE"
          - facteurs_risque: liste des top 5 facteurs
          - recommandations: liste d'actions
    """
    clf          = charger_modele(modele)
    scaler       = charger_scaler()
    feature_names = charger_feature_names()

    # Construire le vecteur dans le bon ordre
    X = np.array([[features_dict.get(f, 0.0) for f in feature_names]])
    X_scaled = scaler.transform(X)

    label_num = clf.predict(X_scaled)[0]
    proba     = clf.predict_proba(X_scaled)[0][1]  # P(Réussi)

    # Note prédite estimée (sur 20) à partir de la probabilité
    note_predite = proba * 20

    couleur  = classifier_couleur(proba, note_predite)
    facteurs = top_facteurs_risque(features_dict, feature_names, couleur)
    recs     = recommandations(couleur, facteurs)

    return {
        "label":          "Réussi" if label_num == 1 else "Échec",
        "probabilite":    round(float(proba), 4),
        "note_predite":   round(note_predite, 2),
        "statut_couleur": couleur,
        "facteurs_risque": facteurs,
        "recommandations": recs,
        "modele_utilise":  modele,
    }


def predict_batch(liste_features: list, modele: str = "RandomForest") -> list:
    """Prédiction par lot (liste de dicts). Retourne une liste de résultats."""
    return [predict(f, modele) for f in liste_features]


if __name__ == "__main__":
    # Test rapide
    exemple = {
        "Absences_S1":       5,
        "Mathematiques_1":   8.0,
        "Algorithmique_Prog": 9.0,
        "Architecture_Ord":  11.0,
        "Electronique_Num":  7.0,
        "Reseaux_Info_1":    10.0,
        "Anglais_Tech_1":    13.0,
        "Francais_Pro_1":    12.0,
        "Moyenne_S1":        9.5,
        "Absences_S2":       8,
        "Mathematiques_2":   7.0,
        "Structures_Donnees": 8.0,
        "Systemes_Exploitation": 9.0,
        "Bases_Donnees":     10.0,
        "Reseaux_Info_2":    11.0,
        "Anglais_Tech_2":    13.0,
        "Francais_Pro_2":    12.0,
        "PFA_2":             14.0,
        "Modules_Non_Valides": 3,
        "Redoublant":        0,
    }

    result = predict(exemple)
    print("\n📊 Résultat de prédiction:")
    for k, v in result.items():
        print(f"  {k}: {v}")
