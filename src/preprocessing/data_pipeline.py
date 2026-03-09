"""
Pipeline de prétraitement universel — Toutes filières
Étendu pour la prédiction des modules de 3ème année.

Structure:
    - Données 1A : 6 modules S1 + 6 modules S2 + PFA + absences + redoublant
    - Données 2A : idem (optionnel — proxy si absent)
    - Features : notes brutes + features dérivées + scores prérequis 3A
    - Cibles   : Reussite (binaire) + validation de chaque module 3A
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

# ─── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DATA_PATH  = os.path.join(BASE_DIR, "data", "raw")
PROC_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")
MODELS_PATH    = os.path.join(BASE_DIR, "models")

os.makedirs(PROC_DATA_PATH, exist_ok=True)
os.makedirs(MODELS_PATH,    exist_ok=True)

# ─── Mapping par POSITION (identique pour toutes les filières) ─────────────────
POSITION_MAP = {
    0:  "CNE",
    1:  "Nom",
    2:  "Prenom",
    3:  "Absences_S1",
    4:  "Module_S1_1",
    5:  "Module_S1_2",
    6:  "Module_S1_3",
    7:  "Module_S1_4",
    8:  "Module_S1_5",
    9:  "Anglais_Tech_1",
    10: "Francais_Pro_1",
    11: "Moyenne_S1",
    12: "Absences_S2",
    13: "Module_S2_1",
    14: "Module_S2_2",
    15: "Module_S2_3",
    16: "Module_S2_4",
    17: "Module_S2_5",
    18: "Anglais_Tech_2",
    19: "Francais_Pro_2",
    20: "PFA_2",
    21: "Moyenne_S2",
    22: "Moyenne_Annuelle",
    23: "Modules_Non_Valides",
    24: "Redoublant",
}

FEATURE_COLS = [
    "Absences_S1",
    "Module_S1_1", "Module_S1_2", "Module_S1_3",
    "Module_S1_4", "Module_S1_5",
    "Anglais_Tech_1", "Francais_Pro_1",
    "Moyenne_S1",
    "Absences_S2",
    "Module_S2_1", "Module_S2_2", "Module_S2_3",
    "Module_S2_4", "Module_S2_5",
    "Anglais_Tech_2", "Francais_Pro_2",
    "PFA_2",
    "Modules_Non_Valides",
    "Redoublant",
    "Filiere_Code",
    # Flags de danger
    "Danger_Absences",
    "Danger_Redoublant",
    "Score_Danger",
    "Profil_Comportement",
]

TARGET_COL = "Moyenne_Annuelle"

FILIERE_MAP = {
    "isic": 1, "ccn": 2, "gee": 3,
    "civil": 4, "industriel": 5, "ite": 6,
}


def detect_filiere(filename: str) -> str:
    """Détecte la filière depuis le nom du fichier."""
    fname = filename.lower()
    for key in FILIERE_MAP:
        if key in fname:
            return key
    return "inconnu"


def load_filiere(filepath: str) -> pd.DataFrame:
    """
    Charge un fichier Excel de n'importe quelle filière.
    Utilise le mapping par position.
    """
    df_raw = pd.read_excel(filepath, header=3)
    cols = list(df_raw.columns)

    col11_empty = str(cols[11]).startswith("Unnamed") or str(cols[11]).strip() == ""

    if col11_empty:
        mapping = {cols[i]: POSITION_MAP[i] for i in POSITION_MAP if i < len(cols)}
        mapping[cols[11]] = "Col_vide"
        mapping[cols[12]] = "Moyenne_S1"
        mapping[cols[13]] = "Absences_S2"
        mapping[cols[14]] = "Module_S2_1"
        mapping[cols[15]] = "Module_S2_2"
        mapping[cols[16]] = "Module_S2_3"
        mapping[cols[17]] = "Module_S2_4"
        mapping[cols[18]] = "Module_S2_5"
        mapping[cols[19]] = "Anglais_Tech_2"
        mapping[cols[20]] = "Francais_Pro_2"
        mapping[cols[21]] = "PFA_2"
        mapping[cols[22]] = "Moyenne_S2"
        mapping[cols[23]] = "Moyenne_Annuelle"
        mapping[cols[24]] = "Modules_Non_Valides"
        if len(cols) > 25:
            mapping[cols[25]] = "Redoublant"
    else:
        mapping = {cols[i]: POSITION_MAP.get(i, f"Col_{i}") for i in range(len(cols))}

    df_raw = df_raw.rename(columns=mapping)

    fname = os.path.basename(filepath)
    filiere_key = detect_filiere(fname)
    df_raw["Filiere"]      = fname.replace(".xlsx", "").replace(".xls", "")
    df_raw["Filiere_Code"] = FILIERE_MAP.get(filiere_key, 0)
    df_raw["Filiere_Key"]  = filiere_key

    if "Col_vide" in df_raw.columns:
        df_raw = df_raw.drop(columns=["Col_vide"])

    return df_raw


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les lignes vides et corrige les types."""
    df = df.dropna(subset=["CNE"]).copy()

    # ⚠️ Encoder Redoublant EN PREMIER (Oui/Non → 1/0) AVANT la conversion numérique
    # Si on laisse pd.to_numeric convertir "Oui", ça donne NaN puis médiane = 0 pour tout le monde
    if "Redoublant" in df.columns:
        r = df["Redoublant"].astype(str).str.strip().str.lower()
        df["Redoublant"] = r.map(
            {"oui": 1, "non": 0, "1": 1, "0": 0, "1.0": 1, "0.0": 0, "nan": 0, "true": 1, "false": 0}
        ).fillna(0).astype(int)

    # Conversion numérique de toutes les autres colonnes (Redoublant déjà traité)
    num_cols = [c for c in FEATURE_COLS + [TARGET_COL, "Moyenne_S2"]
                if c in df.columns and c != "Redoublant"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df



def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Imputation par médiane."""
    num_cols = [c for c in FEATURE_COLS + [TARGET_COL] if c in df.columns]
    for col in num_cols:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering enrichi pour la prédiction 3A."""
    # Features existantes
    if "Moyenne_S1" in df.columns and "Moyenne_S2" in df.columns:
        df["Progression"] = df["Moyenne_S2"] - df["Moyenne_S1"]
    if "Absences_S1" in df.columns and "Absences_S2" in df.columns:
        df["Total_Absences"] = df["Absences_S1"] + df["Absences_S2"]
    if "Module_S1_1" in df.columns and "Module_S2_1" in df.columns:
        df["Moy_Module1"] = (df["Module_S1_1"] + df["Module_S2_1"]) / 2

    # Nouvelles features pour prédiction 3A
    # Moyenne des modules techniques S1
    mod_s1_cols = [c for c in ["Module_S1_2", "Module_S1_3", "Module_S1_4", "Module_S1_5"] if c in df.columns]
    if mod_s1_cols:
        df["Moy_Technique_S1"] = df[mod_s1_cols].mean(axis=1)

    # Moyenne des modules techniques S2
    mod_s2_cols = [c for c in ["Module_S2_2", "Module_S2_3", "Module_S2_4", "Module_S2_5"] if c in df.columns]
    if mod_s2_cols:
        df["Moy_Technique_S2"] = df[mod_s2_cols].mean(axis=1)

    # Score global de prérequis 3A (proxy général)
    if "Moy_Technique_S1" in df.columns and "Moy_Technique_S2" in df.columns:
        df["Score_Prereq_Global"] = df["Moy_Technique_S1"] * 0.4 + df["Moy_Technique_S2"] * 0.6

    # Ratio modules validés
    if "Modules_Non_Valides" in df.columns:
        df["Ratio_NV"] = df["Modules_Non_Valides"] / 12.0  # 12 modules total

    # Stabilité académique (faible écart-type entre modules = stable)
    all_mod_cols = [c for c in [
        "Module_S1_1", "Module_S1_2", "Module_S1_3", "Module_S1_4", "Module_S1_5",
        "Module_S2_1", "Module_S2_2", "Module_S2_3", "Module_S2_4", "Module_S2_5"
    ] if c in df.columns]
    if all_mod_cols:
        df["Stabilite_Notes"] = df[all_mod_cols].std(axis=1)

    # Excellence PFA (proxy pour PFE)
    if "PFA_2" in df.columns:
        df["PFA_Excellence"] = (df["PFA_2"] >= 14).astype(int)

    return df


def create_target_binary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Conditions RÉELLES de réussite (multi-critères):
    ✅ Réussi = 1 si TOUTES ces conditions sont remplies:
        - Moyenne_Annuelle >= 12/20
        - Modules_Non_Valides <= 3
        - PFA_2 >= 12/20
    ❌ Échec = 0 si au moins une condition n'est pas remplie

    Zones de danger (flags supplémentaires):
        ⚠️ Absences_S1 > 10h  ou  Absences_S2 > 10h
        ⚠️ Redoublant = 1
    """
    cond_moy = pd.to_numeric(df.get("Moyenne_Annuelle", pd.Series(0)), errors="coerce").fillna(0) >= 12.0
    cond_mod = pd.to_numeric(df.get("Modules_Non_Valides", pd.Series(0)), errors="coerce").fillna(99) <= 3
    cond_pfa = pd.to_numeric(df.get("PFA_2", pd.Series(0)), errors="coerce").fillna(0) >= 12.0

    df["Reussite"] = (cond_moy & cond_mod & cond_pfa).astype(int)

    abs_s1 = pd.to_numeric(df.get("Absences_S1", pd.Series(0)), errors="coerce").fillna(0)
    abs_s2 = pd.to_numeric(df.get("Absences_S2", pd.Series(0)), errors="coerce").fillna(0)
    df["Danger_Absences"]   = ((abs_s1 > 10) | (abs_s2 > 10)).astype(int)
    df["Danger_Redoublant"] = df.get("Redoublant", pd.Series(0)).astype(int)
    df["Score_Danger"]      = df["Danger_Absences"] + df["Danger_Redoublant"]

    total_abs = abs_s1 + abs_s2
    df["Profil_Comportement"] = pd.cut(
        total_abs,
        bins=[-1, 5, 15, 30, 9999],
        labels=[0, 1, 2, 3]
    ).astype(int)

    counts = df["Reussite"].value_counts().to_dict()
    print(f"Distribution: Réussi(1)={counts.get(1,0)} | Échec(0)={counts.get(0,0)}")
    print(f"En zone danger (absences/redoublant): {df['Score_Danger'].gt(0).sum()} étudiants")
    return df


def create_target_modules_3A(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crée les cibles de validation pour les modules de 3ème année.
    Utilise la logique de module_relations.py pour calculer les scores
    de prérequis de chaque étudiant.

    Ajoute des colonnes: Prereq_Score_[module] et Valide_3A_[module]
    """
    try:
        from src.preprocessing.module_relations import (
            predict_all_modules_3A, FILIERE_CODE_TO_KEY
        )
    except ImportError:
        import sys
        sys.path.insert(0, BASE_DIR)
        from src.preprocessing.module_relations import (
            predict_all_modules_3A, FILIERE_CODE_TO_KEY
        )

    pred_rows = []
    for _, row in df.iterrows():
        filiere_code = int(row.get("Filiere_Code", 1))
        filiere_key  = FILIERE_CODE_TO_KEY.get(filiere_code, "ite")

        etudiant_dict = row.to_dict()
        res = predict_all_modules_3A(etudiant_dict, filiere_key)

        row_data = {
            "nb_modules_3A_valides":    res["nb_valides"],
            "nb_modules_3A_non_valides": res["nb_non_valides"],
            "note_s5_predite":          res["note_s5_predite"],
            "note_pfe_predite":         res["note_pfe_predite"],
            "taux_validation_3A":       res["taux_validation"],
            "statut_3A":                res["statut_global"],
        }
        # Score prérequis pour chaque module 3A
        for mod_key, mod_res in res["modules_3A"].items():
            row_data[f"Prereq_{mod_key}"]  = mod_res["score_prereq"]
            row_data[f"Valide_3A_{mod_key}"] = int(mod_res["valide"])

        pred_rows.append(row_data)

    df_pred = pd.DataFrame(pred_rows, index=df.index)
    df = pd.concat([df, df_pred], axis=1)

    print(f"Modules 3A calculés pour {len(df)} étudiants")
    valide_cols = [c for c in df.columns if c.startswith("Valide_3A_")]
    for col in valide_cols:
        n_val = df[col].sum()
        print(f"  {col}: {n_val}/{len(df)} validés")

    return df


def run_pipeline(filenames=None, test_size=0.2, random_state=42,
                 include_3A_features=True):
    """
    Pipeline universel: charge tous les fichiers Excel, nettoie, encode,
    feature engineering, split, normalise et sauvegarde.

    Args:
        filenames: liste de fichiers (None = tous les fichiers dans data/raw/)
        test_size: proportion du jeu de test
        random_state: graine aléatoire
        include_3A_features: si True, calcule les features de prédiction 3A

    Returns:
        X_train, X_test, y_train, y_test, feature_names
    """
    if filenames is None:
        filenames = [f for f in os.listdir(RAW_DATA_PATH)
                     if f.endswith((".xlsx", ".xls"))]

    if not filenames:
        raise FileNotFoundError(f"Aucun fichier Excel dans {RAW_DATA_PATH}")

    frames = []
    for fname in filenames:
        path = os.path.join(RAW_DATA_PATH, fname)
        print(f"Chargement: {fname}")
        df = load_filiere(path)
        frames.append(df)

    df = pd.concat(frames, ignore_index=True)
    print(f"Total brut: {len(df)} lignes de {len(filenames)} filières")

    df = clean_data(df)
    df = handle_missing(df)
    df = create_features(df)
    df = create_target_binary(df)

    if include_3A_features:
        print("Calcul des features de prédiction 3ème année...")
        try:
            df = create_target_modules_3A(df)
        except Exception as e:
            print(f"  [Attention] Calcul 3A échoué: {e}. Continuation sans features 3A.")

    print(f"Après nettoyage: {len(df)} étudiants valides")

    # Features utilisées
    extra = ["Progression", "Total_Absences", "Moy_Module1",
             "Moy_Technique_S1", "Moy_Technique_S2", "Score_Prereq_Global",
             "Ratio_NV", "Stabilite_Notes", "PFA_Excellence"]
    available_features = [c for c in FEATURE_COLS + extra if c in df.columns]

    # Sauvegarder le CSV propre
    df.to_csv(os.path.join(PROC_DATA_PATH, "students_clean.csv"),
              index=False, encoding="utf-8")

    X = df[available_features].values
    y = df["Reussite"].values

    min_class = int(np.bincount(y).min())
    stratify  = y if min_class >= 2 else None
    if stratify is None:
        print("Attention: stratify désactivé (classe minoritaire < 2 exemples)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    joblib.dump(scaler,             os.path.join(MODELS_PATH, "scaler.pkl"))
    joblib.dump(available_features, os.path.join(MODELS_PATH, "feature_names.pkl"))

    # Sauvegarder aussi le DataFrame complet (avec features 3A)
    joblib.dump(df, os.path.join(MODELS_PATH, "df_processed.pkl"))

    print(f"Sauvegarde: scaler.pkl, feature_names.pkl, students_clean.csv")
    return X_train, X_test, y_train, y_test, available_features


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, features = run_pipeline()
    print(f"\nX_train: {X_train.shape} | X_test: {X_test.shape}")
    print(f"Features ({len(features)}): {features}")
    print(f"Classes train: {dict(zip(*np.unique(y_train, return_counts=True)))}")
