"""
Relations inter-modules : 1ère Année + 2ème Année → 3ème Année
==============================================================
Chaque module de 3ème année est lié à des prérequis de 1A et 2A.
Si l'étudiant a une bonne note dans les prérequis → il va valider le module 3A.

Structure:
    MODULE_RELATIONS_3A[filiere][module_3A] = {
        "prereqs_1A": [(col_name, poids), ...],
        "prereqs_2A": [(col_name, poids), ...],
        "label_fr":   "Nom complet du module",
        "seuil":      12.0  # note minimale pour valider
    }

Positions des colonnes dans les fichiers Excel (1A):
    Module_S1_1 = Maths 1 / équivalent
    Module_S1_2 = Algo/Physique / équivalent
    Module_S1_3 = Architecture/Matériaux / équivalent
    Module_S1_4 = Électronique/Mécanique / équivalent
    Module_S1_5 = Systèmes/Résistance / équivalent
    Anglais_Tech_1, Francais_Pro_1
    Module_S2_1 = Maths 2 / équivalent
    Module_S2_2 = Structures/Physique2 / équivalent
    Module_S2_3 = POO/Électronique2 / équivalent
    Module_S2_4 = BDD/Thermo / équivalent
    Module_S2_5 = Réseaux/Matériaux / équivalent
    PFA_2
"""

import numpy as np

# ─── Définitions des modules 3A par filière ───────────────────────────────────

MODULE_RELATIONS_3A = {

    # ── ITE (Génie Informatique) ────────────────────────────────────────────────
    "ite": {
        "Developpement_Web_Avance": {
            "label_fr": "Développement Web Avancé",
            "prereqs_1A": [("Module_S2_3", 0.7), ("Module_S1_2", 0.3)], # S2_3 = POO
            "prereqs_2A": [("Module_S2_3", 0.7), ("Module_S2_4", 0.3)], # S2_4 = BDD
            "seuil": 12.0,
        },
        "Reseaux_Avances": {
            "label_fr": "Réseaux Avancés & Sécurité",
            "prereqs_1A": [("Module_S2_5", 1.0)], # S2_5 = Réseaux
            "prereqs_2A": [("Module_S2_5", 1.0)],
            "seuil": 12.0,
        },
        "Intelligence_Artificielle": {
            "label_fr": "Intelligence Artificielle & ML",
            "prereqs_1A": [("Module_S1_1", 0.6), ("Module_S2_1", 0.4)], # Maths 1 & Maths 2
            "prereqs_2A": [("Module_S2_1", 0.6), ("Module_S2_2", 0.4)],
            "seuil": 12.0,
        },
        "Genie_Logiciel": {
            "label_fr": "Génie Logiciel & Architecture",
            "prereqs_1A": [("Module_S2_3", 0.6), ("Module_S1_2", 0.4)], # POO & Algo
            "prereqs_2A": [("Module_S2_3", 0.7), ("Module_S2_2", 0.3)],
            "seuil": 12.0,
        },
        "Securite_Informatique": {
            "label_fr": "Sécurité Informatique",
            "prereqs_1A": [("Module_S2_5", 0.8), ("Module_S1_3", 0.2)], # Réseaux & Archi
            "prereqs_2A": [("Module_S2_5", 0.8), ("Module_S2_3", 0.2)],
            "seuil": 12.0,
        },
        "PFE": {
            "label_fr": "Projet de Fin d'Études (PFE)",
            "prereqs_1A": [("PFA_1", 1.0)], # Spécifique Projet
            "prereqs_2A": [("PFA_2", 1.0)], # Spécifique Projet
            "seuil": 12.0,
        },
    },

    # ── ISIC (Systèmes d'Information et Communication) ─────────────────────────
    "isic": {
        "Systemes_Distribues": {
            "label_fr": "Systèmes Distribués & Cloud",
            "prereqs_1A": [("Module_S2_5", 0.6), ("Module_S2_3", 0.4)], # Réseaux & POO
            "prereqs_2A": [("Module_S2_5", 0.6), ("Module_S2_3", 0.4)],
            "seuil": 12.0,
        },
        "Reseaux_Avances": {
            "label_fr": "Réseaux Avancés & Protocoles",
            "prereqs_1A": [("Module_S2_5", 1.0)],
            "prereqs_2A": [("Module_S2_5", 1.0)],
            "seuil": 12.0,
        },
        "Intelligence_Artificielle": {
            "label_fr": "Intelligence Artificielle",
            "prereqs_1A": [("Module_S1_1", 0.6), ("Module_S2_1", 0.4)],
            "prereqs_2A": [("Module_S2_1", 0.7), ("Module_S2_2", 0.3)],
            "seuil": 12.0,
        },
        "Securite_SI": {
            "label_fr": "Sécurité des Systèmes d'Information",
            "prereqs_1A": [("Module_S2_5", 0.8), ("Module_S1_3", 0.2)],
            "prereqs_2A": [("Module_S2_5", 0.8), ("Module_S2_3", 0.2)],
            "seuil": 12.0,
        },
        "Big_Data": {
            "label_fr": "Big Data & Analyse de Données",
            "prereqs_1A": [("Module_S2_4", 0.7), ("Module_S1_1", 0.3)], # BDD & Maths
            "prereqs_2A": [("Module_S2_4", 0.7), ("Module_S2_1", 0.3)],
            "seuil": 12.0,
        },
        "PFE": {
            "label_fr": "Projet de Fin d'Études (PFE)",
            "prereqs_1A": [("PFA_1", 1.0)],
            "prereqs_2A": [("PFA_2", 1.0)],
            "seuil": 12.0,
        },
    },

    # ── CCN (Cybersécurité & Réseaux) ──────────────────────────────────────────
    "ccn": {
        "Securite_Avancee": {
            "label_fr": "Sécurité Avancée & Cryptographie",
            "prereqs_1A": [("Module_S2_5", 0.8), ("Module_S1_1", 0.2)], # Math/Réseaux
            "prereqs_2A": [("Module_S2_5", 0.8), ("Module_S2_1", 0.2)],
            "seuil": 12.0,
        },
        "Reseaux_Entreprise": {
            "label_fr": "Réseaux d'Entreprise & Cloud",
            "prereqs_1A": [("Module_S2_5", 1.0)], # 100% Réseaux
            "prereqs_2A": [("Module_S2_5", 1.0)],
            "seuil": 12.0,
        },
        "Forensique_Numerique": {
            "label_fr": "Forensique Numérique & Audit",
            "prereqs_1A": [("Module_S2_5", 0.6), ("Module_S2_3", 0.4)],
            "prereqs_2A": [("Module_S2_5", 0.6), ("Module_S2_3", 0.4)],
            "seuil": 12.0,
        },
        "Pentesting": {
            "label_fr": "Test de Pénétration & Ethical Hacking",
            "prereqs_1A": [("Module_S2_5", 0.7), ("Module_S2_3", 0.3)],
            "prereqs_2A": [("Module_S2_5", 0.7), ("Module_S2_3", 0.3)],
            "seuil": 12.0,
        },
        "PFE": {
            "label_fr": "Projet de Fin d'Études (PFE)",
            "prereqs_1A": [("PFA_1", 1.0)],
            "prereqs_2A": [("PFA_2", 1.0)],
            "seuil": 12.0,
        },
    },

    # ── GEE (Génie Électrique & Énergétique) ───────────────────────────────────
    "gee": {
        "Electronique_Puissance": {
            "label_fr": "Électronique de Puissance",
            "prereqs_1A": [("Module_S1_4", 0.8), ("Module_S1_1", 0.2)], # Électronique
            "prereqs_2A": [("Module_S2_3", 0.8), ("Module_S2_1", 0.2)], # Électronique 2
            "seuil": 12.0,
        },
        "Machines_Electriques": {
            "label_fr": "Machines Électriques & Motorisation",
            "prereqs_1A": [("Module_S1_4", 0.7), ("Module_S1_5", 0.3)], # Électronique & Systèmes
            "prereqs_2A": [("Module_S2_3", 0.7), ("Module_S2_2", 0.3)],
            "seuil": 12.0,
        },
        "Energies_Renouvelables": {
            "label_fr": "Énergies Renouvelables & Smart Grid",
            "prereqs_1A": [("Module_S1_4", 0.6), ("Module_S1_2", 0.4)], # Électronique & Physique
            "prereqs_2A": [("Module_S2_3", 0.6), ("Module_S2_2", 0.4)], # Électronique 2 & Physique 2
            "seuil": 12.0,
        },
        "Automatique_Avancee": {
            "label_fr": "Automatique Avancée & Régulation",
            "prereqs_1A": [("Module_S1_5", 0.6), ("Module_S1_1", 0.4)], # Systèmes & Maths
            "prereqs_2A": [("Module_S2_2", 0.6), ("Module_S2_1", 0.4)], # Structures/Physique 2 & Maths 2
            "seuil": 12.0,
        },
        "PFE": {
            "label_fr": "Projet de Fin d'Études (PFE)",
            "prereqs_1A": [("PFA_1", 1.0)],
            "prereqs_2A": [("PFA_2", 1.0)],
            "seuil": 12.0,
        },
    },

    # ── Génie Civil ────────────────────────────────────────────────────────────
    "civil": {
        "Beton_Arme": {
            "label_fr": "Béton Armé & Structures",
            "prereqs_1A": [("Module_S1_5", 0.7), ("Module_S1_3", 0.3)], # Résistance/Systèmes & Matériaux
            "prereqs_2A": [("Module_S2_2", 0.7), ("Module_S2_5", 0.3)], # Structures & Matériaux (2A)
            "seuil": 12.0,
        },
        "Geotechnique": {
            "label_fr": "Géotechnique & Mécanique des Sols",
            "prereqs_1A": [("Module_S1_4", 0.6), ("Module_S1_5", 0.4)], # Mécanique & Systèmes
            "prereqs_2A": [("Module_S2_2", 0.6), ("Module_S2_4", 0.4)], # Structures & Thermo/Fluides
            "seuil": 12.0,
        },
        "Hydraulique": {
            "label_fr": "Hydraulique & Fluides",
            "prereqs_1A": [("Module_S1_2", 0.7), ("Module_S1_4", 0.3)], # Physique & Mécanique
            "prereqs_2A": [("Module_S2_4", 0.8), ("Module_S2_2", 0.2)], # Thermo/Fluides & Structures
            "seuil": 12.0,
        },
        "Routes_Ponts": {
            "label_fr": "Routes, Ponts & Ouvrages d'Art",
            "prereqs_1A": [("Module_S1_3", 0.5), ("Module_S1_5", 0.5)], # Matériaux & Résistance
            "prereqs_2A": [("Module_S2_5", 0.6), ("Module_S2_2", 0.4)], # Matériaux & Structures
            "seuil": 12.0,
        },
        "PFE": {
            "label_fr": "Projet de Fin d'Études (PFE)",
            "prereqs_1A": [("PFA_1", 1.0)],
            "prereqs_2A": [("PFA_2", 1.0)],
            "seuil": 12.0,
        },
    },

    # ── Génie Industriel ───────────────────────────────────────────────────────
    "industriel": {
        "Manufacturing_Avance": {
            "label_fr": "Manufacturing Avancé & Lean",
            "prereqs_1A": [("Module_S1_5", 0.5), ("Module_S1_3", 0.5)], # Systèmes & Matériaux
            "prereqs_2A": [("Module_S2_5", 0.6), ("Module_S2_2", 0.4)],
            "seuil": 12.0,
        },
        "Robotique_Automatisation": {
            "label_fr": "Robotique & Automatisation Industrielle",
            "prereqs_1A": [("Module_S1_4", 0.6), ("Module_S1_5", 0.4)], # Méca/Électro & Systèmes
            "prereqs_2A": [("Module_S2_3", 0.6), ("Module_S2_2", 0.4)],
            "seuil": 12.0,
        },
        "Logistique_Supply": {
            "label_fr": "Logistique & Supply Chain",
            "prereqs_1A": [("Module_S1_2", 0.5), ("Module_S1_1", 0.5)], # Algo/Méthodes & Maths
            "prereqs_2A": [("Module_S2_1", 0.6), ("Module_S2_4", 0.4)], # Maths & Thermo/Divers
            "seuil": 12.0,
        },
        "Qualite_HSE": {
            "label_fr": "Qualité & HSE (Hygiène Sécurité Environnement)",
            "prereqs_1A": [("Module_S1_5", 0.6), ("Module_S1_3", 0.4)], # Systèmes & Archi
            "prereqs_2A": [("Module_S2_5", 0.6), ("Module_S2_4", 0.4)],
            "seuil": 12.0,
        },
        "PFE": {
            "label_fr": "Projet de Fin d'Études (PFE)",
            "prereqs_1A": [("PFA_1", 1.0)],
            "prereqs_2A": [("PFA_2", 1.0)],
            "seuil": 12.0,
        },
    },
}

# ─── Mapping filière code → clé ───────────────────────────────────────────────
FILIERE_CODE_TO_KEY = {
    1: "isic",
    2: "ccn",
    3: "gee",
    4: "civil",
    5: "industriel",
    6: "ite",
}


def get_modules_3A(filiere: str) -> dict:
    """Retourne les modules 3A pour une filière donnée."""
    key = filiere.lower()
    for k in MODULE_RELATIONS_3A:
        if k in key:
            return MODULE_RELATIONS_3A[k]
    # Fallback: modules génériques
    return MODULE_RELATIONS_3A.get("ite", {})


def compute_prereq_score(etudiant: dict, module_key: str, filiere: str,
                          donnees_2A: dict = None) -> float:
    """
    Calcule le score de prérequis d'un étudiant pour un module 3A donné.

    Args:
        etudiant: dict avec les notes 1A de l'étudiant (colonnes du data_pipeline)
        module_key: clé du module 3A
        filiere: nom de la filière
        donnees_2A: dict avec les notes 2A (optionnel - si absent, utilise des proxies 1A)

    Returns:
        score float entre 0 et 20 (score de préparation pour ce module 3A)
    """
    modules = get_modules_3A(filiere)
    if module_key not in modules:
        return 12.0  # neutre

    config = modules[module_key]
    prereqs_1A = config.get("prereqs_1A", [])
    prereqs_2A = config.get("prereqs_2A", [])

    score = 0.0
    total_poids = 0.0

    # Contribution des prérequis 1A
    for col, poids in prereqs_1A:
        val = float(etudiant.get(col, 0.0))
        if val > 0:
            score += val * poids
            total_poids += poids

    # Contribution des prérequis 2A (si disponibles, sinon proxy 1A)
    if donnees_2A:
        for col, poids in prereqs_2A:
            val = float(donnees_2A.get(col, 0.0))
            if val > 0:
                score += val * poids
                total_poids += poids
    else:
        # Proxy: utiliser les modules S2 de 1A avec coefficient réduit
        for col, poids in prereqs_2A:
            val = float(etudiant.get(col, etudiant.get("Module_S2_1", 0.0)))
            if val > 0:
                score += val * poids * 0.8  # pénalité car pas de vraies données 2A
                total_poids += poids * 0.8

    if total_poids == 0:
        return 12.0

    return round(score / total_poids, 2)


def predict_module_validation(prereq_score: float, absences_1A: float,
                               absences_2A: float = 0, redoublant_1A: int = 0,
                               redoublant_2A: int = 0, pfa_score: float = None,
                               seuil: float = 12.0) -> dict:
    """
    Prédit si un étudiant va valider un module 3A donné.

    Critères:
        - Score prérequis >= seuil → base de prédiction
        - Absences 1A+2A > 10 → danger (réduction du score)
        - Redoublant 1A ou 2A → facteur de risque
        - Note PFA → influence sur PFE

    Returns:
        dict avec: valide (bool), score_prereq, probabilite, raison
    """
    score = prereq_score

    # Pénalités comportementales
    abs_total = absences_1A + absences_2A
    if abs_total > 30:
        score *= 0.75   # Absentéisme chronique
    elif abs_total > 20:
        score *= 0.85   # Absentéisme préoccupant
    elif abs_total > 10:
        score *= 0.92   # Légères absences

    # Pénalité redoublant
    if redoublant_1A:
        score *= 0.90
    if redoublant_2A:
        score *= 0.88

    # Calcul probabilité (sigmoïde centrée sur seuil)
    delta = score - seuil
    probabilite = 1.0 / (1.0 + np.exp(-delta * 0.5))
    probabilite = round(float(probabilite), 4)

    valide = score >= seuil

    # Raison principale
    if valide:
        if score >= 16:
            raison = "Excellent niveau dans les prérequis"
        elif score >= 14:
            raison = "Bon niveau dans les prérequis"
        else:
            raison = "Niveau suffisant dans les prérequis"
    else:
        if score < 8:
            raison = "Niveau très insuffisant dans les prérequis"
        elif score < 10:
            raison = "Prérequis insuffisants — modules de base non maîtrisés"
        else:
            raison = "Score prérequis légèrement en dessous du seuil"
        if abs_total > 10:
            raison += f" + absences excessives ({abs_total:.0f}h)"
        if redoublant_1A or redoublant_2A:
            raison += " + statut redoublant"

    return {
        "valide":        valide,
        "score_prereq":  round(score, 2),
        "probabilite":   probabilite,
        "raison":        raison,
    }


def predict_all_modules_3A(etudiant_1A: dict, filiere: str,
                            etudiant_2A: dict = None) -> dict:
    """
    Prédit la validation de tous les modules 3A pour un étudiant.

    Args:
        etudiant_1A: dict avec toutes les notes 1A
        filiere: nom/code de la filière
        etudiant_2A: dict avec les notes 2A (optionnel)

    Returns:
        dict complet avec:
            - modules_3A: {module_key: {valide, score_prereq, probabilite, raison, label_fr}}
            - nb_valides: int
            - nb_non_valides: int
            - note_s5_predite: float (estimée)
            - note_pfe_predite: float (estimée)
            - statut_global: "VERT" / "JAUNE" / "ROUGE"
            - resume: str
    """
    modules_3A = get_modules_3A(filiere)

    abs_1A = etudiant_1A.get("Absences_S1", 0) + etudiant_1A.get("Absences_S2", 0)
    abs_2A = (etudiant_2A.get("Absences_S1", 0) + etudiant_2A.get("Absences_S2", 0)) if etudiant_2A else 0
    red_1A = int(etudiant_1A.get("Redoublant", 0))
    red_2A = int(etudiant_2A.get("Redoublant", 0)) if etudiant_2A else 0
    pfa_1A = float(etudiant_1A.get("PFA_1", etudiant_1A.get("PFA_2", 12.0)))
    pfa_2A = float(etudiant_2A.get("PFA_2", pfa_1A)) if etudiant_2A else pfa_1A

    resultats = {}
    scores_valides = []
    scores_tous = []

    for module_key, config in modules_3A.items():
        prereq_score = compute_prereq_score(etudiant_1A, module_key, filiere, etudiant_2A)
        pfa_pour_module = pfa_2A if module_key == "PFE" else None

        res = predict_module_validation(
            prereq_score=prereq_score,
            absences_1A=abs_1A,
            absences_2A=abs_2A,
            redoublant_1A=red_1A,
            redoublant_2A=red_2A,
            pfa_score=pfa_pour_module,
            seuil=config.get("seuil", 12.0),
        )
        res["label_fr"] = config["label_fr"]
        resultats[module_key] = res
        scores_tous.append(res["score_prereq"])
        if res["valide"]:
            scores_valides.append(res["score_prereq"])

    nb_valides = sum(1 for r in resultats.values() if r["valide"])
    nb_total = len(resultats)
    nb_non_valides = nb_total - nb_valides

    # Note S5 estimée: moyenne pondérée des scores modules (hors PFE)
    scores_s5 = [r["score_prereq"] for k, r in resultats.items() if k != "PFE"]
    note_s5 = round(np.mean(scores_s5), 2) if scores_s5 else 12.0

    # Note PFE estimée: basée 100% sur le score PFE qui lui-même est basé sur PFA 1 et PFA 2
    pfe_score = resultats.get("PFE", {}).get("score_prereq", 12.0)
    note_pfe = round(pfe_score, 2)

    # Statut global
    taux_validation = nb_valides / nb_total if nb_total > 0 else 0
    if taux_validation >= 0.8 and note_s5 >= 12:
        statut_global = "VERT"
    elif taux_validation < 0.5 or note_s5 < 10:
        statut_global = "ROUGE"
    else:
        statut_global = "JAUNE"

    # Résumé
    resume = (
        f"{nb_valides}/{nb_total} modules de 3ème année prédits validés. "
        f"Note S5 estimée: {note_s5:.1f}/20 | Note PFE estimée: {note_pfe:.1f}/20."
    )

    return {
        "modules_3A":      resultats,
        "nb_valides":      nb_valides,
        "nb_non_valides":  nb_non_valides,
        "nb_total":        nb_total,
        "note_s5_predite": note_s5,
        "note_pfe_predite": note_pfe,
        "statut_global":   statut_global,
        "taux_validation": round(taux_validation * 100, 1),
        "resume":          resume,
        "filiere":         filiere,
    }


if __name__ == "__main__":
    # Test avec un étudiant ITE fort
    etudiant_fort = {
        "Module_S1_1": 16.0, "Module_S1_2": 15.0, "Module_S1_3": 14.0,
        "Module_S1_4": 15.0, "Module_S1_5": 17.0,
        "Module_S2_1": 15.0, "Module_S2_2": 16.0, "Module_S2_3": 17.0,
        "Module_S2_4": 16.0, "Module_S2_5": 15.0,
        "PFA_2": 16.0, "Absences_S1": 3, "Absences_S2": 2, "Redoublant": 0,
    }
    res = predict_all_modules_3A(etudiant_fort, "ite")
    print(f"=== Étudiant fort (ITE) ===")
    print(f"Résumé: {res['resume']}")
    for k, v in res["modules_3A"].items():
        icon = "✅" if v["valide"] else "❌"
        print(f"  {icon} {v['label_fr']}: {v['score_prereq']:.1f}/20 — {v['raison']}")

    print()
    # Test avec un étudiant en difficulté
    etudiant_faible = {
        "Module_S1_1": 8.0, "Module_S1_2": 7.0, "Module_S1_3": 9.0,
        "Module_S1_4": 8.0, "Module_S1_5": 7.0,
        "Module_S2_1": 9.0, "Module_S2_2": 8.0, "Module_S2_3": 9.0,
        "Module_S2_4": 8.0, "Module_S2_5": 7.0,
        "PFA_2": 9.0, "Absences_S1": 15, "Absences_S2": 20, "Redoublant": 1,
    }
    res2 = predict_all_modules_3A(etudiant_faible, "ite")
    print(f"=== Étudiant faible (ITE) ===")
    print(f"Résumé: {res2['resume']}")
    for k, v in res2["modules_3A"].items():
        icon = "✅" if v["valide"] else "❌"
        print(f"  {icon} {v['label_fr']}: {v['score_prereq']:.1f}/20")
