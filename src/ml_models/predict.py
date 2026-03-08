"""
Module de Prédiction ML — Système intelligent 3ème année
=========================================================
Deux modes de prédiction:

1. predict() — prédiction classique réussite 1A/2A
   Conditions: Moy >= 12, Modules_NV <= 3, PFA >= 12

2. predict_modules_3A() — prédiction des modules de 3ème année
   Entrée: données 1A + données 2A (optionnel)
   Sortie: validation module par module, note S5 et PFE estimées

Absences > 10h → danger | Redoublant → facteur de risque
"""

import os
import numpy as np
import joblib

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_PATH = os.path.join(BASE_DIR, "models")

# ─── Profils comportementaux ──────────────────────────────────────────────────
PROFIL_LABELS = {
    0: "Très assidu",
    1: "Assidu",
    2: "Comportement préoccupant",
    3: "Absentéiste chronique",
}

PROFIL_DESCRIPTIONS = {
    0: "L'étudiant est très régulier, pratiquement aucune absence. Attitude exemplaire.",
    1: "L'étudiant est globalement assidu avec quelques absences ponctuelles.",
    2: "Le nombre d'absences est préoccupant. Un suivi est recommandé.",
    3: "Absentéisme chronique détecté. Intervention urgente nécessaire.",
}


def _load(model_name: str):
    """Charge le modèle, le scaler et les feature names."""
    scaler        = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
    feature_names = joblib.load(os.path.join(MODELS_PATH, "feature_names.pkl"))
    clf           = joblib.load(os.path.join(MODELS_PATH, f"{model_name}.pkl"))
    return clf, scaler, feature_names


def classifier_couleur(probabilite: float, note_predite: float = None) -> str:
    """
    VERT/JAUNE/ROUGE basé sur les vraies conditions:
    - VERT  : note >= 12 ET proba >= 70%
    - ROUGE : note < 12  OU  proba < 40%
    - JAUNE : entre les deux
    """
    note = note_predite if note_predite is not None else probabilite * 20

    if note >= 12 and probabilite >= 0.70:
        return "VERT"
    elif note < 12 or probabilite < 0.40:
        return "ROUGE"
    else:
        return "JAUNE"


def profil_comportement(abs_s1: float, abs_s2: float, redoublant: int = 0) -> dict:
    """Analyse comportementale complète de l'étudiant."""
    total = abs_s1 + abs_s2
    progression_abs = abs_s2 - abs_s1

    if total <= 5:    score = 0
    elif total <= 15: score = 1
    elif total <= 30: score = 2
    else:             score = 3

    danger_abs = abs_s1 > 10 or abs_s2 > 10
    danger_red = redoublant == 1

    remarques = []
    if abs_s1 <= 2 and abs_s2 <= 2:
        remarques.append("Présence exemplaire: assiduité parfaite sur les deux semestres.")
    elif abs_s1 <= 5 and abs_s2 <= 5:
        remarques.append("Bonne assiduité globale sur l'année.")
    if abs_s1 > 10:
        remarques.append(f"Absences excessives au S1 ({abs_s1}h > seuil de 10h): zone de danger.")
    if abs_s2 > 10:
        remarques.append(f"Absences excessives au S2 ({abs_s2}h > seuil de 10h): zone de danger.")
    if progression_abs > 5:
        remarques.append(f"Aggravation des absences de S1 à S2 (+{progression_abs}h).")
    elif progression_abs < -5:
        remarques.append(f"Amélioration notable de l'assiduité de S1 à S2 ({progression_abs}h).")
    if redoublant == 1:
        remarques.append("Statut redoublant: nécessite un suivi renforcé.")
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
    """Identifie les facteurs de risque principaux."""
    facteurs = []

    moy_s1     = features_dict.get("Moyenne_S1", 12)
    moy_s2     = features_dict.get("Moyenne_S2", moy_s1)
    pfa        = features_dict.get("PFA_2", 12)
    abs_s1     = features_dict.get("Absences_S1", 0)
    abs_s2     = features_dict.get("Absences_S2", 0)
    modules_nv = features_dict.get("Modules_Non_Valides", 0)
    redoublant = features_dict.get("Redoublant", 0)
    progression = moy_s2 - moy_s1

    if features_dict.get("Moyenne_Annuelle", (moy_s1 + moy_s2) / 2) < 12:
        facteurs.append("Moyenne annuelle insuffisante (seuil requis: 12/20)")
    if modules_nv > 3:
        facteurs.append(f"{int(modules_nv)} modules non validés (seuil max: 3)")
    if pfa < 12:
        facteurs.append(f"Note PFA insuffisante ({pfa:.1f}/20, seuil requis: 12/20)")
    if abs_s1 > 10:
        facteurs.append(f"Absences S1 excessives ({abs_s1}h > 10h: zone de danger)")
    if abs_s2 > 10:
        facteurs.append(f"Absences S2 excessives ({abs_s2}h > 10h: zone de danger)")
    if redoublant == 1:
        facteurs.append("Statut redoublant (facteur de risque majeur)")
    if moy_s1 < 10:
        facteurs.append(f"Moyenne S1 critique ({moy_s1:.1f}/20 < 10)")
    if progression < -2:
        facteurs.append(f"Régression entre S1 et S2 ({progression:+.1f} points)")

    return facteurs[:5] if facteurs else ["Aucun facteur de risque majeur identifié"]


def recommandations(couleur: str, facteurs: list) -> list:
    """Recommandations adaptées aux conditions réelles."""
    if couleur == "ROUGE":
        recs = [
            "URGENT: Convoquer l'étudiant pour un entretien avec le responsable pédagogique",
            "Mettre en place un plan de rattrapage pour les modules non validés",
            "Signaler à l'administration si les absences dépassent le seuil réglementaire",
            "Proposer un tutorat personnalisé pour améliorer la moyenne",
        ]
        if any("PFA" in f for f in facteurs):
            recs.append("Encadrement renforcé sur le projet PFA (note critique)")
        if any("redoublant" in f.lower() for f in facteurs):
            recs.append("Envisager une orientation vers une filière mieux adaptée")
    elif couleur == "JAUNE":
        recs = [
            "Surveiller l'évolution des absences et contacter l'étudiant si > 10h",
            "Renforcement ciblé dans les modules à risque",
            "Encourager la participation active aux TD et TP",
            "Suivi mensuel de la progression académique",
        ]
        if any("PFA" in f for f in facteurs):
            recs.append("Améliorer l'investissement dans le projet PFA")
    else:
        recs = [
            "Continuer sur cette excellente trajectoire académique",
            "Encourager l'étudiant à mentorer ses camarades en difficulté",
            "Proposer des projets enrichissants ou des défis avancés",
        ]
    return recs


def predict(features_dict: dict, modele: str = "LogisticRegression") -> dict:
    """
    Prédiction classique réussite 1A/2A avec profil comportemental.

    Returns:
        dict avec label, probabilite, note_predite, statut_couleur,
        conditions, profil_comportement, facteurs_risque, recommandations
    """
    clf, scaler, feature_names = _load(modele)

    abs_s1 = features_dict.get("Absences_S1", 0)
    abs_s2 = features_dict.get("Absences_S2", 0)
    redoublant = int(features_dict.get("Redoublant", 0))

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

    X    = np.array([[features_dict.get(f, 0.0) for f in feature_names]])
    X_sc = scaler.transform(X)

    label_num = clf.predict(X_sc)[0]
    proba     = float(clf.predict_proba(X_sc)[0][1])

    moy_s1 = features_dict.get("Moyenne_S1", 10)
    moy_s2 = features_dict.get("Moyenne_S2", moy_s1)
    pfa    = features_dict.get("PFA_2", 12)
    note_predite = proba * 20 * 0.7 + ((moy_s1 + moy_s2) / 2) * 0.3

    moy_annuelle = features_dict.get("Moyenne_Annuelle",
                                     features_dict.get("Moyenne_S2", note_predite))
    modules_nv   = features_dict.get("Modules_Non_Valides", 0)

    conditions = {
        "moy_ok":           float(moy_annuelle) >= 12.0,
        "mod_ok":           float(modules_nv)   <= 3,
        "pfa_ok":           float(pfa)          >= 12.0,
        "abs_s1_danger":    abs_s1 > 10,
        "abs_s2_danger":    abs_s2 > 10,
        "redoublant_danger": redoublant == 1,
    }

    couleur      = classifier_couleur(proba, note_predite)
    comportement = profil_comportement(abs_s1, abs_s2, redoublant)
    facteurs     = top_facteurs_risque({**features_dict, "Moyenne_Annuelle": moy_annuelle}, couleur)
    recs         = recommandations(couleur, facteurs)

    return {
        "label":               "Réussi" if label_num == 1 else "Échec",
        "probabilite":         round(proba, 4),
        "note_predite":        round(note_predite, 2),
        "statut_couleur":      couleur,
        "conditions":          conditions,
        "profil_comportement": comportement,
        "facteurs_risque":     facteurs,
        "recommandations":     recs,
        "modele_utilise":      modele,
    }


def predict_modules_3A(etudiant_1A: dict, filiere: str,
                        etudiant_2A: dict = None,
                        modele: str = "RandomForest") -> dict:
    """
    Prédiction intelligente des modules de 3ème année.

    Args:
        etudiant_1A: dict avec les notes 1A (modules, absences, PFA, redoublant)
        filiere: clé ou code de filière (ex: "ite", "isic", 6, ...)
        etudiant_2A: dict avec les notes 2A (optionnel — proxy si absent)
        modele: modèle ML à utiliser pour l'évaluation globale

    Returns:
        dict complet:
            - modules_3A      : {module: {valide, score_prereq, probabilite, raison, label_fr}}
            - nb_valides      : int
            - nb_non_valides  : int
            - note_s5_predite : float
            - note_pfe_predite: float
            - statut_global   : "VERT" / "JAUNE" / "ROUGE"
            - taux_validation : float (%)
            - resume          : str
            - profil_1A       : dict (profil comportemental 1A)
            - profil_2A       : dict (profil comportemental 2A, si disponible)
            - facteurs_risque_3A: list
            - recommandations_3A: list
    """
    import sys
    sys.path.insert(0, BASE_DIR)
    from src.preprocessing.module_relations import predict_all_modules_3A, FILIERE_CODE_TO_KEY

    # Résoudre la filière
    if isinstance(filiere, int):
        filiere = FILIERE_CODE_TO_KEY.get(filiere, "ite")

    # Calcul prédiction 3A (module par module)
    res_3A = predict_all_modules_3A(etudiant_1A, filiere, etudiant_2A)

    # Profils comportementaux
    abs_1A_s1 = float(etudiant_1A.get("Absences_S1", 0))
    abs_1A_s2 = float(etudiant_1A.get("Absences_S2", 0))
    red_1A    = int(etudiant_1A.get("Redoublant", 0))
    profil_1A = profil_comportement(abs_1A_s1, abs_1A_s2, red_1A)

    profil_2A = None
    if etudiant_2A:
        abs_2A_s1 = float(etudiant_2A.get("Absences_S1", 0))
        abs_2A_s2 = float(etudiant_2A.get("Absences_S2", 0))
        red_2A    = int(etudiant_2A.get("Redoublant", 0))
        profil_2A = profil_comportement(abs_2A_s1, abs_2A_s2, red_2A)

    # Facteurs de risque spécifiques à la 3A
    facteurs_3A = []
    if res_3A["taux_validation"] < 60:
        facteurs_3A.append(f"Moins de 60% des modules 3A prédits validés ({res_3A['taux_validation']:.0f}%)")
    if profil_1A["danger_abs"]:
        facteurs_3A.append(f"Absences 1A excessives ({profil_1A['total_abs']:.0f}h > seuil 10h)")
    if red_1A:
        facteurs_3A.append("Redoublant en 1ère année — facteur de risque important")
    if profil_2A and profil_2A["danger_abs"]:
        facteurs_3A.append(f"Absences 2A excessives ({profil_2A['total_abs']:.0f}h > seuil 10h)")

    # Modules non validés (liste)
    modules_non_valides = [
        res["label_fr"]
        for mod_key, res in res_3A["modules_3A"].items()
        if not res["valide"]
    ]
    if modules_non_valides:
        facteurs_3A.append(f"Modules à risque: {', '.join(modules_non_valides)}")

    if not facteurs_3A:
        facteurs_3A = ["Aucun facteur de risque majeur — profil favorable pour la 3A"]

    # Recommandations 3A
    recs_3A = []
    statut = res_3A["statut_global"]
    if statut == "ROUGE":
        recs_3A = [
            "Renforcement urgent des prérequis dans les modules faillis",
            "Travail personnel intensif sur les modules de base (S1 et S2)",
            "Considérer un tutorat spécialisé avant la 3A",
            "Réduire les absences immédiatement — impact direct sur la 3A",
        ]
    elif statut == "JAUNE":
        recs_3A = [
            "Révision ciblée des modules prérequis insuffisants",
            "Maintenir un taux d'assiduité > 90% en 3A",
            "Préparer les projets 3A en avance (PFE)",
        ]
    else:
        recs_3A = [
            "Excellent profil — vous êtes prêt pour la 3ème année",
            "Choisissez des spécialisations ambitieuses en 3A",
            "Préparez un sujet de PFE innovant dès maintenant",
        ]

    return {
        **res_3A,
        "profil_1A":          profil_1A,
        "profil_2A":          profil_2A,
        "facteurs_risque_3A": facteurs_3A,
        "recommandations_3A": recs_3A,
        "modules_non_valides_liste": modules_non_valides,
    }


def predict_batch(students: list, modele: str = "LogisticRegression") -> list:
    """Prédiction classique pour plusieurs étudiants."""
    return [predict(s, modele) for s in students]


def predict_batch_3A(students: list, filieres: list) -> list:
    """Prédiction 3A pour plusieurs étudiants."""
    results = []
    for i, s in enumerate(students):
        filiere = filieres[i] if i < len(filieres) else "ite"
        results.append(predict_modules_3A(s, filiere))
    return results


if __name__ == "__main__":
    # Test prédiction 3A — étudiant ITE fort
    etudiant_test = {
        "Module_S1_1": 16.0, "Module_S1_2": 15.0, "Module_S1_3": 14.0,
        "Module_S1_4": 15.0, "Module_S1_5": 17.0,
        "Module_S2_1": 15.0, "Module_S2_2": 16.0, "Module_S2_3": 17.0,
        "Module_S2_4": 16.0, "Module_S2_5": 15.0,
        "PFA_2": 16.0, "Absences_S1": 3, "Absences_S2": 2, "Redoublant": 0,
        "Moyenne_S1": 15.4, "Moyenne_S2": 15.8, "Modules_Non_Valides": 0,
    }

    res = predict_modules_3A(etudiant_test, "ite")
    print("=== PRÉDICTION 3A — Étudiant ITE ===")
    print(f"Statut: {res['statut_global']}")
    print(f"Modules validés: {res['nb_valides']}/{res['nb_total']}")
    print(f"Note S5 estimée: {res['note_s5_predite']}/20")
    print(f"Note PFE estimée: {res['note_pfe_predite']}/20")
    print(f"Résumé: {res['resume']}")
    print("\nDétail par module:")
    for k, v in res["modules_3A"].items():
        icon = "✅" if v["valide"] else "❌"
        print(f"  {icon} {v['label_fr']}: {v['score_prereq']:.1f}/20")
