"""
Interface 13 — Analyse Predictive Avancee (What-if Analysis)
Streamlit app: simulation interactive, modification des parametres en temps reel
Lancer: streamlit run src/interface_13_whatif.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import joblib

# ─── Config page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interface 13 - What-if Analysis",
    page_icon="🔮",
    layout="wide",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    body { background-color: #0f1117; }
    .title-main {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #9b59b6, #3498db, #2ecc71);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle { color: #a0a8c0; margin-bottom: 1.5rem; }
    .result-box {
        padding: 24px; border-radius: 16px; text-align: center;
        margin: 16px 0; font-size: 1.1rem;
    }
    .vert  { background: linear-gradient(135deg,#155724,#1e6e34); border: 2px solid #2ecc71; }
    .jaune { background: linear-gradient(135deg,#856404,#a07800); border: 2px solid #f39c12; }
    .rouge { background: linear-gradient(135deg,#721c24,#9e2d39); border: 2px solid #e74c3c; }
    .couleur-label { font-size: 3rem; font-weight: 900; letter-spacing: 2px; }
    .proba-val { font-size: 2rem; font-weight: 700; margin-top: 8px; }
    .risk-item {
        background: #1e2130; border-left: 3px solid #e15759;
        padding: 8px 14px; border-radius: 6px; margin: 6px 0;
        color: #fff;
    }
    .rec-item {
        background: #1e2130; border-left: 3px solid #59a14f;
        padding: 8px 14px; border-radius: 6px; margin: 6px 0;
        color: #fff;
    }
    .section-title { font-size: 1.1rem; font-weight: 700; color: #a0c4ff; margin: 1rem 0 0.5rem 0; }
    .stSlider > div > div { color: white; }
</style>
""", unsafe_allow_html=True)

# ─── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_DIR, "models")

FILIERE_LABELS = {
    "ISIC - Ingenierie Systemes":     1,
    "CCN - Cybersecurite":            2,
    "GEE - Genie Electrique":         3,
    "Genie Civil":                    4,
    "Genie Industriel":               5,
    "ITE - Genie Informatique":       6,
}

MODELE_LABELS = ["LogisticRegression", "RandomForest", "SVM"]

# ─── Chargement ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_models():
    scaler        = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
    feature_names = joblib.load(os.path.join(MODELS_PATH, "feature_names.pkl"))
    models = {}
    for name in MODELE_LABELS:
        p = os.path.join(MODELS_PATH, f"{name}.pkl")
        if os.path.exists(p):
            models[name] = joblib.load(p)
    return scaler, feature_names, models


def predict_live(features_dict, model_name, scaler, feature_names, models):
    clf = models[model_name]
    X = np.array([[features_dict.get(f, 0.0) for f in feature_names]])
    X_sc = scaler.transform(X)
    label_num = clf.predict(X_sc)[0]
    proba     = float(clf.predict_proba(X_sc)[0][1])

    # Moyenne estimee
    note_predite = proba * 20.0

    # Couleur
    if note_predite >= 14 or proba >= 0.85:
        couleur = "VERT"
    elif note_predite >= 10 or proba >= 0.50:
        couleur = "JAUNE"
    else:
        couleur = "ROUGE"

    # Facteurs de risque
    risques = []
    abs_s1 = features_dict.get("Absences_S1", 0)
    abs_s2 = features_dict.get("Absences_S2", 0)
    total_abs = abs_s1 + abs_s2
    moy_s1 = features_dict.get("Moyenne_S1", 10)
    modules_nv = features_dict.get("Modules_Non_Valides", 0)
    progression = features_dict.get("Moyenne_S2", moy_s1) - moy_s1

    if total_abs > 30:
        risques.append(f"Absences elevees ({total_abs}h au total)")
    if moy_s1 < 10:
        risques.append(f"Moyenne S1 insuffisante ({moy_s1:.1f}/20)")
    if modules_nv > 1:
        risques.append(f"{int(modules_nv)} modules non valides")
    if progression < -1.5:
        risques.append(f"Regression entre S1 et S2 ({progression:+.1f})")
    if features_dict.get("Redoublant", 0) == 1:
        risques.append("Etudiant redoublant")
    if not risques:
        risques = ["Aucun risque majeur identifie"]

    # Recommandations
    recs = []
    if couleur == "ROUGE":
        recs = [
            "Intervention urgente: contacter un tuteur ou conseiller",
            "Renforcement intensif dans les modules non valides",
            "Plan de rattrapage personnalise",
            "Suivi hebdomadaire obligatoire",
        ]
    elif couleur == "JAUNE":
        recs = [
            "Encourager la participation aux seances de tutorat",
            "Surveiller les absences et intervenir si necessaire",
            "Renforcement cible dans les modules en difficulte",
        ]
    else:
        recs = [
            "Continuer sur cette lancee, excellent parcours",
            "Proposer des projets enrichissants ou avances",
        ]

    return {
        "label":       "Reussi" if label_num == 1 else "Echec",
        "probabilite": round(proba, 4),
        "note_predite": round(note_predite, 2),
        "couleur":     couleur,
        "risques":     risques,
        "recs":        recs,
    }


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">Interface 13 — What-if: Analyse Predictive Avancee</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Simulez et modifiez les parametres d un etudiant en temps reel pour voir evoluer la prediction</div>', unsafe_allow_html=True)

with st.spinner("Chargement des modeles..."):
    try:
        scaler, feature_names, models = load_models()
    except Exception as e:
        st.error(f"Modeles non disponibles: {e}")
        st.info("Lancez d'abord: python -m src.ml_models.train")
        st.stop()

# ─── Layout: Sidebar gauche + Resultats droite ────────────────────────────────
col_inputs, col_results = st.columns([2, 1])

with col_inputs:
    st.markdown("### Parametres de l'etudiant")

    # Modele + Filiere
    c1, c2 = st.columns(2)
    with c1:
        modele_choisi = st.selectbox("Modele ML", list(models.keys()), index=0)
    with c2:
        filiere_label = st.selectbox("Filiere", list(FILIERE_LABELS.keys()), index=0)
        filiere_code = FILIERE_LABELS[filiere_label]

    st.markdown('<div class="section-title">Semestre 1</div>', unsafe_allow_html=True)
    cs1a, cs1b = st.columns(2)
    with cs1a:
        abs_s1     = st.slider("Absences S1 (heures)", 0, 80, 5)
        module_s1_1 = st.slider("Mathematiques 1", 0.0, 20.0, 12.0, 0.5)
        module_s1_2 = st.slider("Module principal S1 (2)", 0.0, 20.0, 12.0, 0.5)
        module_s1_3 = st.slider("Module principal S1 (3)", 0.0, 20.0, 11.0, 0.5)
    with cs1b:
        module_s1_4 = st.slider("Module principal S1 (4)", 0.0, 20.0, 12.0, 0.5)
        module_s1_5 = st.slider("Module principal S1 (5)", 0.0, 20.0, 13.0, 0.5)
        anglais_1   = st.slider("Anglais Technique 1", 0.0, 20.0, 13.0, 0.5)
        francais_1  = st.slider("Francais Professionnel 1", 0.0, 20.0, 13.0, 0.5)

    moy_s1 = round(np.mean([module_s1_1, module_s1_2, module_s1_3, module_s1_4, module_s1_5, anglais_1, francais_1]), 2)
    st.info(f"Moyenne S1 estimee automatiquement: **{moy_s1:.2f}/20**")

    st.markdown('<div class="section-title">Semestre 2</div>', unsafe_allow_html=True)
    cs2a, cs2b = st.columns(2)
    with cs2a:
        abs_s2     = st.slider("Absences S2 (heures)", 0, 80, 5)
        module_s2_1 = st.slider("Mathematiques 2", 0.0, 20.0, 12.0, 0.5)
        module_s2_2 = st.slider("Module principal S2 (2)", 0.0, 20.0, 12.0, 0.5)
        module_s2_3 = st.slider("Module principal S2 (3)", 0.0, 20.0, 11.0, 0.5)
    with cs2b:
        module_s2_4 = st.slider("Module principal S2 (4)", 0.0, 20.0, 12.0, 0.5)
        module_s2_5 = st.slider("Module principal S2 (5)", 0.0, 20.0, 13.0, 0.5)
        anglais_2   = st.slider("Anglais Technique 2", 0.0, 20.0, 13.0, 0.5)
        francais_2  = st.slider("Francais Professionnel 2", 0.0, 20.0, 13.0, 0.5)

    moy_s2 = round(np.mean([module_s2_1, module_s2_2, module_s2_3, module_s2_4, module_s2_5, anglais_2, francais_2]), 2)

    st.markdown('<div class="section-title">PFA & Autres</div>', unsafe_allow_html=True)
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        pfa_2          = st.slider("Note PFA 2", 0.0, 20.0, 14.0, 0.5)
    with cp2:
        modules_nv     = st.slider("Modules Non Valides", 0, 8, 0)
    with cp3:
        redoublant     = 1 if st.checkbox("Redoublant", value=False) else 0

    moy_s2 = round(np.mean([module_s2_1, module_s2_2, module_s2_3, module_s2_4, module_s2_5, anglais_2, francais_2, pfa_2]), 2)
    st.info(f"Moyenne S2 estimee automatiquement: **{moy_s2:.2f}/20**")

# ─── Construction du vecteur features ────────────────────────────────────────
features_dict = {
    "Absences_S1":        float(abs_s1),
    "Module_S1_1":        module_s1_1,
    "Module_S1_2":        module_s1_2,
    "Module_S1_3":        module_s1_3,
    "Module_S1_4":        module_s1_4,
    "Module_S1_5":        module_s1_5,
    "Anglais_Tech_1":     anglais_1,
    "Francais_Pro_1":     francais_1,
    "Moyenne_S1":         moy_s1,
    "Absences_S2":        float(abs_s2),
    "Module_S2_1":        module_s2_1,
    "Module_S2_2":        module_s2_2,
    "Module_S2_3":        module_s2_3,
    "Module_S2_4":        module_s2_4,
    "Module_S2_5":        module_s2_5,
    "Anglais_Tech_2":     anglais_2,
    "Francais_Pro_2":     francais_2,
    "PFA_2":              pfa_2,
    "Modules_Non_Valides": float(modules_nv),
    "Redoublant":         float(redoublant),
    "Filiere_Code":       float(filiere_code),
    "Progression":        moy_s2 - moy_s1,
    "Total_Absences":     float(abs_s1 + abs_s2),
    "Moy_Module1":        (module_s1_1 + module_s2_1) / 2,
}

# ─── Prediction en temps reel ─────────────────────────────────────────────────
result = predict_live(features_dict, modele_choisi, scaler, feature_names, models)

with col_results:
    st.markdown("### Prediction en Temps Reel")

    # Couleur badge
    couleur_css = result["couleur"].lower()
    emoji = {"VERT": "🟢", "JAUNE": "🟡", "ROUGE": "🔴"}[result["couleur"]]
    st.markdown(f"""
    <div class="result-box {couleur_css}">
        <div class="couleur-label">{emoji} {result['couleur']}</div>
        <div class="proba-val">Probabilite de reussite<br><b>{result['probabilite']*100:.1f}%</b></div>
        <div style="margin-top:10px; font-size:1.1rem;">
            Note predite: <b>{result['note_predite']:.1f}/20</b><br/>
            Decision: <b>{result['label']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Jauge probabilite
    fig_gauge, ax = plt.subplots(figsize=(5, 1.5), facecolor="#1e2130")
    ax.set_facecolor("#1e2130")
    proba = result["probabilite"]
    ax.barh([0], [1], color="#333", height=0.5, left=0)
    color_bar = "#2ecc71" if couleur_css == "vert" else "#f39c12" if couleur_css == "jaune" else "#e74c3c"
    ax.barh([0], [proba], color=color_bar, height=0.5, left=0)
    ax.axvline(x=0.5, color="white", linestyle="--", linewidth=1.5, alpha=0.5)
    ax.set_xlim(0, 1); ax.set_yticks([]); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], color="white", fontsize=9)
    ax.set_title("Probabilite de reussite", color="white", fontsize=10, fontweight="bold")
    ax.spines[:].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig_gauge)
    plt.close(fig_gauge)

    # Stats rapides
    st.markdown('<div class="section-title">Resume des entrees</div>', unsafe_allow_html=True)
    st.markdown(f"""
    - Absences totales: **{abs_s1 + abs_s2}h**
    - Moyenne S1: **{moy_s1:.2f}/20**
    - Moyenne S2: **{moy_s2:.2f}/20**
    - Progression: **{moy_s2 - moy_s1:+.2f}**
    - PFA: **{pfa_2:.1f}/20**
    """)

    # Facteurs de risque
    st.markdown('<div class="section-title">Facteurs de risque detectes</div>', unsafe_allow_html=True)
    for r in result["risques"]:
        st.markdown(f'<div class="risk-item">⚠️ {r}</div>', unsafe_allow_html=True)

    # Recommandations
    st.markdown('<div class="section-title">Recommandations</div>', unsafe_allow_html=True)
    for rec in result["recs"]:
        st.markdown(f'<div class="rec-item">✅ {rec}</div>', unsafe_allow_html=True)

# ─── Section: Analyse de sensibilite multi-modeles ────────────────────────────
st.markdown("---")
st.subheader("Comparaison des predictions — Tous les modeles")

cols_models = st.columns(len(models))
for col, (name, _) in zip(cols_models, models.items()):
    res_m = predict_live(features_dict, name, scaler, feature_names, models)
    emoji_c = {"VERT": "🟢", "JAUNE": "🟡", "ROUGE": "🔴"}[res_m["couleur"]]
    with col:
        st.metric(
            label=name,
            value=f"{res_m['probabilite']*100:.1f}%",
            delta=res_m["couleur"]
        )
        st.markdown(f"**{emoji_c} {res_m['couleur']}** — Note: {res_m['note_predite']:.1f}/20")

# ─── Section: What-if Table (variation absences) ──────────────────────────────
st.markdown("---")
st.subheader("Simulation What-if: Impact des Absences")

with st.expander("Voir comment les absences impactent la prediction"):
    absence_vals = list(range(0, 85, 10))
    sim_data = []
    for a in absence_vals:
        fd = features_dict.copy()
        fd["Absences_S1"] = float(a // 2)
        fd["Absences_S2"] = float(a // 2)
        fd["Total_Absences"] = float(a)
        r = predict_live(fd, modele_choisi, scaler, feature_names, models)
        sim_data.append({
            "Absences totales": a,
            "Probabilite (%)": round(r["probabilite"] * 100, 1),
            "Note predite": r["note_predite"],
            "Statut": r["couleur"],
        })

    df_sim = pd.DataFrame(sim_data)

    fig2, ax2 = plt.subplots(figsize=(10, 4), facecolor="#1e2130")
    ax2.set_facecolor("#1e2130")
    ax2.plot(df_sim["Absences totales"], df_sim["Probabilite (%)"], "o-", color="#4e79a7", linewidth=2.5, markersize=8)
    ax2.axhline(y=85, color="#2ecc71", linestyle="--", linewidth=1.5, alpha=0.7, label="Seuil VERT (85%)")
    ax2.axhline(y=50, color="#f39c12", linestyle="--", linewidth=1.5, alpha=0.7, label="Seuil JAUNE (50%)")
    ax2.set_xlabel("Absences totales (heures)", fontsize=11, color="white")
    ax2.set_ylabel("Probabilite de reussite (%)", fontsize=11, color="white")
    ax2.set_title("Impact des Absences sur la Probabilite de Reussite", fontsize=12, fontweight="bold", color="white")
    ax2.legend(facecolor="#1e2130", labelcolor="white", fontsize=10)
    ax2.tick_params(colors="white")
    ax2.spines[:].set_color("#333")
    ax2.set_ylim(0, 110)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.dataframe(df_sim, use_container_width=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>PFA — Systeme Intelligent de Prediction de la Reussite Academique | "
    "Interface 13 — What-if Analysis | ML Engineer</small></center>",
    unsafe_allow_html=True
)
