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
    st.subheader("Comparaison des performances des 3 modeles")

    # Métriques en cartes
    cols = st.columns(3)
    best_f1 = max(results.values(), key=lambda r: r["f1"])

    for i, (name, res) in enumerate(results.items()):
        is_best = name == best_f1["name"]
        card_class = "metric-card best-card" if is_best else "metric-card"
        color = MODEL_COLORS.get(name, "#888888")
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
        color = MODEL_COLORS.get(name, "#888888")
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
        color = MODEL_COLORS.get(name, "#888888")
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
        color = MODEL_COLORS.get(name, "#888888")
        with col:
            st.metric(label=f"{name} — AUC", value=f"{res['roc_auc']:.4f}",
                      delta=f"+{res['roc_auc']-0.5:.4f} vs aléatoire")


# ════════════════════════════════════════════════════════════
# TAB 4: Recommandation
# ════════════════════════════════════════════════════════════
with tab4:
    best = max(results.values(), key=lambda r: r["f1"])

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

# ════════════════════════════════════════════════════════════
# TAB 5: Prédiction 3A par filière
# ════════════════════════════════════════════════════════════
with tab5:
    st.subheader("🎓 Prédiction des Modules 3ème Année — Par Filière")
    st.info(
        "Ce tableau montre la prédiction de validation des modules 3A "
        "pour un étudiant type (notes moyennes de chaque filière)."
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
        fig5, ax5 = plt.subplots(figsize=(10, 4), facecolor="#1e2130")
        ax5.set_facecolor("#1e2130")
        taux_vals  = [r["Taux (%)"] for r in rows_3A]
        fil_labels = [r["Filière"] for r in rows_3A]
        colors5 = ["#2ecc71" if t >= 80 else "#f39c12" if t >= 60 else "#e74c3c" for t in taux_vals]
        bars5 = ax5.bar(fil_labels, taux_vals, color=colors5, alpha=0.85)
        ax5.axhline(y=80, color="#2ecc71", linestyle="--", alpha=0.7, linewidth=1.5, label="80% (VERT)")
        ax5.axhline(y=60, color="#f39c12", linestyle="--", alpha=0.7, linewidth=1.5, label="60% (JAUNE)")
        for b, t in zip(bars5, taux_vals):
            ax5.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5,
                     f"{t:.0f}%", ha="center", color="white", fontsize=11, fontweight="bold")
        ax5.set_ylabel("Taux de validation 3A (%)", color="white")
        ax5.set_title("Taux de validation modules 3A — Étudiant moyen par filière",
                      color="white", fontweight="bold", fontsize=12)
        ax5.set_ylim(0, 115)
        ax5.tick_params(colors="white"); ax5.spines[:].set_color("#333")
        ax5.legend(facecolor="#1e2130", labelcolor="white", fontsize=9)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

    except Exception as e:
        st.warning(f"Prédiction 3A non disponible: {e}")
        st.info("Vérifiez que src/preprocessing/module_relations.py est présent.")


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small>PFA — Système Intelligent de Prédiction | "
    "Interface 6 — Comparaison ML + Prédiction 3A</small></center>",
    unsafe_allow_html=True
)
