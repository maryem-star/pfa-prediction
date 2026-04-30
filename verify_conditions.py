"""
Script de vérification : L'algorithme respecte-t-il nos conditions ?
=====================================================================

Conditions documentées pour la prédiction :
  1. Moy >= 12 ET Modules_NV <= 3 ET PFA >= 12  →  Réussi
  2. Absences > 10h  →  Danger
  3. Redoublant  →  Facteur de risque
  4. Un étudiant moy >= 13 → JAMAIS en échec
  5. Module validé si score_prereq >= 12 (seuil)

Ce script teste chaque condition avec des étudiants fictifs.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ml_models.predict import (
    predict, predict_modules_3A,
    classifier_couleur, profil_comportement, diagnostiquer_causes_echec
)

# Couleurs pour le terminal
OK = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
tests_total = 0
tests_passed = 0

def check(name, condition, detail=""):
    global tests_total, tests_passed
    tests_total += 1
    if condition:
        tests_passed += 1
        print(f"  {OK} {name}")
    else:
        print(f"  {FAIL} {name} — {detail}")

print("=" * 70)
print("  AUDIT DES CONDITIONS DE L'ALGORITHME DE PREDICTION")
print("=" * 70)

# ── Étudiant de base (bon) ──
etudiant_bon = {
    "Module_S1_1": 14.0, "Module_S1_2": 15.0, "Module_S1_3": 13.5,
    "Module_S1_4": 14.0, "Module_S1_5": 13.0,
    "Module_S2_1": 14.5, "Module_S2_2": 15.0, "Module_S2_3": 14.0,
    "Module_S2_4": 13.5, "Module_S2_5": 14.0,
    "Anglais_Tech_1": 14.0, "Francais_Pro_1": 13.5,
    "Anglais_Tech_2": 14.0, "Francais_Pro_2": 14.0,
    "PFA_1": 15.0, "PFA_2": 15.0, "Participation": 16.0,
    "Absences_S1": 3.0, "Absences_S2": 2.0,
    "Redoublant_1A": 0, "Redoublant_2A": 0, "Redoublant": 0,
    "Modules_Non_Valides": 0,
    "Moyenne_S1": 13.86, "Moyenne_S2": 14.19, "Moyenne_Annuelle": 14.0,
}

# ── Étudiant faible ──
etudiant_faible = {
    "Module_S1_1": 7.0, "Module_S1_2": 6.0, "Module_S1_3": 8.0,
    "Module_S1_4": 7.0, "Module_S1_5": 6.5,
    "Module_S2_1": 8.0, "Module_S2_2": 7.0, "Module_S2_3": 7.5,
    "Module_S2_4": 8.5, "Module_S2_5": 6.0,
    "Anglais_Tech_1": 9.0, "Francais_Pro_1": 8.0,
    "Anglais_Tech_2": 9.0, "Francais_Pro_2": 8.5,
    "PFA_1": 8.0, "PFA_2": 8.0, "Participation": 8.0,
    "Absences_S1": 25.0, "Absences_S2": 30.0,
    "Redoublant_1A": 1, "Redoublant_2A": 0, "Redoublant": 1,
    "Modules_Non_Valides": 8,
    "Moyenne_S1": 7.29, "Moyenne_S2": 7.81, "Moyenne_Annuelle": 7.55,
}

# ── Étudiant Chafik-like (bonne moy mais notes déséquilibrées) ──
etudiant_chafik = {
    "Module_S1_1": 18.0, "Module_S1_2": 17.0, "Module_S1_3": 8.0,
    "Module_S1_4": 9.0, "Module_S1_5": 8.5,
    "Module_S2_1": 17.5, "Module_S2_2": 18.0, "Module_S2_3": 9.0,
    "Module_S2_4": 8.0, "Module_S2_5": 9.0,
    "Anglais_Tech_1": 15.0, "Francais_Pro_1": 14.0,
    "Anglais_Tech_2": 15.0, "Francais_Pro_2": 14.0,
    "PFA_1": 15.0, "PFA_2": 15.0, "Participation": 14.0,
    "Absences_S1": 5.0, "Absences_S2": 3.0,
    "Redoublant_1A": 0, "Redoublant_2A": 0, "Redoublant": 0,
    "Modules_Non_Valides": 3,
    "Moyenne_S1": 12.79, "Moyenne_S2": 13.19, "Moyenne_Annuelle": 13.4,
}

# ── Étudiant moyen (10-12, zone tolérance) ──
etudiant_moyen = {
    "Module_S1_1": 11.0, "Module_S1_2": 10.5, "Module_S1_3": 10.0,
    "Module_S1_4": 11.0, "Module_S1_5": 10.5,
    "Module_S2_1": 12.0, "Module_S2_2": 11.0, "Module_S2_3": 11.5,
    "Module_S2_4": 10.0, "Module_S2_5": 11.0,
    "Anglais_Tech_1": 12.0, "Francais_Pro_1": 11.0,
    "Anglais_Tech_2": 12.0, "Francais_Pro_2": 11.5,
    "PFA_1": 13.0, "PFA_2": 13.0, "Participation": 14.0,
    "Absences_S1": 8.0, "Absences_S2": 5.0,
    "Redoublant_1A": 0, "Redoublant_2A": 0, "Redoublant": 0,
    "Modules_Non_Valides": 4,
    "Moyenne_S1": 10.86, "Moyenne_S2": 11.5, "Moyenne_Annuelle": 11.18,
}

# ══════════════════════════════════════════════════════════════════════
# TEST 1 : Conditions de réussite 1A (Moy>=12, NV<=3, PFA>=12)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 1 : Conditions de Réussite 1A (Moy >= 12, NV <= 3, PFA >= 12)")
print("─" * 70)

res_bon = predict(etudiant_bon.copy())
check("Étudiant bon (14.0) → moy_ok = True",
      res_bon["conditions"]["moy_ok"] == True,
      f"Got {res_bon['conditions']['moy_ok']}")
check("Étudiant bon → mod_ok (NV=0 <= 3) = True",
      res_bon["conditions"]["mod_ok"] == True)
check("Étudiant bon → pfa_ok (PFA=15 >= 12) = True",
      res_bon["conditions"]["pfa_ok"] == True)
check("Étudiant bon → label = Réussi",
      "ussi" in res_bon["label"] or res_bon["label"] == "Réussi",
      f"Got '{res_bon['label']}'")

res_faible = predict(etudiant_faible.copy())
check("Étudiant faible (7.55) → moy_ok = False",
      res_faible["conditions"]["moy_ok"] == False,
      f"Got {res_faible['conditions']['moy_ok']}")
check("Étudiant faible → mod_ok (NV=8 > 3) = False",
      res_faible["conditions"]["mod_ok"] == False,
      f"Got {res_faible['conditions']['mod_ok']}")
check("Étudiant faible → pfa_ok (PFA=8 < 12) = False",
      res_faible["conditions"]["pfa_ok"] == False,
      f"Got {res_faible['conditions']['pfa_ok']}")

# ══════════════════════════════════════════════════════════════════════
# TEST 2 : Danger absences (> 10h)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 2 : Danger Absences (seuil > 10h)")
print("─" * 70)

check("Étudiant bon (3h S1, 2h S2) → Pas de danger",
      res_bon["conditions"]["abs_s1_danger"] == False and
      res_bon["conditions"]["abs_s2_danger"] == False)

check("Étudiant faible (25h S1, 30h S2) → Danger S1 ET S2",
      res_faible["conditions"]["abs_s1_danger"] == True and
      res_faible["conditions"]["abs_s2_danger"] == True)

profil_b = profil_comportement(3, 2, 0)
check("Profil bon (3h+2h) → score 0 (Très assidu)",
      profil_b["score"] == 0, f"Got score={profil_b['score']}")

profil_f = profil_comportement(25, 30, 1)
check("Profil faible (25h+30h, redoublant) → score 3 (Chronique)",
      profil_f["score"] == 3, f"Got score={profil_f['score']}")
check("Profil faible → danger_abs = True",
      profil_f["danger_abs"] == True)
check("Profil faible → danger_red = True (redoublant)",
      profil_f["danger_red"] == True)

# ══════════════════════════════════════════════════════════════════════
# TEST 3 : Diagnostic des Causes d'Echec (Remplace la tolérance)
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 3 : Diagnostic des Causes d'Echec")
print("─" * 70)

diag_bon = diagnostiquer_causes_echec(etudiant_bon.copy())
check("Étudiant bon (moy=14) → pas à risque",
      diag_bon["etudiant_a_risque"] == False,
      f"Got a_risque={diag_bon['etudiant_a_risque']}")

diag_moyen = diagnostiquer_causes_echec(etudiant_moyen.copy())
check("Étudiant moyen (moy=11.18 < 12) → à risque",
      diag_moyen["etudiant_a_risque"] == True,
      f"Got a_risque={diag_moyen['etudiant_a_risque']}")
check("Étudiant moyen → Causes détectées",
      diag_moyen["nb_causes"] > 0,
      f"Got nb_causes={diag_moyen['nb_causes']}")

# ══════════════════════════════════════════════════════════════════════
# TEST 4 : Prédiction 3A — Statut COHÉRENT avec la moyenne
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 4 : Prédiction 3A — Cohérence Statut Global vs Moyenne")
print("─" * 70)

res3a_bon = predict_modules_3A(etudiant_bon.copy(), "ite")
check("Étudiant bon (14.0) → statut VERT",
      res3a_bon["statut_global"] == "VERT",
      f"Got '{res3a_bon['statut_global']}'")

res3a_chafik = predict_modules_3A(etudiant_chafik.copy(), "ite")
check("Étudiant type Chafik (moy=13.4, notes déséquilibrées) → statut VERT",
      res3a_chafik["statut_global"] == "VERT",
      f"Got '{res3a_chafik['statut_global']}'")
check("  → JAMAIS en ROUGE (anciennement le bug)",
      res3a_chafik["statut_global"] != "ROUGE",
      f"Got '{res3a_chafik['statut_global']}'")

res3a_faible = predict_modules_3A(etudiant_faible.copy(), "ite")
check("Étudiant faible (7.55) → statut ROUGE",
      res3a_faible["statut_global"] == "ROUGE",
      f"Got '{res3a_faible['statut_global']}'")

res3a_moyen = predict_modules_3A(etudiant_moyen.copy(), "ite")
check("Étudiant moyen (11.18) → statut JAUNE (max, jamais ROUGE)",
      res3a_moyen["statut_global"] == "JAUNE",
      f"Got '{res3a_moyen['statut_global']}'")

# Test moy = 12.5 avec faible taux validation
etud_12_5 = dict(etudiant_chafik)
etud_12_5["Moyenne_Annuelle"] = 12.5
res3a_12_5 = predict_modules_3A(etud_12_5, "ite")
check("Étudiant moy=12.5 → statut != ROUGE (jamais ROUGE si moy >= 12)",
      res3a_12_5["statut_global"] != "ROUGE",
      f"Got '{res3a_12_5['statut_global']}'")

# ══════════════════════════════════════════════════════════════════════
# TEST 5 : Module individuel — seuil 12/20
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 5 : Validation Module Individuel (seuil = 12/20)")
print("─" * 70)

from src.preprocessing.module_relations import predict_module_validation

res_valide = predict_module_validation(prereq_score=14.0, absences_1A=5, seuil=12.0)
check("Module score 14/20, abs=5h → Validé",
      res_valide["valide"] == True,
      f"Got valide={res_valide['valide']}")
check("  → Score >= 12 (seuil)",
      res_valide["score_prereq"] >= 12,
      f"Got score={res_valide['score_prereq']}")

res_invalide = predict_module_validation(prereq_score=9.0, absences_1A=5, seuil=12.0)
check("Module score 9/20, abs=5h → Non validé",
      res_invalide["valide"] == False,
      f"Got valide={res_invalide['valide']}")

# Pénalité absences
res_penalise = predict_module_validation(prereq_score=12.5, absences_1A=25, absences_2A=20, seuil=12.0)
check("Module score 12.5 mais abs=45h → score réduit par pénalité absences",
      res_penalise["score_prereq"] < 12.5,
      f"Got score={res_penalise['score_prereq']}")

# Pénalité redoublant
res_red = predict_module_validation(prereq_score=13.0, absences_1A=0, redoublant_1A=1, seuil=12.0, moy_ann_ref=10.0)
check("Module score 13, redoublant → score réduit (pénalité *0.95)",
      res_red["score_prereq"] < 13.0,
      f"Got score={res_red['score_prereq']}")
check("  → Mais pénalité atténuée (score > 12)",
      res_red["score_prereq"] >= 12.0,
      f"Got score={res_red['score_prereq']}")



# ══════════════════════════════════════════════════════════════════════
# TEST 7 : Classifier couleur
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 7 : Classification VERT / JAUNE / ROUGE")
print("─" * 70)

check("Note=15, proba=0.85 → VERT",
      classifier_couleur(0.85, 15.0) == "VERT")
check("Note=11, proba=0.60 → ROUGE (note < 12 = toujours ROUGE en strict)",
      classifier_couleur(0.60, 11.0) == "ROUGE",
      f"Got {classifier_couleur(0.60, 11.0)}")
check("Note=12.5, proba=0.60 → JAUNE (note>=12 mais proba<70%)",
      classifier_couleur(0.60, 12.5) == "JAUNE",
      f"Got {classifier_couleur(0.60, 12.5)}")
check("Note=8, proba=0.25 → ROUGE",
      classifier_couleur(0.25, 8.0) == "ROUGE")
check("Note=13, proba=0.35 → ROUGE (proba < 0.40)",
      classifier_couleur(0.35, 13.0) == "ROUGE")

# ══════════════════════════════════════════════════════════════════════
# TEST 8 : Règle métier — minimum 2 modules validés
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 8 : Règle Métier — Minimum 2 modules validés")
print("─" * 70)

check("Étudiant faible → au moins 2 modules validés (règle métier)",
      res3a_faible["nb_valides"] >= 2,
      f"Got nb_valides={res3a_faible['nb_valides']}")

# ══════════════════════════════════════════════════════════════════════
# TEST 9 : Interface — Conditions Bilan 1A
# ══════════════════════════════════════════════════════════════════════
print("\n" + "─" * 70)
print("TEST 9 : Bilan 1A affiché dans l'interface")
print("─" * 70)

# Simuler le calcul du Bilan 1A (comme dans interface_13_whatif.py, ligne 902)
def bilan_1a(moy_ann, modules_nv, pfa):
    return moy_ann >= 12 and modules_nv <= 3 and pfa >= 12

check("Moy=14, NV=0, PFA=15 → REUSSI",
      bilan_1a(14, 0, 15) == True)
check("Moy=14, NV=5, PFA=15 → ECHEC (NV > 3)",
      bilan_1a(14, 5, 15) == False)
check("Moy=14, NV=0, PFA=10 → ECHEC (PFA < 12)",
      bilan_1a(14, 0, 10) == False)
check("Moy=11, NV=0, PFA=15 → ECHEC (Moy < 12)",
      bilan_1a(11, 0, 15) == False)
check("Moy=12, NV=3, PFA=12 → REUSSI (exactement aux seuils)",
      bilan_1a(12, 3, 12) == True)

# ══════════════════════════════════════════════════════════════════════
# RÉSUMÉ
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print(f"  RÉSULTAT FINAL : {tests_passed}/{tests_total} tests passés")
if tests_passed == tests_total:
    print(f"  {OK} TOUTES LES CONDITIONS SONT RESPECTÉES !")
else:
    failed = tests_total - tests_passed
    print(f"  {FAIL} {failed} condition(s) NON RESPECTÉE(S)")
print("=" * 70)
