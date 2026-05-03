"""
Module de Prédiction ML — Système intelligent 3ème année
=========================================================
Trois modes:

1. predict() — prédiction classique réussite 1A/2A
   Conditions: Moy >= 12, Modules_NV <= 3, PFA >= 12

2. diagnostiquer_causes_echec() — diagnostic des causes d'échec
   Analyse: absences, notes faibles, regression, PFA, modules NV
   Ne modifie aucune note — diagnostic pur

3. predict_modules_3A() — prédiction des modules de 3ème année
   Entrée: données 1A + données 2A (optionnel)
   Sortie: validation module par module, note S5 et PFE estimées

Absences > 10h → danger | Redoublant → facteur de risque
"""

import os
import numpy as np
import joblib
from functools import lru_cache

# PrÃ©-importation pour Ã©viter les erreurs d'import circulaire dans FastAPI
try:
    import sklearn.linear_model._logistic
    import sklearn.svm._base
except ImportError:
    pass

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_PATH = os.path.join(BASE_DIR, "models")

# â”€â”€â”€ Profils comportementaux â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROFIL_LABELS = {
    0: "TrÃ¨s assidu",
    1: "Assidu",
    2: "Comportement prÃ©occupant",
    3: "AbsentÃ©iste chronique",
}

PROFIL_DESCRIPTIONS = {
    0: "L'Ã©tudiant est trÃ¨s rÃ©gulier, pratiquement aucune absence. Attitude exemplaire.",
    1: "L'Ã©tudiant est globalement assidu avec quelques absences ponctuelles.",
    2: "Le nombre d'absences est prÃ©occupant. Un suivi est recommandÃ©.",
    3: "AbsentÃ©isme chronique dÃ©tectÃ©. Intervention urgente nÃ©cessaire.",
}


@lru_cache(maxsize=10)
def _load(model_name: str):
    """Charge le modÃ¨le, le scaler et les feature names avec mise en cache."""
    scaler        = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
    feature_names = joblib.load(os.path.join(MODELS_PATH, "feature_names.pkl"))
    clf           = joblib.load(os.path.join(MODELS_PATH, f"{model_name}.pkl"))
    return clf, scaler, feature_names


def classifier_couleur(probabilite: float, note_predite: float = None) -> str:
    """
    Classification stricte basÃ©e uniquement sur la note prÃ©dite :
      VERT  : note >= 12.0
      JAUNE : 10.0 <= note < 12.0
      ROUGE : note < 10.0
    """
    note = float(note_predite) if note_predite is not None else float(probabilite) * 20.0
    note = max(0.0, min(20.0, note))

    if note >= 12.0:
        return "VERT"
    elif note >= 10.0:
        return "JAUNE"
    else:
        return "ROUGE"


def profil_comportement(abs_s1: float, abs_s2: float, redoublant: int = 0) -> dict:
    """Analyse comportementale complÃ¨te de l'Ã©tudiant."""
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
        remarques.append("PrÃ©sence exemplaire: assiduitÃ© parfaite sur les deux semestres.")
    elif abs_s1 <= 5 and abs_s2 <= 5:
        remarques.append("Bonne assiduitÃ© globale sur l'annÃ©e.")
    if abs_s1 > 10:
        remarques.append(f"Absences excessives au S1 ({abs_s1}h > seuil de 10h): zone de danger.")
    if abs_s2 > 10:
        remarques.append(f"Absences excessives au S2 ({abs_s2}h > seuil de 10h): zone de danger.")
    if progression_abs > 5:
        remarques.append(f"Aggravation des absences de S1 Ã  S2 (+{progression_abs}h).")
    elif progression_abs < -5:
        remarques.append(f"AmÃ©lioration notable de l'assiduitÃ© de S1 Ã  S2 ({progression_abs}h).")
    if redoublant == 1:
        remarques.append("Statut redoublant: nÃ©cessite un suivi renforcÃ©.")
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
        facteurs.append(f"{int(modules_nv)} modules non validÃ©s (seuil max: 3)")
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
        facteurs.append(f"RÃ©gression entre S1 et S2 ({progression:+.1f} points)")

    return facteurs[:5] if facteurs else ["Aucun facteur de risque majeur identifiÃ©"]


def recommandations(couleur: str, facteurs: list) -> list:
    """Recommandations adaptÃ©es aux conditions rÃ©elles."""
    if couleur == "ROUGE":
        recs = [
            "URGENT: Convoquer l'Ã©tudiant pour un entretien avec le responsable pÃ©dagogique",
            "Mettre en place un plan de rattrapage pour les modules non validÃ©s",
            "Signaler Ã  l'administration si les absences dÃ©passent le seuil rÃ©glementaire",
            "Proposer un tutorat personnalisÃ© pour amÃ©liorer la moyenne",
        ]
        if any("PFA" in f for f in facteurs):
            recs.append("Encadrement renforcÃ© sur le projet PFA (note critique)")
        if any("redoublant" in f.lower() for f in facteurs):
            recs.append("Envisager une orientation vers une filiÃ¨re mieux adaptÃ©e")
    elif couleur == "JAUNE":
        recs = [
            "Surveiller l'Ã©volution des absences et contacter l'Ã©tudiant si > 10h",
            "Renforcement ciblÃ© dans les modules Ã  risque",
            "Encourager la participation active aux TD et TP",
            "Suivi mensuel de la progression acadÃ©mique",
        ]
        if any("PFA" in f for f in facteurs):
            recs.append("AmÃ©liorer l'investissement dans le projet PFA")
    else:
        recs = [
            "Continuer sur cette excellente trajectoire acadÃ©mique",
            "Encourager l'Ã©tudiant Ã  mentorer ses camarades en difficultÃ©",
            "Proposer des projets enrichissants ou des dÃ©fis avancÃ©s",
        ]
    return recs


def predict(features_dict: dict, modele: str = "LogisticRegression") -> dict:
    """
    PrÃ©diction classique rÃ©ussite 1A/2A avec profil comportemental.

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
    # Features comportementales
    abs_s1     = float(features_dict.get("Absences_S1", 0) or 0)
    abs_s2     = float(features_dict.get("Absences_S2", 0) or 0)
    redoublant = int(features_dict.get("Redoublant", 0) or 0)

    # Construire le vecteur de features
    X    = np.array([[features_dict.get(f, 0.0) for f in feature_names]])
    X    = np.nan_to_num(X, nan=0.0)
    X_sc = scaler.transform(X)
    X_sc = np.nan_to_num(X_sc, nan=0.0)

    # PrÃ©diction numÃ©rique
    label_num = int(clf.predict(X_sc)[0])
    probas    = clf.predict_proba(X_sc)[0]
    
    # Extraire la probabilitÃ© de rÃ©ussite (VERT est Ã  l'index 2 dans ['JAUNE', 'ROUGE', 'VERT'] aprÃ¨s rÃ©entraÃ®nement)
    if len(probas) == 3:
        proba = float(probas[2])
    else:
        proba = float(probas[label_num]) if label_num < len(probas) else float(np.max(probas))

    # -- Calcul de la note prÃ©dite basÃ© sur les VRAIES notes --
    moy_s1 = float(features_dict.get("Moyenne_S1", 0) or 0)
    moy_s2 = float(features_dict.get("Moyenne_S2", 0) or 0)
    pfa    = float(features_dict.get("PFA_2", 0) or 0)
    
    # Formule acadÃ©mique pondÃ©rÃ©e (35% S1, 35% S2, 30% PFA)
    if moy_s1 > 0 and moy_s2 > 0 and pfa > 0:
        note_predite = moy_s1 * 0.35 + moy_s2 * 0.35 + pfa * 0.30
    elif moy_s1 > 0 and moy_s2 > 0:
        note_predite = (moy_s1 + moy_s2) / 2.0
    else:
        # Fallback : on utilise la probabilitÃ© du modÃ¨le
        note_predite = proba * 20.0

    note_predite = max(0.0, min(20.0, float(note_predite)))

    # Moyenne annuelle
    moy_annuelle = features_dict.get("Moyenne_Annuelle")
    if not moy_annuelle:
        moy_annuelle = (moy_s1 + moy_s2) / 2 if (moy_s1 > 0 and moy_s2 > 0) else note_predite

    modules_nv = int(features_dict.get("Modules_Non_Valides", 0) or 0)

    conditions = {
        "moy_ok":           bool(float(moy_annuelle) >= 12.0),
        "mod_ok":           bool(float(modules_nv or 0) <= 3),
        "pfa_ok":           bool(float(pfa) >= 12.0),
        "abs_s1_danger":    bool(float(abs_s1) > 10),
        "abs_s2_danger":    bool(float(abs_s2) > 10),
        "redoublant_danger": bool(int(redoublant) == 1),
    }

    couleur = classifier_couleur(proba, note_predite)
    label_text = couleur

    comportement = profil_comportement(abs_s1, abs_s2, redoublant)
    facteurs     = top_facteurs_risque({**features_dict, "Moyenne_Annuelle": moy_annuelle}, couleur)
    recs         = recommandations(couleur, facteurs)

    return {
        "label":               str(label_text),
        "probabilite":         round(float(proba), 4),
        "note_predite":        round(float(note_predite), 2),
        "statut_couleur":      str(couleur),
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
    PrÃ©diction intelligente des modules de 3Ã¨me annÃ©e.

    Args:
        etudiant_1A: dict avec les notes 1A (modules, absences, PFA, redoublant)
        filiere: clÃ© ou code de filiÃ¨re (ex: "ite", "isic", 6, ...)
        etudiant_2A: dict avec les notes 2A (optionnel â€” proxy si absent)
        modele: modÃ¨le ML Ã  utiliser pour l'Ã©valuation globale

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

    # RÃ©soudre la filiÃ¨re
    if isinstance(filiere, int):
        filiere = FILIERE_CODE_TO_KEY.get(filiere, "ite")

    # Calcul prÃ©diction 3A (module par module)
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

    # Facteurs de risque spÃ©cifiques Ã  la 3A
    facteurs_3A = []
    if res_3A["taux_validation"] < 60:
        facteurs_3A.append(f"Moins de 60% des modules 3A prÃ©dits validÃ©s ({res_3A['taux_validation']:.0f}%)")
    if profil_1A["danger_abs"]:
        facteurs_3A.append(f"Absences 1A excessives ({profil_1A['total_abs']:.0f}h > seuil 10h)")
    if red_1A:
        facteurs_3A.append("Redoublant en 1Ã¨re annÃ©e â€” facteur de risque important")
    if profil_2A and profil_2A["danger_abs"]:
        facteurs_3A.append(f"Absences 2A excessives ({profil_2A['total_abs']:.0f}h > seuil 10h)")

    # Modules non validÃ©s (liste)
    modules_non_valides = [
        res["label_fr"]
        for mod_key, res in res_3A["modules_3A"].items()
        if not res["valide"]
    ]
    if modules_non_valides:
        facteurs_3A.append(f"Modules Ã  risque: {', '.join(modules_non_valides)}")

    if not facteurs_3A:
        facteurs_3A = ["Aucun facteur de risque majeur â€” profil favorable pour la 3A"]

    # Recommandations 3A
    recs_3A = []
    statut = res_3A["statut_global"]
    if statut == "ROUGE":
        recs_3A = [
            "Renforcement urgent des prÃ©requis dans les modules faillis",
            "Travail personnel intensif sur les modules de base (S1 et S2)",
            "ConsidÃ©rer un tutorat spÃ©cialisÃ© avant la 3A",
            "RÃ©duire les absences immÃ©diatement â€” impact direct sur la 3A",
        ]
    elif statut == "JAUNE":
        recs_3A = [
            "RÃ©vision ciblÃ©e des modules prÃ©requis insuffisants",
            "Maintenir un taux d'assiduitÃ© > 90% en 3A",
            "PrÃ©parer les projets 3A en avance (PFE)",
        ]
    else:
        recs_3A = [
            "Excellent profil â€” vous Ãªtes prÃªt pour la 3Ã¨me annÃ©e",
            "Choisissez des spÃ©cialisations ambitieuses en 3A",
            "PrÃ©parez un sujet de PFE innovant dÃ¨s maintenant",
        ]

    return {
        **res_3A,
        "profil_1A":          profil_1A,
        "profil_2A":          profil_2A,
        "facteurs_risque_3A": facteurs_3A,
        "recommandations_3A": recs_3A,
        "modules_non_valides_liste": modules_non_valides,
    }


# â”€â”€â”€ Diagnostic des Causes d'Ã‰chec â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def diagnostiquer_causes_echec(features_dict: dict) -> dict:
    """
    Analyse les causes d'Ã©chec d'un Ã©tudiant a partir de ses donnees reelles.
    Ne modifie AUCUNE note â€” diagnostic pur.
    """
    causes = []
    moy_s1 = features_dict.get("Moyenne_S1", 10.0)
    moy_s2 = features_dict.get("Moyenne_S2", 10.0)
    moy_ann = features_dict.get("Moyenne_Annuelle", (moy_s1 + moy_s2) / 2)
    progression = moy_s2 - moy_s1
    pfa = features_dict.get("PFA_2", 12.0)
    abs_s1 = features_dict.get("Absences_S1", 0)
    abs_s2 = features_dict.get("Absences_S2", 0)
    total_abs = abs_s1 + abs_s2
    modules_nv = features_dict.get("Modules_Non_Valides", 0)
    redoublant = features_dict.get("Redoublant", 0)

    if moy_ann >= 12.0 and modules_nv <= 3 and pfa >= 12.0:
        return {"etudiant_a_risque": False, "causes": [], "nb_causes": 0, "severite_globale": "OK"}

    if moy_ann < 12.0:
        sev = "critique" if moy_ann < 10.0 else "majeure" if moy_ann < 11.0 else "moderee"
        causes.append({"titre": "Moyenne Annuelle Insuffisante", "categorie": "academique", "severite": sev,
            "description": f"Moyenne de {moy_ann:.1f}/20, il manque {12.0 - moy_ann:.1f} pts pour le seuil de 12/20.",
            "couleur": "#f43f5e" if sev == "critique" else "#f59e0b", "valeur": f"{moy_ann:.1f}/20"})

    if abs_s1 > 10:
        sev = "critique" if abs_s1 > 25 else "majeure" if abs_s1 > 15 else "moderee"
        causes.append({"titre": "Absences Excessives S1", "categorie": "comportemental", "severite": sev,
            "description": f"{abs_s1:.0f}h d'absence au S1 (seuil danger: 10h).",
            "couleur": "#f43f5e" if sev == "critique" else "#f97316", "valeur": f"{abs_s1:.0f}h"})

    if abs_s2 > 10:
        sev = "critique" if abs_s2 > 25 else "majeure" if abs_s2 > 15 else "moderee"
        causes.append({"titre": "Absences Excessives S2", "categorie": "comportemental", "severite": sev,
            "description": f"{abs_s2:.0f}h d'absence au S2 (seuil danger: 10h).",
            "couleur": "#f43f5e" if sev == "critique" else "#f97316", "valeur": f"{abs_s2:.0f}h"})

    if abs_s2 > abs_s1 + 5 and abs_s2 > 10:
        causes.append({"titre": "Aggravation des Absences S1->S2", "categorie": "comportemental", "severite": "majeure",
            "description": f"Absences passees de {abs_s1:.0f}h (S1) a {abs_s2:.0f}h (S2), soit +{abs_s2 - abs_s1:.0f}h.",
            "couleur": "#dc2626", "valeur": f"+{abs_s2 - abs_s1:.0f}h"})

    if progression < -2.0:
        causes.append({"titre": "Regression Academique S1->S2", "categorie": "academique", "severite": "majeure",
            "description": f"Moyenne chutee de {moy_s1:.1f} (S1) a {moy_s2:.1f} (S2), soit {progression:+.1f} pts.",
            "couleur": "#dc2626", "valeur": f"{progression:+.1f} pts"})
    elif progression < -0.5:
        causes.append({"titre": "Legere Baisse au S2", "categorie": "academique", "severite": "moderee",
            "description": f"Baisse de {abs(progression):.1f} pts entre S1 et S2.",
            "couleur": "#f59e0b", "valeur": f"{progression:+.1f} pts"})

    if pfa < 12.0:
        sev = "critique" if pfa < 8.0 else "majeure" if pfa < 10.0 else "moderee"
        causes.append({"titre": "Note PFA Insuffisante", "categorie": "academique", "severite": sev,
            "description": f"Note PFA de {pfa:.1f}/20, seuil requis: 12/20.",
            "couleur": "#f43f5e" if sev != "moderee" else "#f59e0b", "valeur": f"{pfa:.1f}/20"})

    if modules_nv > 3:
        sev = "critique" if modules_nv >= 6 else "majeure"
        causes.append({"titre": "Trop de Modules Non Valides", "categorie": "academique", "severite": sev,
            "description": f"{int(modules_nv)} modules non valides (seuil max: 3).",
            "couleur": "#f43f5e", "valeur": f"{int(modules_nv)} modules"})

    if redoublant == 1:
        causes.append({"titre": "Statut Redoublant", "categorie": "historique", "severite": "moderee",
            "description": "L'etudiant a deja redouble, un suivi renforce est necessaire.",
            "couleur": "#f97316", "valeur": "Oui"})

    modules_faibles = []
    for i in range(1, 6):
        for sem in ["S1", "S2"]:
            col = f"Module_{sem}_{i}"
            val = features_dict.get(col, None)
            if val is not None and float(val) < 8.0:
                modules_faibles.append((col, float(val)))
    if modules_faibles:
        mods_txt = ", ".join([f"{m[0].replace('_', ' ')} ({m[1]:.1f})" for m in modules_faibles[:4]])
        causes.append({"titre": f"{len(modules_faibles)} Module(s) Critique(s)", "categorie": "academique",
            "severite": "critique" if len(modules_faibles) >= 3 else "majeure",
            "description": f"Modules < 8/20: {mods_txt}.",
            "couleur": "#f43f5e", "valeur": f"{len(modules_faibles)} modules"})

    if total_abs > 20 and moy_ann < 11.0:
        causes.append({"titre": "Correlation Absences-Resultats", "categorie": "comportemental", "severite": "majeure",
            "description": f"{total_abs:.0f}h d'absence + moyenne {moy_ann:.1f}/20: correlation directe.",
            "couleur": "#dc2626", "valeur": f"{total_abs:.0f}h/{moy_ann:.1f}"})

    severites = [c["severite"] for c in causes]
    if "critique" in severites: sev_g = "critique"
    elif "majeure" in severites: sev_g = "majeure"
    elif severites: sev_g = "moderee"
    else: sev_g = "OK"

    return {"etudiant_a_risque": len(causes) > 0, "causes": causes, "nb_causes": len(causes), "severite_globale": sev_g}


def predict_batch(students: list, modele: str = "LogisticRegression") -> list:
    """Prediction classique pour plusieurs etudiants."""
    return [predict(s, modele) for s in students]


def predict_batch_3A(students: list, filieres: list) -> list:
    """Prediction 3A pour plusieurs etudiants."""
    results = []
    for i, s in enumerate(students):
        filiere = filieres[i] if i < len(filieres) else "ite"
        results.append(predict_modules_3A(s, filiere))
    return results
