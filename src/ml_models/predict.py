"""
Module de Prediction ML — Conditions reelles de reussite
=========================================================
Conditions de reussite:
    ✅ Moyenne_Annuelle >= 12/20
    ✅ Modules_Non_Valides <= 3
    ✅ PFA_2 >= 12/20

Zones de danger:
    ⚠️ Absences_S1 > 10h  ou  Absences_S2 > 10h
    ⚠️ Redoublant = 1

Profil comportemental deduit des absences:
    0 = Tres assidu    (total abs <= 5h)
    1 = Assidu         (total abs 6-15h)
    2 = Preoccupant    (total abs 16-30h)
    3 = Absenteiste    (total abs > 30h)
"""

import os
import numpy as np
import joblib

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_PATH = os.path.join(BASE_DIR, "models")

# ─── Profils comportementaux ──────────────────────────────────────────────────
PROFIL_LABELS = {
    0: "Tres assidu",
    1: "Assidu",
    2: "Comportement preoccupant",
    3: "Absenteiste chronique",
}

PROFIL_DESCRIPTIONS = {
    0: "L'etudiant est tres regulier, pratiquement aucune absence. Attitude exemplaire.",
    1: "L'etudiant est globalement assidu avec quelques absences ponctuelles.",
    2: "Le nombre d'absences est preoccupant. Un suivi est recommande.",
    3: "Absenteisme chronique detecte. Intervention urgente necessaire.",
}


def _load(model_name: str):
    """Charge le modele, le scaler et les feature names."""
    scaler        = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
    feature_names = joblib.load(os.path.join(MODELS_PATH, "feature_names.pkl"))
    clf           = joblib.load(os.path.join(MODELS_PATH, f"{model_name}.pkl"))
    return clf, scaler, feature_names


def classifier_couleur(probabilite: float, note_predite: float = None) -> str:
    """
    VERT/JAUNE/ROUGE base sur les vraies conditions:
    - VERT  : note >= 12 ET proba >= 70%  (reussite probable)
    - ROUGE : note < 12  OU  proba < 40%  (echec probable)
    - JAUNE : entre les deux (zone incertaine)
    """
    note = note_predite if note_predite is not None else probabilite * 20

    if note >= 12 and probabilite >= 0.70:
        return "VERT"
    elif note < 12 or probabilite < 0.40:
        return "ROUGE"
    else:
        return "JAUNE"


def profil_comportement(abs_s1: float, abs_s2: float, redoublant: int = 0) -> dict:
    """
    Analyse comportementale complete de l'etudiant.
    Deduit le profil a partir des absences et du statut redoublant.
    """
    total = abs_s1 + abs_s2
    progression_abs = abs_s2 - abs_s1  # positif = aggravation

    # Score de profil (0-3)
    if total <= 5:
        score = 0
    elif total <= 15:
        score = 1
    elif total <= 30:
        score = 2
    else:
        score = 3

    # Zones de danger
    danger_abs = abs_s1 > 10 or abs_s2 > 10
    danger_red = redoublant == 1

    # Remarques comportementales
    remarques = []

    if abs_s1 <= 2 and abs_s2 <= 2:
        remarques.append("Presence exemplaire: assiduite parfaite sur les deux semestres.")
    elif abs_s1 <= 5 and abs_s2 <= 5:
        remarques.append("Bonne assiduite globale sur l'annee.")

    if abs_s1 > 10:
        remarques.append(f"Absences excessives au S1 ({abs_s1}h > seuil de 10h): zone de danger.")
    if abs_s2 > 10:
        remarques.append(f"Absences excessives au S2 ({abs_s2}h > seuil de 10h): zone de danger.")

    if progression_abs > 5:
        remarques.append(f"Aggravation des absences de S1 a S2 (+{progression_abs}h): deterioration comportementale.")
    elif progression_abs < -5:
        remarques.append(f"Amelioration notable de l'assiduite de S1 a S2 ({progression_abs}h): bonne dynamique.")

    if redoublant == 1:
        remarques.append("Statut redoublant: necessite un suivi renforce et un accompagnement personnalise.")

    if not remarques:
        remarques.append(PROFIL_DESCRIPTIONS[score])

    return {
        "score":        score,
        "label":        PROFIL_LABELS[score],
        "remarques":    remarques,
        "danger_abs":   danger_abs,
        "danger_red":   danger_red,
        "score_danger": int(danger_abs) + int(danger_red),
        "abs_s1":       abs_s1,
        "abs_s2":       abs_s2,
        "total_abs":    total,
    }


def top_facteurs_risque(features_dict: dict, couleur: str) -> list:
    """
    Identifie les facteurs de risque principaux selon les vraies conditions.
    """
    facteurs = []

    moy_s1     = features_dict.get("Moyenne_S1", 12)
    moy_s2     = features_dict.get("Moyenne_S2", moy_s1)
    pfa        = features_dict.get("PFA_2", 12)
    abs_s1     = features_dict.get("Absences_S1", 0)
    abs_s2     = features_dict.get("Absences_S2", 0)
    modules_nv = features_dict.get("Modules_Non_Valides", 0)
    redoublant = features_dict.get("Redoublant", 0)
    progression = moy_s2 - moy_s1

    # Conditions de reussite non satisfaites
    if features_dict.get("Moyenne_Annuelle", (moy_s1 + moy_s2) / 2) < 12:
        facteurs.append(f"Moyenne annuelle insuffisante (seuil requis: 12/20)")
    if modules_nv > 3:
        facteurs.append(f"{int(modules_nv)} modules non valides (seuil max: 3)")
    if pfa < 12:
        facteurs.append(f"Note PFA insuffisante ({pfa:.1f}/20, seuil requis: 12/20)")

    # Zones de danger
    if abs_s1 > 10:
        facteurs.append(f"Absences S1 excessives ({abs_s1}h > 10h: zone de danger)")
    if abs_s2 > 10:
        facteurs.append(f"Absences S2 excessives ({abs_s2}h > 10h: zone de danger)")
    if redoublant == 1:
        facteurs.append("Statut redoublant (facteur de risque majeur)")

    # Autres alertes
    if moy_s1 < 10:
        facteurs.append(f"Moyenne S1 critique ({moy_s1:.1f}/20 < 10)")
    if progression < -2:
        facteurs.append(f"Regression entre S1 et S2 ({progression:+.1f} points)")

    return facteurs[:5] if facteurs else ["Aucun facteur de risque majeur identifie"]


def recommandations(couleur: str, facteurs: list) -> list:
    """
    Recommandations adaptees aux conditions reelles.
    """
    if couleur == "ROUGE":
        recs = [
            "URGENT: Convoquer l'etudiant pour un entretien avec le responsable pedagogique",
            "Mettre en place un plan de rattrapage pour les modules non valides",
            "Signaler a l'administration si les absences depassent le seuil reglementaire",
            "Proposer un tutorat personnalise pour ameliorer la moyenne",
        ]
        if any("PFA" in f for f in facteurs):
            recs.append("Encadrement renforce sur le projet PFA (note critique)")
        if any("redoublant" in f.lower() for f in facteurs):
            recs.append("Envisager une orientation vers une filiere mieux adaptee")
    elif couleur == "JAUNE":
        recs = [
            "Surveiller l'evolution des absences et contacter l'etudiant si > 10h",
            "Renforcement cible dans les modules a risque",
            "Encourager la participation active aux TD et TP",
            "Suivi mensuel de la progression academique",
        ]
        if any("PFA" in f for f in facteurs):
            recs.append("Ameliorer l'investissement dans le projet PFA")
    else:  # VERT
        recs = [
            "Continuer sur cette excellente trajectoire academique",
            "Encourager l'etudiant a mentorer ses camarades en difficulte",
            "Proposer des projets enrichissants ou des defis avances",
        ]
    return recs


def predict(features_dict: dict, modele: str = "LogisticRegression") -> dict:
    """
    Prediction complete avec vraies conditions de reussite.

    Args:
        features_dict: dictionnaire des features de l'etudiant
        modele: nom du modele ML a utiliser

    Returns:
        dict avec label, probabilite, note_predite, couleur, profil comportemental,
             facteurs de risque, recommandations, verification des 3 conditions
    """
    clf, scaler, feature_names = _load(modele)

    # Calculer les features derivees si absentes
    abs_s1 = features_dict.get("Absences_S1", 0)
    abs_s2 = features_dict.get("Absences_S2", 0)
    redoublant = int(features_dict.get("Redoublant", 0))

    # Ajouter les flags de danger si absents
    if "Danger_Absences" not in features_dict:
        features_dict["Danger_Absences"]   = 1 if (abs_s1 > 10 or abs_s2 > 10) else 0
    if "Danger_Redoublant" not in features_dict:
        features_dict["Danger_Redoublant"] = redoublant
    if "Score_Danger" not in features_dict:
        features_dict["Score_Danger"] = features_dict["Danger_Absences"] + features_dict["Danger_Redoublant"]
    if "Profil_Comportement" not in features_dict:
        total_abs = abs_s1 + abs_s2
        if total_abs <= 5:    features_dict["Profil_Comportement"] = 0
        elif total_abs <= 15: features_dict["Profil_Comportement"] = 1
        elif total_abs <= 30: features_dict["Profil_Comportement"] = 2
        else:                 features_dict["Profil_Comportement"] = 3

    X = np.array([[features_dict.get(f, 0.0) for f in feature_names]])
    X_sc = scaler.transform(X)

    label_num = clf.predict(X_sc)[0]
    proba     = float(clf.predict_proba(X_sc)[0][1])

    # Estimation de la note (ponderation intelligente)
    moy_s1 = features_dict.get("Moyenne_S1", 10)
    moy_s2 = features_dict.get("Moyenne_S2", moy_s1)
    pfa    = features_dict.get("PFA_2", 12)
    # Note estimee: 70% basee sur la proba, 30% ancree sur les vraies moyennes
    note_predite = proba * 20 * 0.7 + ((moy_s1 + moy_s2) / 2) * 0.3

    # Verification explicite des 3 conditions
    moy_annuelle = features_dict.get("Moyenne_Annuelle",
                                     features_dict.get("Moyenne_S2", note_predite))
    modules_nv   = features_dict.get("Modules_Non_Valides", 0)

    conditions = {
        "moy_ok":  float(moy_annuelle) >= 12.0,
        "mod_ok":  float(modules_nv)   <= 3,
        "pfa_ok":  float(pfa)          >= 12.0,
        "abs_s1_danger": abs_s1 > 10,
        "abs_s2_danger": abs_s2 > 10,
        "redoublant_danger": redoublant == 1,
    }

    couleur  = classifier_couleur(proba, note_predite)
    comportement = profil_comportement(abs_s1, abs_s2, redoublant)
    facteurs = top_facteurs_risque({**features_dict, "Moyenne_Annuelle": moy_annuelle}, couleur)
    recs     = recommandations(couleur, facteurs)

    return {
        "label":              "Reussi" if label_num == 1 else "Echec",
        "probabilite":        round(proba, 4),
        "note_predite":       round(note_predite, 2),
        "statut_couleur":     couleur,
        "conditions":         conditions,
        "profil_comportement": comportement,
        "facteurs_risque":    facteurs,
        "recommandations":    recs,
        "modele_utilise":     modele,
    }


def predict_batch(students: list, modele: str = "LogisticRegression") -> list:
    """Prediction pour plusieurs etudiants."""
    return [predict(s, modele) for s in students]


if __name__ == "__main__":
    # Test: un etudiant en difficulte
    etudiant_test = {
        "Absences_S1": 15, "Absences_S2": 12,
        "Module_S1_1": 8.0, "Module_S1_2": 7.5, "Module_S1_3": 9.0,
        "Module_S1_4": 8.0, "Module_S1_5": 7.0,
        "Anglais_Tech_1": 11.0, "Francais_Pro_1": 12.0,
        "Moyenne_S1": 8.9,
        "Module_S2_1": 9.0, "Module_S2_2": 8.5, "Module_S2_3": 9.5,
        "Module_S2_4": 8.0, "Module_S2_5": 9.0,
        "Anglais_Tech_2": 12.0, "Francais_Pro_2": 12.0,
        "PFA_2": 10.0, "Moyenne_S2": 9.6,
        "Modules_Non_Valides": 4, "Redoublant": 1,
        "Filiere_Code": 1, "Moyenne_Annuelle": 9.25,
        "Progression": 0.7, "Total_Absences": 27, "Moy_Module1": 8.5,
    }
    res = predict(etudiant_test)
    print("=== TEST PREDICTION ===")
    print(f"Label:       {res['label']}")
    print(f"Probabilite: {res['probabilite']*100:.1f}%")
    print(f"Note predite:{res['note_predite']:.1f}/20")
    print(f"Couleur:     {res['statut_couleur']}")
    print(f"Conditions:  {res['conditions']}")
    print(f"Profil:      {res['profil_comportement']['label']}")
    print(f"Remarques:   {res['profil_comportement']['remarques']}")
    print(f"Facteurs:    {res['facteurs_risque']}")
    print(f"Recs:        {res['recommandations']}")
