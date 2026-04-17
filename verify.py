"""Script de verification complete du projet ML"""
import sys, ast, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.dirname(os.path.abspath(__file__))

files_to_check = [
    "src/preprocessing/__init__.py",
    "src/preprocessing/data_pipeline.py",
    "src/ml_models/__init__.py",
    "src/ml_models/train.py",
    "src/ml_models/evaluate.py",
    "src/ml_models/predict.py",
    "src/api/routes/predictions.py",
    "src/interface_6_model_comparison.py",
    "src/interface_13_whatif.py",
    "tests/test_ml.py",
]

print("=" * 60)
print("  VERIFICATION SYNTAXE")
print("=" * 60)
syntax_errors = []
for rel in files_to_check:
    fpath = os.path.join(BASE, rel)
    fname = os.path.basename(fpath)
    try:
        with open(fpath, "r", encoding="utf-8") as fh:
            ast.parse(fh.read())
        print(f"  OK        {fname}")
    except SyntaxError as e:
        msg = f"ERREUR SYNTAXE: {fname} -> ligne {e.lineno}: {e.msg}"
        print(f"  {msg}")
        syntax_errors.append(msg)
    except FileNotFoundError:
        msg = f"MANQUANT: {fname}"
        print(f"  {msg}")
        syntax_errors.append(msg)

print()
print("=" * 60)
print("  VERIFICATION IMPORTS")
print("=" * 60)
import_errors = []

def try_import(module, label):
    try:
        __import__(module)
        print(f"  OK        {label}")
    except ImportError as e:
        msg = f"IMPORT MANQUANT: {label} -> pip install {module.split('.')[0]}"
        print(f"  {msg}")
        import_errors.append(msg)

try_import("pandas",     "pandas")
try_import("numpy",      "numpy")
try_import("sklearn",    "scikit-learn")
try_import("joblib",     "joblib")
try_import("openpyxl",   "openpyxl")
try_import("matplotlib", "matplotlib")
try_import("seaborn",    "seaborn")
try_import("streamlit",  "streamlit")
try_import("fastapi",    "fastapi")
try_import("sqlalchemy", "sqlalchemy")
try_import("pydantic",   "pydantic")

print()
print("=" * 60)
print("  VERIFICATION FICHIERS MODELES")
print("=" * 60)
models_dir = os.path.join(BASE, "models")
model_files = ["scaler.pkl", "feature_names.pkl",
               "LogisticRegression.pkl", "RandomForest.pkl", "SVM.pkl"]
model_errors = []
for mf in model_files:
    mp = os.path.join(models_dir, mf)
    if os.path.exists(mp):
        size_kb = os.path.getsize(mp) / 1024
        print(f"  OK        {mf} ({size_kb:.1f} KB)")
    else:
        msg = f"MANQUANT: {mf}"
        print(f"  {msg}")
        model_errors.append(msg)

print()
print("=" * 60)
print("  VERIFICATION DONNÉES")
print("=" * 60)
raw_dir = os.path.join(BASE, "data", "raw")
expected_files = ["isic.xlsx", "ccn_cybersec.xlsx",
                  "gee_genie_electrique.xlsx", "genie_civil.xlsx",
                  "genie_industriel.xlsx", "ite_genie_info.xlsx"]
data_errors = []
for df_name in expected_files:
    dp = os.path.join(raw_dir, df_name)
    if os.path.exists(dp):
        size_kb = os.path.getsize(dp) / 1024
        print(f"  OK        {df_name} ({size_kb:.0f} KB)")
    else:
        msg = f"MANQUANT: {df_name}"
        print(f"  {msg}")
        data_errors.append(msg)

print()
print("=" * 60)
print("  RESUME FINAL")
print("=" * 60)
total_errors = len(syntax_errors) + len(import_errors) + len(model_errors) + len(data_errors)
if total_errors == 0:
    print("  TOUT EST OK! Aucune erreur detectee.")
else:
    print(f"  {total_errors} erreur(s) a corriger:")
    for e in syntax_errors + import_errors + model_errors + data_errors:
        print(f"    - {e}")

sys.exit(0 if total_errors == 0 else 1)
