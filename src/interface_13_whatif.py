"""
Interface 13 — Prédiction Intelligente des Modules 3ème Année avec Données Réelles
==================================================================================

Améliorations apportées :
1. Menu déroulant pour filtrer par filière
2. Menu déroulant pour choisir un étudiant réel dans cette filière
3. Les notes et absences se mettent à jour automatiquement dans les sliders
4. Amélioration du design (police Montserrat, couleurs dynamiques, glassmorphism)
5. Résultat Global affiché clairement (Réussi/Échec 1A vs Prédiction 3A)
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
    page_title="Prédiction 3ème Année — Données Réelles",
    page_icon="🎓",
    layout="wide",
)

# ─── DESIGN & TYPOGRAPHY ──────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
    }
    .main { 
        background: radial-gradient(circle at 10% 20%, #0c1222 0%, #060913 100%);
        color: #f1f5f9;
    }
    
    .title-main {
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #e879f9);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        text-align: center;
        padding-top: 1.5rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle { 
        color: #94a3b8; margin-bottom: 2.5rem; font-size: 1.15rem; 
        text-align: center; font-weight: 400; font-family: 'Outfit', sans-serif;
    }
    
    .section-hdr {
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem; font-weight: 700; color: #818cf8;
        text-transform: uppercase; letter-spacing: 2px;
        margin: 2rem 0 1rem 0; border-bottom: 1px solid rgba(129, 140, 248, 0.2); 
        padding-bottom: 10px;
    }
    
    .module-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.03);
        border-radius: 16px; padding: 16px 20px; margin: 10px 0;
        display: flex; justify-content: space-between; align-items: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .module-card:hover { 
        transform: translateY(-4px) scale(1.01); 
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04); 
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .mod-valide   { border-left: 6px solid #10b981; }
    .mod-invalide { border-left: 6px solid #f43f5e; }
    .mod-marginal { border-left: 6px solid #eab308; }
    
    .score-badge { font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 800; }
    
    .statut-box {
        border-radius: 24px; padding: 35px; text-align: center;
        color: white; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3);
        position: relative; overflow: hidden;
    }
    .statut-vert  { background: linear-gradient(135deg, #059669 0%, #10b981 100%); border: 1px solid rgba(255,255,255,0.2); }
    .statut-jaune { background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); border: 1px solid rgba(255,255,255,0.2); }
    .statut-rouge { background: linear-gradient(135deg, #be123c 0%, #e11d48 100%); border: 1px solid rgba(255,255,255,0.2); }
    
    .risk-item  { 
        background: rgba(244, 63, 94, 0.1); border-left: 4px solid #f43f5e; 
        padding: 14px 18px; border-radius: 12px; margin: 10px 0; color: #fda4af; font-weight: 500;
    }
    .rec-item   { 
        background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; 
        padding: 14px 18px; border-radius: 12px; margin: 10px 0; color: #a7f3d0; font-weight: 500;
    }
    
    .profil-box { 
        background: rgba(30, 41, 59, 0.4); border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px; padding: 20px; margin-top: 16px; 
    }
    .danger-abs { background: rgba(244, 63, 94, 0.15); border: 1px dashed #f43f5e; border-radius: 10px; padding: 10px 14px; color: #fda4af; font-weight: 600; }
    .safe-abs   { background: rgba(16, 185, 129, 0.15); border: 1px dashed #10b981; border-radius: 10px; padding: 10px 14px; color: #6ee7b7; font-weight: 600; }
    
    .metric-highlight { 
        background: rgba(15, 23, 42, 0.6); border-radius: 16px; padding: 24px; text-align: center; 
        border: 1px solid rgba(255,255,255,0.03);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-highlight:hover { transform: translateY(-5px); }
    
    /* Onglets Custom */
    .stTabs [data-baseweb="tab"] { font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 600; }
    .stTabs [aria-selected="true"] { color: #818cf8 !important; }
    
    .student-selector {
        background: rgba(30, 41, 59, 0.5); padding: 24px; border-radius: 16px; margin-bottom: 24px;
        border: 1px solid rgba(129, 140, 248, 0.3); box-shadow: 0 0 20px rgba(129, 140, 248, 0.1);
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_PATH = os.path.join(BASE_DIR, "models")
DATA_PATH   = os.path.join(BASE_DIR, "data", "processed", "students_clean.csv")

FILIERES = {
    "ITE — Génie Info":              "ite",
    "ISIC":                          "isic",
    "CCN — Cybersécurité":           "ccn",
    "GEE — Génie Électrique":        "gee",
    "Génie Civil":                   "civil",
    "Génie Industriel":              "industriel",
}

PROFIL_EMOJI  = {0: "🟢", 1: "🔵", 2: "🟡", 3: "🔴"}
PROFIL_LABELS = {0: "Très assidu", 1: "Assidu", 2: "Préoccupant", 3: "Absentéiste chronique"}

# ─── CHARGEMENT DES DONNÉES ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        return df
    return None

df_students = load_data()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown('<div class="title-main">🎓 Prédiction Intelligente 3ème Année</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Sélectionnez un étudiant réel depuis sa filière pour voir ses prédictions modules S5 et PFE. '
    'Vous pouvez ajuster les notes pour voir l\'impact en temps réel (What-If).</div>',
    unsafe_allow_html=True
)

if df_students is None or df_students.empty:
    st.error("Aucune donnée d'étudiant trouvée. Vérifiez que la pipeline de données a été exécutée.")
    st.stop()

# ─── SELECTION ETUDIANT (Top Bar) ──────────────────────────────────────────────
st.markdown('<div class="student-selector">', unsafe_allow_html=True)
c_fil, c_etud = st.columns([1, 2])
with c_fil:
    st.markdown("**1. Choisissez la filière**")
    fil_label    = st.selectbox("Filière", list(FILIERES.keys()), label_visibility="collapsed")
    filiere_key  = FILIERES[fil_label]

# Filtrer les étudiants de la filière
df_fil = df_students[df_students['Filiere'].str.contains(filiere_key, case=False, na=False)]
if df_fil.empty:
    df_fil = df_students # Fallback

with c_etud:
    st.markdown("**2. Choisissez l'étudiant**")
    
    # Créer une liste lisible pour le menu déroulant
    student_options = []
    student_dict = {}
    for _, row in df_fil.iterrows():
        cne = row.get('CNE', 'INCONNU')
        nom = row.get('Nom', '')
        prenom = row.get('Prenom', '')
        label = f"{cne} - {nom} {prenom}"
        student_options.append(label)
        student_dict[label] = row
                       
    selected_student_label = st.selectbox("Étudiant", student_options, label_visibility="collapsed")
    selected_student_data = student_dict[selected_student_label]

st.markdown('</div>', unsafe_allow_html=True)

# Clé unique pour forcer le re-rendu des widgets (sliders) lors d'un changement d'étudiant
widget_key = str(selected_student_data.get('CNE', 'INCONNU'))

# ─── Sidebar ─────────────────────────────────────────────────────────────────
a2_dispo = True  # Simulation 2A toujours active

with st.sidebar:
    st.success(f"**Étudiant sélectionné :**\n\n{selected_student_label}")
    st.info("💡 **Mode What-If** : \nModifiez les sliders pour voir l'impact immédiat sur la prédiction.")

# ─── ETAT INITIAL DES SLIDERS ────────────────────────────────────────────────
# On lit les données réelles pour pépépler les sliders par défaut
def get_val(col_name, default=12.0):
    val = selected_student_data.get(col_name, default)
    if pd.isna(val): return float(default)
    return float(val)

# ─── Onglets principaux ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📋 Données 1ère Année",
    "📋 Données 2ème Année" if a2_dispo else "📋 2ème Année (désactivé)",
    "🔮 Résultats & Prédiction 3A"
])

# ─── NOMS DES MODULES PAR FILIERE ──────────────────────────────────────────
# Mapping dynamique pour affichage
mod_labels = {
    "ite": {
        "s1": ["Maths 1 / Prog C", "Physique / Algo", "Architecture Numérique", "Électronique S1", "Systèmes S1"],
        "s2": ["Maths 2 / Avancé", "POO C++", "Réseaux S2", "Mécanique / Thermo", "Compilation S2"],
        "s3": ["Maths 3 / Oracles", "Java Avancé", "Bases de Données", "Analyse S3", "Génie Logiciel S3"],
        "s4": ["Web S4", "Réseau Avancé S4", "UML / Conception", "Système d'Exploitation", "Management S4"]
    },
    "isic": {
        "s1": ["Maths 1", "Physique S1", "Management", "Electronique", "Info S1"],
        "s2": ["Maths 2", "Physique S2", "Réseaux S2", "Ondes", "POO S2"],
        "s3": ["Maths 3", "Architecture Réseaux", "Signaux", "Télécoms S3", "Génie Logiciel"],
        "s4": ["Systèmes Répartis", "Traitement d'Image", "Sécurité", "Routage S4", "Management"]
    },
    "ccn": {
        "s1": ["Maths 1 / Cyber", "Physique S1", "Architecture", "Réseaux de Base", "Systèmes S1"],
        "s2": ["Maths 2 / Crypto", "POO / Scripting", "Réseaux Locaux", "Système Linux", "Télécoms"],
        "s3": ["Maths 3 / Proba", "Administration Sécurité", "Vulnérabilités", "Python Avancé", "Droit Cyber"],
        "s4": ["Sécurité Avancée", "IoT & Sécurité", "Forensique Numérique", "Pentesting S4", "Management"]
    },
    "gee": {
        "s1": ["Maths 1", "Mécanique du Point", "Machines Électriques 1", "Électronique S1", "Thermo S1"],
        "s2": ["Maths 2", "Mécanique du Solide", "Machines Électriques 2", "Automatique", "Dessin Industriel"],
        "s3": ["Maths 3", "Réseaux Électriques", "Électronique de Puissance", "Énergies Renouvelables", "Automatisme S3"],
        "s4": ["Gestion d'Énergie", "Capteurs S4", "Traitement de Signal", "Informatique Indust.", "Management"]
    },
    "civil": {
        "s1": ["Maths 1", "Mécanique S1", "Matériaux 1", "Dessin Civil S1", "Géologie S1"],
        "s2": ["Maths 2", "RDM S2", "Hydro S2", "Matériaux 2", "Topographie"],
        "s3": ["Maths 3", "Béton Armé 1", "Mécanique des Sols", "Hydraulique S3", "BIM S3"],
        "s4": ["Béton Armé 2", "Ouvrages d'Art", "Thermique Bâtiment", "Voiries S4", "Management"]
    },
    "industriel": {
        "s1": ["Maths 1", "Physique S1", "Procédés de Fab 1", "Dessin Industriel", "Matériaux"],
        "s2": ["Maths 2", "Recherche Opérationnelle", "Procédés de Fab 2", "Mécanique S2", "Informatique"],
        "s3": ["Maths 3", "CAO / PAO", "Gestion de Produit", "Automatique S3", "Qualité S3"],
        "s4": ["Logistique S4", "Gestion de Maintenance", "Lean Management", "Systèmes Indust.", "Management"]
    }
}
# Fallback sécurisé
cur_labels = mod_labels.get(filiere_key, mod_labels["ite"])

# ════════════════════════ TAB 1: Données 1A ══════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Semestre 1</div>', unsafe_allow_html=True)
        abs_s1_1A   = st.slider("Absences S1 (heures)", 0, 60, int(get_val('Absences_S1', 0)), key=f"abs_s1_1a_{widget_key}")
        mod1_s1_1A  = st.slider(cur_labels["s1"][0], 0.0, 20.0, get_val('Module_S1_1'), 0.5, key=f"m1s1_1a_{widget_key}")
        mod2_s1_1A  = st.slider(cur_labels["s1"][1], 0.0, 20.0, get_val('Module_S1_2'), 0.5, key=f"m2s1_1a_{widget_key}")
        mod3_s1_1A  = st.slider(cur_labels["s1"][2], 0.0, 20.0, get_val('Module_S1_3'), 0.5, key=f"m3s1_1a_{widget_key}")
        mod4_s1_1A  = st.slider(cur_labels["s1"][3], 0.0, 20.0, get_val('Module_S1_4'), 0.5, key=f"m4s1_1a_{widget_key}")
        mod5_s1_1A  = st.slider(cur_labels["s1"][4], 0.0, 20.0, get_val('Module_S1_5'), 0.5, key=f"m5s1_1a_{widget_key}")
        ang1_1A     = st.slider("Anglais Technique 1", 0.0, 20.0, get_val('Anglais_Tech_1', 13.0), 0.5, key=f"ang1_1a_{widget_key}")
        fr1_1A      = st.slider("Français Professionnel 1", 0.0, 20.0, get_val('Francais_Pro_1', 13.0), 0.5, key=f"fr1_1a_{widget_key}")

    with c2:
        st.markdown('<div class="section-hdr">Semestre 2</div>', unsafe_allow_html=True)
        abs_s2_1A   = st.slider("Absences S2 (heures)", 0, 60, int(get_val('Absences_S2', 0)), key=f"abs_s2_1a_{widget_key}")
        mod1_s2_1A  = st.slider(cur_labels["s2"][0], 0.0, 20.0, get_val('Module_S2_1'), 0.5, key=f"m1s2_1a_{widget_key}")
        mod2_s2_1A  = st.slider(cur_labels["s2"][1], 0.0, 20.0, get_val('Module_S2_2'), 0.5, key=f"m2s2_1a_{widget_key}")
        mod3_s2_1A  = st.slider(cur_labels["s2"][2], 0.0, 20.0, get_val('Module_S2_3'), 0.5, key=f"m3s2_1a_{widget_key}")
        mod4_s2_1A  = st.slider(cur_labels["s2"][3], 0.0, 20.0, get_val('Module_S2_4'), 0.5, key=f"m4s2_1a_{widget_key}")
        mod5_s2_1A  = st.slider(cur_labels["s2"][4], 0.0, 20.0, get_val('Module_S2_5'), 0.5, key=f"m5s2_1a_{widget_key}")
        ang2_1A     = st.slider("Anglais Technique 2", 0.0, 20.0, get_val('Anglais_Tech_2', 13.0), 0.5, key=f"ang2_1a_{widget_key}")
        fr2_1A      = st.slider("Français Professionnel 2", 0.0, 20.0, get_val('Francais_Pro_2', 13.0), 0.5, key=f"fr2_1a_{widget_key}")

    st.markdown('<div class="section-hdr">Évaluation Annuelle (Réelle)</div>', unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1: 
        pfa_1A = st.slider("Note PFA (1A)", 0.0, 20.0, get_val('PFA_2', 14.0), 0.5, key=f"pfa_1a_{widget_key}")
    with p2: 
        modules_nv_1A = st.slider("Modules Non Validés (1A)", 0, 12, int(get_val('Modules_Non_Valides', 0)), key=f"mnv_1a_{widget_key}")
    with p3: 
        redoublant_1A = 1 if st.checkbox("Redoublant 1A", value=bool(get_val('Redoublant', 0)), key=f"red_1a_{widget_key}") else 0

    moy_s1_1A = round(np.mean([mod1_s1_1A, mod2_s1_1A, mod3_s1_1A, mod4_s1_1A, mod5_s1_1A, ang1_1A, fr1_1A]), 2)
    moy_s2_1A = round(np.mean([mod1_s2_1A, mod2_s2_1A, mod3_s2_1A, mod4_s2_1A, mod5_s2_1A, ang2_1A, fr2_1A, pfa_1A]), 2)
    moy_ann_1A = round((moy_s1_1A + moy_s2_1A) / 2, 2)

    col_m1, col_m2, col_m3 = st.columns(3)
    c1v = "#10b981" if moy_s1_1A >= 12 else "#f59e0b" if moy_s1_1A >= 10 else "#ef4444"
    c2v = "#10b981" if moy_s2_1A >= 12 else "#f59e0b" if moy_s2_1A >= 10 else "#ef4444"
    c3v = "#10b981" if moy_ann_1A >= 12 else "#f59e0b" if moy_ann_1A >= 10 else "#ef4444"
    with col_m1: st.markdown(f"<div class='metric-highlight'>Moyenne S1 act.<br><b style='color:{c1v};font-size:1.6rem'>{moy_s1_1A}/20</b></div>", unsafe_allow_html=True)
    with col_m2: st.markdown(f"<div class='metric-highlight'>Moyenne S2 act.<br><b style='color:{c2v};font-size:1.6rem'>{moy_s2_1A}/20</b></div>", unsafe_allow_html=True)
    with col_m3: st.markdown(f"<div class='metric-highlight'>Moy. Annuelle act.<br><b style='color:{c3v};font-size:1.6rem'>{moy_ann_1A}/20</b></div>", unsafe_allow_html=True)

# ════════════════════════ TAB 2: Données 2A ══════════════════════════════════
with tab2:
    if not a2_dispo:
        st.info("ℹ️ Vous n'avez pas activé les données de 2ème année. Le système utilise les données de 1ère année comme références (proxy) avec une pénalités pour prédire le comportement 3A.")
        # Valeurs par défaut
        abs_s1_2A = abs_s1_1A; abs_s2_2A = abs_s2_1A
        mod1_s1_2A = mod1_s1_1A; mod2_s1_2A = mod2_s1_1A; mod3_s1_2A = mod3_s1_1A
        mod4_s1_2A = mod4_s1_1A; mod5_s1_2A = mod5_s1_1A
        ang1_2A = ang1_1A; fr1_2A = fr1_1A
        mod1_s2_2A = mod1_s2_1A; mod2_s2_2A = mod2_s2_1A; mod3_s2_2A = mod3_s2_1A
        mod4_s2_2A = mod4_s2_1A; mod5_s2_2A = mod5_s2_1A
        ang2_2A = ang2_1A; fr2_2A = fr2_1A
        pfa_2A_v = pfa_1A; modules_nv_2A = modules_nv_1A; redoublant_2A = 0
    else:
        st.markdown("### 📚 Informations 2ème Année")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-hdr">Semestre 3</div>', unsafe_allow_html=True)
            abs_s1_2A   = st.slider("Absences S3 (heures)", 0, 60, int(get_val('Absences_S1', 0)), key=f"abs_s1_2a_{widget_key}")
            mod1_s1_2A  = st.slider(cur_labels["s3"][0], 0.0, 20.0, get_val('Module_S1_1'), 0.5, key=f"m1s1_2a_{widget_key}")
            mod2_s1_2A  = st.slider(cur_labels["s3"][1], 0.0, 20.0, get_val('Module_S1_2'), 0.5, key=f"m2s1_2a_{widget_key}")
            mod3_s1_2A  = st.slider(cur_labels["s3"][2], 0.0, 20.0, get_val('Module_S1_3'), 0.5, key=f"m3s1_2a_{widget_key}")
            mod4_s1_2A  = st.slider(cur_labels["s3"][3], 0.0, 20.0, get_val('Module_S1_4'), 0.5, key=f"m4s1_2a_{widget_key}")
            mod5_s1_2A  = st.slider(cur_labels["s3"][4], 0.0, 20.0, get_val('Module_S1_5'), 0.5, key=f"m5s1_2a_{widget_key}")
            ang1_2A     = st.slider("Anglais Technique S3", 0.0, 20.0, get_val('Anglais_Tech_1', 13.0), 0.5, key=f"ang1_2a_{widget_key}")
            fr1_2A      = st.slider("Français Pro. S3", 0.0, 20.0, get_val('Francais_Pro_1', 13.0), 0.5, key=f"fr1_2a_{widget_key}")

        with c2:
            st.markdown('<div class="section-hdr">Semestre 4</div>', unsafe_allow_html=True)
            abs_s2_2A   = st.slider("Absences S4 (heures)", 0, 60, int(get_val('Absences_S2', 0)), key=f"abs_s2_2a_{widget_key}")
            mod1_s2_2A  = st.slider(cur_labels["s4"][0], 0.0, 20.0, get_val('Module_S2_1'), 0.5, key=f"m1s2_2a_{widget_key}")
            mod2_s2_2A  = st.slider(cur_labels["s4"][1], 0.0, 20.0, get_val('Module_S2_2'), 0.5, key=f"m2s2_2a_{widget_key}")
            mod3_s2_2A  = st.slider(cur_labels["s4"][2], 0.0, 20.0, get_val('Module_S2_3'), 0.5, key=f"m3s2_2a_{widget_key}")
            mod4_s2_2A  = st.slider(cur_labels["s4"][3], 0.0, 20.0, get_val('Module_S2_4'), 0.5, key=f"m4s2_2a_{widget_key}")
            mod5_s2_2A  = st.slider(cur_labels["s4"][4], 0.0, 20.0, get_val('Module_S2_5'), 0.5, key=f"m5s2_2a_{widget_key}")
            ang2_2A     = st.slider("Anglais Technique S4", 0.0, 20.0, get_val('Anglais_Tech_2', 13.0), 0.5, key=f"ang2_2a_{widget_key}")
            fr2_2A      = st.slider("Français Pro. S4", 0.0, 20.0, get_val('Francais_Pro_2', 13.0), 0.5, key=f"fr2_2a_{widget_key}")

        p1, p2, p3 = st.columns(3)
        with p1: pfa_2A_v     = st.slider("Note PFA 2 (2A)", 0.0, 20.0, get_val('PFA_2', 14.0), 0.5, key=f"pfa_2a_{widget_key}")
        with p2: modules_nv_2A = st.slider("Modules Non Validés (2A)", 0, 12, int(get_val('Modules_Non_Valides', 0)), key=f"mnv_2a_{widget_key}")
        with p3: redoublant_2A = 1 if st.checkbox("Redoublant 2A", value=bool(get_val('Redoublant', 0)), key=f"red_2a_{widget_key}") else 0

# ─── Construction DATA ───────────────────────────────────────────────────────
etudiant_1A = {
    "Module_S1_1": mod1_s1_1A, "Module_S1_2": mod2_s1_1A, "Module_S1_3": mod3_s1_1A, "Module_S1_4": mod4_s1_1A, "Module_S1_5": mod5_s1_1A,
    "Anglais_Tech_1": ang1_1A, "Francais_Pro_1": fr1_1A,
    "Module_S2_1": mod1_s2_1A, "Module_S2_2": mod2_s2_1A, "Module_S2_3": mod3_s2_1A, "Module_S2_4": mod4_s2_1A, "Module_S2_5": mod5_s2_1A,
    "Anglais_Tech_2": ang2_1A, "Francais_Pro_2": fr2_1A,
    "PFA_2": pfa_1A,
    "Absences_S1": float(abs_s1_1A), "Absences_S2": float(abs_s2_1A),
    "Redoublant": redoublant_1A, "Modules_Non_Valides": float(modules_nv_1A),
    "Moyenne_S1": moy_s1_1A, "Moyenne_S2": moy_s2_1A, "Moyenne_Annuelle": moy_ann_1A,
}

etudiant_2A = None
if a2_dispo:
    etudiant_2A = {
        "Module_S1_1": mod1_s1_2A, "Module_S1_2": mod2_s1_2A, "Module_S1_3": mod3_s1_2A, "Module_S1_4": mod4_s1_2A, "Module_S1_5": mod5_s1_2A,
        "Anglais_Tech_1": ang1_2A, "Francais_Pro_1": fr1_2A,
        "Module_S2_1": mod1_s2_2A, "Module_S2_2": mod2_s2_2A, "Module_S2_3": mod3_s2_2A, "Module_S2_4": mod4_s2_2A, "Module_S2_5": mod5_s2_2A,
        "Anglais_Tech_2": ang2_2A, "Francais_Pro_2": fr2_2A,
        "PFA_2": pfa_2A_v, "Absences_S1": float(abs_s1_2A), "Absences_S2": float(abs_s2_2A),
        "Redoublant": redoublant_2A, "Modules_Non_Valides": float(modules_nv_2A),
    }

# ════════════════════════ TAB 3: RÉSULTATS ════════════════════════════════════
with tab3:
    with st.spinner("Calcul de la prédiction intelligente..."):
        try:
            from src.ml_models.predict import predict_modules_3A
            res = predict_modules_3A(etudiant_1A, filiere_key, etudiant_2A)
            prediction_ok = True
        except Exception as e:
            st.error(f"Erreur de prédiction: {e}")
            prediction_ok = False

    if prediction_ok:
        # ── RESULTAT DE 1A (REEL) VS 3A (PREDICTION) ──────────────────────────
        st.markdown('<div class="section-hdr">État du passage d\'année</div>', unsafe_allow_html=True)
        
        # Réel 1A
        reussi_1a_bool = moy_ann_1A >= 12 and modules_nv_1A <= 3 and pfa_1A >= 12
        txt_1a = "✅ RÉUSSI (Admis)" if reussi_1a_bool else "❌ ÉCHEC (Rattrapage/Redoublement)"
        col_1a = "#10b981" if reussi_1a_bool else "#ef4444"
        
        # Prédit 3A
        statut = res["statut_global"]
        emoji_map = {"VERT": "✅ SUCCÈS", "JAUNE": "⚠️ À RISQUE", "ROUGE": "❌ ÉCHEC CRITIQUE"}
        css_map   = {"VERT": "statut-vert", "JAUNE": "statut-jaune", "ROUGE": "statut-rouge"}
        
        c_1a, c_3a = st.columns(2)
        with c_1a:
            st.markdown(f"""
            <div style="background: rgba(30,41,59,0.5); padding: 20px; border-radius: 15px; border-top: 5px solid {col_1a}; text-align: center;">
                <h3 style="margin:0; font-family:'Outfit';">Résultat 1ère Année (Réel)</h3>
                <h1 style="color:{col_1a}; margin:10px 0;">{txt_1a}</h1>
                <p style="color:#94a3b8; margin:0;">Moyenne: {moy_ann_1A}/20 | Modules NV: {int(modules_nv_1A)}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with c_3a:
            # Case cachée pour le résultat global
            with st.expander("👁️ Cliquer ici pour voir le Résultat Global de Prédiction 3A", expanded=False):
                st.markdown(f"""
                <div class="{css_map[statut]} statut-box">
                    <h3 style="margin:0; font-family:'Outfit';">Prédiction 3ème Année</h3>
                    <h1 style="color:white; margin:10px 0;">{emoji_map[statut]}</h1>
                    <p style="margin:0;">{res['nb_valides']}/{res['nb_total']} modules validés en S5/S6</p>
                </div>
                """, unsafe_allow_html=True)


        st.markdown("<br><br>", unsafe_allow_html=True)

        # ── Notes estimées S5 et PFE ──────────────────────────────────────────
        col_notes1, col_notes2 = st.columns(2)
        s5_color  = "#10b981" if res["note_s5_predite"] >= 12 else "#f59e0b" if res["note_s5_predite"] >= 10 else "#ef4444"
        pfe_color = "#10b981" if res["note_pfe_predite"] >= 12 else "#f59e0b" if res["note_pfe_predite"] >= 10 else "#ef4444"
        with col_notes1:
            st.markdown(f"""
            <div class="metric-highlight">
                <span style="font-size:1.1rem; color:#94a3b8; font-weight:600;">📊 Note S5 Estimée</span><br>
                <b style="color:{s5_color}; font-size:2.8rem; font-family:'Outfit';">{res['note_s5_predite']:.1f}/20</b>
            </div>""", unsafe_allow_html=True)
        with col_notes2:
            st.markdown(f"""
            <div class="metric-highlight">
                <span style="font-size:1.1rem; color:#94a3b8; font-weight:600;">🎓 Note PFE Estimée</span><br>
                <b style="color:{pfe_color}; font-size:2.8rem; font-family:'Outfit';">{res['note_pfe_predite']:.1f}/20</b>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align:center; color:#94a3b8; font-style:italic; margin-top:20px;'>{res['resume']}</p>", unsafe_allow_html=True)

        # ── Modules 3A détaillés ──────────────────────────────────────────────
        st.markdown('<div class="section-hdr">Détail des Modules 3ème Année (Prédiction)</div>', unsafe_allow_html=True)
        modules = res["modules_3A"]
        n_cols = 2
        rows = [list(modules.items())[i:i+n_cols] for i in range(0, len(modules), n_cols)]

        for row in rows:
            cols = st.columns(n_cols)
            for col_idx, (mod_key, mod_res) in enumerate(row):
                with cols[col_idx]:
                    score = mod_res["score_prereq"]
                    if mod_res["valide"]:
                        css_cls = "mod-valide"; icon = "✅"; color = "#10b981"
                    elif score >= 10:
                        css_cls = "mod-marginal"; icon = "⚠️"; color = "#f59e0b"
                    else:
                        css_cls = "mod-invalide"; icon = "❌"; color = "#ef4444"

                    proba_pct = round(mod_res["probabilite"] * 100, 0)
                    status_txt = "VALIDÉ" if mod_res["valide"] else "NON VALIDÉ"
                    
                    st.markdown(f"""
                    <div class="module-card {css_cls}">
                        <div>
                            <b style="color:white; font-size:1.1rem;">{icon} {mod_res['label_fr']}</b><br>
                            <span style="color:#94a3b8; font-size:0.85rem;">{mod_res['raison']}</span>
                        </div>
                        <div style="text-align:right">
                            <div class="score-badge" style="color:{color}">{score:.1f}/20</div>
                            <span style="color:{color}; font-size:0.85rem; font-weight:bold;">{proba_pct:.0f}% — {status_txt}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


        # ── Profil comportemental + Graphique radar ───────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        cl_g, cl_p = st.columns([1.5, 1])
        
        with cl_g:
            st.markdown('<div class="section-hdr">Scores de Prérequis par Module</div>', unsafe_allow_html=True)
            mod_labels = [v["label_fr"] for v in modules.values()]
            mod_scores = [v["score_prereq"] for v in modules.values()]
            mod_colors = ["#10b981" if v["valide"] else "#ef4444" for v in modules.values()]

            fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0a0e1a")
            ax.set_facecolor("#0a0e1a")
            bars = ax.barh(mod_labels, mod_scores, color=mod_colors, alpha=0.9, height=0.6)
            ax.axvline(x=12, color="#f59e0b", linestyle="--", linewidth=2, label="Seuil (12/20)")
            ax.set_xlim(0, 20)
            ax.set_xlabel("Score Prérequis (/20)", color="white", fontsize=10, family="sans-serif")
            ax.tick_params(colors="white", labelsize=9)
            ax.spines[:].set_color("#1e293b")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with cl_p:
            st.markdown('<div class="section-hdr">Profil Comportemental</div>', unsafe_allow_html=True)
            p1A = res["profil_1A"]
            pe = PROFIL_EMOJI[p1A["score"]]
            pl = PROFIL_LABELS[p1A["score"]]
            abs_css = "danger-abs" if p1A["danger_abs"] else "safe-abs"
            red_css = "danger-abs" if p1A["danger_red"] else "safe-abs"
            st.markdown(f"""
            <div class="profil-box">
                <h4 style="margin:0; font-family:'Outfit';">{pe} {pl}</h4>
                <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:15px;">Total absences 1A : {p1A['total_abs']:.0f}h</p>
                
                <div class="{abs_css}">
                    {'⚠️' if p1A['danger_abs'] else '✅'} Absences: {p1A['abs_s1']:.0f}h (S1) + {p1A['abs_s2']:.0f}h (S2)
                </div>
                <div class="{red_css}" style="margin-top:10px">
                    {'⚠️' if p1A['danger_red'] else '✅'} Redoublant: {'Oui' if redoublant_1A else 'Non'}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if len(res["facteurs_risque_3A"]) > 0:
                st.markdown("<br><b>Facteurs de Risque :</b>", unsafe_allow_html=True)
                for f in res["facteurs_risque_3A"]:
                    st.markdown(f'<div class="risk-item">⚠️ {f}</div>', unsafe_allow_html=True)
                    
            if len(res["recommandations_3A"]) > 0:
                st.markdown("<br><b>Recommandations :</b>", unsafe_allow_html=True)
                for r in res["recommandations_3A"]:
                    st.markdown(f'<div class="rec-item">💡 {r}</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<center><small style='color:#64748b;'>Projet de Fin d'Année (PFA) — Système Intelligent de Prédiction Academic | "
    "Interface 13 V2.0</small></center>",
    unsafe_allow_html=True
)
