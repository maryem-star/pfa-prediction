"""
Interface 13 — What-if: Analyse Predictive Avancee
===================================================
Conditions reelles de reussite:
    ✅ Moyenne Annuelle >= 12/20
    ✅ Modules Non Valides <= 3
    ✅ PFA >= 12/20

Zones de danger:
    ⚠️ Absences S1 > 10h  |  Absences S2 > 10h
    ⚠️ Redoublant = 1

Lancer: streamlit run src/interface_13_whatif.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib; matplotlib.use("Agg")
import joblib

st.set_page_config(
    page_title="Interface 13 — What-if Analysis",
    page_icon="🔮",
    layout="wide",
)

st.markdown("""
<style>
    .title-main {
        font-size: 2.1rem; font-weight: 800;
        background: linear-gradient(90deg, #9b59b6, #3498db, #2ecc71);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle { color: #a0a8c0; margin-bottom: 1.5rem; }
    .cond-ok   { background:#155724; border:1.5px solid #2ecc71; border-radius:8px; padding:8px 14px; color:#fff; margin:4px 0; }
    .cond-fail { background:#721c24; border:1.5px solid #e74c3c; border-radius:8px; padding:8px 14px; color:#fff; margin:4px 0; }
    .danger-box{ background:#856404; border:1.5px solid #f39c12; border-radius:8px; padding:8px 14px; color:#fff; margin:4px 0; }
    .safe-box  { background:#155724; border:1.5px solid #2ecc71; border-radius:8px; padding:8px 14px; color:#fff; margin:4px 0; }
    .vert   { background:linear-gradient(135deg,#155724,#1a7a30); border:2px solid #2ecc71; border-radius:14px; padding:22px; text-align:center; }
    .jaune  { background:linear-gradient(135deg,#856404,#a07800); border:2px solid #f39c12; border-radius:14px; padding:22px; text-align:center; }
    .rouge  { background:linear-gradient(135deg,#721c24,#9e2d39); border:2px solid #e74c3c; border-radius:14px; padding:22px; text-align:center; }
    .badge  { font-size:2.8rem; font-weight:900; letter-spacing:2px; }
    .proba  { font-size:1.8rem; font-weight:700; margin-top:8px; }
    .remarque { background:#1e2130; border-left:3px solid #a0c4ff; padding:8px 14px; border-radius:6px; margin:5px 0; color:#dde; font-size:0.95rem; }
    .risk-item{ background:#1e2130; border-left:3px solid #e15759; padding:8px 14px; border-radius:6px; margin:5px 0; color:#fff; }
    .rec-item { background:#1e2130; border-left:3px solid #59a14f; padding:8px 14px; border-radius:6px; margin:5px 0; color:#fff; }
    .profil-label { font-size:1.2rem; font-weight:700; }
    .section-hdr { font-size:1rem; font-weight:700; color:#a0c4ff; margin:1rem 0 0.4rem 0; }
</style>
""", unsafe_allow_html=True)

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_DIR, "models")

FILIERES = {
    "ISIC — Systemes d Information": 1,
    "CCN — Cybersecurite":           2,
    "GEE — Genie Electrique":        3,
    "Genie Civil":                   4,
    "Genie Industriel":              5,
    "ITE — Genie Informatique":      6,
}

PROFIL_EMOJI = {0: "🟢", 1: "🔵", 2: "🟡", 3: "🔴"}
PROFIL_LABELS = {
    0: "Tres assidu",
    1: "Assidu",
    2: "Comportement preoccupant",
    3: "Absenteiste chronique",
}

@st.cache_resource
def load_models():
    scaler        = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
    feature_names = joblib.load(os.path.join(MODELS_PATH, "feature_names.pkl"))
    models = {}
    for nm in ["LogisticRegression", "RandomForest", "SVM"]:
        p = os.path.join(MODELS_PATH, f"{nm}.pkl")
        if os.path.exists(p):
            models[nm] = joblib.load(p)
    return scaler, feature_names, models


def live_predict(fd: dict, model_name: str, scaler, feature_names, models):
    clf  = models[model_name]
    X    = np.array([[fd.get(f, 0.0) for f in feature_names]])
    X_sc = scaler.transform(X)
    label_num = clf.predict(X_sc)[0]
    proba     = float(clf.predict_proba(X_sc)[0][1])

    # Estimer note
    moy_s1 = fd.get("Moyenne_S1", 10)
    moy_s2 = fd.get("Moyenne_S2", moy_s1)
    note   = proba * 20 * 0.7 + (moy_s1 + moy_s2) / 2 * 0.3

    # Couleur selon vraies conditions
    if note >= 12 and proba >= 0.70:
        couleur = "VERT"
    elif note < 12 or proba < 0.40:
        couleur = "ROUGE"
    else:
        couleur = "JAUNE"

    return label_num, proba, note, couleur


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">Interface 13 — What-if: Simulation Predictive</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Modifiez les parametres en temps reel — Conditions reelles: Moy >= 12 | Modules NV <= 3 | PFA >= 12</div>', unsafe_allow_html=True)

try:
    scaler, feature_names, models = load_models()
except Exception as e:
    st.error(f"Modeles non disponibles: {e}")
    st.info("Lancez: python -m src.ml_models.train")
    st.stop()

col_inp, col_res = st.columns([2, 1], gap="large")

# ══════════════════════ COLONNE GAUCHE: INPUTS ════════════════════════════════
with col_inp:
    st.markdown("### Profil de l'etudiant")

    r1, r2 = st.columns(2)
    with r1: modele = st.selectbox("Modele ML", list(models.keys()), index=1)
    with r2:
        fil_label = st.selectbox("Filiere", list(FILIERES.keys()))
        filiere_code = FILIERES[fil_label]

    # ── SEMESTRE 1 ──────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Semestre 1</div>', unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        abs_s1      = st.slider("Absences S1 (heures)", 0, 80, 5)
        mod_s1_1    = st.slider("Maths / Module principal 1", 0.0, 20.0, 13.0, 0.5)
        mod_s1_2    = st.slider("Module S1 (2)", 0.0, 20.0, 12.0, 0.5)
        mod_s1_3    = st.slider("Module S1 (3)", 0.0, 20.0, 12.0, 0.5)
    with a2:
        mod_s1_4    = st.slider("Module S1 (4)", 0.0, 20.0, 12.0, 0.5)
        mod_s1_5    = st.slider("Module S1 (5)", 0.0, 20.0, 12.0, 0.5)
        anglais_1   = st.slider("Anglais Tech. 1", 0.0, 20.0, 13.0, 0.5)
        francais_1  = st.slider("Francais Pro. 1", 0.0, 20.0, 13.0, 0.5)

    moy_s1 = round(np.mean([mod_s1_1,mod_s1_2,mod_s1_3,mod_s1_4,mod_s1_5,anglais_1,francais_1]),2)
    color_moy_s1 = "#2ecc71" if moy_s1 >= 12 else "#f39c12" if moy_s1 >= 10 else "#e74c3c"
    st.markdown(f"Moyenne S1 calculee: <b style='color:{color_moy_s1}'>{moy_s1:.2f}/20</b>", unsafe_allow_html=True)

    # ── SEMESTRE 2 ──────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Semestre 2</div>', unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        abs_s2      = st.slider("Absences S2 (heures)", 0, 80, 5)
        mod_s2_1    = st.slider("Maths / Module principal 2", 0.0, 20.0, 13.0, 0.5)
        mod_s2_2    = st.slider("Module S2 (2)", 0.0, 20.0, 12.0, 0.5)
        mod_s2_3    = st.slider("Module S2 (3)", 0.0, 20.0, 12.0, 0.5)
    with b2:
        mod_s2_4    = st.slider("Module S2 (4)", 0.0, 20.0, 12.0, 0.5)
        mod_s2_5    = st.slider("Module S2 (5)", 0.0, 20.0, 12.0, 0.5)
        anglais_2   = st.slider("Anglais Tech. 2", 0.0, 20.0, 13.0, 0.5)
        francais_2  = st.slider("Francais Pro. 2", 0.0, 20.0, 13.0, 0.5)

    # ── PFA + Autres ────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">PFA et Informations complementaires</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        pfa_2      = st.slider("Note PFA 2", 0.0, 20.0, 14.0, 0.5)
    with c2:
        modules_nv = st.slider("Modules Non Valides", 0, 10, 0)
    with c3:
        redoublant = 1 if st.checkbox("Redoublant", value=False) else 0

    moy_s2 = round(np.mean([mod_s2_1,mod_s2_2,mod_s2_3,mod_s2_4,mod_s2_5,anglais_2,francais_2,pfa_2]),2)
    moy_ann = round((moy_s1 + moy_s2) / 2, 2)
    color_moy_s2 = "#2ecc71" if moy_s2 >= 12 else "#f39c12" if moy_s2 >= 10 else "#e74c3c"
    color_moy_ann = "#2ecc71" if moy_ann >= 12 else "#f39c12" if moy_ann >= 10 else "#e74c3c"
    st.markdown(
        f"Moyenne S2: <b style='color:{color_moy_s2}'>{moy_s2:.2f}/20</b> &nbsp;|&nbsp; "
        f"Moyenne Annuelle estimee: <b style='color:{color_moy_ann}'>{moy_ann:.2f}/20</b>",
        unsafe_allow_html=True
    )

# ── Construction du vecteur features ─────────────────────────────────────────
total_abs   = abs_s1 + abs_s2
progression = moy_s2 - moy_s1
danger_abs  = 1 if (abs_s1 > 10 or abs_s2 > 10) else 0
danger_red  = redoublant
score_danger= danger_abs + danger_red

if total_abs <= 5:    profil_comp = 0
elif total_abs <= 15: profil_comp = 1
elif total_abs <= 30: profil_comp = 2
else:                  profil_comp = 3

fd = {
    "Absences_S1":        float(abs_s1),
    "Module_S1_1":        mod_s1_1, "Module_S1_2": mod_s1_2,
    "Module_S1_3":        mod_s1_3, "Module_S1_4": mod_s1_4,
    "Module_S1_5":        mod_s1_5,
    "Anglais_Tech_1":     anglais_1, "Francais_Pro_1": francais_1,
    "Moyenne_S1":         moy_s1,
    "Absences_S2":        float(abs_s2),
    "Module_S2_1":        mod_s2_1, "Module_S2_2": mod_s2_2,
    "Module_S2_3":        mod_s2_3, "Module_S2_4": mod_s2_4,
    "Module_S2_5":        mod_s2_5,
    "Anglais_Tech_2":     anglais_2, "Francais_Pro_2": francais_2,
    "PFA_2":              pfa_2,
    "Modules_Non_Valides": float(modules_nv),
    "Redoublant":         float(redoublant),
    "Filiere_Code":       float(filiere_code),
    "Danger_Absences":    float(danger_abs),
    "Danger_Redoublant":  float(danger_red),
    "Score_Danger":       float(score_danger),
    "Profil_Comportement": float(profil_comp),
    "Progression":        progression,
    "Total_Absences":     float(total_abs),
    "Moy_Module1":        (mod_s1_1 + mod_s2_1) / 2,
    "Moyenne_S2":         moy_s2,
    "Moyenne_Annuelle":   moy_ann,
}

label_num, proba, note, couleur = live_predict(fd, modele, scaler, feature_names, models)

# ══════════════════════ COLONNE DROITE: RESULTATS ════════════════════════════
with col_res:
    st.markdown("### Prediction en Temps Reel")

    emoji_c = {"VERT":"🟢","JAUNE":"🟡","ROUGE":"🔴"}[couleur]
    css_c   = couleur.lower()
    st.markdown(f"""
    <div class="{css_c}">
        <div class="badge">{emoji_c} {couleur}</div>
        <div class="proba">Prob. reussite: <b>{proba*100:.1f}%</b></div>
        <div style="margin-top:8px;font-size:1.1rem;">
            Note estimee: <b>{note:.1f}/20</b><br>
            Decision: <b>{"Reussi" if label_num==1 else "Echec"}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3 Conditions de reussite ─────────────────────────────────────────
    st.markdown('<div class="section-hdr">Verification des 3 conditions</div>', unsafe_allow_html=True)

    cond_moy = moy_ann >= 12
    cond_mod = modules_nv <= 3
    cond_pfa = pfa_2 >= 12

    def cond_row(label, ok, detail=""):
        icon = "✅" if ok else "❌"
        css  = "cond-ok" if ok else "cond-fail"
        return f'<div class="{css}">{icon} {label}{f" ({detail})" if detail else ""}</div>'

    st.markdown(cond_row("Moyenne Annuelle >= 12", cond_moy, f"{moy_ann:.2f}/20"), unsafe_allow_html=True)
    st.markdown(cond_row("Modules Non Valides <= 3", cond_mod, f"{modules_nv} module(s)"), unsafe_allow_html=True)
    st.markdown(cond_row("PFA >= 12/20", cond_pfa, f"{pfa_2:.1f}/20"), unsafe_allow_html=True)

    nb_cond_ok = sum([cond_moy, cond_mod, cond_pfa])
    st.markdown(f"**{nb_cond_ok}/3 conditions satisfaites**")

    # ── Zones de danger ──────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Zones de danger</div>', unsafe_allow_html=True)

    def danger_row(label, is_danger):
        css  = "danger-box" if is_danger else "safe-box"
        icon = "⚠️" if is_danger else "✅"
        return f'<div class="{css}">{icon} {label}</div>'

    st.markdown(danger_row(f"Absences S1: {abs_s1}h (seuil: 10h)", abs_s1 > 10), unsafe_allow_html=True)
    st.markdown(danger_row(f"Absences S2: {abs_s2}h (seuil: 10h)", abs_s2 > 10), unsafe_allow_html=True)
    st.markdown(danger_row(f"Redoublant: {'Oui' if redoublant else 'Non'}", redoublant == 1), unsafe_allow_html=True)

    # ── Profil comportemental ─────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Profil comportemental</div>', unsafe_allow_html=True)
    pe = PROFIL_EMOJI[profil_comp]
    pl = PROFIL_LABELS[profil_comp]
    st.markdown(f'<div class="profil-label">{pe} {pl}</div>', unsafe_allow_html=True)
    st.markdown(f"Total absences: **{total_abs}h** | Progression S1➜S2: **{progression:+.1f} pts**")

    # Remarques automatiques
    st.markdown('<div class="section-hdr">Remarques comportementales</div>', unsafe_allow_html=True)
    remarques = []
    if abs_s1 <= 2 and abs_s2 <= 2:
        remarques.append("Presence exemplaire — assiduite parfaite sur les deux semestres.")
    if abs_s1 > 10:
        remarques.append(f"Absences excessives au S1 ({abs_s1}h > 10h) — zone de danger.")
    if abs_s2 > 10:
        remarques.append(f"Absences excessives au S2 ({abs_s2}h > 10h) — zone de danger.")
    if progression > 1.5:
        remarques.append(f"Progression entre S1 et S2 (+{progression:.1f} pts) — bonne dynamique.")
    elif progression < -1.5:
        remarques.append(f"Regression entre S1 et S2 ({progression:.1f} pts) — deterioration.")
    if redoublant:
        remarques.append("Statut redoublant — suivi personnalise necessaire.")
    if modules_nv > 3:
        remarques.append(f"{modules_nv} modules non valides depassent le seuil de 3.")
    if pfa_2 < 12:
        remarques.append(f"Note PFA ({pfa_2:.1f}/20) insuffisante — investissement supplementaire requis.")
    if not remarques:
        remarques.append("Aucune anomalie detectee. Etudiant dans la norme.")

    for r in remarques:
        st.markdown(f'<div class="remarque">📝 {r}</div>', unsafe_allow_html=True)

    # Recommandations
    st.markdown('<div class="section-hdr">Recommandations</div>', unsafe_allow_html=True)
    if couleur == "ROUGE":
        recs = [
            "URGENT: Entretien avec le responsable pedagogique",
            "Plan de rattrapage pour les modules non valides",
            "Signalement si absences depassent le seuil",
            "Tutorat personnalise pour la moyenne",
        ]
        if pfa_2 < 12: recs.append("Encadrement renforce du projet PFA")
    elif couleur == "JAUNE":
        recs = [
            "Surveiller les absences (contacter si > 10h)",
            "Renforcement cible dans les modules faibles",
            "Suivi mensuel de la progression",
        ]
    else:
        recs = [
            "Continuer sur cette excellente lancee",
            "Proposer des projets enrichissants",
        ]
    for r in recs:
        st.markdown(f'<div class="rec-item">✅ {r}</div>', unsafe_allow_html=True)

# ══════════════════════ SECTION BAS: Comparaison multi-modeles ════════════════
st.markdown("---")
st.subheader("Comparaison des predictions — Tous les modeles")
mcols = st.columns(len(models))
for mcol, (nm, _) in zip(mcols, models.items()):
    ln, pr, nt, cl = live_predict(fd, nm, scaler, feature_names, models)
    em = {"VERT":"🟢","JAUNE":"🟡","ROUGE":"🔴"}[cl]
    with mcol:
        st.metric(nm, f"{pr*100:.1f}%", cl)
        st.markdown(f"{em} **{cl}** — Note: {nt:.1f}/20")

# ══════════════════════ SECTION BAS: What-if Absences ════════════════════════
st.markdown("---")
st.subheader("Simulation What-if: Impact des Absences sur les 3 Conditions")

with st.expander("Voir la simulation"):
    absence_range = list(range(0, 90, 5))
    sim_rows = []
    for total_a in absence_range:
        fd2 = fd.copy()
        a1 = total_a // 2; a2 = total_a - a1
        fd2.update({
            "Absences_S1": float(a1), "Absences_S2": float(a2),
            "Total_Absences": float(total_a),
            "Danger_Absences": 1 if (a1 > 10 or a2 > 10) else 0,
            "Score_Danger": (1 if (a1>10 or a2>10) else 0) + redoublant,
        })
        _, pr2, nt2, cl2 = live_predict(fd2, modele, scaler, feature_names, models)
        sim_rows.append({
            "Absences totales": total_a,
            "Probabilite (%)": round(pr2*100, 1),
            "Note estimee": round(nt2, 1),
            "Statut": cl2,
            "Danger Abs": "OUI" if (a1>10 or a2>10) else "NON",
        })

    df_sim = pd.DataFrame(sim_rows)
    colors_line = ["#2ecc71" if r=="VERT" else "#f39c12" if r=="JAUNE" else "#e74c3c"
                   for r in df_sim["Statut"]]

    fig, ax = plt.subplots(figsize=(10, 4), facecolor="#1e2130")
    ax.set_facecolor("#1e2130")
    ax.plot(df_sim["Absences totales"], df_sim["Probabilite (%)"], "o-",
            color="#4e79a7", linewidth=2.5, markersize=7)
    ax.axhline(y=70, color="#2ecc71", linestyle="--", linewidth=1.5, alpha=0.7, label="Seuil VERT (70%)")
    ax.axhline(y=40, color="#e74c3c", linestyle="--", linewidth=1.5, alpha=0.7, label="Seuil ROUGE (<40%)")
    ax.axvline(x=20, color="#f39c12", linestyle=":", linewidth=1.5, alpha=0.7, label="Danger abs (20h)")
    ax.set_xlabel("Absences totales (h)", fontsize=11, color="white")
    ax.set_ylabel("Probabilite de reussite (%)", fontsize=11, color="white")
    ax.set_title("Impact des Absences — Probabilite de Reussite", fontsize=12, fontweight="bold", color="white")
    ax.legend(facecolor="#1e2130", labelcolor="white", fontsize=10)
    ax.tick_params(colors="white"); ax.spines[:].set_color("#333")
    ax.set_ylim(0, 110)
    plt.tight_layout()
    st.pyplot(fig); plt.close(fig)
    st.dataframe(df_sim, use_container_width=True)

st.markdown("---")
st.markdown("<center><small>PFA — Prediction Reussite Academique | Interface 13 — What-if | Conditions: Moy≥12, Modules_NV≤3, PFA≥12</small></center>", unsafe_allow_html=True)
