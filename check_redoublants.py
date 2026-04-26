"""
Liste complète des redoublants (1A et/ou 2A) dans tous les fichiers raw
+ Rappel des conditions de réussite
"""
import pandas as pd
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

RAW_DIR = 'data/raw'
files = {
    'ITE  — Génie Informatique':         'ite_genie_info.xlsx',
    'ISIC — Ingénierie Systèmes Info':   'isic.xlsx',
    'CCN  — Cybersécurité':              'ccn_cybersec.xlsx',
    'GEE  — Génie Électrique':           'gee_genie_electrique.xlsx',
    'Génie Civil':                       'genie_civil.xlsx',
    'Génie Industriel':                  'genie_industriel.xlsx',
}

print("=" * 80)
print("  LISTE DES REDOUBLANTS PAR FILIÈRE (données Raw)")
print("=" * 80)

all_redoublants = []

for filiere_label, filename in files.items():
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_excel(path, header=3)
    df = df.iloc[0:]  # toutes les lignes

    # Repérer les colonnes clés
    cne_col    = df.columns[0]
    nom_col    = df.columns[1]
    prenom_col = df.columns[2]

    mnv_col = None
    red_col = None
    moy_col = None

    for c in df.columns:
        cs = str(c).lower()
        if 'non valid' in cs or 'non\nvalid' in cs:
            mnv_col = c
        if 'redoublant' in cs:
            red_col = c
        if 'annuelle' in cs or ('moyenne' in cs and 'annuelle' in cs.replace('\n', ' ')):
            moy_col = c

    # Nettoyer — garder uniquement les lignes étudiant (CNE commence par lettre)
    df_clean = df[df[cne_col].notna()].copy()
    df_clean = df_clean[df_clean[cne_col].astype(str).str.match(r'^[A-Za-z]\d+')]

    if not red_col:
        print(f"\n[{filiere_label}] — Colonne Redoublant introuvable")
        continue

    # Filtrer les redoublants
    redoublants = df_clean[
        df_clean[red_col].astype(str).str.strip().str.lower().isin(['oui', '1', 'yes'])
    ].copy()

    print(f"\n{'─'*80}")
    print(f"  {filiere_label}  →  {len(redoublants)} redoublant(s) / {len(df_clean)} étudiants")
    print(f"{'─'*80}")

    if len(redoublants) == 0:
        print("  (aucun redoublant dans cette filière)")
    else:
        # En-tête
        print(f"  {'CNE':<12} {'Nom':<18} {'Prénom':<18} {'MNV':>5} {'Moy.Ann':>8}  {'Statut'}")
        print(f"  {'-'*12} {'-'*18} {'-'*18} {'-'*5} {'-'*8}  {'-'*12}")
        for _, row in redoublants.iterrows():
            cne    = str(row[cne_col]).strip()
            nom    = str(row[nom_col]).strip()    if pd.notna(row[nom_col])    else '?'
            prenom = str(row[prenom_col]).strip() if pd.notna(row[prenom_col]) else '?'
            mnv    = int(row[mnv_col])             if mnv_col and pd.notna(row[mnv_col]) else '?'
            moy    = round(float(row[moy_col]),2)  if moy_col and pd.notna(row[moy_col]) else '?'

            # Déterminer si 1A ou 2A (on cherche Redoublant_1A / Redoublant_2A si dispo)
            r1a_col = next((c for c in df.columns if '1a' in str(c).lower() and 'red' in str(c).lower()), None)
            r2a_col = next((c for c in df.columns if '2a' in str(c).lower() and 'red' in str(c).lower()), None)

            if r1a_col and r2a_col:
                r1a = str(row.get(r1a_col,'')).strip().lower() in ['oui','1','yes']
                r2a = str(row.get(r2a_col,'')).strip().lower() in ['oui','1','yes']
                if r1a and r2a:
                    statut = "RED 1A + 2A"
                elif r1a:
                    statut = "RED 1A"
                else:
                    statut = "RED 2A"
            else:
                statut = "RED (1A)"  # par défaut, données 1A

            print(f"  {cne:<12} {nom:<18} {prenom:<18} {str(mnv):>5} {str(moy):>8}  {statut}")
            all_redoublants.append({
                'Filière': filiere_label, 'CNE': cne, 'Nom': nom, 'Prénom': prenom,
                'Modules_NV': mnv, 'Moyenne_Ann': moy, 'Statut': statut
            })

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print(f"  TOTAL REDOUBLANTS : {len(all_redoublants)} étudiants sur 210")
print("=" * 80)

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("  CONDITIONS DE RÉUSSITE — SYSTÈME PFA PREDICTION")
print("=" * 80)
print("""
  ┌─────────────────────────────────────────────────────────────────────┐
  │           CONDITIONS OBLIGATOIRES pour RÉUSSIR (1A ou 2A)          │
  │                                                                     │
  │  1. Moyenne Annuelle   ≥  12.0 / 20                                │
  │  2. Modules Non Validés ≤   3  (maximum 3 modules échoués)         │
  │  3. Note PFA           ≥   12.0 / 20  (Projet Fin Année)           │
  │                                                                     │
  │  ➜ Les 3 conditions DOIVENT être respectées simultanément          │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                     RÈGLES PAR PROFIL                               │
  │                                                                     │
  │  NON-REDOUBLANT (Redoublant = Non) :                               │
  │    → Modules_Non_Validés ∈ { 0, 1, 2, 3 }                         │
  │    → Réussite si Moy ≥ 12 ET NV ≤ 3 ET PFA ≥ 12                  │
  │                                                                     │
  │  REDOUBLANT (Redoublant = Oui) :                                   │
  │    → Modules_Non_Validés ∈ { 4, 5 }  (nouveau seuil appliqué)     │
  │    → NV > 3 = ÉCHEC automatique                                    │
  │    → Même si Moy ≥ 12, les 3 conditions doivent être OK           │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                   ZONES DE DANGER (Alertes ML)                     │
  │                                                                     │
  │  ⚠️  Absences S1 > 10h  →  DANGER zone                            │
  │  ⚠️  Absences S2 > 10h  →  DANGER zone                            │
  │  ⚠️  Redoublant = Oui   →  Facteur de risque majeur               │
  │  ⚠️  Total Absences > 20h → Risque accru                          │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │            CLASSIFICATION COULEUR (Prédiction ML)                  │
  │                                                                     │
  │   🟢 VERT        : Moy ≥ 12 ET Proba ≥ 70%  → Réussite assurée    │
  │   🟡 JAUNE       : Zone intermédiaire        → Risque Modéré      │
  │   🔴 ROUGE       : Moy < 12 OU Proba < 40% → Échec probable      │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │            PRÉDICTION 3ÈME ANNÉE (Modules 3A)                      │
  │                                                                     │
  │   ✅ VERT  : Moy ≥ 12 ET 4+ modules 3A prédits validés            │
  │   ⚠️  JAUNE : Moy ≥ 12 MAIS < 4 modules validés OU alertes       │
  │   🚨 ROUGE : Moy < 10 → Échec critique                           │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
""")
