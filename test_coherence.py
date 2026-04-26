"""
Test rapide : Vérifier que la logique corrigée fonctionne pour les cas critiques.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ml_models.predict import predict_modules_3A

OK = "[PASS]"
FAIL = "[FAIL]"
tests_total = 0
tests_passed = 0

def check(name, condition, detail=""):
    global tests_total, tests_passed
    tests_total += 1
    if condition:
        tests_passed += 1
        print(f"  {OK} {name}")
    else:
        print(f"  {FAIL} {name} -- {detail}")

# == Etudiant type Gourari Zineb ==
# Moy=13.6, PFA=11.84, NV=3, Redoublant=1, Abs=16h
zineb = {
    "Module_S1_1": 12.92, "Module_S1_2": 14.37, "Module_S1_3": 10.54,
    "Module_S1_4": 15.47, "Module_S1_5": 12.13,
    "Module_S2_1": 18.11, "Module_S2_2": 11.98, "Module_S2_3": 12.2,
    "Module_S2_4": 12.6, "Module_S2_5": 13.8,
    "Anglais_Tech_1": 19.08, "Francais_Pro_1": 12.73,
    "Anglais_Tech_2": 14.12, "Francais_Pro_2": 14.52,
    "PFA_1": 11.84, "PFA_2": 11.84, "Participation": 10.0,
    "Absences_S1": 1.0, "Absences_S2": 15.0,
    "Redoublant_1A": 0, "Redoublant_2A": 1, "Redoublant": 1,
    "Modules_Non_Valides": 3,
    "Moyenne_S1": 13.62, "Moyenne_S2": 13.59, "Moyenne_Annuelle": 13.61,
}

# == Etudiant type Chafik Omar ==
# Moy=13.4, PFA=15, NV=0, pas redoublant, pas d'absences
chafik = {
    "Module_S1_1": 18.0, "Module_S1_2": 17.0, "Module_S1_3": 8.0,
    "Module_S1_4": 9.0, "Module_S1_5": 8.5,
    "Module_S2_1": 17.5, "Module_S2_2": 18.0, "Module_S2_3": 9.0,
    "Module_S2_4": 8.0, "Module_S2_5": 9.0,
    "Anglais_Tech_1": 15.0, "Francais_Pro_1": 14.0,
    "Anglais_Tech_2": 15.0, "Francais_Pro_2": 14.0,
    "PFA_1": 15.0, "PFA_2": 15.0, "Participation": 14.0,
    "Absences_S1": 5.0, "Absences_S2": 3.0,
    "Redoublant_1A": 0, "Redoublant_2A": 0, "Redoublant": 0,
    "Modules_Non_Valides": 0,
    "Moyenne_S1": 12.79, "Moyenne_S2": 13.19, "Moyenne_Annuelle": 13.4,
}

# == Etudiant parfait ==
parfait = {
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

# == Etudiant faible ==
faible = {
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

# == Etudiant moy >= 13 mais PFA < 12 (comme beaucoup dans le dataset) ==
pfa_faible = {
    "Module_S1_1": 14.0, "Module_S1_2": 15.0, "Module_S1_3": 13.5,
    "Module_S1_4": 14.0, "Module_S1_5": 13.0,
    "Module_S2_1": 14.5, "Module_S2_2": 15.0, "Module_S2_3": 14.0,
    "Module_S2_4": 13.5, "Module_S2_5": 14.0,
    "Anglais_Tech_1": 14.0, "Francais_Pro_1": 13.5,
    "Anglais_Tech_2": 14.0, "Francais_Pro_2": 14.0,
    "PFA_1": 10.5, "PFA_2": 10.5, "Participation": 16.0,
    "Absences_S1": 3.0, "Absences_S2": 2.0,
    "Redoublant_1A": 0, "Redoublant_2A": 0, "Redoublant": 0,
    "Modules_Non_Valides": 3,
    "Moyenne_S1": 13.86, "Moyenne_S2": 14.19, "Moyenne_Annuelle": 14.0,
}

print("=" * 70)
print("  TESTS DE COHERENCE STATUT GLOBAL 3A")
print("=" * 70)

print("\nCAS 1 : Gourari Zineb (moy=13.6, PFA=11.84, Red=1)")
r = predict_modules_3A(zineb, "ite")
print(f"  Statut: {r['statut_global']} | Resume: {r['resume']}")
check("Zineb DEVRAIT etre VERT (4+ modules + Moy >= 12)",
      r["statut_global"] == "VERT",
      f"Got {r['statut_global']}")
check("Zineb ne doit plus etre impactee negativement par PFA/Red",
      "EXCELLENCE" in r["resume"] or "REUSSITE" in r["resume"],
      f"Resume: {r['resume']}")

print("\nCAS 2 : Chafik Omar (moy=13.4, PFA=15, NV=0, pas red)")
r = predict_modules_3A(chafik, "ite")
print(f"  Statut: {r['statut_global']} | Resume: {r['resume']}")
# Si < 4 modules, il devrait etre JAUNE (Risque Modere) malgre sa moyenne.
# SAUF si la moyenne S5 >= 12 (compensation possible -> VERT)
if r["note_s5_predite"] >= 12.0:
    check("Chafik est VERT par compensation (moyenne S5 >= 12)", r["statut_global"] == "VERT")
elif r["nb_valides"] >= 4:
    check("Chafik est VERT car il valide 4+ modules", r["statut_global"] == "VERT")
else:
    check("Chafik est JAUNE car il valide < 4 modules (Risque Modere)", r["statut_global"] == "JAUNE")

print("\nCAS 3 : Etudiant parfait (moy=14, PFA=15, NV=0)")
r = predict_modules_3A(parfait, "ite")
print(f"  Statut: {r['statut_global']} | Resume: {r['resume']}")
check("Parfait devrait etre VERT",
      r["statut_global"] == "VERT",
      f"Got {r['statut_global']}")

print("\nCAS 4 : Etudiant faible (moy=7.55)")
r = predict_modules_3A(faible, "ite")
print(f"  Statut: {r['statut_global']} | Resume: {r['resume']}")
check("Faible devrait etre ROUGE",
      r["statut_global"] == "ROUGE",
      f"Got {r['statut_global']}")

print("\nCAS 5 : Moy=14 mais PFA=10.5 (seul defaut)")
r = predict_modules_3A(pfa_faible, "ite")
print(f"  Statut: {r['statut_global']} | Resume: {r['resume']}")
check("PFA faible avec bonne moyenne -> devrait etre VERT",
      r["statut_global"] == "VERT",
      f"Got {r['statut_global']}")

print("\n" + "=" * 70)
print(f"  RESULTAT : {tests_passed}/{tests_total} tests passes")
if tests_passed == tests_total:
    print(f"  {OK} TOUTES LES CONDITIONS RESPECTEES !")
else:
    print(f"  {FAIL} {tests_total - tests_passed} echec(s)")
print("=" * 70)
