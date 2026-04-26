"""
Interface 6 — Comparaison des Modeles ML
Streamlit app: metriques, matrices de confusion, courbes ROC, recommandations
Lancer: streamlit run src/interface_6_model_comparison.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score, precision_score, recall_score, f1_score
import joblib

# ─── Config page ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interface 6 - Comparaison Modeles ML",
    page_icon="🤖",
    layout="wide",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Poppins:wght@500;600;700;800&display=swap');

    /* Targeting the overall app background */
    [data-testid="stAppViewContainer"], .main { 
        background-color: #000000;
        background-image: none;
        color: #e2e8f0; 
        font-family: 'Inter', sans-serif;
    }
    /* Ensure the sidebar also blends if used */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
    }
    h1, h2, h3, h4 { font-family: 'Poppins', sans-serif !important; }

    /* Title Styling */
    .title-main {
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #34d399, #fbbf24);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem; letter-spacing: -0.5px;
    }
    .subtitle { 
        color: #94a3b8; font-size: 1.1rem; margin-bottom: 2.5rem; 
        font-weight: 400; letter-spacing: 0.2px;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem; font-weight: 600; padding: 12px 20px;
        background: rgba(30,41,59,0.5); border-radius: 8px 8px 0 0;
        border: 1px solid rgba(255,255,255,0.05); border-bottom: none;
        color: #94a3b8; transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(15,23,42,0.9) !important; color: #f8fafc !important;
        border-top: 2px solid #3b82f6 !important;
    }

    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.65);
        border-radius: 16px; padding: 24px; margin: 12px 0;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative; overflow: hidden;
    }
    .metric-card:hover { align-items: default;
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4);
        border-color: rgba(255,255,255,0.15);
    }
    .best-card { 
        border-left: 0 !important;
        background: linear-gradient(145deg, rgba(30,41,59,0.8), rgba(16,185,129,0.05));
    }
    .best-card::before {
        content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
        background: #10b981; box-shadow: 0 0 15px #10b981;
    }

    .model-name { font-size: 1.4rem; font-weight: 700; letter-spacing: 0.5px; display:inline-block; }
    
    /* Progress Bars inside cards */
    .metric-row { display: flex; justify-content: space-between; align-items: center; margin: 10px 0 4px 0; }
    .metric-label { font-size: 0.9rem; color: #cbd5e1; font-weight: 500; }
    .metric-val { font-size: 1.05rem; font-weight: 700; }
    .mini-bar-bg { width: 100%; background: rgba(0,0,0,0.3); height: 6px; border-radius: 4px; overflow: hidden; }
    .mini-bar-fill { height: 100%; border-radius: 4px; }

    /* Badges */
    .badge-best { background: rgba(16,185,129,0.2); color: #34d399; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(16,185,129,0.3); vertical-align: middle; margin-left: 8px;}
    
    /* Section Headers */
    .section-hdr {
        font-family: 'Poppins', sans-serif; font-size: 1.3rem; font-weight: 600;
        color: #f8fafc; margin-top: 1.5rem; margin-bottom: 1rem;
        display: flex; align-items: center; gap: 10px;
    }
    .section-hdr::before { content: ''; display: inline-block; width: 4px; height: 20px; background: #3b82f6; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── Chemins ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_DIR, "models")
DOCS_PATH   = os.path.join(BASE_DIR, "docs")

MODEL_COLORS = {
    "LogisticRegression": "#4e79a7",
    "RandomForest":       "#59a14f",
    "SVM":                "#e15759",
}

# ─── Chargement ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_resources():
    scaler         = joblib.load(os.path.join(MODELS_PATH, "scaler.pkl"))
    feature_names  = joblib.load(os.path.join(MODELS_PATH, "feature_names.pkl"))
    models = {}
    for name in ["LogisticRegression", "RandomForest", "SVM"]:
        path = os.path.join(MODELS_PATH, f"{name}.pkl")
        if os.path.exists(path):
            models[name] = joblib.load(path)
    return scaler, feature_names, models


@st.cache_data
def load_test_data():
    from src.preprocessing.data_pipeline import run_pipeline
    return run_pipeline()


def compute_metrics(model, X_test, y_test, name):
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    return {
        "name":      name,
        "accuracy":  accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall":    recall_score(y_test, y_pred, zero_division=0),
        "f1":        f1_score(y_test, y_pred, zero_division=0),
        "roc_auc":   roc_auc,
        "y_pred":    y_pred,
        "y_proba":   y_proba,
        "fpr":       fpr,
        "tpr":       tpr,
    }


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">Interface 6 — Comparaison des Modeles ML</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyse comparative des 3 modeles de Machine Learning entraines sur le dataset academique</div>', unsafe_allow_html=True)

# ─── Chargement des donnees ───────────────────────────────────────────────────
with st.spinner("Chargement des modeles et donnees..."):
    try:
        scaler, feature_names, models = load_resources()
        X_train, X_test, y_train, y_test, feats = load_test_data()
        results = {name: compute_metrics(m, X_test, y_test, name) for name, m in models.items()}
        models_loaded = True
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        st.info("Assurez-vous d'avoir lance train.py d'abord.")
        st.stop()


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Tableau des Metriques",
    "🔲 Matrices de Confusion",
    "📈 Courbes ROC",
    "🏆 Recommandation",
    "🎓 Prédiction 3A par Filière",
])

# ════════════════════════════════════════════════════════════
# TAB 1: Tableau des metriques
# ════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-hdr">Scores de Performance</div>', unsafe_allow_html=True)

    # Métriques en cartes
    cols = st.columns(3)
    best_f1 = max(results.values(), key=lambda r: r["f1"])

    for i, (name, res) in enumerate(results.items()):
        is_best = name == best_f1["name"]
        card_class = "metric-card best-card" if is_best else "metric-card"
        color = MODEL_COLORS.get(name, "#888888")
        badge = '<span class="badge-best">🏆 Gagnant</span>' if is_best else ""
        
        # HTML Helper for Progress Bars
        def make_bar(label, val, c):
            return f'<div class="metric-row"><span class="metric-label">{label}</span><span class="metric-val" style="color:{c}">{val:.1%}</span></div><div class="mini-bar-bg"><div class="mini-bar-fill" style="width:{val*100}%; background:{c}; box-shadow:0 0 8px {c}"></div></div>'

        with cols[i]:
            html_content = f'<div class="{card_class}"><div class="model-name" style="color:{color}">{name}</div> {badge}<hr style="border:0; height:1px; background:rgba(255,255,255,0.08); margin:15px 0 10px 0;"/>{make_bar("Accuracy", res["accuracy"], color)}<div style="height:12px;"></div>{make_bar("F1-Score", res["f1"], color)}<div style="height:12px;"></div>{make_bar("Roc-AUC", res["roc_auc"], color)}</div>'
            st.markdown(html_content, unsafe_allow_html=True)

    # Tableau DataFrame
    st.markdown("---")
    st.subheader("Tableau comparatif complet")
    data = []
    for name, res in results.items():
        data.append({
            "Modele": name,
            "Accuracy":  f"{res['accuracy']:.4f}",
            "Precision": f"{res['precision']:.4f}",
            "Recall":    f"{res['recall']:.4f}",
            "F1-Score":  f"{res['f1']:.4f}",
            "ROC-AUC":   f"{res['roc_auc']:.4f}",
        })
    df_metrics = pd.DataFrame(data).set_index("Modele")
    st.dataframe(df_metrics, use_container_width=True)

    # Graphique en barres groupees
    st.markdown("---")
    st.markdown('<div class="section-hdr">Performance Gloable</div>', unsafe_allow_html=True)
    metrics_keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 5), facecolor="#0b0f19")
    ax.set_facecolor("#0b0f19")
    for i, (name, res) in enumerate(results.items()):
        vals  = [res[k] for k in metrics_keys]
        color = MODEL_COLORS.get(name, "#888888")
        bars  = ax.bar(x + i * width, vals, width, label=name, color=color, alpha=0.9, edgecolor='none')
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01,
                    f"{b.get_height():.2f}", ha="center", va="bottom", fontsize=8, color="white")
    ax.set_xticks(x + width)
    ax.set_xticklabels(labels, fontsize=11, color="#cbd5e1", fontweight="500")
    ax.set_ylim([0, 1.15])
    ax.set_ylabel("Score", fontsize=11, color="#94a3b8", fontweight="500")
    
    ax.legend(fontsize=10, facecolor="#1e293b", edgecolor="none", labelcolor="#cbd5e1")
    ax.tick_params(colors="#64748b")
    ax.spines[:].set_color("#1e293b")
    ax.grid(axis='y', color='#1e293b', linestyle='--', alpha=0.5)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ════════════════════════════════════════════════════════════
# TAB 2: Matrices de confusion
# ════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-hdr">Matrices de Confusion</div>', unsafe_allow_html=True)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), facecolor="#0b0f19")
    for ax, (name, res) in zip(axes, results.items()):
        cm = confusion_matrix(y_test, res["y_pred"])
        ax.set_facecolor("#0b0f19")
        sns.heatmap(cm, annot=True, fmt="d", cmap="mako", ax=ax,
                    xticklabels=["Echec (0)", "Reussi (1)"],
                    yticklabels=["Echec (0)", "Reussi (1)"],
                    annot_kws={"size": 16, "weight": "bold"})
        ax.set_title(name, fontsize=13, fontweight="bold", color="#f8fafc", pad=12)
        ax.set_xlabel("Valeur predite", color="#94a3b8", fontweight="500")
        ax.set_ylabel("Valeur reelle", color="#94a3b8", fontweight="500")
        ax.tick_params(colors="#cbd5e1")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Explication
    st.info("""
    **Lecture de la matrice :**
    - **Vrai Positif (VP)** — Reussi prédit comme Reussi ✅
    - **Vrai Negatif (VN)** — Echec prédit comme Echec ✅
    - **Faux Positif (FP)** — Echec prédit comme Reussi ❌
    - **Faux Negatif (FN)** — Reussi prédit comme Echec ❌
    """)


# ════════════════════════════════════════════════════════════
# TAB 3: Courbes ROC
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-hdr">Courbes ROC (Receiver Operating Characteristic)</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#0b0f19")
    ax.set_facecolor("#0b0f19")
    ax.plot([0, 1], [0, 1], color="#475569", linestyle="--", linewidth=1.5, label="Aleatoire (AUC=0.50)", alpha=0.8)
    for name, res in results.items():
        color = MODEL_COLORS.get(name, "#888888")
        ax.plot(res["fpr"], res["tpr"], color=color, linewidth=3,
                label=f"{name} (AUC={res['roc_auc']:.3f})", alpha=0.9)
    ax.set_xlabel("Taux de Faux Positifs (FPR)", fontsize=11, color="#94a3b8", fontweight="500")
    ax.set_ylabel("Taux de Vrais Positifs (TPR)", fontsize=11, color="#94a3b8", fontweight="500")
    ax.legend(loc="lower right", fontsize=11, facecolor="#1e293b", edgecolor="none", labelcolor="#cbd5e1")
    ax.tick_params(colors="#64748b")
    ax.spines[:].set_color("#1e293b")
    ax.grid(color='#1e293b', linestyle='--', alpha=0.4)
    ax.fill_between([0, 1], [0, 1], alpha=0.02, color="white")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, (name, res) in zip([col1, col2, col3], results.items()):
        color = MODEL_COLORS.get(name, "#888888")
        with col:
            st.markdown(f"""
            <div style="background:rgba(30,41,59,0.5); border:1px solid rgba(255,255,255,0.05); border-radius:12px; padding:15px; text-align:center;">
                <div style="color:{color}; font-weight:700; font-size:1.1rem; margin-bottom:5px;">{name} AUC</div>
                <div style="font-size:1.8rem; font-weight:800; color:#f8fafc;">{res['roc_auc']:.4f}</div>
                <div style="color:#34d399; font-size:0.9rem;">+{res['roc_auc']-0.5:.4f} vs aléatoire</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# TAB 4: Recommandation
# ════════════════════════════════════════════════════════════
with tab4:
    best = max(results.values(), key=lambda r: r["f1"])

    st.markdown(f"""
    <div style="background:linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(30,41,59,0.8) 100%); 
                border-radius:20px; padding:32px; border:1px solid rgba(16,185,129,0.3); 
                box-shadow:0 10px 30px rgba(0,0,0,0.2); margin:20px 0 30px 0; position:relative; overflow:hidden;">
        <div style="position:absolute; top:-20px; right:-20px; font-size:150px; opacity:0.03; 
                    transform:rotate(15deg); pointer-events:none;">🏆</div>
        <h3 style="color:#10b981; font-family:'Poppins'; margin-top:0; font-size:1.8rem; margin-bottom:8px;">
            ✨ Modèle Recommandé : {best['name']}
        </h3>
        <p style="color:#cbd5e1; font-size:1.05rem; line-height:1.6; max-width:800px; margin-bottom:0;">
            Ce modèle est sélectionné comme <b>moteur principal de prédiction</b> pour l'interface utilisateur. 
            Il offre le meilleur compromis (F1-Score) pour réduire à la fois les fausses alertes et identifier 
            efficacement les étudiants en difficulté absolue.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background:rgba(30,41,59,0.4); border-radius:16px; padding:24px; border:1px solid rgba(255,255,255,0.05); height:100%;">
            <h4 style="color:#f8fafc; font-family:'Poppins'; margin-top:0; font-size:1.3rem;">📊 Performances Détaillées</h4>
            <ul style="color:#cbd5e1; font-size:1rem; line-height:1.8; margin-top:15px; padding-left:20px;">
                <li><b>F1-Score Pivot</b> : <span style="color:#34d399; font-weight:bold;">{best['f1']:.4f}</span> <i>(Meilleur compromis global)</i></li>
                <li><b>ROC-AUC Robustesse</b> : <span style="color:#60a5fa; font-weight:bold;">{best['roc_auc']:.4f}</span></li>
                <li><b>Accuracy Globale</b> : <span style="color:#f8fafc; font-weight:bold;">{best['accuracy']:.4f}</span></li>
                <li><b>Recall Sensibilité</b> : <span style="color:#fbbf24; font-weight:bold;">{best['recall']:.0%}</span> des échecs réels correctement anticipés</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""<div style="background:rgba(30,41,59,0.4); border-radius:16px; padding:24px; border:1px solid rgba(255,255,255,0.05); height:100%;">""", unsafe_allow_html=True)
        st.markdown("<h4 style=\"color:#f8fafc; font-family:'Poppins'; margin-top:0; font-size:1.3rem;\">🥇 Classement Général</h4>", unsafe_allow_html=True)
        st.markdown("""<table style="width:100%; color:#cbd5e1; border-collapse:collapse; margin-top:15px;">
        <tr style="border-bottom:1px solid rgba(255,255,255,0.1); color:#94a3b8; font-size:0.9rem; text-align:left;">
            <th style="padding:10px 5px;">Rang</th><th style="padding:10px 5px;">Modèle</th><th style="padding:10px 5px; text-align:right;">F1-Score</th>
        </tr>""", unsafe_allow_html=True)
        
        for i, (name, res) in enumerate(sorted(results.items(), key=lambda x: x[1]["f1"], reverse=True), 1):
            medal = ["🥇", "🥈", "🥉"][i-1]
            color_row = "#10b981" if i==1 else "#e2e8f0"
            fw = "bold" if i==1 else "normal"
            st.markdown(f"""<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">
                <td style="padding:12px 5px;">{medal}</td>
                <td style="padding:12px 5px; font-weight:{fw}; color:{color_row};">{name}</td>
                <td style="padding:12px 5px; text-align:right; font-weight:{fw}; color:{color_row};">{res['f1']:.4f}</td>
            </tr>""", unsafe_allow_html=True)
        
        st.markdown("</table></div>", unsafe_allow_html=True)

    # Explication des metriques
    with st.expander("Explication des metriques"):
        st.markdown("""
        | Metrique | Definition | Quand privilegier |
        |---------|-----------|------------------|
        | **Accuracy** | % predictions correctes | Dataset equilibre |
        | **Precision** | % vrais positifs parmi predits positifs | Eviter fausses alertes |
        | **Recall** | % vrais positifs detectes | Detecter tous les echecs |
        | **F1-Score** | Moyenne harmonique Precision/Recall | Equilibre general |
        | **ROC-AUC** | Aire sous la courbe ROC | Robustesse du classifieur |
        """)

# ════════════════════════════════════════════════════════════
# TAB 5: Prédiction 3A par filière
# ════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-hdr">Prédiction des Modules 3A — Profil Moyen par Filière</div>', unsafe_allow_html=True)
    st.info(
        "Ce tableau montre la prédiction de validation des modules de 3ème année "
        "pour un étudiant 'type' (notes moyennes de chaque filière)."
    )

    try:
        from src.preprocessing.module_relations import predict_all_modules_3A, FILIERE_CODE_TO_KEY

        # Profil étudiant moyen (par défaut)
        etudiant_moyen = {
            "Module_S1_1": 13.0, "Module_S1_2": 12.5, "Module_S1_3": 12.5,
            "Module_S1_4": 13.0, "Module_S1_5": 12.5,
            "Module_S2_1": 13.0, "Module_S2_2": 13.0, "Module_S2_3": 13.5,
            "Module_S2_4": 12.5, "Module_S2_5": 13.0,
            "PFA_2": 14.0, "Absences_S1": 8, "Absences_S2": 8, "Redoublant": 0,
        }

        all_filieres = {
            "ITE — Génie Info": "ite",
            "ISIC": "isic",
            "CCN — Cybersec": "ccn",
            "GEE — Elec": "gee",
            "Génie Civil": "civil",
            "Génie Industriel": "industriel",
        }

        rows_3A = []
        for fil_name, fil_key in all_filieres.items():
            res3 = predict_all_modules_3A(etudiant_moyen, fil_key)
            row = {"Filière": fil_name,
                   "Modules validés": f"{res3['nb_valides']}/{res3['nb_total']}",
                   "Taux (%)": res3["taux_validation"],
                   "Note S5 estimée": res3["note_s5_predite"],
                   "Note PFE estimée": res3["note_pfe_predite"],
                   "Statut": res3["statut_global"]}
            # Ajouter chaque module
            for mod_key, mod_res in res3["modules_3A"].items():
                row[mod_res["label_fr"]] = "✅" if mod_res["valide"] else "❌"
            rows_3A.append(row)

        df_3A = pd.DataFrame(rows_3A).set_index("Filière")
        st.dataframe(df_3A, use_container_width=True)

        # Graphique comparatif
        fig5, ax5 = plt.subplots(figsize=(10, 4), facecolor="#0b0f19")
        ax5.set_facecolor("#0b0f19")
        taux_vals  = [r["Taux (%)"] for r in rows_3A]
        fil_labels = [r["Filière"] for r in rows_3A]
        colors5 = ["#10b981" if t >= 80 else "#fbbf24" if t >= 60 else "#f43f5e" for t in taux_vals]
        bars5 = ax5.bar(fil_labels, taux_vals, color=colors5, alpha=0.9, edgecolor="none")
        ax5.axhline(y=80, color="#10b981", linestyle="--", alpha=0.5, linewidth=1.5, label="80% (Excellence)")
        ax5.axhline(y=60, color="#fbbf24", linestyle="--", alpha=0.5, linewidth=1.5, label="60% (Risque Modéré)")
        for b, t in zip(bars5, taux_vals):
            ax5.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                     f"{t:.0f}%", ha="center", color="#f8fafc", fontsize=11, fontweight="bold")
        ax5.set_ylabel("Taux de validation 3A (%)", color="#94a3b8", fontweight="500")
        ax5.set_ylim(0, 115)
        ax5.tick_params(colors="#cbd5e1")
        ax5.spines[:].set_color("#1e293b")
        ax5.grid(axis='y', color='#1e293b', linestyle='--', alpha=0.5)
        ax5.legend(facecolor="#1e293b", edgecolor="none", labelcolor="#cbd5e1", fontsize=9, loc='upper right')
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

    except Exception as e:
        st.warning(f"Prédiction 3A non disponible: {e}")
        st.info("Vérifiez que src/preprocessing/module_relations.py est présent.")


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small style='color:#64748b;'>PFA — Système Intelligent de Prédiction | "
    "Interface 6 — Comparaison ML + Prédiction 3A</small></center>",
    unsafe_allow_html=True
)
