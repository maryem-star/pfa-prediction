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

    /* ── Advanced Glowing Status Box ── */
    .statut-box {
        border-radius: 26px; padding: 40px 30px; text-align: center;
        color: white; box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        position: relative; overflow: hidden;
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }
    .statut-box:hover { transform: scale(1.02); }
    .statut-box::before {
        content: ''; position: absolute; top:-50%; left:-50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: pulseGlow 4s infinite alternate;
    }
    @keyframes pulseGlow { 0% { opacity: 0.5; transform: scale(0.95); } 100% { opacity: 1; transform: scale(1.05); } }
    
    .glow-vert  { background: linear-gradient(135deg, #059669 0%, #10b981 100%); border: 2px solid #34d399; box-shadow: 0 0 60px rgba(16,185,129,0.25); }
    .glow-jaune { background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); border: 2px solid #fbbf24; box-shadow: 0 0 60px rgba(245,158,11,0.25); }
    .glow-rouge { background: linear-gradient(135deg, #be123c 0%, #e11d48 100%); border: 2px solid #fb7185; box-shadow: 0 0 60px rgba(225,29,72,0.25); }

    /* ── Metric Highlight Enhanced ── */
    .metric-highlight {
        background: rgba(15, 23, 42, 0.8); border-radius: 24px; padding: 32px 20px;
        text-align: center; border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        backdrop-filter: blur(12px);
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-highlight:hover { transform: translateY(-8px); border-color: rgba(255,255,255,0.25); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }

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
    "PFA_1": pfa_1A, "PFA_2": pfa_1A, # PFA_1 explicitement ajouté pour la prédiction PFE
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
        emoji_map = {"VERT": "✅", "JAUNE": "⚠️", "ROUGE": "❌"}
        title_map = {"VERT": "VALIDATION ASSURÉE", "JAUNE": "RISQUE MODÉRÉ", "ROUGE": "ÉCHEC CRITIQUE"}
        css_map   = {"VERT": "glow-vert", "JAUNE": "glow-jaune", "ROUGE": "glow-rouge"}
        desc_map  = {
            "VERT":  "L'étudiant est sur une excellente trajectoire pour valider sa 3ème année brillamment.",
            "JAUNE": "Des modules nécessitent une attention particulière pour éviter un blocage de diplôme.",
            "ROUGE": "Risque majeur — L'étudiant ne réunit pas les prérequis nécessaires pour obtenir son diplôme.",
        }

        # ── Résultat 1A vs 3A ────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">Bilan Comparatif : Passé vs Futur (Prédit)</div>', unsafe_allow_html=True)
        reussi_1a_bool = moy_ann_1A >= 12 and modules_nv_1A <= 3 and pfa_1A >= 12
        txt_1a  = "✅ RÉUSSI (Admis)" if reussi_1a_bool else "❌ ÉCHEC (Rattrapage/Redoublement)"
        col_1a  = "#10b981" if reussi_1a_bool else "#ef4444"

        c_left, empty, c_right = st.columns([1, 0.05, 1.4])
        with c_left:
            st.markdown(f"""
            <div style="background:rgba(22,32,58,0.4); padding:32px; border-radius:24px;
                        border: 1px solid rgba(255,255,255,0.05); border-top:5px solid {col_1a}; 
                        text-align:center; height:100%; display:flex; flex-direction:column; justify-content:center;">
                <p style="margin:0; color:#94a3b8; font-size:0.85rem; font-family:'Poppins'; text-transform:uppercase; letter-spacing:2px;">Bilan 1ère Année (Réel)</p>
                <h2 style="color:{col_1a}; margin:16px 0; font-family:'Poppins'; font-size:1.6rem;">{txt_1a}</h2>
                <div style="background:rgba(0,0,0,0.2); padding:12px; border-radius:12px; display:inline-block; margin:0 auto;">
                    <p style="color:#94a3b8; margin:0; font-size:0.95rem;">Moy. Annuelle : <b style="color:white; font-size:1.1rem;">{moy_ann_1A}/20</b> &nbsp;|&nbsp; NV : <b style="color:white; font-size:1.1rem;">{int(modules_nv_1A)}</b></p>
                </div>
            </div>""", unsafe_allow_html=True)

        with c_right:
            st.markdown(f"""
            <div class="{css_map[statut]} statut-box">
                <p style="margin:0; font-size:0.9rem; font-family:'Poppins'; text-transform:uppercase; letter-spacing:3px; opacity:0.9; text-shadow:0 2px 4px rgba(0,0,0,0.3);">Prédiction PFA & Diapason IA</p>
                <h2 style="margin:16px 0 8px 0; font-family:'Poppins'; font-size:2.2rem; font-weight:800; text-shadow:0 2px 10px rgba(0,0,0,0.4);">
                    <span style="font-size:3rem; vertical-align:middle; margin-right:12px;">{emoji_map[statut]}</span> 
                    {title_map[statut]}
                </h2>
                <div style="background:rgba(0,0,0,0.15); padding:8px 16px; border-radius:20px; display:inline-block; margin-bottom:14px; border:1px solid rgba(255,255,255,0.2);">
                    <b style="font-size:1.1rem; letter-spacing:1px;">{res['nb_valides']}/{res['nb_total']} MODULES PRÉDITS VALIDÉS</b>
                </div>
                <p style="margin:0; font-size:0.98rem; opacity:0.95; line-height:1.5;">{desc_map[statut]}</p>
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
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.08); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:1.5rem; margin-bottom:12px;">📊</div><br>
                <span style="font-size:0.85rem; color:#94a3b8; font-family:'Poppins'; letter-spacing:1px; text-transform:uppercase;">Note S5 Estimée</span><br>
                <b style="color:{s5_color}; font-size:3rem; font-family:'Poppins'; display:block; margin:8px 0; text-shadow:0 0 20px {s5_color}40;">{res['note_s5_predite']:.1f}<span style="font-size:1.2rem;color:#64748b;">/20</span></b>
                <div class="progress-bar-container" style="height:6px;"><div class="progress-bar-fill" style="width:{pct}%;background:{s5_color}; box-shadow:0 0 10px {s5_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        with col_n2:
            pct = int(res["note_pfe_predite"] / 20 * 100)
            st.markdown(f"""<div class="metric-highlight">
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.08); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:1.5rem; margin-bottom:12px;">🎓</div><br>
                <span style="font-size:0.85rem; color:#94a3b8; font-family:'Poppins'; letter-spacing:1px; text-transform:uppercase;">Note PFE Estimée</span><br>
                <b style="color:{pfe_color}; font-size:3rem; font-family:'Poppins'; display:block; margin:8px 0; text-shadow:0 0 20px {pfe_color}40;">{res['note_pfe_predite']:.1f}<span style="font-size:1.2rem;color:#64748b;">/20</span></b>
                <div class="progress-bar-container" style="height:6px;"><div class="progress-bar-fill" style="width:{pct}%;background:{pfe_color}; box-shadow:0 0 10px {pfe_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        with col_n3:
            st.markdown(f"""<div class="metric-highlight">
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.08); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:1.5rem; margin-bottom:12px;">🏅</div><br>
                <span style="font-size:0.85rem; color:#94a3b8; font-family:'Poppins'; letter-spacing:1px; text-transform:uppercase;">Modules Validés</span><br>
                <b style="color:{badge_col}; font-size:3rem; font-family:'Poppins'; display:block; margin:8px 0; text-shadow:0 0 20px {badge_col}40;">{res['nb_valides']}<span style="font-size:1.2rem;color:#64748b;">/{res['nb_total']}</span></b>
                <div class="progress-bar-container" style="height:6px;"><div class="progress-bar-fill" style="width:{pct_val}%;background:{badge_col}; box-shadow:0 0 10px {badge_col};"></div></div>
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
                        css_cls = "mod-valide";   icon = "✅"; color = "#10b981"; bg_color = "rgba(16, 185, 129, 0.05)"
                    elif score >= 10:
                        css_cls = "mod-marginal"; icon = "⚠️"; color = "#f59e0b"; bg_color = "rgba(245, 158, 11, 0.05)"
                    else:
                        css_cls = "mod-invalide"; icon = "❌"; color = "#f43f5e"; bg_color = "rgba(244, 63, 94, 0.05)"

                    proba_pct  = round(mod_res["probabilite"] * 100, 0)
                    status_txt = "VALIDÉ" if mod_res["valide"] else "RATTRAPAGE" if score >= 10 else "NON VALIDÉ"
                    score_pct  = int((score / 20) * 100)

                    st.markdown(f"""
                    <div class="module-card {css_cls}" style="background:{bg_color}; position:relative; overflow:hidden;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                            <div>
                                <b style="color:white; font-size:1.05rem; font-family:'Poppins'; letter-spacing:0.5px;">{icon} {mod_res['label_fr']}</b><br>
                                <span style="color:#94a3b8; font-size:0.85rem;">{mod_res['raison']}</span>
                            </div>
                            <div style="text-align:right; min-width:90px;">
                                <div class="score-badge" style="color:{color}; text-shadow:0 0 10px {color}40;">{score:.1f}<span style="font-size:0.8rem; color:#64748b;">/20</span></div>
                            </div>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Probabilité de réussite</span>
                            <span style="color:{color}; font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:10px;">{proba_pct:.0f}% · {status_txt}</span>
                        </div>
                        <div class="progress-bar-container" style="height:6px; background:rgba(0,0,0,0.2);">
                            <div class="progress-bar-fill" style="width:{score_pct}%; background: linear-gradient(90deg, {color}40, {color}); box-shadow:0 0 10px {color}80;"></div>
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

            st.markdown('<div class="section-hdr">Bilan Personnel & Plan d\'Action</div>', unsafe_allow_html=True)

            p1A = res["profil_1A"]

            if statut == "VERT":
                # Message de motivation pour les bons étudiants
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.02) 100%); 
                            border-radius:20px; padding:32px; border:1px solid rgba(16,185,129,0.2); 
                            box-shadow:0 10px 30px rgba(0,0,0,0.2); margin-bottom:20px;">
                    <h3 style="color:#10b981; font-family:'Poppins'; margin-top:0; font-size:1.6rem;">🌟 Parcours d'Excellence</h3>
                    <p style="color:#e2e8f0; font-size:1.05rem; line-height:1.6; margin-bottom:20px;">
                        Félicitations ! Vos bases académiques sont extrêmement solides. Avec ce rythme, la validation 
                        de votre 3ème année (diplôme) est quasiment assurée. Vous avez une marge de manœuvre suffisante 
                        pour viser une mention d'excellence.
                    </p>
                    <div style="background:rgba(255,255,255,0.05); border-radius:12px; padding:16px;">
                        <b style="color:#a7f3d0; font-size:1.1rem; display:block; margin-bottom:10px;">💡 Conseils pour aller plus loin :</b>
                        <ul style="color:#cbd5e1; margin:0; padding-left:20px; font-size:0.95rem; line-height:1.5;">
                            <li style="margin-bottom:6px;">Commencez dès maintenant à chercher un stage de fin d'études (PFE) stimulant et techniquement challengeant.</li>
                            <li style="margin-bottom:6px;">Impliquez-vous dans des projets parascolaires ou des compétitions pour étoffer votre CV.</li>
                            <li>Explorez les thématiques avancées de votre filière pour anticiper le marché de l'emploi.</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Messages d'alerte et de coaching pour les étudiants à risque
                color_theme  = "#f43f5e" if statut == "ROUGE" else "#f59e0b"
                bg_theme     = "rgba(244,63,94,0.1)" if statut == "ROUGE" else "rgba(245,158,11,0.1)"
                border_theme = "rgba(244,63,94,0.3)" if statut == "ROUGE" else "rgba(245,158,11,0.3)"
                titre        = "🚨 Alerte Académique Majeure" if statut == "ROUGE" else "⚠️ Points de Vigilance"

                # Compilation des alertes personnalisées
                alertes_html = ""
                # 1. Absences
                if p1A["danger_abs"]:
                    alertes_html += f"""
<div style="background:rgba(255,255,255,0.03); border-left:4px solid #f43f5e; padding:12px 16px; border-radius:10px; margin-bottom:10px;">
    <b style="color:#fda4af; display:block; margin-bottom:4px;">⏱️ Assiduité Critique ({p1A['total_abs']:.0f}h d'absence)</b>
    <span style="color:#cbd5e1; font-size:0.9rem;">L'absentéisme est le premier facteur d'échec statitisque en 3A. Il est impératif de réduire vos absences à zéro.</span>
</div>"""
                # 2. Redoublant
                if p1A["danger_red"]:
                     alertes_html += f"""
<div style="background:rgba(255,255,255,0.03); border-left:4px solid #f59e0b; padding:12px 16px; border-radius:10px; margin-bottom:10px;">
    <b style="color:#fcd34d; display:block; margin-bottom:4px;">🔄 Historique de Redoublement</b>
    <span style="color:#cbd5e1; font-size:0.9rem;">Votre statut de redoublant montre des fragilités antérieures. Un suivi rigoureux dès les premières semaines est crucial.</span>
</div>"""
                # 3. Modules fail
                if res["facteurs_risque_3A"] and len(res["modules_non_valides_liste"]) > 0:
                    mods = ", ".join(res["modules_non_valides_liste"])
                    alertes_html += f"""
<div style="background:rgba(255,255,255,0.03); border-left:4px solid {color_theme}; padding:12px 16px; border-radius:10px; margin-bottom:10px;">
    <b style="color:{color_theme}; display:block; margin-bottom:4px;">📚 Lacunes Prérequis Identifiées</b>
    <span style="color:#cbd5e1; font-size:0.9rem;">Vous risquez de bloquer sur les modules suivants : <b>{mods}</b>.</span>
</div>"""

                st.markdown(f"""
<div style="background:linear-gradient(135deg, {bg_theme} 0%, rgba(0,0,0,0.2) 100%); 
            border-radius:20px; padding:32px; border:1px solid {border_theme}; 
            box-shadow:0 10px 30px rgba(0,0,0,0.2); margin-bottom:20px;">
    <h3 style="color:{color_theme}; font-family:'Poppins'; margin-top:0; font-size:1.6rem;">{titre}</h3>
    
    <div style="margin-bottom:24px;">
        <p style="color:#e2e8f0; font-size:1rem; margin-bottom:16px;">
            L'Intelligence Artificielle a détecté des blocages majeurs qui pourraient compromettre l'obtention de votre diplôme. 
            Agissez dès maintenant sur ces points :
        </p>
        {alertes_html}
    </div>

    <div style="background:rgba(0,0,0,0.3); border-radius:12px; padding:16px; border-top:2px solid {color_theme};">
        <b style="color:#e2e8f0; font-size:1.05rem; display:block; margin-bottom:12px;">🛠️ Plan d'Action Recommandé :</b>
        <ul style="color:#cbd5e1; margin:0; padding-left:20px; font-size:0.95rem; line-height:1.6;">
            <li style="margin-bottom:6px;"><b>Révision intensive:</b> Reprenez les cours des modules 1A/2A qui bloquent en 3A.</li>
            <li style="margin-bottom:6px;"><b>Tutorat:</b> Demandez de l'aide à vos enseignants ou camarades sur les concepts fondamentaux non acquis.</li>
            <li><b>Assiduité stricte:</b> Ne manquez aucune séance de TD/TP cette année.</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<center><small style='color:#334155;'>🎓 Projet de Fin d'Année (PFA) &nbsp;·&nbsp; Système Intelligent de Prédiction Académique &nbsp;·&nbsp; Interface What-If v3.0</small></center>",
    unsafe_allow_html=True
)
