"""
Interface 13 â€” Prediction Intelligente des Modules 3eme Annee avec Donnees Reelles
==================================================================================

Ameliorations v4 (Diagnostic des Causes d'Echec) :

Ameliorations v3 :
1. Sidebar enrichie avec mini-KPIs et resume etudiant
2. Progress bars animees pour chaque module 3A
3. Affichage du Resultat Global visible directement (sans expander)
4. Compteur de modules valides sous forme de badge visuel
5. Meilleur design CSS : glassmorphism ameliore, animations, Poppins
8. NOUVEAU: Section "Diagnostic & Analyse" des causes d'echec
9. NOUVEAU: Analyse automatique des donnees reelles (notes, absences, patterns)
10. NOUVEAU: Cartes visuelles par cause avec severite
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
    page_title="Prediction 3eme Annee - Analyse What-If",
    page_icon="W",
    layout="wide",
)

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ DESIGN & CSS ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* ====== FOND JAUNE & VERT - GLOBAL ====== */
    html, body {
        background: #ffffff !important; /* Emerald a Dore/Jaune sombre */
    }
    .stApp {
        background: transparent !important;
    }
    .stApp > header {
        background: transparent !important;
    }
    [data-testid="stAppViewContainer"] {
        background: #ffffff !important;
    }
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stToolbar"] {
        background: transparent !important;
    }
    [data-testid="stSidebar"] {
        background-color: #f1f5f9 !important; /* Sidebar claire */
    }
    [data-testid="stMain"] {
        background: transparent !important;
    }
    .main .block-container {
        background: transparent !important;
        padding-top: 2rem;
    }
    section[data-testid="stSidebar"] > div {
        background-color: transparent !important;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    .main {
        background: transparent !important;
        color: #1e293b;
    }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Header ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
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

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Section Header ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .section-hdr {
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem; font-weight: 700; color: #818cf8;
        text-transform: uppercase; letter-spacing: 3px;
        margin: 2rem 0 1rem 0;
        border-bottom: 1px solid rgba(129,140,248,0.25);
        padding-bottom: 10px;
    }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Student Selector Bar ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .student-selector {
        background: rgba(20, 30, 55, 0.7);
        padding: 22px 28px; border-radius: 20px; margin-bottom: 24px;
        border: 1px solid rgba(129,140,248,0.3);
        box-shadow: 0 0 40px rgba(129,140,248,0.08);
        backdrop-filter: blur(16px);
    }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Module Cards ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
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

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Progress Bar ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .progress-bar-container {
        background: rgba(255,255,255,0.07);
        border-radius: 10px; height: 8px; margin-top: 10px; overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%; border-radius: 10px;
        transition: width 0.8s ease-in-out;
    }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Score Badge ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .score-badge { font-family: 'Poppins', sans-serif; font-size: 1.4rem; font-weight: 800; }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Advanced Glowing Status Box ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
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

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Metric Highlight Enhanced ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .metric-highlight {
        background: rgba(15, 23, 42, 0.8); border-radius: 24px; padding: 32px 20px;
        text-align: center; border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
        backdrop-filter: blur(12px);
        transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-highlight:hover { transform: translateY(-8px); border-color: rgba(255,255,255,0.25); box-shadow: 0 20px 40px rgba(0,0,0,0.4); }

    .progress-bar-container {
        width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%; border-radius: 4px; transition: width 0.5s ease-in-out;
    }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ KPI Mini Card (Sidebar) ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .kpi-mini {
        background: rgba(30,41,70,0.6); border-radius: 14px; padding: 14px 16px;
        margin: 8px 0; border: 1px solid rgba(255,255,255,0.06);
        text-align: center;
    }
    .kpi-mini .kpi-val { font-family:'Poppins'; font-size:1.6rem; font-weight:800; }
    .kpi-mini .kpi-lbl { font-size:0.75rem; color:#94a3b8; text-transform: uppercase; letter-spacing:1px; }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Risk / Rec items ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
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

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Profil Box ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .profil-box {
        background: rgba(22,32,58,0.5); border: 1px solid rgba(255,255,255,0.06);
        border-radius: 18px; padding: 20px;
    }
    .danger-abs { background: rgba(244,63,94,0.12); border: 1px dashed #f43f5e; border-radius: 10px; padding: 10px 14px; color: #fda4af; font-weight: 600; margin-top:8px; }
    .safe-abs   { background: rgba(16,185,129,0.12); border: 1px dashed #10b981; border-radius: 10px; padding: 10px 14px; color: #6ee7b7; font-weight: 600; margin-top:8px; }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Tabs ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    .stTabs [data-baseweb="tab"] { font-family: 'Poppins'; font-size: 1rem; font-weight: 600; padding: 10px 18px; }
    .stTabs [aria-selected="true"] { color: #818cf8 !important; border-bottom: 3px solid #818cf8 !important; }
    .stTabs [data-baseweb="tab-panel"] { padding-top: 20px; }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Divider ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Annee card ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ */
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
    "ITE - Genie Info":       "ite",
    "ISIC":                   "isic",
    "CCN - Cybersecurite":    "ccn",
    "GEE - Genie Electrique": "gee",
    "Genie Civil":            "civil",
    "Genie Industriel":       "industriel",
}

PROFIL_EMOJI  = {0: "+", 1: "o", 2: "!", 3: "x"}
PROFIL_LABELS = {0: "Tres assidu", 1: "Assidu", 2: "Preoccupant", 3: "Absenteiste chronique"}

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ CHARGEMENT DES DONNEES ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
@st.cache_data
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    return None

df_students = load_data()

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ HEADER ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
st.markdown('<div class="title-main">Prediction Intelligente 3eme Annee</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Selectionnez un etudiant reel &middot; Ajustez les notes &middot; Visualisez l\'impact en temps reel <span style="color:#818cf8;">Mode What-If</span></div>',
    unsafe_allow_html=True
)

if df_students is None or df_students.empty:
    st.error("Aucune donnee d'etudiant trouvee. Verifiez que la pipeline de donnees a ete executee.")
    st.stop()

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ SELECTION ETUDIANT ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
st.markdown('<div class="student-selector">', unsafe_allow_html=True)
c_fil, c_etud, c_info = st.columns([1, 2, 1])
with c_fil:
    st.markdown("**Filiere**")
    fil_label   = st.selectbox("Filiere", list(FILIERES.keys()), label_visibility="collapsed")
    filiere_key = FILIERES[fil_label]

df_fil = df_students[df_students['Filiere'].str.contains(filiere_key, case=False, na=False)]
if df_fil.empty:
    df_fil = df_students

with c_etud:
    st.markdown("**Etudiant**")
    student_options = []
    student_dict = {}
    for _, row in df_fil.iterrows():
        cne    = row.get('CNE', 'INCONNU')
        nom    = row.get('Nom', '')
        prenom = row.get('Prenom', '')
        is_red = int(row.get('Redoublant_1A', 0)) == 1 or int(row.get('Redoublant_2A', 0)) == 1
        label = f"{'[R] ' if is_red else ''}{cne} - {nom} {prenom}"
        student_options.append(label)
        student_dict[label] = row

    selected_student_label = st.selectbox("Etudiant", student_options, label_visibility="collapsed")
    selected_student_data  = student_dict[selected_student_label]

with c_info:
    st.markdown("**Filiere choisie**")
    st.info(f"**{fil_label}**\n\n{len(df_fil)} etudiants")

st.markdown('</div>', unsafe_allow_html=True)

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Variables Redoublant ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
widget_key = str(selected_student_data.get('CNE', 'INCONNU'))

_r1a = selected_student_data.get('Redoublant_1A', 0)
redoublant_1A = 0 if (pd.isna(_r1a) if hasattr(pd, 'isna') else False) else int(_r1a or 0)

_r2a = selected_student_data.get('Redoublant_2A', 0)
redoublant_2A = 0 if (pd.isna(_r2a) if hasattr(pd, 'isna') else False) else int(_r2a or 0)

# Redoublant global pour la pastille dans le titre du selecteur
redoublant_global = bool(redoublant_1A or redoublant_2A)


# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ HELPER ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
def get_val(col_name, default=12.0):
    val = selected_student_data.get(col_name, default)
    if pd.isna(val): return float(default)
    return float(val)

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ NOMS DES MODULES PAR FILIERE ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
mod_labels = {
    "ite": {
        "s1": ["Maths 1 / Prog C", "Physique / Algo", "Architecture Numerique", "Electronique S1", "Systemes S1"],
        "s2": ["Maths 2 / Avance", "POO C++", "Reseaux S2", "Mecanique / Thermo", "Compilation S2"],
        "s3": ["Maths 3 / Oracles", "Java Avance", "Bases de Donnees", "Analyse S3", "Genie Logiciel S3"],
        "s4": ["Web S4", "Reseau Avance S4", "UML / Conception", "Systeme d'Exploitation", "Management S4"],
    },
    "isic": {
        "s1": ["Maths 1", "Physique S1", "Management", "Electronique", "Info S1"],
        "s2": ["Maths 2", "Physique S2", "Reseaux S2", "Ondes", "POO S2"],
        "s3": ["Maths 3", "Architecture Reseaux", "Signaux", "Telecoms S3", "Genie Logiciel"],
        "s4": ["Systemes Repartis", "Traitement d'Image", "Securite", "Routage S4", "Management"],
    },
    "ccn": {
        "s1": ["Maths 1 / Cyber", "Physique S1", "Architecture", "Reseaux de Base", "Systemes S1"],
        "s2": ["Maths 2 / Crypto", "POO / Scripting", "Reseaux Locaux", "Systeme Linux", "Telecoms"],
        "s3": ["Maths 3 / Proba", "Administration Securite", "Vulnerabilites", "Python Avance", "Droit Cyber"],
        "s4": ["Securite Avancee", "IoT & Securite", "Forensique Numerique", "Pentesting S4", "Management"],
    },
    "gee": {
        "s1": ["Maths 1", "Mecanique du Point", "Machines Electriques 1", "Electronique S1", "Thermo S1"],
        "s2": ["Maths 2", "Mecanique du Solide", "Machines Electriques 2", "Automatique", "Dessin Industriel"],
        "s3": ["Maths 3", "Reseaux Electriques", "Electronique de Puissance", "Energies Renouvelables", "Automatisme S3"],
        "s4": ["Gestion d'Energie", "Capteurs S4", "Traitement de Signal", "Informatique Indust.", "Management"],
    },
    "civil": {
        "s1": ["Maths 1", "Mecanique S1", "Materiaux 1", "Dessin Civil S1", "Geologie S1"],
        "s2": ["Maths 2", "RDM S2", "Hydro S2", "Materiaux 2", "Topographie"],
        "s3": ["Maths 3", "Beton Arme 1", "Mecanique des Sols", "Hydraulique S3", "BIM S3"],
        "s4": ["Beton Arme 2", "Ouvrages d'Art", "Thermique Batiment", "Voiries S4", "Management"],
    },
    "industriel": {
        "s1": ["Maths 1", "Physique S1", "Procedes de Fab 1", "Dessin Industriel", "Materiaux"],
        "s2": ["Maths 2", "Recherche Operationnelle", "Procedes de Fab 2", "Mecanique S2", "Informatique"],
        "s3": ["Maths 3", "CAO / PAO", "Gestion de Produit", "Automatique S3", "Qualite S3"],
        "s4": ["Logistique S4", "Gestion de Maintenance", "Lean Management", "Systemes Indust.", "Management"],
    },
}
cur_labels = mod_labels.get(filiere_key, mod_labels["ite"])

# --- Detection de Genre pour Accord ---
liste_femmes = {
    "Basma", "Sara", "Sanae", "Latifa", "Hafsa", "Meriem", "Meryem", "Dounia", "Samira", 
    "Rania", "Fatima", "Houda", "Imane", "Rim", "Nora", "Chaimaa", "Zineb", "Ghita", 
    "Hasnaa", "Salma", "Safae", "Lamia", "Widad"
}
est_femme = prenom.strip().title() in liste_femmes
label_reussite = "REUSSITE" if est_femme else "REUSSIT"

# Year 1 Status Dynamic Definitions
if redoublant_1A:
    red_1a_title = "⚠️ STATUT CRITIQUE 1A"
    red_1a_txt   = "REDOUBLANT 1A"
    red_1a_col   = "#f43f5e" # Rouge
else:
    red_1a_title = "✅ STATUT 1ERE ANNEE"
    red_1a_txt   = label_reussite
    red_1a_col   = "#10b981" # Vert

# Year 2 Status Dynamic Definitions
if redoublant_2A:
    red_2a_title = "⚠️ STATUT CRITIQUE 2A"
    red_2a_txt   = "REDOUBLANT 2A"
    red_2a_col   = "#f43f5e" # Rouge
else:
    red_2a_title = "✅ STATUT 2EME ANNEE"
    red_2a_txt   = label_reussite
    red_2a_col   = "#10b981" # Vert


#  ONGLETS 
tab1, tab2, tab_diag, tab3 = st.tabs([
    "[ DATA ]  Donnees 1ere Annee",
    "[ DATA ]  Donnees 2eme Annee",
    "[ SYS ]  Diagnostic & Analyse",
    "[ OUT ]  Resultats & Prediction 3A",
])

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ TAB 1 : 1ere Annee ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Semestre 1</div>', unsafe_allow_html=True)
        abs_s1_1A  = st.slider(" Absences S1 (heures)", 0, 60, int(get_val('Absences_S1', 0)), key=f"abs_s1_1a_{widget_key}")
        mod1_s1_1A = st.slider(cur_labels["s1"][0], 0.0, 20.0, get_val('Module_S1_1'), 0.5, key=f"m1s1_1a_{widget_key}")
        mod2_s1_1A = st.slider(cur_labels["s1"][1], 0.0, 20.0, get_val('Module_S1_2'), 0.5, key=f"m2s1_1a_{widget_key}")
        mod3_s1_1A = st.slider(cur_labels["s1"][2], 0.0, 20.0, get_val('Module_S1_3'), 0.5, key=f"m3s1_1a_{widget_key}")
        mod4_s1_1A = st.slider(cur_labels["s1"][3], 0.0, 20.0, get_val('Module_S1_4'), 0.5, key=f"m4s1_1a_{widget_key}")
        mod5_s1_1A = st.slider(cur_labels["s1"][4], 0.0, 20.0, get_val('Module_S1_5'), 0.5, key=f"m5s1_1a_{widget_key}")
        ang1_1A    = st.slider("Anglais Technique 1", 0.0, 20.0, get_val('Anglais_Tech_1', 13.0), 0.5, key=f"ang1_1a_{widget_key}")
        fr1_1A     = st.slider("Francais Professionnel 1", 0.0, 20.0, get_val('Francais_Pro_1', 13.0), 0.5, key=f"fr1_1a_{widget_key}")

    with c2:
        st.markdown('<div class="section-hdr">Semestre 2</div>', unsafe_allow_html=True)
        abs_s2_1A  = st.slider(" Absences S2 (heures)", 0, 60, int(get_val('Absences_S2', 0)), key=f"abs_s2_1a_{widget_key}")
        mod1_s2_1A = st.slider(cur_labels["s2"][0], 0.0, 20.0, get_val('Module_S2_1'), 0.5, key=f"m1s2_1a_{widget_key}")
        mod2_s2_1A = st.slider(cur_labels["s2"][1], 0.0, 20.0, get_val('Module_S2_2'), 0.5, key=f"m2s2_1a_{widget_key}")
        mod3_s2_1A = st.slider(cur_labels["s2"][2], 0.0, 20.0, get_val('Module_S2_3'), 0.5, key=f"m3s2_1a_{widget_key}")
        mod4_s2_1A = st.slider(cur_labels["s2"][3], 0.0, 20.0, get_val('Module_S2_4'), 0.5, key=f"m4s2_1a_{widget_key}")
        mod5_s2_1A = st.slider(cur_labels["s2"][4], 0.0, 20.0, get_val('Module_S2_5'), 0.5, key=f"m5s2_1a_{widget_key}")
        ang2_1A    = st.slider("Anglais Technique 2", 0.0, 20.0, get_val('Anglais_Tech_2', 13.0), 0.5, key=f"ang2_1a_{widget_key}")
        fr2_1A     = st.slider("Francais Professionnel 2", 0.0, 20.0, get_val('Francais_Pro_2', 13.0), 0.5, key=f"fr2_1a_{widget_key}")

    st.markdown('<div class="section-hdr">Evaluation Annuelle</div>', unsafe_allow_html=True)
    p1, p2, p3, p4 = st.columns(4)
    with p1: pfa_1A = st.slider(" Note PFA (1A)", 0.0, 20.0, get_val('PFA_2', 14.0), 0.5, key=f"pfa_1a_{widget_key}")
    with p2: part_1A = st.slider(" Participation", 0.0, 20.0, get_val('Participation', 14.0), 0.5, key=f"part_1a_{widget_key}")
    with p3: 
        # Regle dynamique pour le slider Modules Non Valides 1A
        min_nv_1a = 4 if redoublant_1A else 0
        max_nv_1a = 5 if redoublant_1A else 3
        default_nv_1a = int(get_val('Modules_Non_Valides', min_nv_1a))
        # S'assurer que le defaut est bien dans les limites
        default_nv_1a = max(min_nv_1a, min(default_nv_1a, max_nv_1a))

        modules_nv_1A = st.slider(
            "[ X ]  Modules Non Valides", 
            min_nv_1a, max_nv_1a, default_nv_1a, 
            key=f"mnv_1a_{widget_key}",
            help="S'adapte dynamiquement selon si l'etudiant est redoublant ou non (Regle PFA)."
        )
        # Redoublant 1A
        st.markdown(f"""
        <div style="background:rgba(22,32,58,0.6); border:1px solid rgba(255,255,255,0.06);
                    border-left: 4px solid {red_1a_col}; border-radius:12px; padding:12px 16px; margin-top:4px;">
            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">{red_1a_title}</span><br>
            <b style="color:{red_1a_col}; font-size:1rem; font-family:'Poppins';">{red_1a_txt}</b>
        </div>""", unsafe_allow_html=True)

    moy_s1_1A  = round(np.mean([mod1_s1_1A, mod2_s1_1A, mod3_s1_1A, mod4_s1_1A, mod5_s1_1A, ang1_1A, fr1_1A]), 2)
    moy_s2_1A  = round(np.mean([mod1_s2_1A, mod2_s2_1A, mod3_s2_1A, mod4_s2_1A, mod5_s2_1A, ang2_1A, fr2_1A, pfa_1A]), 2)
    moy_ann_1A = round((moy_s1_1A + moy_s2_1A) / 2, 2)

    st.markdown('<div class="section-hdr">Recapitulatif Moyennes</div>', unsafe_allow_html=True)
    col_m1, col_m2, col_m3 = st.columns(3)
    for col, val, label in [(col_m1, moy_s1_1A, " Moyenne S1"), (col_m2, moy_s2_1A, " Moyenne S2"), (col_m3, moy_ann_1A, " Moyenne Annuelle")]:
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

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ TAB 2 : 2eme Annee ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
with tab2:
    st.markdown("###  Informations 2eme Annee")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-hdr">Semestre 3</div>', unsafe_allow_html=True)
        abs_s1_2A  = st.slider(" Absences S3 (heures)", 0, 60, int(get_val('Absences_S3', 0)), key=f"abs_s1_2a_{widget_key}")
        mod1_s1_2A = st.slider(cur_labels["s3"][0], 0.0, 20.0, get_val('Module_S3_1', 12.0), 0.5, key=f"m1s1_2a_{widget_key}")
        mod2_s1_2A = st.slider(cur_labels["s3"][1], 0.0, 20.0, get_val('Module_S3_2', 12.0), 0.5, key=f"m2s1_2a_{widget_key}")
        mod3_s1_2A = st.slider(cur_labels["s3"][2], 0.0, 20.0, get_val('Module_S3_3', 12.0), 0.5, key=f"m3s1_2a_{widget_key}")
        mod4_s1_2A = st.slider(cur_labels["s3"][3], 0.0, 20.0, get_val('Module_S3_4', 12.0), 0.5, key=f"m4s1_2a_{widget_key}")
        mod5_s1_2A = st.slider(cur_labels["s3"][4], 0.0, 20.0, get_val('Module_S3_5', 12.0), 0.5, key=f"m5s1_2a_{widget_key}")
        ang1_2A    = st.slider("Anglais Technique S3", 0.0, 20.0, get_val('Anglais_Tech_S3', 13.0), 0.5, key=f"ang1_2a_{widget_key}")
        fr1_2A     = st.slider("Francais Pro. S3",     0.0, 20.0, get_val('Francais_Pro_S3', 13.0), 0.5, key=f"fr1_2a_{widget_key}")

    with c2:
        st.markdown('<div class="section-hdr">Semestre 4</div>', unsafe_allow_html=True)
        abs_s2_2A  = st.slider(" Absences S4 (heures)", 0, 60, int(get_val('Absences_S4', 0)), key=f"abs_s2_2a_{widget_key}")
        mod1_s2_2A = st.slider(cur_labels["s4"][0], 0.0, 20.0, get_val('Module_S4_1', 12.0), 0.5, key=f"m1s2_2a_{widget_key}")
        mod2_s2_2A = st.slider(cur_labels["s4"][1], 0.0, 20.0, get_val('Module_S4_2', 12.0), 0.5, key=f"m2s2_2a_{widget_key}")
        mod3_s2_2A = st.slider(cur_labels["s4"][2], 0.0, 20.0, get_val('Module_S4_3', 12.0), 0.5, key=f"m3s2_2a_{widget_key}")
        mod4_s2_2A = st.slider(cur_labels["s4"][3], 0.0, 20.0, get_val('Module_S4_4', 12.0), 0.5, key=f"m4s2_2a_{widget_key}")
        mod5_s2_2A = st.slider(cur_labels["s4"][4], 0.0, 20.0, get_val('Module_S4_5', 12.0), 0.5, key=f"m5s2_2a_{widget_key}")
        ang2_2A    = st.slider("Anglais Technique S4", 0.0, 20.0, get_val('Anglais_Tech_S4', 13.0), 0.5, key=f"ang2_2a_{widget_key}")
        fr2_2A     = st.slider("Francais Pro. S4",     0.0, 20.0, get_val('Francais_Pro_S4', 13.0), 0.5, key=f"fr2_2a_{widget_key}")

    p1, p2, p3 = st.columns(3)
    with p1: pfa_2A_v      = st.slider(" Note PFA 2 (2A)", 0.0, 20.0, get_val('PFA_2', 14.0), 0.5, key=f"pfa_2a_{widget_key}")
    with p2: 
        # Regle dynamique pour le slider Modules Non Valides 2A
        min_nv_2a = 4 if redoublant_2A else 0
        max_nv_2a = 5 if redoublant_2A else 3
        default_nv_2a = int(get_val('Modules_Non_Valides', min_nv_2a))
        # S'assurer que le defaut est bien dans les limites
        default_nv_2a = max(min_nv_2a, min(default_nv_2a, max_nv_2a))

        modules_nv_2A = st.slider(
            "[ X ]  Modules Non Valides (2A)", 
            min_nv_2a, max_nv_2a, default_nv_2a, 
            key=f"mnv_2a_{widget_key}",
            help="S'adapte dynamiquement selon si l'etudiant est redoublant ou non (Regle PFA)."
        )
        # Redoublant 2A
        st.markdown(f"""
        <div style="background:rgba(22,32,58,0.6); border:1px solid rgba(255,255,255,0.06);
                    border-left: 4px solid {red_2a_col}; border-radius:12px; padding:12px 16px; margin-top:4px;">
            <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;">{red_2a_title}</span><br>
            <b style="color:{red_2a_col}; font-size:1rem; font-family:'Poppins';">{red_2a_txt}</b>
        </div>""", unsafe_allow_html=True)

    moy_s1_2A  = round(np.mean([mod1_s1_2A, mod2_s1_2A, mod3_s1_2A, mod4_s1_2A, mod5_s1_2A, ang1_2A, fr1_2A]), 2)
    moy_s2_2A  = round(np.mean([mod1_s2_2A, mod2_s2_2A, mod3_s2_2A, mod4_s2_2A, mod5_s2_2A, ang2_2A, fr2_2A, pfa_2A_v]), 2)
    moy_ann_2A = round((moy_s1_2A + moy_s2_2A) / 2, 2)

    st.markdown('<div class="section-hdr">Recapitulatif Moyennes (2A)</div>', unsafe_allow_html=True)
    col_m1_2A, col_m2_2A, col_m3_2A = st.columns(3)
    for col, val, label in [(col_m1_2A, moy_s1_2A, " Moyenne S3"), (col_m2_2A, moy_s2_2A, " Moyenne S4"), (col_m3_2A, moy_ann_2A, " Moyenne Annuelle 2A")]:
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

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Construction donnees ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬


etudiant_1A = {
    "Module_S1_1": mod1_s1_1A, "Module_S1_2": mod2_s1_1A, "Module_S1_3": mod3_s1_1A,
    "Module_S1_4": mod4_s1_1A, "Module_S1_5": mod5_s1_1A,
    "Anglais_Tech_1": ang1_1A, "Francais_Pro_1": fr1_1A,
    "Module_S2_1": mod1_s2_1A, "Module_S2_2": mod2_s2_1A, "Module_S2_3": mod3_s2_1A,
    "Module_S2_4": mod4_s2_1A, "Module_S2_5": mod5_s2_1A,
    "Anglais_Tech_2": ang2_1A, "Francais_Pro_2": fr2_1A,
    "PFA_1": pfa_1A, "PFA_2": pfa_1A, "Participation": part_1A,
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

with tab_diag:

    # Calcul du diagnostic des causes d'echec
    from src.ml_models.predict import diagnostiquer_causes_echec
    diagnostic = diagnostiquer_causes_echec(etudiant_1A)
    etudiant_a_risque = diagnostic["etudiant_a_risque"]
    causes_detectees = diagnostic.get("causes", [])

    # IMPORTANT: Verifier aussi la prediction 3A reelle pour coherence
    from src.ml_models.predict import predict_modules_3A
    try:
        pred_3a = predict_modules_3A(etudiant_1A, filiere_key, etudiant_2A)
        statut_3a = pred_3a.get("statut_global", "JAUNE")
    except Exception:
        statut_3a = "JAUNE"

    # Si la prediction 3A indique une reussite (VERT ou Moyenne S5 >= 12), 
    # on desactive le diagnostic d'echec pour assurer la compatibilite (pas de diagnostic pour ceux qui reussissent).
    res_3a_note = pred_3a.get("note_s5_predite", 0.0) if 'pred_3a' in locals() else 0.0
    if statut_3a == "VERT" or res_3a_note >= 12.0:
        etudiant_a_risque = False
        diagnostic["etudiant_a_risque"] = False
        statut_3a = "VERT" # On le force au vert pour la suite s'il valide son annee

    # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ CAS 1 : Etudiant PAS a risque ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Motivation & Preparation Carriere ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
    if not etudiant_a_risque:
        etud_nom = selected_student_data.get('Nom', '')
        etud_prenom = selected_student_data.get('Prenom', '')
        st.markdown(f"""
<div style="text-align:center; padding:40px 30px 20px 30px; margin:10px 0;">
<div style="width:110px; height:110px; background:linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(56,189,248,0.1) 100%); 
            border:3px solid rgba(16,185,129,0.5); border-radius:50%; margin:0 auto 24px auto; 
            display:flex; align-items:center; justify-content:center;
            box-shadow:0 0 50px rgba(16,185,129,0.2); animation: pulseGlow 3s infinite alternate;">
    <span style="font-size:2.8rem; color:#10b981; font-weight:800;">OK</span>
</div>
<h2 style="color:#10b981; font-family:'Poppins'; margin-bottom:8px; font-size:1.8rem; font-weight:800;
           background:linear-gradient(135deg, #10b981, #38bdf8); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
    Felicitations {etud_prenom} !
</h2>
<h3 style="color:#e2e8f0; font-family:'Poppins'; margin-bottom:16px; font-size:1.2rem; font-weight:400;">
    Vous etes sur la voie de l'excellence
</h3>
<p style="color:#94a3b8; font-size:1.05rem; max-width:700px; margin:0 auto 10px auto; line-height:1.8;">
    Avec une moyenne 2ème année de <b style="color:#e2e8f0;">{moy_ann_2A:.1f}/20</b>, et une prédiction 3ème année estimée à 
    <b style="color:#10b981;">{res_3a_note:.1f}/20 (S5)</b> et <b style="color:#10b981;">{pred_3a.get('note_pfe_predite', 12.0):.1f}/20 (PFE)</b>, 
    votre parcours est remarquable. Vous êtes en excellente position pour <b style="color:#e2e8f0;">décrocher votre diplôme d'ingénieur</b>.
</p>
<p style="color:#94a3b8; font-size:1rem; max-width:650px; margin:0 auto 30px auto; line-height:1.7;">
    Il est maintenant temps de penser a <b style="color:#e2e8f0;">votre avenir professionnel</b>. 
    Les certifications sont un atout majeur pour se demarquer sur le marche du travail 
    et decrocher les meilleures opportunites des la sortie de l'ecole.
</p>
</div>
        """, unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Section Certifications Recommandees ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown('<div class="section-hdr">Certifications Recommandees pour Votre Carriere</div>', unsafe_allow_html=True)
        
        st.markdown("""
<p style="color:#94a3b8; font-size:0.95rem; margin-bottom:24px; line-height:1.6;">
    Boostez votre CV et preparez-vous au monde professionnel avec ces certifications reconnues mondialement. 
    Chaque certification ouvre des portes vers des postes a haute responsabilite et des salaires competitifs.
</p>
        """, unsafe_allow_html=True)

        cert_col1, cert_col2 = st.columns(2)

        with cert_col1:
            st.markdown("""
<a href="https://www.cisco.com/site/us/en/learn/training-certifications/certifications/enterprise/ccna/index.html" target="_blank" style="text-decoration:none;">
<div style="background:rgba(22,32,58,0.7); border:1px solid rgba(56,189,248,0.2); border-left:5px solid #38bdf8;
            border-radius:18px; padding:24px; margin-bottom:16px; cursor:pointer;
            box-shadow:0 6px 20px rgba(0,0,0,0.15); transition: all 0.3s ease;">
<div style="display:flex; align-items:center; gap:16px; margin-bottom:14px;">
    <div style="width:50px; height:50px; background:rgba(56,189,248,0.12); border:2px solid rgba(56,189,248,0.3);
                border-radius:14px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <span style="font-size:1.5rem; color:#38bdf8; font-weight:800;">R</span>
    </div>
    <div>
        <h4 style="color:white; font-family:'Poppins'; margin:0; font-size:1.1rem;">Cisco CCNA</h4>
        <span style="color:#38bdf8; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Reseaux & Infrastructure</span>
    </div>
</div>
<p style="color:#94a3b8; font-size:0.88rem; line-height:1.5; margin:0 0 14px 0;">
    La reference mondiale en administration reseau. Maitrisez le routage, switching, et les architectures reseau d'entreprise.
</p>
<div style="display:inline-block; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.3);
            padding:6px 16px; border-radius:20px;">
    <span style="color:#38bdf8; font-size:0.8rem; font-weight:600;">Passer la certification &#8594;</span>
</div>
</div>
</a>
            """, unsafe_allow_html=True)

            st.markdown("""
<a href="https://aws.amazon.com/fr/certification/certified-solutions-architect-associate/" target="_blank" style="text-decoration:none;">
<div style="background:rgba(22,32,58,0.7); border:1px solid rgba(245,158,11,0.2); border-left:5px solid #f59e0b;
            border-radius:18px; padding:24px; margin-bottom:16px; cursor:pointer;
            box-shadow:0 6px 20px rgba(0,0,0,0.15); transition: all 0.3s ease;">
<div style="display:flex; align-items:center; gap:16px; margin-bottom:14px;">
    <div style="width:50px; height:50px; background:rgba(245,158,11,0.12); border:2px solid rgba(245,158,11,0.3);
                border-radius:14px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <span style="font-size:1.5rem; color:#f59e0b; font-weight:800;">C</span>
    </div>
    <div>
        <h4 style="color:white; font-family:'Poppins'; margin:0; font-size:1.1rem;">AWS Solutions Architect</h4>
        <span style="color:#f59e0b; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Cloud & DevOps</span>
    </div>
</div>
<p style="color:#94a3b8; font-size:0.88rem; line-height:1.5; margin:0 0 14px 0;">
    Concevez des architectures cloud evolutives et securisees. La certification la plus demandee dans le Cloud Computing.
</p>
<div style="display:inline-block; background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.3);
            padding:6px 16px; border-radius:20px;">
    <span style="color:#f59e0b; font-size:0.8rem; font-weight:600;">Passer la certification &#8594;</span>
</div>
</div>
</a>
            """, unsafe_allow_html=True)

        with cert_col2:
            st.markdown("""
<a href="https://www.comptia.org/certifications/security" target="_blank" style="text-decoration:none;">
<div style="background:rgba(22,32,58,0.7); border:1px solid rgba(244,63,94,0.2); border-left:5px solid #f43f5e;
            border-radius:18px; padding:24px; margin-bottom:16px; cursor:pointer;
            box-shadow:0 6px 20px rgba(0,0,0,0.15); transition: all 0.3s ease;">
<div style="display:flex; align-items:center; gap:16px; margin-bottom:14px;">
    <div style="width:50px; height:50px; background:rgba(244,63,94,0.12); border:2px solid rgba(244,63,94,0.3);
                border-radius:14px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <span style="font-size:1.5rem; color:#f43f5e; font-weight:800;">S</span>
    </div>
    <div>
        <h4 style="color:white; font-family:'Poppins'; margin:0; font-size:1.1rem;">CompTIA Security+</h4>
        <span style="color:#f43f5e; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Cybersecurite</span>
    </div>
</div>
<p style="color:#94a3b8; font-size:0.88rem; line-height:1.5; margin:0 0 14px 0;">
    La porte d'entree vers les metiers de la cybersecurite. Apprenez a proteger les systemes et a detecter les menaces.
</p>
<div style="display:inline-block; background:rgba(244,63,94,0.1); border:1px solid rgba(244,63,94,0.3);
            padding:6px 16px; border-radius:20px;">
    <span style="color:#f43f5e; font-size:0.8rem; font-weight:600;">Passer la certification &#8594;</span>
</div>
</div>
</a>
            """, unsafe_allow_html=True)

            st.markdown("""
<a href="https://www.coursera.org/professional-certificates/meta-front-end-developer" target="_blank" style="text-decoration:none;">
<div style="background:rgba(22,32,58,0.7); border:1px solid rgba(129,140,248,0.2); border-left:5px solid #818cf8;
            border-radius:18px; padding:24px; margin-bottom:16px; cursor:pointer;
            box-shadow:0 6px 20px rgba(0,0,0,0.15); transition: all 0.3s ease;">
<div style="display:flex; align-items:center; gap:16px; margin-bottom:14px;">
    <div style="width:50px; height:50px; background:rgba(129,140,248,0.12); border:2px solid rgba(129,140,248,0.3);
                border-radius:14px; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
        <span style="font-size:1.5rem; color:#818cf8; font-weight:800;">D</span>
    </div>
    <div>
        <h4 style="color:white; font-family:'Poppins'; margin:0; font-size:1.1rem;">Meta Developer Certificate</h4>
        <span style="color:#818cf8; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;">Developpement Web & Mobile</span>
    </div>
</div>
<p style="color:#94a3b8; font-size:0.88rem; line-height:1.5; margin:0 0 14px 0;">
    Developpez des applications web et mobiles modernes avec React, JavaScript et les technologies Meta. Tres prise par les recruteurs.
</p>
<div style="display:inline-block; background:rgba(129,140,248,0.1); border:1px solid rgba(129,140,248,0.3);
            padding:6px 16px; border-radius:20px;">
    <span style="color:#818cf8; font-size:0.8rem; font-weight:600;">Passer la certification &#8594;</span>
</div>
</div>
</a>
            """, unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Message de motivation final ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown(f"""
<div style="background:linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(56,189,248,0.05) 100%);
            border:1px solid rgba(16,185,129,0.15); border-radius:20px; padding:28px; margin-top:16px;
            text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
<p style="color:#e2e8f0; font-size:1.1rem; font-family:'Poppins'; font-weight:600; margin:0 0 10px 0;">
    Votre diplome d'ingenieur est a portee de main, {etud_prenom} !
</p>
<p style="color:#94a3b8; font-size:0.95rem; margin:0; line-height:1.7; max-width:600px; display:inline-block;">
    Investissez des maintenant dans une certification pour arriver sur le marche du travail 
    avec une longueur d'avance. Les entreprises recrutent des profils certifies en priorite.
    <b style="color:#34d399;">Votre avenir commence aujourd'hui.</b>
</p>
</div>
        """, unsafe_allow_html=True)

    # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ CAS 2 : Etudiant a risque ÃƒÂ¢Ã¢â‚¬Â Ã¢â‚¬â„¢ Diagnostic des Causes d'Echec ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
    else:
        nb_causes = diagnostic["nb_causes"]
        severite = diagnostic["severite_globale"]
        sev_color = "#f43f5e" if severite == "critique" else "#f59e0b" if severite == "majeure" else "#818cf8"
        sev_label = severite.upper()

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Alerte Severite ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown(f"""
<div style="text-align:center; margin-bottom:28px; animation: pulseGlow 2.5s infinite alternate;">
<div style="display:inline-block; background:linear-gradient(135deg, {sev_color}20 0%, {sev_color}10 100%); 
            border:2px solid {sev_color}; padding:14px 32px; border-radius:40px; 
            box-shadow:0 0 40px {sev_color}30;">
    <b style="color:{sev_color}; font-size:1.1rem; font-family:'Poppins'; letter-spacing:2px;">
        [ DIAGNOSTIC ] {nb_causes} CAUSE{'S' if nb_causes > 1 else ''} D'ECHEC DETECTEE{'S' if nb_causes > 1 else ''} - Severite {sev_label}
    </b>
</div>
</div>
        """, unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Resume de la situation ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        etud_nom = selected_student_data.get('Nom', '')
        etud_prenom = selected_student_data.get('Prenom', '')
        etud_cne = selected_student_data.get('CNE', 'N/A')

        st.markdown(f"""
<div style="background:{sev_color}08; border:1px solid {sev_color}30; border-left:6px solid {sev_color};
            border-radius:20px; padding:28px; margin-bottom:28px; box-shadow:0 10px 30px rgba(0,0,0,0.15);">
<h3 style="color:{sev_color}; font-family:'Poppins'; margin-top:0; margin-bottom:14px; font-size:1.2rem; letter-spacing:1px;">
    [ ANALYSE ] Diagnostic Academique - {etud_prenom} {etud_nom}
</h3>
<p style="color:#e2e8f0; font-size:1.05rem; line-height:1.7; margin-bottom:14px;">
    L'analyse automatique du dossier de l'etudiant(e) <b>{etud_prenom} {etud_nom}</b> (CNE: {etud_cne}) 
    a identifie <b style="color:{sev_color};">{nb_causes} cause{'s' if nb_causes > 1 else ''} d'echec</b> 
    a partir des donnees academiques reelles (notes, absences, modules).
</p>
<p style="color:#94a3b8; font-size:0.92rem; line-height:1.5; margin:0; border-top:1px solid rgba(255,255,255,0.06); padding-top:14px;">
    Ce diagnostic permet d'identifier precisement les points de blocage pour orienter 
    les actions de remise a niveau et le suivi pedagogique.
</p>
</div>
        """, unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Cartes des causes detectees ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown('<div class="section-hdr">Detail des Causes Detectees par l\'IA</div>', unsafe_allow_html=True)

        cat_labels = {
            "academique": "ACADEMIQUE",
            "comportemental": "COMPORTEMENTAL",
            "historique": "HISTORIQUE",
        }

        for i, cause in enumerate(causes_detectees):
            couleur = cause["couleur"]
            cat_label = cat_labels.get(cause["categorie"], "AUTRE")
            sev_badge_bg = "#f43f5e" if cause["severite"] == "critique" else "#f59e0b" if cause["severite"] == "majeure" else "#818cf8"
            sev_upper = cause['severite'].upper()
            titre = cause['titre']
            valeur = cause['valeur']
            desc = cause['description']

            st.markdown(f"""
<div style="background:rgba(22,32,58,0.6); border:1px solid rgba(255,255,255,0.06); border-left:5px solid {couleur};
            border-radius:18px; padding:22px 26px; margin-bottom:14px;
            box-shadow:0 6px 20px rgba(0,0,0,0.15); transition: all 0.3s ease;">
<div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px;">
    <div>
        <span style="font-size:0.7rem; color:{couleur}; text-transform:uppercase; letter-spacing:2px; font-weight:700;
                     background:{couleur}15; padding:3px 10px; border-radius:8px; border:1px solid {couleur}30;">{cat_label}</span>
        <span style="font-size:0.7rem; color:{sev_badge_bg}; text-transform:uppercase; letter-spacing:2px; font-weight:700;
                     background:{sev_badge_bg}15; padding:3px 10px; border-radius:8px; border:1px solid {sev_badge_bg}30; margin-left:8px;">{sev_upper}</span>
        <h4 style="color:white; font-family:'Poppins'; margin:8px 0 0 0; font-size:1.1rem;">{titre}</h4>
    </div>
    <div style="text-align:right; min-width:80px;">
        <div style="background:{couleur}15; border:2px solid {couleur}60; border-radius:14px; padding:6px 14px;
                    display:inline-block;">
            <b style="color:{couleur}; font-family:'Poppins'; font-size:1.1rem;">{valeur}</b>
        </div>
    </div>
</div>
<p style="color:#94a3b8; font-size:0.92rem; line-height:1.6; margin:0;">{desc}</p>
</div>
            """, unsafe_allow_html=True)

#  TAB 3 : RESULTATS 
with tab3:
    with st.spinner(" Calcul de la prediction IA en cours..."):
        try:
            from src.ml_models.predict import predict_modules_3A
            res = predict_modules_3A(etudiant_1A, filiere_key, etudiant_2A)
            prediction_ok = True
        except Exception as e:
            st.error(f"[ X ]  Erreur de prediction : {e}")
            prediction_ok = False

    if prediction_ok:
        statut    = res["statut_global"]
        emoji_map = {"VERT": "[ OK ] ", "JAUNE": "[ ! ] ", "ROUGE": "[ X ] "}
        title_map = {"VERT": "VALIDATION ASSUREE", "JAUNE": "RISQUE MODERE", "ROUGE": "ECHEC CRITIQUE"}
        css_map   = {"VERT": "glow-vert", "JAUNE": "glow-jaune", "ROUGE": "glow-rouge"}
        desc_map  = {
            "VERT":  "L'etudiant est sur une excellente trajectoire pour valider sa 3eme annee brillamment.",
            "JAUNE": f"Avec une note S5 estimee a <b>{res['note_s5_predite']:.1f}/20</b> et un PFE estime a <b>{res['note_pfe_predite']:.1f}/20</b>, le profil necessite une attention particuliere pour garantir le diplome.",
            "ROUGE": f"Risque majeur - Avec une note S5 estimee a <b>{res['note_s5_predite']:.1f}/20</b> et un PFE estime a <b>{res['note_pfe_predite']:.1f}/20</b>, l'etudiant ne reunit pas les prerequis.",
        }

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Resultat Prediction 3A ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown('<div class="section-hdr">Resultat de la Prediction (3eme Annee)</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="{css_map[statut]} statut-box" style="max-width:800px; margin: 0 auto;">
            <p style="margin:0; font-size:0.9rem; font-family:'Poppins'; text-transform:uppercase; letter-spacing:3px; opacity:0.9; text-shadow:0 2px 4px rgba(0,0,0,0.3);">Prediction PFA & Diapason IA</p>
            <h2 style="margin:16px 0 8px 0; font-family:'Poppins'; font-size:2.2rem; font-weight:800; text-shadow:0 2px 10px rgba(0,0,0,0.4);">
                <span style="font-size:3rem; vertical-align:middle; margin-right:12px;">{emoji_map[statut]}</span> 
                {title_map[statut]}
            </h2>
            <div style="background:rgba(0,0,0,0.15); padding:8px 16px; border-radius:20px; display:inline-block; margin-bottom:14px; border:1px solid rgba(255,255,255,0.2);">
                <b style="font-size:1.1rem; letter-spacing:1px;">{res['nb_valides']}/{res['nb_total']} MODULES PREDITS VALIDES</b>
            </div>
            <p style="margin:0; font-size:0.98rem; opacity:0.95; line-height:1.5;">{desc_map[statut]}</p>
        </div>""", unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Notes estimees S5 & PFE ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown('<div class="section-hdr">Notes Estimees en 3eme Annee</div>', unsafe_allow_html=True)
        col_n1, col_n2, col_n3 = st.columns(3)
        s5_color  = "#10b981" if res["note_s5_predite"] >= 12 else "#f59e0b" if res["note_s5_predite"] >= 10 else "#ef4444"
        pfe_color = "#10b981" if res["note_pfe_predite"] >= 12 else "#f59e0b" if res["note_pfe_predite"] >= 10 else "#ef4444"
        pct_val   = int(res['nb_valides'] / max(res['nb_total'], 1) * 100)
        badge_col = "#10b981" if pct_val >= 70 else "#f59e0b" if pct_val >= 40 else "#ef4444"

        with col_n1:
            pct = int(res["note_s5_predite"] / 20 * 100)
            st.markdown(f"""<div class="metric-highlight">
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.08); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:1.5rem; margin-bottom:12px;"></div><br>
                <span style="font-size:0.85rem; color:#94a3b8; font-family:'Poppins'; letter-spacing:1px; text-transform:uppercase;">Note S5 Estimee</span><br>
                <b style="color:{s5_color}; font-size:3rem; font-family:'Poppins'; display:block; margin:8px 0; text-shadow:0 0 20px {s5_color}40;">{res['note_s5_predite']:.1f}<span style="font-size:1.2rem;color:#64748b;">/20</span></b>
                <div class="progress-bar-container" style="height:6px;"><div class="progress-bar-fill" style="width:{pct}%;background:{s5_color}; box-shadow:0 0 10px {s5_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        with col_n2:
            pct = int(res["note_pfe_predite"] / 20 * 100)
            st.markdown(f"""<div class="metric-highlight">
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.08); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:1.5rem; margin-bottom:12px;"></div><br>
                <span style="font-size:0.85rem; color:#94a3b8; font-family:'Poppins'; letter-spacing:1px; text-transform:uppercase;">Note PFE Estimee</span><br>
                <b style="color:{pfe_color}; font-size:3rem; font-family:'Poppins'; display:block; margin:8px 0; text-shadow:0 0 20px {pfe_color}40;">{res['note_pfe_predite']:.1f}<span style="font-size:1.2rem;color:#64748b;">/20</span></b>
                <div class="progress-bar-container" style="height:6px;"><div class="progress-bar-fill" style="width:{pct}%;background:{pfe_color}; box-shadow:0 0 10px {pfe_color};"></div></div>
            </div>""", unsafe_allow_html=True)

        with col_n3:
            st.markdown(f"""<div class="metric-highlight">
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.08); border-radius:12px; display:inline-flex; align-items:center; justify-content:center; font-size:1.5rem; margin-bottom:12px;"></div><br>
                <span style="font-size:0.85rem; color:#94a3b8; font-family:'Poppins'; letter-spacing:1px; text-transform:uppercase;">Modules Valides</span><br>
                <b style="color:{badge_col}; font-size:3rem; font-family:'Poppins'; display:block; margin:8px 0; text-shadow:0 0 20px {badge_col}40;">{res['nb_valides']}<span style="font-size:1.2rem;color:#64748b;">/{res['nb_total']}</span></b>
                <div class="progress-bar-container" style="height:6px;"><div class="progress-bar-fill" style="width:{pct_val}%;background:{badge_col}; box-shadow:0 0 10px {badge_col};"></div></div>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align:center; color:#64748b; font-style:italic; margin-top:16px; font-size:0.9rem;'>{res['resume']}</p>", unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Modules 3A detailles avec progress bar ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown('<div class="section-hdr">Detail des Modules 3eme Annee</div>', unsafe_allow_html=True)
        modules = res["modules_3A"]
        n_cols  = 2
        rows    = [list(modules.items())[i:i+n_cols] for i in range(0, len(modules), n_cols)]

        for row in rows:
            cols = st.columns(n_cols)
            for col_idx, (mod_key, mod_res) in enumerate(row):
                with cols[col_idx]:
                    score = mod_res["score_prereq"]
                    if mod_res["valide"]:
                        css_cls = "mod-valide";   icon = "[ OK ] "; color = "#10b981"; bg_color = "rgba(16, 185, 129, 0.05)"
                    elif score >= 10:
                        css_cls = "mod-marginal"; icon = "[ ! ] "; color = "#f59e0b"; bg_color = "rgba(245, 158, 11, 0.05)"
                    else:
                        css_cls = "mod-invalide"; icon = "[ X ] "; color = "#f43f5e"; bg_color = "rgba(244, 63, 94, 0.05)"

                    proba_pct  = round(mod_res["probabilite"] * 100, 0)
                    if mod_key == "PFE":
                        status_txt = "VALIDE" if mod_res["valide"] else "NON VALIDE"
                    else:
                        status_txt = "VALIDE" if mod_res["valide"] else "RATTRAPAGE" if score >= 10 else "NON VALIDE"
                    score_pct  = int((score / 20) * 100)
                    
                    raison_txt = mod_res['raison']
                    # Ne pas afficher de diagnostics negatifs pour un etudiant qui a valide son annee (statut VERT)
                    if statut == "VERT":
                        if "Validé d'office" in raison_txt:
                            raison_txt = "Validé par compensation"
                        elif mod_res["valide"]:
                            raison_txt = "Validation acquise"
                        else:
                            raison_txt = "Module à consolider"

                    st.markdown(f"""
                    <div class="module-card {css_cls}" style="background:{bg_color}; position:relative; overflow:hidden;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                            <div>
                                <b style="color:white; font-size:1.05rem; font-family:'Poppins'; letter-spacing:0.5px;">{icon} {mod_res['label_fr']}</b><br>
                                <span style="color:#94a3b8; font-size:0.85rem;">{raison_txt}</span>
                            </div>
                            <div style="text-align:right; min-width:90px;">
                                <div class="score-badge" style="color:{color}; text-shadow:0 0 10px {color}40;">{score:.1f}<span style="font-size:0.8rem; color:#64748b;">/20</span></div>
                            </div>
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                            <span style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:1px; font-weight:600;">Probabilite de reussite</span>
                            <span style="color:{color}; font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:10px;">{proba_pct:.0f}% - {status_txt}</span>
                        </div>
                        <div class="progress-bar-container" style="height:6px; background:rgba(0,0,0,0.2);">
                            <div class="progress-bar-fill" style="width:{score_pct}%; background: linear-gradient(90deg, {color}40, {color}); box-shadow:0 0 10px {color}80;"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

        # ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ Graphique + Profil ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
        st.markdown("<br>", unsafe_allow_html=True)
        cl_g, cl_p = st.columns([1.6, 1])

        with cl_g:
            st.markdown('<div class="section-hdr">Scores de Prerequis</div>', unsafe_allow_html=True)
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
            ax.set_xlabel("Score Prerequis (/20)", color="#94a3b8", fontsize=9)
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
                # Message de motivation pour les bons etudiants
                st.markdown(f"""
                <div style="background:linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0.02) 100%); 
                            border-radius:20px; padding:32px; border:1px solid rgba(16,185,129,0.2); 
                            box-shadow:0 10px 30px rgba(0,0,0,0.2); margin-bottom:20px;">
                    <h3 style="color:#10b981; font-family:'Poppins'; margin-top:0; font-size:1.6rem;">[ EXCELLENCE ]  Parcours d'Excellence</h3>
                    <p style="color:#e2e8f0; font-size:1.05rem; line-height:1.6; margin-bottom:20px;">
                        Felicitations ! Vos bases academiques sont extremement solides. Avec ce rythme, la validation 
                        de votre 3eme annee (diplome) est quasiment assuree. Vous avez une marge de manÃƒâ€¦Ã¢â‚¬Å“uvre suffisante 
                        pour viser une mention d'excellence.
                    </p>
                    <div style="background:rgba(255,255,255,0.05); border-radius:12px; padding:16px;">
                        <b style="color:#a7f3d0; font-size:1.1rem; display:block; margin-bottom:10px;">[ INFO ]  Conseils pour aller plus loin :</b>
                        <ul style="color:#cbd5e1; margin:0; padding-left:20px; font-size:0.95rem; line-height:1.5;">
                            <li style="margin-bottom:6px;">Commencez des maintenant a chercher un stage de fin d'etudes (PFE) stimulant et techniquement challengeant.</li>
                            <li style="margin-bottom:6px;">Impliquez-vous dans des projets parascolaires ou des competitions pour etoffer votre CV.</li>
                            <li>Explorez les thematiques avancees de votre filiere pour anticiper le marche de l'emploi.</li>
                        </ul>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Messages d'alerte et de coaching pour les etudiants a risque
                color_theme  = "#f43f5e" if statut == "ROUGE" else "#f59e0b"
                bg_theme     = "rgba(244,63,94,0.1)" if statut == "ROUGE" else "rgba(245,158,11,0.1)"
                border_theme = "rgba(244,63,94,0.3)" if statut == "ROUGE" else "rgba(245,158,11,0.3)"
                titre        = "[ ALERTE ]  Alerte Academique Majeure" if statut == "ROUGE" else "[ ! ]  Points d'Attention"

                # Compilation des alertes personnalisees
                alertes_html = ""
                # 1. Absences
                if p1A["danger_abs"]:
                    alertes_html += f"""
<div style="background:rgba(255,255,255,0.03); border-left:4px solid #f43f5e; padding:12px 16px; border-radius:10px; margin-bottom:10px;">
<b style="color:#fda4af; display:block; margin-bottom:4px;"> Assiduite Critique ({p1A['total_abs']:.0f}h d'absence)</b>
<span style="color:#cbd5e1; font-size:0.9rem;">L'absenteisme est le premier facteur d'echec statitisque en 3A. Il est imperatif de reduire vos absences a zero.</span>
</div>"""
                # 2. Redoublant
                if p1A["danger_red"]:
                     alertes_html += f"""
<div style="background:rgba(255,255,255,0.03); border-left:4px solid #f59e0b; padding:12px 16px; border-radius:10px; margin-bottom:10px;">
<b style="color:#fcd34d; display:block; margin-bottom:4px;">[ R ]  Historique de Redoublement</b>
<span style="color:#cbd5e1; font-size:0.9rem;">Votre statut de redoublant montre des fragilites anterieures. Un suivi rigoureux des les premieres semaines est crucial.</span>
</div>"""
                # 3. Modules fail
                if res["facteurs_risque_3A"] and len(res["modules_non_valides_liste"]) > 0:
                    mods = ", ".join(res["modules_non_valides_liste"])
                    alertes_html += f"""
<div style="background:rgba(255,255,255,0.03); border-left:4px solid {color_theme}; padding:12px 16px; border-radius:10px; margin-bottom:10px;">
<b style="color:{color_theme}; display:block; margin-bottom:4px;"> Lacunes Prerequis Identifiees</b>
<span style="color:#cbd5e1; font-size:0.9rem;">Vous risquez de bloquer sur les modules suivants : <b>{mods}</b>.</span>
</div>"""

                st.markdown(f"""
<div style="background:linear-gradient(135deg, {bg_theme} 0%, rgba(0,0,0,0.2) 100%); border-radius:20px; padding:32px; border:1px solid {border_theme}; box-shadow:0 10px 30px rgba(0,0,0,0.2); margin-bottom:20px;">
<h3 style="color:{color_theme}; font-family:'Poppins'; margin-top:0; font-size:1.6rem;">{titre}</h3>
<div style="margin-bottom:24px;">
<p style="color:#e2e8f0; font-size:1rem; margin-bottom:16px;">
L'Intelligence Artificielle a detecte des blocages majeurs qui pourraient compromettre l'obtention de votre diplome. Agissez des maintenant sur ces points :
</p>
{alertes_html}
</div>
<div style="background:rgba(0,0,0,0.3); border-radius:12px; padding:16px; border-top:2px solid {color_theme};">
<b style="color:#e2e8f0; font-size:1.05rem; display:block; margin-bottom:12px;">[ ACTION ]  Plan d'Action Recommande :</b>
<ul style="color:#cbd5e1; margin:0; padding-left:20px; font-size:0.95rem; line-height:1.6;">
<li style="margin-bottom:6px;"><b>Revision intensive:</b> Reprenez les cours des modules 1A/2A qui bloquent en 3A.</li>
<li style="margin-bottom:6px;"><b>Tutorat:</b> Demandez de l'aide a vos enseignants ou camarades sur les concepts fondamentaux non acquis.</li>
<li><b>Assiduite stricte:</b> Ne manquez aucune seance de TD/TP cette annee.</li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)

# ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ FOOTER ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬ÃƒÂ¢Ã¢â‚¬Â-Ã¢â€šÂ¬
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(
    "<center><small style='color:#334155;'> Projet de Fin d'Annee (PFA) &nbsp;-&nbsp; Systeme Intelligent de Prediction Academique &nbsp;-&nbsp; Interface What-If v4.0</small></center>",
    unsafe_allow_html=True
)
