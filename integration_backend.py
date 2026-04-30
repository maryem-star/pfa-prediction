"""
Script d'intégration ML ↔ Backend
==================================
Guide d'intégration ML — PFA 2025-2026
Backend: FastAPI + MySQL  |  API: http://127.0.0.1:8000

Workflow complet:
  1. Login → Token JWT
  2. Récupérer les étudiants + notes depuis l'API
  3. Entraîner les modèles ML (RandomForest, SVM, LogisticRegression)
  4. Envoyer les prédictions via POST /predictions/
  5. Vérifier les stats du dashboard
"""

import sys
import io
# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, f1_score, classification_report

# ─── Configuration ────────────────────────────────────────────────────────────
API_URL   = "http://127.0.0.1:8000"
EMAIL     = "admin@pfa.com"
PASSWORD  = "admin123"
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")

# ─── Étape 1 : Login ──────────────────────────────────────────────────────────
def login() -> dict:
    """Authentification et récupération du token JWT."""
    print("🔐 Connexion à l'API backend...")
    resp = requests.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    if resp.status_code != 200:
        raise ConnectionError(f"❌ Login échoué ({resp.status_code}): {resp.text}")
    token = resp.json()["access_token"]
    print("✅ Connecté avec succès!")
    return {"Authorization": f"Bearer {token}"}


# ─── Étape 2 : Récupérer les données ──────────────────────────────────────────
def get_students(headers: dict) -> pd.DataFrame:
    """Récupère la liste des étudiants depuis l'API."""
    print("\n📥 Récupération des étudiants...")
    resp = requests.get(f"{API_URL}/students/", headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(f"❌ Impossible de récupérer les étudiants: {resp.text}")
    students = resp.json()
    df = pd.DataFrame(students)
    print(f"✅ {len(df)} étudiants récupérés")
    return df


def get_grades(headers: dict) -> pd.DataFrame:
    """Récupère les notes depuis l'API."""
    print("\n📥 Récupération des notes...")
    resp = requests.get(f"{API_URL}/grades/", headers=headers)
    if resp.status_code != 200:
        print(f"⚠️  Notes non disponibles ({resp.status_code}). Utilise ton dataset Excel.")
        return pd.DataFrame()
    grades = resp.json()
    df = pd.DataFrame(grades)
    print(f"✅ {len(df)} enregistrements de notes récupérés")
    return df


def merge_data(df_students: pd.DataFrame, df_grades: pd.DataFrame) -> pd.DataFrame:
    """Fusionne étudiants + notes en transformant les matières en colonnes."""
    if df_grades.empty:
        return df_students
        
    # Extraire l'ID depuis l'objet étudiant complet de l'API si nécessaire
    if 'id' not in df_students.columns:
        print("Erreur: Colonne 'id' absente dans la liste des étudiants.")
        return df_students

    # Renommer temporairement pour le pivot
    df_grades_pivot = df_grades.pivot(index='student_id', columns='matiere', values='note').reset_index()
    
    # Mapper les noms de base "Matiere_1", etc. vers les features attendues si elles ne correspondent pas
    col_mapping = {
        "Matiere_1": "Mathematiques_1",
        "Matiere_2": "Algorithmique_Prog",
        "Matiere_3": "Architecture_Ord",
        "Matiere_4": "Electronique_Num",
        "Matiere_5": "Reseaux_Info_1",
        "Anglais": "Anglais_Tech_1",
        "Francais": "Francais_Pro_1"
    }
    df_grades_pivot.rename(columns=col_mapping, inplace=True)
    
    # Calculer une 'Moyenne_S1' factice pour le ML si on ne l'a pas
    matieres_s1 = ["Mathematiques_1", "Algorithmique_Prog", "Architecture_Ord", "Electronique_Num", "Reseaux_Info_1", "Anglais_Tech_1", "Francais_Pro_1"]
    dispo_s1 = [m for m in matieres_s1 if m in df_grades_pivot.columns]
    if dispo_s1:
        df_grades_pivot["Moyenne_S1"] = df_grades_pivot[dispo_s1].mean(axis=1)

    # Fusion
    df_merged = df_students.merge(df_grades_pivot, left_on="id", right_on="student_id", how="left")
    
    # Créer une target artificielle 'statut_couleur' puisque on n'en a pas pour les étudiants bruts
    # juste pour que le script puisse s'entraîner (ce script semble être un POC/Test)
    def determine_statut(row):
        moy = row.get("Moyenne_S1", 0)
        if pd.isna(moy): return "JAUNE"
        if moy >= 12: return "VERT"
        if moy >= 10: return "JAUNE"
        return "ROUGE"
        
    df_merged["statut_couleur"] = df_merged.apply(determine_statut, axis=1)

    print(f"✅ Fusion réussie: {len(df_merged)} lignes, colonnes utiles trouvées: {[c for c in df_merged.columns if c in FEATURES]}")
    return df_merged


# ─── Étape 3 : Entraîner les modèles ML ───────────────────────────────────────
FEATURES = [
    "Absences_S1", "Mathematiques_1", "Algorithmique_Prog", "Architecture_Ord",
    "Electronique_Num", "Reseaux_Info_1", "Anglais_Tech_1", "Francais_Pro_1", "Moyenne_S1",
    "Absences_S2", "Mathematiques_2", "Structures_Donnees", "Systemes_Exploitation",
    "Bases_Donnees", "Reseaux_Info_2", "Anglais_Tech_2", "Francais_Pro_2", "PFA_2",
    "Modules_Non_Valides", "Redoublant",
]

MODELES = {
    "RandomForest":       RandomForestClassifier(n_estimators=100, random_state=42),
    "SVM":                SVC(probability=True, random_state=42),
    "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
}


def preparer_features(df: pd.DataFrame) -> tuple:
    """Prépare X et y depuis le DataFrame."""
    # Colonnes disponibles seulement
    features_dispo = [f for f in FEATURES if f in df.columns]

    if not features_dispo:
        raise ValueError(
            "❌ Aucune feature disponible dans le DataFrame. "
            "Vérifie la structure des données de l'API."
        )

    X = df[features_dispo].fillna(0)

    # Target : encoder 'statut_predit' ou 'statut_couleur'
    target_col = None
    for col in ["statut_couleur", "statut_predit", "resultat"]:
        if col in df.columns:
            target_col = col
            break

    if target_col is None:
        raise ValueError(
            "❌ Aucune colonne cible (statut_couleur / statut_predit) trouvée."
        )

    le = LabelEncoder()
    y = le.fit_transform(df[target_col].fillna("JAUNE"))
    print(f"   Features utilisées : {features_dispo}")
    print(f"   Classes target     : {list(le.classes_)}")
    return X, y, le, features_dispo


def entrainer_modeles(X, y) -> dict:
    """Entraîne et évalue les 3 modèles ML."""
    print("\n🤖 Entraînement des modèles ML...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    resultats = {}
    for nom, clf in MODELES.items():
        print(f"\n   🔧 Entraînement {nom}...")
        clf.fit(X_train_sc, y_train)
        y_pred = clf.predict(X_test_sc)
        acc    = accuracy_score(y_test, y_pred)
        f1     = f1_score(y_test, y_pred, average="weighted")

        # Sauvegarder le modèle
        os.makedirs(MODELS_DIR, exist_ok=True)
        joblib.dump(clf, os.path.join(MODELS_DIR, f"{nom}.pkl"))
        print(f"   ✅ {nom}: Accuracy={acc:.2%}, F1={f1:.2%} → sauvegardé dans models/{nom}.pkl")
        resultats[nom] = {"accuracy": round(acc, 4), "f1": round(f1, 4)}

    # Sauvegarder scaler + feature names
    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(list(X.columns), os.path.join(MODELS_DIR, "feature_names.pkl"))
    joblib.dump(resultats, os.path.join(MODELS_DIR, "metrics.pkl"))
    print(f"\n✅ Scaler et feature_names sauvegardés.")
    return resultats, scaler


# ─── Étape 4 : Envoyer les prédictions à l'API ────────────────────────────────
def envoyer_predictions(df: pd.DataFrame, scaler, headers: dict,
                        modele_nom: str = "RandomForest"):
    """Prédit pour chaque étudiant et envoie les résultats à l'API."""
    print(f"\n📤 Envoi des prédictions ({modele_nom}) vers l'API...")

    clf_path = os.path.join(MODELS_DIR, f"{modele_nom}.pkl")
    if not os.path.exists(clf_path):
        print(f"⚠️  Modèle {modele_nom} non trouvé, entraîne d'abord le modèle.")
        return

    clf           = joblib.load(clf_path)
    feature_names = joblib.load(os.path.join(MODELS_DIR, "feature_names.pkl"))

    succes = 0
    echecs = 0
    for _, row in df.iterrows():
        if "id" not in row or pd.isna(row["id"]):
            continue

        features = np.array([[row.get(f, 0) for f in feature_names]])
        features_sc = scaler.transform(features)

        # Probabilité de réussite
        proba = float(clf.predict_proba(features_sc)[0].max())
        moy_annuelle = (row.get("Moyenne_S1", 10) + row.get("PFA_2", 12)) / 2
        note_predite = round(proba * 20 * 0.7 + moy_annuelle * 0.3, 2)

        payload = {
            "student_id":           int(row["id"]),
            "modele_utilise":       modele_nom,
            "probabilite_reussite": round(proba, 4),
            "note_predite":         note_predite,
        }

        resp = requests.post(
            f"{API_URL}/predictions/",
            headers=headers,
            json=payload
        )
        if resp.status_code in (200, 201):
            succes += 1
        else:
            echecs += 1
            if echecs <= 3:  # Afficher seulement les 3 premières erreurs
                print(f"   ⚠️  Étudiant {row['id']}: {resp.status_code} - {resp.text[:100]}")

    print(f"✅ {succes} prédictions envoyées avec succès | {echecs} erreurs")


# ─── Étape 5 : Vérifier les stats ─────────────────────────────────────────────
def verifier_dashboard(headers: dict):
    """Affiche les statistiques finales du dashboard."""
    print("\n📊 Vérification des stats du dashboard...")
    resp = requests.get(f"{API_URL}/predictions/dashboard/couleurs", headers=headers)
    if resp.status_code == 200:
        stats = resp.json()
        print(f"   🟢 VERT  : {stats.get('VERT', 0)} étudiants")
        print(f"   🟡 JAUNE : {stats.get('JAUNE', 0)} étudiants")
        print(f"   🔴 ROUGE : {stats.get('ROUGE', 0)} étudiants")
        print(f"   📋 Total : {stats.get('total', 0)} prédictions")
    else:
        print(f"⚠️  Dashboard non disponible: {resp.status_code}")


# ─── MAIN : Workflow complet ───────────────────────────────────────────────────
def run_integration():
    print("=" * 60)
    print("  INTEGRATION ML ↔ BACKEND — PFA 2025-2026")
    print("=" * 60)

    try:
        # 1. Login
        headers = login()

        # 2. Récupérer les données
        df_students = get_students(headers)
        df_grades   = get_grades(headers)
        df          = merge_data(df_students, df_grades)
        print(f"\n📋 DataFrame final: {df.shape[0]} lignes × {df.shape[1]} colonnes")

        # 3. Préparer features et entraîner
        try:
            X, y, le, features_dispo = preparer_features(df)
            metriques, scaler = entrainer_modeles(X, y)
            print("\n📈 Résumé des métriques:")
            for nom, m in metriques.items():
                print(f"   {nom}: Accuracy={m['accuracy']:.2%}, F1={m['f1']:.2%}")

            # 4. Envoyer prédictions pour les 3 modèles
            for modele in ["RandomForest", "SVM", "LogisticRegression"]:
                envoyer_predictions(df, scaler, headers, modele)

        except ValueError as e:
            print(f"\n⚠️  {e}")
            print("   → Les données de l'API ne contiennent pas encore de notes.")
            print("   → Les modèles existants sont conservés dans /models/.")

        # 5. Vérifier le dashboard
        verifier_dashboard(headers)

        print("\n" + "=" * 60)
        print("  ✅ INTÉGRATION TERMINÉE AVEC SUCCÈS!")
        print("=" * 60)

    except ConnectionError as e:
        print(f"\n❌ ERREUR DE CONNEXION: {e}")
        print("   → Assure-toi que le serveur backend est bien lancé:")
        print("   → cd pfa-student-prediction && uvicorn src.main:app --reload")

    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE: {e}")
        import traceback; traceback.print_exc()


if __name__ == "__main__":
    run_integration()
