"""
Interface 13 — Prédiction Intelligente des Modules 3ème Année avec Données Réelles
==================================================================================

Améliorations v3 :
1. Sidebar enrichie avec mini-KPIs et résumé étudiant
2. Progress bars animées pour chaque module 3A
3. Affichage du Résultat Global visible directement (sans expander)
4. Compteur de modules validés sous forme de badge visuel
5. Meilleur design CSS : glassmorphism amélioré, animations, Poppins
6. Graphique barres horizontales stylisé avec valeurs affichées
7. Indicateur de risque global avec tooltip couleur
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib

st.set_page_config(
    page_title="Prédiction 3ème Année — Analyse What-If",
    page_icon="🎓",
    layout="wide",
)

# ─── DESIGN & CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main {
        background: radial-gradient(circle at 10% 20%, #0d1224 0%, #060913 100%);
        color: #f1f5f9;
    }

    /* ── Header ── */
    .title-main {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #e879f9 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding-top: 1.5rem; letter-spacing: -1px;
        margin-bottom: 0.2rem;
        animation: fadeInDown 0.8s ease;
    }
    .subtitle {
        color: #94a3b8; margin-bottom: 2.5rem; font-size: 1.1rem;
        text-align: center; font-weight: 400; font-family: 'Poppins', sans-serif;
        animation: fadeInUp 0.8s ease;
    }
    @keyframes fadeInDown { from { opacity:0; transform:translateY(-20px); } to { opacity:1; transform:translateY(0); } }
    @keyframes fadeInUp   { from { opacity:0; transform:translateY(20px);  } to { opacity:1; transform:translateY(0); } }

    /* ── Section Header ── */
    .section-hdr {
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem; font-weight: 700; color: #818cf8;
        text-transform: uppercase; letter-spacing: 3px;
        margin: 2rem 0 1rem 0;
        border-bottom: 1px solid rgba(129,140,248,0.25);
        padding-bottom: 10px;
    }

    /* ── Student Selector Bar ── */
    .student-selector {
        background: rgba(20, 30, 55, 0.7);
        padding: 22px 28px; border-radius: 20px; margin-bottom: 24px;
        border: 1px solid rgba(129,140,248,0.3);
        box-shadow: 0 0 40px rgba(129,140,248,0.08);
        backdrop-filter: blur(16px);
    }

    /* ── Module Cards ── */
    .module-card {
        background: rgba(22, 32, 58, 0.6);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,0.04);
        border-radius: 18px; padding: 18px 22px; margin: 8px 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .module-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.12);
    }
    .mod-valide   { border-left: 5px solid #10b981; }
    .mod-invalide { border-left: 5px solid #f43f5e; }
    .mod-marginal { border-left: 5px solid #eab308; }

    /* ── Progress Bar ── */
    .progress-bar-container {
        background: rgba(255,255,255,0.07);
        border-radius: 10px; height: 8px; margin-top: 10px; overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%; border-radius: 10px;
        transition: width 0.8s ease-in-out;
    }

    /* ── Score Badge ── */
    .score-badge { font-family: 'Poppins', sans-serif; font-size: 1.4rem; font-weight: 800; }

    /* ── Statut Box ── */
    .statut-box {
        border-radius: 22px; padding: 32px 24px; text-align: center;
        color: white; box-shadow: 0 20px 40px rgba(0,0,0,0.35);
        position: relative; overflow: hidden;
    }
    .statut-box::before {
        content: ''; position: absolute; top:-40%; left:-40%;
        width: 180%; height: 180%;
        background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    }
    .statut-vert  { background: linear-gradient(135deg, #047857 0%, #10b981 100%); }
    .statut-jaune { background: linear-gradient(135deg, #b45309 0%, #f59e0b 100%); }
    .statut-rouge { background: linear-gradient(135deg, #9f1239 0%, #e11d48 100%); }

    /* ── Metric Highlight ── */
    .metric-highlight {
        background: rgba(12, 20, 42, 0.7); border-radius: 18px; padding: 26px;
        text-align: center; border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-highlight:hover { transform: translateY(-6px); box-shadow: 0 16px 40px rgba(0,0,0,0.3); }

    /* ── KPI Mini Card (Sidebar) ── */
    .kpi-mini {
        background: rgba(30,41,70,0.6); border-radius: 14px; padding: 14px 16px;
        margin: 8px 0; border: 1px solid rgba(255,255,255,0.06);
        text-align: center;
    }
    .kpi-mini .kpi-val { font-family:'Poppins'; font-size:1.6rem; font-weight:800; }
    .kpi-mini .kpi-lbl { font-size:0.75rem; color:#94a3b8; text-transform: uppercase; letter-spacing:1px; }

    /* ── Risk / Rec items ── */
    .risk-item {
        background: rgba(244,63,94,0.08); border-left: 4px solid #f43f5e;
        padding: 13px 17px; border-radius: 12px; margin: 8px 0;
        color: #fda4af; font-weight: 500; font-size: 0.9rem;
    }
    .rec-item {
        background: rgba(16,185,129,0.08); border-left: 4px solid #10b981;
        padding: 13px 17px; border-radius: 12px; margin: 8px 0;
        color: #a7f3d0; font-weight: 500; font-size: 0.9rem;
    }

    /* ── Profil Box ── */
    .profil-box {
        background: rgba(22,32,58,0.5); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px; padding: 20px;
    }
    .danger-abs { background: rgba(244,63,94,0.12); border: 1px dashed #f43f5e; border-radius: 10px; padding: 10px 14px; color: #fda4af; font-weight: 600; margin-top:8px; }
    .safe-abs   { background: rgba(16,185,129,0.12); border: 1px dashed #10b981; border-radius: 10px; padding: 10px 14px; color: #6ee7b7; font-weight: 600; margin-top:8px; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab"] { font-family: 'Poppins'; font-size: 1rem; font-weight: 600; padding: 10px 18px; }
    .stTabs [aria-selected="true"] { color: #818cf8 !important; border-bottom: 3px solid #818cf8 !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 20px; }

    /* ── Divider ── */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ── Année card ── */
    .annee-card {
        padding: 22px; border-radius: 18px; text-align: center;
        border-top: 5px solid;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_DIR, "models")
DATA_PATH   = os.path.join(BASE_DIR, "data", "processed", "students_clean.csv")

FILIERES = {
    "ITE — Génie Info":       "ite",
    "ISIC":                   "isic",
    "CCN — Cybersécurité":    "ccn",
    "GEE — Génie Électrique": "gee",
    "Génie Civil":            "civil",
    "Génie Industriel":       "industriel",
}

PROFIL_EMOJI  = {0: "🟢", 1: "🔵", 2: "🟡", 3: "🔴"}
PROFIL_LABELS = {0: "Très assidu", 1: "Assidu", 2: "Préoccupant", 3: "Absentéiste chronique"}

# ─── CHARGEMENT DES DONNÉES ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

df_students = load_data()

# ─── HEADER ────────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">🎓 Prédiction Intelligente 3ème Année</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Sélectionnez un étudiant réel · Ajustez les notes · Visualisez l\'impact en temps réel <span style="color:#818cf8;">⚡ Mode What-If</span></div>',
    unsafe_allow_html=True
)

if df_students is None or df_students.empty:
    st.error("⚠️ Aucune donnée d'étudiant trouvée. Vérifiez que la pipeline de données a été exécutée.")
    st.stop()

# ─── SÉLECTION ÉTUDIANT ────────────────────────────────────────────────────────
st.markdown('<div class="student-selector">', unsafe_allow_html=True)
c_fil, c_etud, c_info = st.columns([1, 2, 1])
with c_fil:
    st.markdown("**🏫 Filière**")
    fil_label   = st.selectbox("Filière", list(FILIERES.keys()), label_visibility="collapsed")
    filiere_key = FILIERES[fil_label]

df_fil = df_students[df_students['Filiere'].str.contains(filiere_key, case=False, na=False)]
if df_fil.empty:
    df_fil = df_students

    with c_etud:
        st.markdown("**👤 Étudiant**")
        student_options = []
        student_dict = {}
        for _, row in df_fil.iterrows():
            cne    = row.get('CNE', 'INCONNU')
            nom    = row.get('Nom', '')
            prenom = row.get('Prenom', '')
            is_red = int(row.get('Redoublant_1A', 0)) == 1 or int(row.get('Redoublant_2A', 0)) == 1
            # Marqueur rouge visible dans le menu déroulant pour les redoublants globaux
            label = f"{'🔴 ' if is_red else ''}{cne} — {nom} {prenom}"
            student_options.append(label)
            student_dict[label] = row

        selected_student_label = st.selectbox("Étudiant", student_options, label_visibility="collapsed")
        selected_student_data  = student_dict[selected_student_label]

with c_info:
    st.markdown("**📌 Filière choisie**")
    st.info(f"**{fil_label}**\n\n{len(df_fil)} étudiants")

st.markdown('</div>', unsafe_allow_html=True)

# ── Variables Redoublant ───────────────────────────────────────────────────────
widget_key = str(selected_student_data.get('CNE', 'INCONNU'))

_r1a = selected_student_data.get('Redoublant_1A', 0)
redoublant_1A = 0 if (pd.isna(_r1a) if hasattr(pd, 'isna') else False) else int(_r1a or 0)

_r2a = selected_student_data.get('Redoublant_2A', 0)
redoublant_2A = 0 if (pd.isna(_r2a) if hasattr(pd, 'isna') else False) else int(_r2a or 0)

# Redoublant global pour la pastille dans le titre du selecteur
redoublant_global = bool(redoublant_1A or redoublant_2A)


# ─── HELPER ────────────────────────────────────────────────────────────────────
def get_val(col_name, default=12.0):
    val = selected_student_data.get(col_name, default)
    if pd.isna(val): return float(default)
    return float(val)

# ─── NOMS DES MODULES PAR FILIERE ──────────────────────────────────────────────
mod_labels = {
    "ite": {
        "s1": ["Maths 1 / Prog C", "Physique / Algo", "Architecture Numérique", "Électronique S1", "Systèmes S1"],
        "s2": ["Maths 2 / Avancé", "POO C++", "Réseaux S2", "Mécanique / Thermo", "Compilation S2"],
        "s3": ["Maths 3 / Oracles", "Java Avancé", "Bases de Données", "Analyse S3", "Génie Logiciel S3"],
        "s4": ["Web S4", "Réseau Avancé S4", "UML / Conception", "Système d'Exploitation", "Management S4"],
    },
    "isic": {
        "s1": ["Maths 1", "Physique S1", "Management", "Electronique", "Info S1"],
        "s2": ["Maths 2", "Physique S2", "Réseaux S2", "Ondes", "POO S2"],
        "s3": ["Maths 3", "Architecture Réseaux", "Signaux", "Télécoms S3", "Génie Logiciel"],
        "s4": ["Systèmes Répartis", "Traitement d'Image", "Sécurité", "Routage S4", "Management"],
    },
    "ccn": {
        "s1": ["Maths 1 / Cyber", "Physique S1", "Architecture", "Réseaux de Base", "Systèmes S1"],
        "s2": ["Maths 2 / Crypto", "POO / Scripting", "Réseaux Locaux", "Système Linux", "Télécoms"],
        "s3": ["Maths 3 / Proba", "Administration Sécurité", "Vulnérabilités", "Python Avancé", "Droit Cyber"],
        "s4": ["Sécurité Avancée", "IoT & Sécurité", "Forensique Numérique", "Pentesting S4", "Management"],
    },
    "gee": {
        "s1": ["Maths 1", "Mécanique du Point", "Machines Électriques 1", "Électronique S1", "Thermo S1"],
        "s2": ["Maths 2", "Mécanique du Solide", "Machines Électriques 2", "Automatique", "Dessin Industriel"],
        "s3": ["Maths 3", "Réseaux Électriques", "Électronique de Puissance", "Énergies Renouvelables", "Automatisme S3"],
        "s4": ["Gestion d'Énergie", "Capteurs S4", "Traitement de Signal", "Informatique Indust.", "Management"],
    },
    "civil": {
        "s1": ["Maths 1", "Mécanique S1", "Matériaux 1", "Dessin Civil S1", "Géologie S1"],
        "s2": ["Maths 2", "RDM S2", "Hydro S2", "Matériaux 2", "Topographie"],
        "s3": ["Maths 3", "Béton Armé 1", "Mécanique des Sols", "Hydraulique S3", "BIM S3"],
        "s4": ["Béton Armé 2", "Ouvrages d'Art", "Thermique Bâtiment", "Voiries S4", "Management"],
    },
    "industriel": {
        "s1": ["Maths 1", "Physique S1", "Procédés de Fab 1", "Dessin Industriel", "Matériaux"],
        "s2": ["Maths 2", "Recherche Opérationnelle", "Procédés de Fab 2", "Mécanique S2", "Informatique"],
        "s3": ["Maths 3", "CAO / PAO", "Gestion de Produit", "Automatique S3", "Qualité S3"],
        "s4": ["Logistique S4", "Gestion de Maintenance", "Lean Management", "Systèmes Indust.", "Management"],
    },
}
cur_labels = mod_labels.get(filiere_key, mod_labels["ite"])

# Textes et couleurs dérivés
red_1a_txt = "🔴 Oui — Redoublé en 1A" if redoublant_1A else "🟢 Non — Réussi du 1er coup"
red_1a_col = "#f43f5e" if redoublant_1A else "#10b981"

red_2a_txt = "🔴 Oui — Redoublé en 2A" if redoublant_2A else "🟢 Non — Réussi du 1er coup"
red_2a_col = "#f43f5e" if redoublant_2A else "#10b981"

# ════════════════════════ ONGLETS ════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "📋 Données 1ère Année",
    "📋 Données 2ème Année",
    "🔮 Résultats & Prédiction 3A",
])

# ─── TAB 1 : 1ère Année ────────────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Semestre 1</div>', unsafe_allow_html=True)
        abs_s1_1A  = st.slider("⏱️ Absences S1 (heures)", 0, 60, int(get_val('Absences_S1', 0)), key=f"abs_s1_1a_{widget_key}")
        mod1_s1_1A = st.slider(cur_labels["s1"][0], 0.0, 20.0, get_val('Module_S1_1'), 0.5, key=f"m1s1_1a_{widget_key}")
        mod2_s1_1A = st.slider(cur_labels["s1"][1], 0.0, 20.0, get_val('Module_S1_2'), 0.5, key=f"m2s1_1a_{widget_key}")
        mod3_s1_1A = st.slider(cur_labels["s1"][2], 0.0, 20.0, get_val('Module_S1_3'), 0.5, key=f"m3s1_1a_{widget_key}")
        mod4_s1_1A = st.slider(cur_labels["s1"][3], 0.0, 20.0, get_val('Module_S1_4'), 0.5, key=f"m4s1_1a_{widget_key}")
        mod5_s1_1A = st.slider(cur_labels["s1"][4], 0.0, 20.0, get_val('Module_S1_5'), 0.5, key=f"m5s1_1a_{widget_key}")
        ang1_1A    = st.slider("Anglais Technique 1", 0.0, 20.0, get_val('Anglais_Tech_1', 13.0), 0.5, key=f"ang1_1a_{widget_key}")
        fr1_1A     = st.slider("Français Professionnel 1", 0.0, 20.0, get_val('Francais_Pro_1', 13.0), 0.5, key=f"fr1_1a_{widget_key}")

    with c2:
        st.markdown('<div class="section-hdr">Semestre 2</div>', unsafe_allow_html=True)
        abs_s2_1A  = st.slider("⏱️ Absences S2 (heures)", 0, 60, int(get_val('Absences_S2', 0)), key=f"abs_s2_1a_{widget_key}")
        mod1_s2_1A = st.slider(cur_labels["s2"][0], 0.0, 20.0, get_val('Module_S2_1'), 0.5, key=f"m1s2_1a_{widget_key}")
        mod2_s2_1A = st.slider(cur_labels["s2"][1], 0.0, 20.0, get_val('Module_S2_2'), 0.5, key=f"m2s2_1a_{widget_key}")
        mod3_s2_1A = st.slider(cur_labels["s2"][2], 0.0, 20.0, get_val('Module_S2_3'), 0.5, key=f"m3s2_1a_{widget_key}")
        mod4_s2_1A = st.slider(cur_labels["s2"][3], 0.0, 20.0, get_val('Module_S2_4'), 0.5, key=f"m4s2_1a_{widget_key}")
        mod5_s2_1A = st.slider(cur_labels["s2"][4], 0.0, 20.0, get_val('Module_S2_5'), 0.5, key=f"m5s2_1a_{widget_key}")
        ang2_1A    = st.slider("Anglais Technique 2", 0.0, 20.0, get_val('Anglais_Tech_2', 13.0), 0.5, key=f"ang2_1a_{widget_key}")
        fr2_1A     = st.slider("Français Professionnel 2", 0.0, 20.0, get_val('Francais_Pro_2', 13.0), 0.5, key=f"fr2_1a_{widget_key}")

    st.markdown('<div class="section-hdr">Évaluation Annuelle</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1: pfa_1A = st.slider("🏆 Note PFA (1A)", 0.0, 20.0, get_val('PFA_2', 14.0), 0.5, key=f"pfa_1a_{widget_key}")
    with p2: modules_nv_1A = st.slider("❌ Modules Non Validés", 0, 12, int(get_val('Modules_Non_Valides', 0)), key=f"mnv_1a_{widget_key}")
    with p3:
        # Redoublant 1A
        st.markdown(f"""
        <div style="background:rgba(22,32,58,0.6); border:1px solid rgba(255,255,255,0.06);
                    border-left: 4px solid {red_1a_col}; border-radius:12px; padding:12px 16px; margin-top:4px;">
            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">🔄 Redoublant 1ère Année</span><br>
            <b style="color:{red_1a_col}; font-size:1rem; font-family:'Poppins';">{red_1a_txt}</b>
        </div>""", unsafe_allow_html=True)

    moy_s1_1A  = round(np.mean([mod1_s1_1A, mod2_s1_1A, mod3_s1_1A, mod4_s1_1A, mod5_s1_1A, ang1_1A, fr1_1A]), 2)
    moy_s2_1A  = round(np.mean([mod1_s2_1A, mod2_s2_1A, mod3_s2_1A, mod4_s2_1A, mod5_s2_1A, ang2_1A, fr2_1A, pfa_1A]), 2)
    moy_ann_1A = round((moy_s1_1A + moy_s2_1A) / 2, 2)

    st.markdown('<div class="section-hdr">Récapitulatif Moyennes</div>', unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    for col, val, label in [(col_m1, moy_s1_1A, "📘 Moyenne S1"), (col_m2, moy_s2_1A, "📗 Moyenne S2"), (col_m3, moy_ann_1A, "🏅 Moyenne Annuelle")]:
        color = "#10b981" if val >= 12 else "#f59e0b" if val >= 10 else "#ef4444"
        pct   = int(val / 20 * 100)
        with col:
            st.markdown(f"""
            <div class="metric-highlight">
                <span style="font-size:0.85rem; color:#94a3b8; font-weight:600;">{label}</span><br>
                <b style="color:{color}; font-size:2.4rem; font-family:'Poppins';">{val}/20</b>
                <div class="progress-bar-container" style="margin-top:12px;">
                    <div class="progress-bar-fill" style="width:{pct}%; background:{color};"></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ─── TAB 2 : 2ème Année ────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📚 Informations 2ème Année")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Semestre 3</div>', unsafe_allow_html=True)
        abs_s1_2A  = st.slider("⏱️ Absences S3 (heures)", 0, 60, int(get_val('Absences_S3', get_val('Absences_S1', 0))), key=f"abs_s1_2a_{widget_key}")
        mod1_s1_2A = st.slider(cur_labels["s3"][0], 0.0, 20.0, get_val('Module_S3_1', get_val('Module_S1_1')), 0.5, key=f"m1s1_2a_{widget_key}")
        mod2_s1_2A = st.slider(cur_labels["s3"][1], 0.0, 20.0, get_val('Module_S3_2', get_val('Module_S1_2')), 0.5, key=f"m2s1_2a_{widget_key}")
        mod3_s1_2A = st.slider(cur_labels["s3"][2], 0.0, 20.0, get_val('Module_S3_3', get_val('Module_S1_3')), 0.5, key=f"m3s1_2a_{widget_key}")
        mod4_s1_2A = st.slider(cur_labels["s3"][3], 0.0, 20.0, get_val('Module_S3_4', get_val('Module_S1_4')), 0.5, key=f"m4s1_2a_{widget_key}")
        mod5_s1_2A = st.slider(cur_labels["s3"][4], 0.0, 20.0, get_val('Module_S3_5', get_val('Module_S1_5')), 0.5, key=f"m5s1_2a_{widget_key}")
        ang1_2A    = st.slider("Anglais Technique S3", 0.0, 20.0, get_val('Anglais_Tech_S3', get_val('Anglais_Tech_1', 13.0)), 0.5, key=f"ang1_2a_{widget_key}")
        fr1_2A     = st.slider("Français Pro. S3",     0.0, 20.0, get_val('Francais_Pro_S3', get_val('Francais_Pro_1', 13.0)), 0.5, key=f"fr1_2a_{widget_key}")

    with c2:
        st.markdown('<div class="section-hdr">Semestre 4</div>', unsafe_allow_html=True)
        abs_s2_2A  = st.slider("⏱️ Absences S4 (heures)", 0, 60, int(get_val('Absences_S4', get_val('Absences_S2', 0))), key=f"abs_s2_2a_{widget_key}")
        mod1_s2_2A = st.slider(cur_labels["s4"][0], 0.0, 20.0, get_val('Module_S4_1', get_val('Module_S2_1')), 0.5, key=f"m1s2_2a_{widget_key}")
        mod2_s2_2A = st.slider(cur_labels["s4"][1], 0.0, 20.0, get_val('Module_S4_2', get_val('Module_S2_2')), 0.5, key=f"m2s2_2a_{widget_key}")
        mod3_s2_2A = st.slider(cur_labels["s4"][2], 0.0, 20.0, get_val('Module_S4_3', get_val('Module_S2_3')), 0.5, key=f"m3s2_2a_{widget_key}")
        mod4_s2_2A = st.slider(cur_labels["s4"][3], 0.0, 20.0, get_val('Module_S4_4', get_val('Module_S2_4')), 0.5, key=f"m4s2_2a_{widget_key}")
        mod5_s2_2A = st.slider(cur_labels["s4"][4], 0.0, 20.0, get_val('Module_S4_5', get_val('Module_S2_5')), 0.5, key=f"m5s2_2a_{widget_key}")
        ang2_2A    = st.slider("Anglais Technique S4", 0.0, 20.0, get_val('Anglais_Tech_S4', get_val('Anglais_Tech_2', 13.0)), 0.5, key=f"ang2_2a_{widget_key}")
        fr2_2A     = st.slider("Français Pro. S4",     0.0, 20.0, get_val('Francais_Pro_S4', get_val('Francais_Pro_2', 13.0)), 0.5, key=f"fr2_2a_{widget_key}")

    p1, p2, p3 = st.columns(3)
    with p1: pfa_2A_v      = st.slider("🏆 Note PFA 2 (2A)", 0.0, 20.0, get_val('PFA_2', 14.0), 0.5, key=f"pfa_2a_{widget_key}")
    with p2: modules_nv_2A = st.slider("❌ Modules Non Validés (2A)", 0, 12, int(get_val('Modules_Non_Valides', 0)), key=f"mnv_2a_{widget_key}")
    with p3:
        # Redoublant 2A
        st.markdown(f"""
        <div style="background:rgba(22,32,58,0.6); border:1px solid rgba(255,255,255,0.06);
                    border-left: 4px solid {red_2a_col}; border-radius:12px; padding:12px 16px; margin-top:4px;">
            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">🔄 Redoublant 2ème Année</span><br>
            <b style="color:{red_2a_col}; font-size:1rem; font-family:'Poppins';">{red_2a_txt}</b>
        </div>""", unsafe_allow_html=True)

# ─── Construction données ───────────────────────────────────────────────────────
etudiant_1A = {
    "Module_S1_1": mod1_s1_1A, "Module_S1_2": mod2_s1_1A, "Module_S1_3": mod3_s1_1A,
    "Module_S1_4": mod4_s1_1A, "Module_S1_5": mod5_s1_1A,
    "Anglais_Tech_1": ang1_1A, "Francais_Pro_1": fr1_1A,
    "Module_S2_1": mod1_s2_1A, "Module_S2_2": mod2_s2_1A, "Module_S2_3": mod3_s2_1A,
    "Module_S2_4": mod4_s2_1A, "Module_S2_5": mod5_s2_1A,
    "Anglais_Tech_2": ang2_1A, "Francais_Pro_2": fr2_1A,
    "PFA_2": pfa_1A,
    "Absences_S1": float(abs_s1_1A), "Absences_S2": float(abs_s2_1A),
    "Redoublant_1A": redoublant_1A, "Redoublant_2A": redoublant_2A, "Redoublant": 1 if (redoublant_1A or redoublant_2A) else 0,
    "Modules_Non_Valides": float(modules_nv_1A),
    "Moyenne_S1": moy_s1_1A, "Moyenne_S2": moy_s2_1A, "Moyenne_Annuelle": moy_ann_1A,
}
etudiant_2A = {
    "Module_S1_1": mod1_s1_2A, "Module_S1_2": mod2_s1_2A, "Module_S1_3": mod3_s1_2A,
    "Module_S1_4": mod4_s1_2A, "Module_S1_5": mod5_s1_2A,
    "Anglais_Tech_1": ang1_2A, "Francais_Pro_1": fr1_2A,
    "Module_S2_1": mod1_s2_2A, "Module_S2_2": mod2_s2_2A, "Module_S2_3": mod3_s2_2A,
    "Module_S2_4": mod4_s2_2A, "Module_S2_5": mod5_s2_2A,
    "Anglais_Tech_2": ang2_2A, "Francais_Pro_2": fr2_2A,
    "PFA_2": pfa_2A_v,
    "Absences_S1": float(abs_s1_2A), "Absences_S2": float(abs_s2_2A),
    "Redoublant_1A": redoublant_1A, "Redoublant_2A": redoublant_2A, "Redoublant": 1 if (redoublant_1A or redoublant_2A) else 0,
    "Modules_Non_Valides": float(modules_nv_2A),
}

# ════════════════════════ TAB 3 : RÉSULTATS ═══════════════════════════════════
with tab3:
    with st.spinner("⚡ Calcul de la prédiction IA en cours..."):
        try:
            from src.ml_models.predict import predict_modules_3A
            res = predict_modules_3A(etudiant_1A, filiere_key, etudiant_2A)
            prediction_ok = True
        except Exception as e:
            st.error(f"❌ Erreur de prédiction : {e}")
            prediction_ok = False

    if prediction_ok:
        statut    = res["statut_global"]
        emoji_map = {"VERT": "✅ SUCCÈS", "JAUNE": "⚠️ À RISQUE", "ROUGE": "❌ ÉCHEC CRITIQUE"}
        css_map   = {"VERT": "statut-vert", "JAUNE": "statut-jaune", "ROUGE": "statut-rouge"}
        desc_map  = {
            "VERT":  "L'étudiant est sur la bonne voie pour valider sa 3ème année.",
            "JAUNE": "Des modules nécessitent une attention particulière.",
            "ROUGE": "Risque élevé d'échec — intervention recommandée.",
        }

        # ── Résultat 1A vs 3A ────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">Bilan Comparatif : 1A Réel vs 3A Prédit</div>', unsafe_allow_html=True)
        reussi_1a_bool = moy_ann_1A >= 12 and modules_nv_1A <= 3 and pfa_1A >= 12
        txt_1a  = "✅ RÉUSSI (Admis)" if reussi_1a_bool else "❌ ÉCHEC (Rattrapage)"
        col_1a  = "#10b981" if reussi_1a_bool else "#ef4444"

        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown(f"""
            <div style="background:rgba(22,32,58,0.6); padding:24px; border-radius:18px;
                        border-top:5px solid {col_1a}; text-align:center;">
                <p style="margin:0; color:#94a3b8; font-size:0.85rem; font-family:'Poppins'; text-transform:uppercase; letter-spacing:2px;">Résultat 1ère Année (Réel)</p>
                <h2 style="color:{col_1a}; margin:12px 0; font-family:'Poppins';">{txt_1a}</h2>
                <p style="color:#94a3b8; margin:0; font-size:0.9rem;">Moy. annuelle : <b style="color:white;">{moy_ann_1A}/20</b> &nbsp;|&nbsp; Modules NV : <b style="color:white;">{int(modules_nv_1A)}</b></p>
            </div>""", unsafe_allow_html=True)

        with c_right:
            st.markdown(f"""
            <div class="{css_map[statut]} statut-box">
                <p style="margin:0; font-size:0.85rem; font-family:'Poppins'; text-transform:uppercase; letter-spacing:2px; opacity:0.85;">Prédiction 3ème Année (IA)</p>
                <h2 style="margin:12px 0; font-family:'Poppins'; font-size:1.8rem;">{emoji_map[statut]}</h2>
                <p style="margin:0; font-size:0.9rem; opacity:0.9;">{res['nb_valides']}/{res['nb_total']} modules validés · {desc_map[statut]}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Notes estimées S5 & PFE ──────────────────────────────────────────
        st.markdown('<div class="section-hdr">Notes Estimées en 3ème Année</div>', unsafe_allow_html=True)
        col_n1, col_n2, col_n3 = st.columns(3)
        s5_color  = "#10b981" if res["note_s5_predite"] >= 12 else "#f59e0b" if res["note_s5_predite"] >= 10 else "#ef4444"
        pfe_color = "#10b981" if res["note_pfe_predite"] >= 12 else "#f59e0b" if res["note_pfe_predite"] >= 10 else "#ef4444"
        pct_val   = int(res['nb_valides'] / max(res['nb_total'], 1) * 100)
        badge_col = "#10b981" if pct_val >= 70 else "#f59e0b" if pct_val >= 40 else "#ef4444"

        with col_n1:
            pct = int(res["note_s5_predite"] / 20 * 100)
            st.markdown(f"""<div class="metric-highlight">
                <span style="font-size:0.85rem; color:#94a3b8; font-weight:600;">📊 Note S5 Estimée</span><br>
                <b style="color:{s5_color}; font-size:2.6rem; font-family:'Poppins';">{res['note_s5_predite']:.1f}/20</b>
                <div class="progress-bar-container"><div class="progress-bar-fill" style="width:{pct}%;background:{s5_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        with col_n2:
            pct = int(res["note_pfe_predite"] / 20 * 100)
            st.markdown(f"""<div class="metric-highlight">
                <span style="font-size:0.85rem; color:#94a3b8; font-weight:600;">🎓 Note PFE Estimée</span><br>
                <b style="color:{pfe_color}; font-size:2.6rem; font-family:'Poppins';">{res['note_pfe_predite']:.1f}/20</b>
                <div class="progress-bar-container"><div class="progress-bar-fill" style="width:{pct}%;background:{pfe_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        with col_n3:
            st.markdown(f"""<div class="metric-highlight">
                <span style="font-size:0.85rem; color:#94a3b8; font-weight:600;">🏅 Modules Validés</span><br>
                <b style="color:{badge_col}; font-size:2.6rem; font-family:'Poppins';">{res['nb_valides']}/{res['nb_total']}</b>
                <div class="progress-bar-container"><div class="progress-bar-fill" style="width:{pct_val}%;background:{badge_col};"></div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align:center; color:#64748b; font-style:italic; margin-top:16px; font-size:0.9rem;'>{res['resume']}</p>", unsafe_allow_html=True)

        # ── Modules 3A détaillés avec progress bar ───────────────────────────
        st.markdown('<div class="section-hdr">Détail des Modules 3ème Année</div>', unsafe_allow_html=True)
        modules = res["modules_3A"]
        n_cols  = 2
        rows    = [list(modules.items())[i:i+n_cols] for i in range(0, len(modules), n_cols)]

        for row in rows:
            cols = st.columns(n_cols)
            for col_idx, (mod_key, mod_res) in enumerate(row):
                with cols[col_idx]:
                    score = mod_res["score_prereq"]
                    if mod_res["valide"]:
                        css_cls = "mod-valide";   icon = "✅"; color = "#10b981"
                    elif score >= 10:
                        css_cls = "mod-marginal"; icon = "⚠️"; color = "#eab308"
                    else:
                        css_cls = "mod-invalide"; icon = "❌"; color = "#f43f5e"

                    proba_pct  = round(mod_res["probabilite"] * 100, 0)
                    status_txt = "VALIDÉ" if mod_res["valide"] else "NON VALIDÉ"
                    score_pct  = int(score / 20 * 100)

                    st.markdown(f"""
                    <div class="module-card {css_cls}">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <b style="color:white; font-size:1rem; font-family:'Poppins';">{icon} {mod_res['label_fr']}</b><br>
                                <span style="color:#64748b; font-size:0.8rem;">{mod_res['raison']}</span>
                            </div>
                            <div style="text-align:right; min-width:90px;">
                                <div class="score-badge" style="color:{color};">{score:.1f}/20</div>
                                <span style="color:{color}; font-size:0.78rem; font-weight:700;">{proba_pct:.0f}% · {status_txt}</span>
                            </div>
                        </div>
                        <div class="progress-bar-container" style="margin-top:12px;">
                            <div class="progress-bar-fill" style="width:{score_pct}%; background: linear-gradient(90deg, {color}88, {color});"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        # ── Graphique + Profil ────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        cl_g, cl_p = st.columns([1.6, 1])

        with cl_g:
            st.markdown('<div class="section-hdr">Scores de Prérequis</div>', unsafe_allow_html=True)
            m_labels = [v["label_fr"] for v in modules.values()]
            m_scores = [v["score_prereq"] for v in modules.values()]
            m_colors = ["#10b981" if v["valide"] else "#f43f5e" if v["score_prereq"] < 10 else "#eab308" for v in modules.values()]

            fig, ax = plt.subplots(figsize=(8, max(3, len(m_labels) * 0.65)), facecolor="#090e1c")
            ax.set_facecolor("#090e1c")
            bars = ax.barh(m_labels, m_scores, color=m_colors, alpha=0.88, height=0.55,
                           edgecolor="none", zorder=2)
            for bar, score in zip(bars, m_scores):
                ax.text(score + 0.3, bar.get_y() + bar.get_height()/2,
                        f"{score:.1f}", va='center', color='white', fontsize=9, fontweight='bold')
            ax.axvline(x=12, color="#818cf8", linestyle="--", linewidth=1.5, alpha=0.8, label="Seuil 12/20", zorder=3)
            ax.set_xlim(0, 22)
            ax.set_xlabel("Score Prérequis (/20)", color="#94a3b8", fontsize=9)
            ax.tick_params(colors="#94a3b8", labelsize=8.5)
            ax.spines[:].set_color("#1e293b")
            ax.grid(axis='x', color='#1e293b', linewidth=0.5, zorder=1)
            ax.legend(loc='lower right', fontsize=8, labelcolor='#94a3b8', facecolor='#090e1c', edgecolor='#1e293b')
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with cl_p:
            st.markdown('<div class="section-hdr">Profil Comportemental</div>', unsafe_allow_html=True)
            p1A     = res["profil_1A"]
            pe      = PROFIL_EMOJI[p1A["score"]]
            pl      = PROFIL_LABELS[p1A["score"]]
            abs_css = "danger-abs" if p1A["danger_abs"] else "safe-abs"
            red_css = "danger-abs" if p1A["danger_red"] else "safe-abs"
            st.markdown(f"""
            <div class="profil-box">
                <h4 style="margin:0 0 4px 0; font-family:'Poppins';">{pe} {pl}</h4>
                <p style="color:#64748b; font-size:0.85rem; margin-bottom:14px;">Total absences 1A : <b style="color:#94a3b8;">{p1A['total_abs']:.0f}h</b></p>
                <div class="{abs_css}">{'⚠️' if p1A['danger_abs'] else '✅'} Absences : {p1A['abs_s1']:.0f}h (S1) + {p1A['abs_s2']:.0f}h (S2)</div>
                <div class="{red_css}">{'⚠️' if p1A['danger_red'] else '✅'} Redoublant : {'Oui' if redoublant_1A else 'Non'}</div>
            </div>""", unsafe_allow_html=True)

            if res["facteurs_risque_3A"]:
                st.markdown("<br><b style='color:#fda4af;'>⚠️ Facteurs de Risque</b>", unsafe_allow_html=True)
                for f in res["facteurs_risque_3A"]:
                    st.markdown(f'<div class="risk-item">{f}</div>', unsafe_allow_html=True)

            if res["recommandations_3A"]:
                st.markdown("<br><b style='color:#a7f3d0;'>💡 Recommandations</b>", unsafe_allow_html=True)
                for r in res["recommandations_3A"]:
                    st.markdown(f'<div class="rec-item">{r}</div>', unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<center><small style='color:#334155;'>🎓 Projet de Fin d'Année (PFA) &nbsp;·&nbsp; Système Intelligent de Prédiction Académique &nbsp;·&nbsp; Interface What-If v3.0</small></center>",
    unsafe_allow_html=True
)
