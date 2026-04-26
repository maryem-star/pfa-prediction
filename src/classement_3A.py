"""
Classement des Étudiants — Prédiction 3ème Année par Filière
=============================================================
Boutons de filière → Classement complet de la filière sélectionnée
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Classement 3A — Par Filière",
    page_icon="🏆",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
html, body, [data-testid="stApp"] {
    background: linear-gradient(135deg, #0a3d1f 0%, #1a5c2a 30%, #2d7a1f 60%, #4a9e12 100%) !important;
    min-height: 100vh;
}
* { font-family: 'Poppins', sans-serif !important; }
[data-testid="stSidebar"] { display:none !important; }
div[data-testid="stHorizontalBlock"] > div { padding: 0 4px !important; }
.stButton > button {
    width: 100%; border-radius: 14px;
    font-family: 'Poppins' !important; font-weight: 700;
    font-size: 0.95rem; padding: 14px 8px;
    border: 2px solid rgba(212,175,55,0.3);
    background: rgba(15,23,42,0.7);
    color: #e2e8f0;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: rgba(212,175,55,0.15) !important;
    border-color: #d4af37 !important;
    color: #d4af37 !important;
    transform: translateY(-2px);
}
.stButton > button:focus, .stButton > button:active {
    background: rgba(212,175,55,0.25) !important;
    border-color: #d4af37 !important;
    color: #f0c040 !important;
    box-shadow: 0 0 0 3px rgba(212,175,55,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "students_clean.csv")

FILIERES = {
    "🖥️  ITE — Génie Info":       "ite",
    "📡  ISIC":                    "isic",
    "🔐  CCN — Cybersécurité":     "ccn",
    "⚡  GEE — Génie Électrique":  "gee",
    "🏗️  Génie Civil":             "civil",
    "⚙️  Génie Industriel":        "industriel",
}

STATUT_EMOJI = {"VERT": "✅", "JAUNE": "⚠️", "ROUGE": "❌"}
STATUT_COLOR = {"VERT": "#10b981", "JAUNE": "#f59e0b", "ROUGE": "#ef4444"}
MEDAL = ["🥇", "🥈", "🥉"]

# ─── CHARGEMENT ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

@st.cache_data
def compute_predictions_for_filiere(fil_key: str, _df: pd.DataFrame) -> pd.DataFrame:
    from src.ml_models.predict import predict_modules_3A
    results = []
    for _, row in _df.iterrows():
        etud = row.to_dict()
        filiere_code = etud.get("Filiere_Code", 6)
        try:
            res = predict_modules_3A(etud, filiere_code)
            results.append({
                "CNE":              str(etud.get("CNE", "")),
                "Nom":              etud.get("Nom", ""),
                "Prenom":           etud.get("Prenom", ""),
                "Moy_1A":           round(float(etud.get("Moyenne_Annuelle", 0) or 0), 2),
                "Moy_2A":           round(float(etud.get("Moyenne_Annuelle_2A", 0) or 0), 2),
                "Note_S5_Predite":  round(float(res.get("note_s5_predite", 0)), 2),
                "Nb_Valides":       int(res.get("nb_valides", 0)),
                "Nb_Total":         int(res.get("nb_total", 1)),
                "Statut":           res.get("statut_global", "JAUNE"),
                "Redoublant":       int(etud.get("Redoublant", 0)),
            })
        except Exception:
            results.append({
                "CNE": str(etud.get("CNE", "")), "Nom": etud.get("Nom",""), "Prenom": etud.get("Prenom",""),
                "Moy_1A": 0.0, "Moy_2A": 0.0, "Note_S5_Predite": 0.0,
                "Nb_Valides": 0, "Nb_Total": 1, "Statut": "ROUGE", "Redoublant": 0,
            })
    df_res = pd.DataFrame(results)
    df_res = df_res.sort_values("Note_S5_Predite", ascending=False).reset_index(drop=True)
    df_res["Rang"] = range(1, len(df_res) + 1)
    return df_res

# ─── DONNÉES ──────────────────────────────────────────────────────────────────
df_all = load_data()
if df_all is None or df_all.empty:
    st.error("Aucune donnée trouvée.")
    st.stop()

# ─── ÉTAT SESSION (filière sélectionnée) ─────────────────────────────────────
if "fil_selectionnee" not in st.session_state:
    st.session_state.fil_selectionnee = list(FILIERES.keys())[0]

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div style="text-align:center;font-size:2.2rem;font-weight:800;background:linear-gradient(135deg,#f0c040,#d4af37,#10b981);-webkit-background-clip:text;-webkit-text-fill-color:transparent;padding:20px 0 4px 0;">🏆 Classement Prédictif — 3ème Année</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center;color:#94a3b8;font-size:0.95rem;margin-bottom:24px;">Sélectionnez une filière pour afficher le classement complet par note prédite S5</div>', unsafe_allow_html=True)

# ─── BOUTONS FILIÈRES ─────────────────────────────────────────────────────────
cols = st.columns(len(FILIERES))
for col, (fil_label, fil_key) in zip(cols, FILIERES.items()):
    with col:
        if st.button(fil_label, key=f"btn_{fil_key}"):
            st.session_state.fil_selectionnee = fil_label

# Filière active
fil_label_active = st.session_state.fil_selectionnee
fil_key_active   = FILIERES[fil_label_active]

st.markdown("<hr style='border-color:rgba(255,255,255,0.08);margin:20px 0;'>", unsafe_allow_html=True)

# ─── FILTRE DES DONNÉES ───────────────────────────────────────────────────────
df_fil = df_all[df_all["Filiere_Key"].str.lower() == fil_key_active].copy()

if df_fil.empty:
    st.warning(f"Aucun étudiant trouvé pour la filière {fil_label_active}.")
    st.stop()

# ─── CALCUL PRÉDICTIONS ───────────────────────────────────────────────────────
with st.spinner(f"⏳ Calcul des prédictions pour {fil_label_active}..."):
    df_ranked = compute_predictions_for_filiere(fil_key_active, df_fil)

# ─── MÉTRIQUES DE LA FILIÈRE ─────────────────────────────────────────────────
nb_total  = len(df_ranked)
nb_vert   = (df_ranked["Statut"] == "VERT").sum()
nb_jaune  = (df_ranked["Statut"] == "JAUNE").sum()
nb_rouge  = (df_ranked["Statut"] == "ROUGE").sum()
moy_promo = round(df_ranked["Note_S5_Predite"].mean(), 2)

st.markdown(f'<div style="font-size:1.3rem;font-weight:800;color:#d4af37;margin:0 0 16px 0;border-left:4px solid #d4af37;padding-left:14px;">🎓 {fil_label_active}</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
for col, val, label, color in [
    (c1, nb_total,          "Total Étudiants",  "#818cf8"),
    (c2, nb_vert,           "✅ Validation",     "#10b981"),
    (c3, nb_jaune,          "⚠️ Risque Modéré",  "#f59e0b"),
    (c4, nb_rouge,          "❌ Danger",         "#ef4444"),
    (c5, f"{moy_promo}/20", "Moy. Promo S5",    "#d4af37"),
]:
    with col:
        st.markdown(
            f'<div style="background:rgba(8,20,35,0.80);border-radius:18px;padding:18px 12px;text-align:center;'
            f'border:1px solid rgba(255,255,255,0.08);margin-bottom:12px;">'
            f'<div style="font-size:0.68rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">{label}</div>'
            f'<div style="font-size:2rem;font-weight:800;color:{color};font-family:Poppins;line-height:1;">{val}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

# ─── BARRE DE RECHERCHE ───────────────────────────────────────────────────────
search = st.text_input("🔍 Rechercher un étudiant", placeholder="Nom, Prénom ou CNE...")
if search.strip():
    df_ranked = df_ranked[
        df_ranked["Nom"].str.contains(search, case=False, na=False) |
        df_ranked["Prenom"].str.contains(search, case=False, na=False) |
        df_ranked["CNE"].str.contains(search, case=False, na=False)
    ]

st.markdown("<br>", unsafe_allow_html=True)

# ─── CLASSEMENT ───────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:1rem;font-weight:700;color:#e2e8f0;margin-bottom:12px;border-left:4px solid #d4af37;padding-left:14px;">🏆 Classement Complet</div>', unsafe_allow_html=True)

for _, row in df_ranked.iterrows():
    rang       = int(row["Rang"])
    note_s5    = row["Note_S5_Predite"]
    statut     = row["Statut"]
    nb_val     = row["Nb_Valides"]
    nb_tot     = row["Nb_Total"]
    moy_1a     = row["Moy_1A"]
    moy_2a     = row["Moy_2A"]
    cne        = row["CNE"]
    nom_p      = f"{row['Nom']} {row['Prenom']}"

    emoji_rang = MEDAL[rang - 1] if rang <= 3 else f"#{rang}"
    color      = STATUT_COLOR.get(statut, "#94a3b8")
    emoji_stat = STATUT_EMOJI.get(statut, "?")
    pct        = int(min(note_s5 / 20 * 100, 100))
    nc         = "#10b981" if note_s5 >= 14 else "#34d399" if note_s5 >= 12 else "#f59e0b" if note_s5 >= 10 else "#ef4444"
    red        = '<b style="color:#ef4444;font-size:0.75rem;">[R]</b>' if row["Redoublant"] else ""
    stxt       = statut.replace("_", " ")

    html = (
        f'<div style="background:rgba(8,20,35,0.75);border-radius:14px;padding:12px 20px;margin-bottom:7px;border:1px solid rgba(255,255,255,0.05);border-left:5px solid {color};">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
        # Gauche : rang + nom
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="font-size:1.6rem;min-width:42px;text-align:center;">{emoji_rang}</div>'
        f'<div>'
        f'<div style="font-size:1rem;font-weight:700;color:#e2e8f0;">{nom_p} {red}</div>'
        f'<div style="font-size:0.72rem;color:#64748b;">CNE : {cne}</div>'
        f'</div>'
        f'</div>'
        # Droite : métriques
        f'<div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;">'
        # Note S5
        f'<div style="text-align:center;min-width:85px;">'
        f'<div style="font-size:0.62rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Note S5</div>'
        f'<div style="font-size:1.6rem;font-weight:800;color:{nc};line-height:1.1;">{note_s5:.1f}<span style="font-size:0.75rem;color:#475569;">/20</span></div>'
        f'<div style="width:75px;height:3px;background:rgba(255,255,255,0.08);border-radius:2px;overflow:hidden;margin:3px auto 0 auto;">'
        f'<div style="width:{pct}%;height:100%;background:{nc};border-radius:2px;"></div></div>'
        f'</div>'
        # Moy 1A
        f'<div style="text-align:center;">'
        f'<div style="font-size:0.62rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Moy 1A</div>'
        f'<div style="font-size:1rem;font-weight:600;color:#94a3b8;">{moy_1a:.1f}</div>'
        f'</div>'
        # Moy 2A
        f'<div style="text-align:center;">'
        f'<div style="font-size:0.62rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Moy 2A</div>'
        f'<div style="font-size:1rem;font-weight:600;color:#94a3b8;">{moy_2a:.1f}</div>'
        f'</div>'
        # Modules
        f'<div style="text-align:center;">'
        f'<div style="font-size:0.62rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Modules 3A</div>'
        f'<div style="font-size:1rem;font-weight:700;color:{color};">{nb_val}/{nb_tot}</div>'
        f'</div>'
        # Statut badge
        f'<div style="background:rgba(16,16,16,0.5);border:1px solid rgba(255,255,255,0.1);border-radius:10px;'
        f'padding:4px 12px;text-align:center;min-width:72px;">'
        f'<div style="font-size:0.9rem;">{emoji_stat}</div>'
        f'<div style="font-size:0.65rem;color:{color};font-weight:700;text-transform:uppercase;letter-spacing:1px;">{stxt}</div>'
        f'</div>'
        f'</div></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# ─── EXPORT ───────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
csv = df_ranked[["Rang","CNE","Nom","Prenom","Moy_1A","Moy_2A","Note_S5_Predite","Nb_Valides","Nb_Total","Statut"]].to_csv(index=False)
st.download_button(
    label="⬇️ Télécharger ce classement (CSV)",
    data=csv,
    file_name=f"classement_{fil_key_active}.csv",
    mime="text/csv",
)

st.markdown("<br>---<center><small style='color:#334155;'>🏆 Classement 3A par Filière · IA · PFA</small></center>", unsafe_allow_html=True)
