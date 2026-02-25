"""
Pipeline de pretraitement universel — Toutes filieres
Structure identique pour: ISIC, CCN, GEE, Genie Civil, Genie Industriel, ITE
26 colonnes, header a la ligne 4, mapping par position.
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

# ─── Mapping par POSITION (identique pour toutes les filieres) ────────────────
# Position → nom Python
POSITION_MAP = {
    0:  "CNE",
    1:  "Nom",
    2:  "Prenom",
    3:  "Absences_S1",
    4:  "Module_S1_1",     # Maths 1 ou equivalent
    5:  "Module_S1_2",
    6:  "Module_S1_3",
    7:  "Module_S1_4",
    8:  "Module_S1_5",
    9:  "Anglais_Tech_1",
    10: "Francais_Pro_1",
    11: "Moyenne_S1",      # position 11 ou 12 selon filiere
    12: "Absences_S2",
    13: "Module_S2_1",     # Maths 2 ou equivalent
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
    "Filiere_Code",  # encodage numerique de la filiere
]

TARGET_COL = "Moyenne_Annuelle"

# Code numerique par filiere
FILIERE_MAP = {
    "isic": 1, "ccn": 2, "gee": 3,
    "civil": 4, "industriel": 5, "ite": 6,
}


def detect_filiere(filename: str) -> str:
    """Detecte la filiere depuis le nom du fichier."""
    fname = filename.lower()
    for key in FILIERE_MAP:
        if key in fname:
            return key
    return "inconnu"


def load_filiere(filepath: str) -> pd.DataFrame:
    """
    Charge un fichier Excel de n'importe quelle filiere.
    Utilise le mapping par position pour garantir la coherence.
    Gere les fichiers avec ou sans colonne vide en position 11.
    """
    df_raw = pd.read_excel(filepath, header=3)
    cols = list(df_raw.columns)

    # Detecter si la colonne 11 est vide (comme dans ISIC/CCN/GEE/ITE/GI)
    # vs. pas de colonne vide (comme dans Genie Civil)
    col11_empty = str(cols[11]).startswith("Unnamed") or str(cols[11]).strip() == ""

    if col11_empty:
        # Decaler: col 11 = vide (a ignorer), Moyenne_S1 = col 12
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
        # Pas de colonne vide: mapping direct
        mapping = {cols[i]: POSITION_MAP.get(i, f"Col_{i}") for i in range(len(cols))}

    df_raw = df_raw.rename(columns=mapping)

    # Ajouter la filiere
    fname = os.path.basename(filepath)
    df_raw["Filiere"] = fname.replace(".xlsx", "").replace(".xls", "")
    df_raw["Filiere_Code"] = FILIERE_MAP.get(detect_filiere(fname), 0)

    # Supprimer colonne vide si elle existe
    if "Col_vide" in df_raw.columns:
        df_raw = df_raw.drop(columns=["Col_vide"])

    return df_raw


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les lignes vides et corrige les types."""
    df = df.dropna(subset=["CNE"]).copy()

    # Colonnes numeriques
    num_cols = [c for c in FEATURE_COLS + [TARGET_COL, "Moyenne_S2"]
                if c in df.columns]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Redoublant: Oui/Non -> 1/0
    if "Redoublant" in df.columns:
        r = df["Redoublant"].astype(str).str.strip().str.lower()
        df["Redoublant"] = r.map(
            {"oui": 1, "non": 0, "1": 1, "0": 0, "1.0": 1, "0.0": 0, "nan": 0}
        ).fillna(0).astype(int)

    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Imputation par mediane."""
    num_cols = [c for c in FEATURE_COLS + [TARGET_COL] if c in df.columns]
    for col in num_cols:
        if col in df.columns and df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median())
    return df


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering."""
    if "Moyenne_S1" in df.columns and "Moyenne_S2" in df.columns:
        df["Progression"]    = df["Moyenne_S2"] - df["Moyenne_S1"]
    if "Absences_S1" in df.columns and "Absences_S2" in df.columns:
        df["Total_Absences"] = df["Absences_S1"] + df["Absences_S2"]
    if "Module_S1_1" in df.columns and "Module_S2_1" in df.columns:
        df["Moy_Module1"] = (df["Module_S1_1"] + df["Module_S2_1"]) / 2
    return df


def create_target_binary(df: pd.DataFrame, seuil: float = 10.0) -> pd.DataFrame:
    """
    Cible binaire adaptative:
    - Si tous ont reussi (>= seuil), utilise la mediane comme seuil alternatif.
    - Sinon: 1 = Reussi, 0 = Echec
    """
    if TARGET_COL not in df.columns:
        return df

    notes = pd.to_numeric(df[TARGET_COL], errors="coerce").dropna()
    tous_reussis = (notes >= seuil).all()

    if tous_reussis:
        seuil_adapte = float(notes.median())
        print(f"Seuil adaptatif: mediane = {seuil_adapte:.2f} (tous ont reussi >= {seuil})")
    else:
        seuil_adapte = seuil

    df["Reussite"] = (df[TARGET_COL] >= seuil_adapte).astype(int)
    counts = df["Reussite"].value_counts().to_dict()
    print(f"Distribution: Reussi(1)={counts.get(1,0)} | Echec(0)={counts.get(0,0)}")
    return df


def run_pipeline(filenames=None, test_size=0.2, random_state=42):
    """
    Pipeline universel: charge tous les fichiers Excel de data/raw/,
    nettoie, encode, feature engineering, split, normalise et sauvegarde.

    Returns: X_train, X_test, y_train, y_test, feature_names
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
    print(f"Total brut: {len(df)} lignes de {len(filenames)} filieres")

    df = clean_data(df)
    df = handle_missing(df)
    df = create_features(df)
    df = create_target_binary(df)

    print(f"Apres nettoyage: {len(df)} etudiants valides")

    # Features utilisees
    extra = ["Progression", "Total_Absences", "Moy_Module1"]
    available_features = [c for c in FEATURE_COLS + extra if c in df.columns]

    # Sauvegarder le CSV propre
    df.to_csv(os.path.join(PROC_DATA_PATH, "students_clean.csv"),
              index=False, encoding="utf-8")

    X = df[available_features].values
    y = df["Reussite"].values

    # Stratify si au moins 2 exemples de chaque classe
    min_class = int(np.bincount(y).min())
    stratify  = y if min_class >= 2 else None
    if stratify is None:
        print("Attention: stratify desactive (classe minoritaire < 2 exemples)")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    joblib.dump(scaler,            os.path.join(MODELS_PATH, "scaler.pkl"))
    joblib.dump(available_features, os.path.join(MODELS_PATH, "feature_names.pkl"))

    print(f"Sauvegarde: scaler.pkl, feature_names.pkl, students_clean.csv")
    return X_train, X_test, y_train, y_test, available_features


if __name__ == "__main__":
    X_train, X_test, y_train, y_test, features = run_pipeline()
    print(f"\nX_train: {X_train.shape} | X_test: {X_test.shape}")
    print(f"Features ({len(features)}): {features}")
    print(f"Classes train: {dict(zip(*np.unique(y_train, return_counts=True)))}")
