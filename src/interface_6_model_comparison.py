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
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
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
    .main { background-color: #0f1117; color: white; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border-radius: 12px; padding: 20px; margin: 8px 0;
        border-left: 4px solid #4e79a7;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .best-card { border-left: 4px solid #2ecc71 !important; }
    .title-main {
        font-size: 2.2rem; font-weight: 800;
        background: linear-gradient(90deg, #4e79a7, #59a14f, #e15759);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle { color: #a0a8c0; font-size: 1rem; margin-bottom: 2rem; }
    .model-name { font-size: 1.2rem; font-weight: 700; color: #e0e6ff; }
    .metric-val { font-size: 2rem; font-weight: 800; color: #4e79a7; }
    .stTabs [data-baseweb="tab"] { font-size: 1rem; font-weight: 600; }
    .badge-vert  { background:#2ecc71; color:white; padding:3px 10px; border-radius:20px; font-weight:700; }
    .badge-jaune { background:#f39c12; color:white; padding:3px 10px; border-radius:20px; font-weight:700; }
    .badge-rouge { background:#e74c3c; color:white; padding:3px 10px; border-radius:20px; font-weight:700; }
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
        models_loaded = False
        st.stop()

if not models_loaded:
    st.stop()

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Tableau des Metriques",
    "🔲 Matrices de Confusion",
    "📈 Courbes ROC",
    "🏆 Recommandation"
])

# ════════════════════════════════════════════════════════════
# TAB 1: Tableau des metriques
# ════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Comparaison des performances des 3 modeles")

    # Métriques en cartes
    cols = st.columns(3)
    best_f1 = max(results.values(), key=lambda r: r["f1"])

    for i, (name, res) in enumerate(results.items()):
        is_best = name == best_f1["name"]
        card_class = "metric-card best-card" if is_best else "metric-card"
        color = MODEL_COLORS[name]
        badge = "⭐ Meilleur" if is_best else ""
        with cols[i]:
            st.markdown(f"""
            <div class="{card_class}">
                <div class="model-name" style="color:{color}">{name} {badge}</div>
                <hr style="border-color:#333; margin:10px 0"/>
                <b>Accuracy</b> <span style="float:right;font-size:1.3rem;color:{color}">{res['accuracy']:.1%}</span><br/>
                <b>Precision</b> <span style="float:right;font-size:1.3rem;color:{color}">{res['precision']:.1%}</span><br/>
                <b>Recall</b> <span style="float:right;font-size:1.3rem;color:{color}">{res['recall']:.1%}</span><br/>
                <b>F1-Score</b> <span style="float:right;font-size:1.3rem;color:{color}">{res['f1']:.1%}</span><br/>
                <b>ROC-AUC</b> <span style="float:right;font-size:1.3rem;color:{color}">{res['roc_auc']:.1%}</span>
            </div>
            """, unsafe_allow_html=True)

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
    st.subheader("Graphique de comparaison")
    metrics_keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    labels = ["Accuracy", "Precision", "Recall", "F1-Score", "ROC-AUC"]
    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 5), facecolor="#1e2130")
    ax.set_facecolor("#1e2130")
    for i, (name, res) in enumerate(results.items()):
        vals  = [res[k] for k in metrics_keys]
        color = MODEL_COLORS[name]
        bars  = ax.bar(x + i * width, vals, width, label=name, color=color, alpha=0.9)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01,
                    f"{b.get_height():.2f}", ha="center", va="bottom", fontsize=8, color="white")
    ax.set_xticks(x + width)
    ax.set_xticklabels(labels, fontsize=11, color="white")
    ax.set_ylim([0, 1.15])
    ax.set_ylabel("Score", fontsize=12, color="white")
    ax.set_title("Comparaison des Metriques — 3 Modeles ML", fontsize=13, fontweight="bold", color="white")
    ax.legend(fontsize=10)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#333")
    ax.yaxis.label.set_color("white")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ════════════════════════════════════════════════════════════
# TAB 2: Matrices de confusion
# ════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Matrices de Confusion")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), facecolor="#1e2130")
    for ax, (name, res) in zip(axes, results.items()):
        cm = confusion_matrix(y_test, res["y_pred"])
        ax.set_facecolor("#1e2130")
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["Echec (0)", "Reussi (1)"],
                    yticklabels=["Echec (0)", "Reussi (1)"],
                    annot_kws={"size": 16, "weight": "bold"})
        ax.set_title(name, fontsize=12, fontweight="bold", color="white", pad=10)
        ax.set_xlabel("Valeur predite", color="white")
        ax.set_ylabel("Valeur reelle", color="white")
        ax.tick_params(colors="white")
    plt.suptitle("Matrices de Confusion — Comparaison", fontsize=14, fontweight="bold", color="white", y=1.02)
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
    st.subheader("Courbes ROC (Receiver Operating Characteristic)")
    fig, ax = plt.subplots(figsize=(8, 6), facecolor="#1e2130")
    ax.set_facecolor("#1e2130")
    ax.plot([0, 1], [0, 1], "w--", linewidth=1.5, label="Aleatoire (AUC=0.50)", alpha=0.5)
    for name, res in results.items():
        color = MODEL_COLORS[name]
        ax.plot(res["fpr"], res["tpr"], color=color, linewidth=2.5,
                label=f"{name} (AUC={res['roc_auc']:.3f})")
    ax.set_xlabel("Taux de Faux Positifs (FPR)", fontsize=12, color="white")
    ax.set_ylabel("Taux de Vrais Positifs (TPR)", fontsize=12, color="white")
    ax.set_title("Courbes ROC — Comparaison des Modeles", fontsize=13, fontweight="bold", color="white")
    ax.legend(loc="lower right", fontsize=11, facecolor="#1e2130", labelcolor="white")
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#333")
    ax.fill_between([0, 1], [0, 1], alpha=0.05, color="white")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    col1, col2, col3 = st.columns(3)
    for col, (name, res) in zip([col1, col2, col3], results.items()):
        color = MODEL_COLORS[name]
        with col:
            st.metric(label=f"{name} — AUC", value=f"{res['roc_auc']:.4f}",
                      delta=f"+{res['roc_auc']-0.5:.4f} vs aléatoire")


# ════════════════════════════════════════════════════════════
# TAB 4: Recommandation
# ════════════════════════════════════════════════════════════
with tab4:
    best = max(results.values(), key=lambda r: r["f1"])
    second = sorted(results.values(), key=lambda r: r["f1"], reverse=True)[1]

    st.subheader("Recommandation du Modele")
    st.success(f"**Modele recommande : {best['name']}**")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        ### 🏆 {best['name']}
        - **F1-Score** : `{best['f1']:.4f}` (meilleur)
        - **ROC-AUC**  : `{best['roc_auc']:.4f}`
        - **Accuracy** : `{best['accuracy']:.4f}`
        - **Recall**   : `{best['recall']:.4f}` — detecte {best['recall']:.0%} des vrais echecs

        **Avantages :**
        - Rapide et interpretable
        - Performant meme avec peu de donnees
        - Coefficients directement utilisables pour expliquer les decisions
        """)
    with c2:
        st.markdown(f"""
        ### 📊 Classement des modeles

        | Rang | Modele | F1-Score |
        |------|--------|---------|
        """)
        for i, (name, res) in enumerate(sorted(results.items(), key=lambda x: x[1]["f1"], reverse=True), 1):
            medal = ["🥇", "🥈", "🥉"][i-1]
            st.markdown(f"| {medal} | {name} | `{res['f1']:.4f}` |")

        st.markdown(f"""
        ---
        **Modele en production : `{best['name']}`**

        Pour chaque etudiant, la prediction utilisera ce modele par defaut.
        Les autres modeles restent disponibles via le parametre `modele_utilise`.
        """)

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

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>PFA — Systeme Intelligent de Prediction de la Reussite Academique | "
    "Interface 6 — ML Engineer</small></center>",
    unsafe_allow_html=True
)
