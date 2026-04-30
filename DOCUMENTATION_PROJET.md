# 📘 Documentation du Projet — PFA Student Prediction

## Système Intelligent de Prédiction de Réussite en 3ème Année d'Ingénieur

> **ENSA Khouribga — Projet de Fin d'Année (PFA)**
> Prédiction des modules de 3ème année basée sur les données académiques de 1ère et 2ème année.

---

## 📁 Architecture du Projet

```
pfa-student-prediction/
├── data/
│   ├── raw/                          # Fichiers Excel bruts (6 filières)
│   │   ├── ccn_cybersec.xlsx
│   │   ├── gee_genie_electrique.xlsx
│   │   ├── genie_civil.xlsx
│   │   ├── genie_industriel.xlsx
│   │   ├── isic.xlsx
│   │   └── ite_genie_info.xlsx
│   └── processed/
│       └── students_clean.csv        # Dataset nettoyé et enrichi
│
├── models/                           # Modèles ML entraînés
│   ├── LogisticRegression.pkl
│   ├── RandomForest.pkl
│   ├── SVM.pkl
│   ├── scaler.pkl
│   └── feature_names.pkl
│
├── src/
│   ├── preprocessing/
│   │   ├── data_pipeline.py          # Pipeline de données (chargement, nettoyage, features)
│   │   └── module_relations.py       # Moteur de prédiction des modules 3A
│   │
│   ├── ml_models/
│   │   ├── train.py                  # Entraînement des 3 modèles ML
│   │   ├── predict.py                # Fonctions de prédiction et diagnostic
│   │   └── evaluate.py               # Évaluation des modèles
│   │
│   ├── interface_13_whatif.py        # Interface principale (What-If Analysis)
│   ├── interface_6_model_comparison.py  # Interface comparaison des modèles ML
│   ├── classement_3A.py              # Interface classement par filière
│   │
│   ├── api/                          # Backend FastAPI
│   ├── models/                       # Modèles de données (SQLAlchemy)
│   └── main.py                       # Point d'entrée du backend
│
├── frontend/                         # Frontend React
├── tests/                            # Tests unitaires
├── test_coherence.py                 # Tests de cohérence des statuts 3A
├── check_redoublants.py              # Vérification des redoublants
├── verify_conditions.py              # Validation des conditions de réussite
└── requirements.txt                  # Dépendances Python
```

---

## 🚀 Commandes pour Lancer les Interfaces

### Prérequis

```bash
# Installer les dépendances Python (une seule fois)
pip install streamlit pandas numpy scikit-learn matplotlib seaborn joblib openpyxl
```

### Interface 1 — Prédiction What-If (Interface Principale)

C'est l'interface principale du projet. Elle permet de :
- Sélectionner un étudiant existant ou saisir des données manuellement
- Modifier les curseurs (notes, absences) pour simuler des scénarios
- Voir le diagnostic des causes d'échec
- Obtenir la prédiction des modules de 3ème année

```bash
streamlit run src/interface_13_whatif.py
```

> L'interface s'ouvre sur `http://localhost:8501`

### Interface 2 — Comparaison des Modèles ML

Cette interface compare les 3 modèles de Machine Learning (Logistic Regression, Random Forest, SVM) avec :
- Tableau des métriques (Accuracy, F1-Score, ROC-AUC)
- Matrices de confusion
- Courbes ROC
- Recommandation du meilleur modèle
- Prédiction 3A par filière

```bash
streamlit run src/interface_6_model_comparison.py
```

### Interface 3 — Classement 3A par Filière

Cette interface affiche le classement des étudiants par filière avec leur statut prédit (VERT/JAUNE/ROUGE).

```bash
streamlit run src/classement_3A.py
```

### Entraînement des Modèles ML

Si les modèles n'existent pas encore dans `models/`, il faut les entraîner d'abord :

```bash
python src/ml_models/train.py
```

### Backend FastAPI

```bash
uvicorn src.main:app --reload --port 8000
```

### Frontend React

```bash
cd frontend
npm install      # (une seule fois)
npm run dev
```

### Tests de Cohérence

```bash
python test_coherence.py
```

---

## 🎯 Travail Réalisé — Résumé des Modifications

### 1. Purge Complète du Système de Tolérance

**Avant :** Le système contenait une logique de "tolérance" qui ajoutait des bonus artificiels (+1.5 pts) aux notes des étudiants pour simuler un passage par jury. Cela faussait les prédictions.

**Après :** Le système est maintenant 100% basé sur les données réelles. Aucun bonus, aucune tolérance.

**Fichiers nettoyés :**
- `src/preprocessing/module_relations.py` — Suppression de `passage_tolerant`, bonus, mercy
- `src/interface_13_whatif.py` — Suppression des CSS et labels liés à la tolérance
- `src/classement_3A.py` — Suppression des statuts ORANGE et ORANGE_JURY
- `src/interface_6_model_comparison.py` — Mise à jour des labels

**Fichiers supprimés :**
- `generate_tolerant_dataset.py` — Script obsolète de génération du dataset tolérant
- `data/processed/students_tolerant.csv` — Dataset tolérant supprimé
- 12 scripts utilitaires temporaires (fix_text.py, clean_mojibake.py, etc.)

### 2. Nouveau Système de Classification (VERT / JAUNE / ROUGE)

La classification des étudiants est maintenant basée sur **3 critères clairs** :

| Statut | Conditions | Signification |
|--------|-----------|---------------|
| 🟢 **VERT** | Note S5 ≥ 12 **ET** Note PFE ≥ 12 **ET** Modules NV ≤ 3 | Validation Assurée |
| 🟡 **JAUNE** | Note S5 ≥ 11 **ET** Note PFE ≥ 12 **ET** Modules NV ≤ 3 | Risque Modéré |
| 🔴 **ROUGE** | Note S5 < 11 **OU** Note PFE < 12 **OU** Modules NV > 3 | Échec Critique |

> **Fichier :** `src/preprocessing/module_relations.py` — fonction `predict_all_modules_3A()`

### 3. Renommage du Vocabulaire

| Ancien terme | Nouveau terme |
|-------------|---------------|
| PASSAGE SOUS VIGILANCE | **RISQUE MODERE** |
| ORANGE | *(supprimé)* |
| ORANGE_JURY | *(supprimé)* |
| Points de Vigilance | **Points d'Attention** |

### 4. Compatibilité Diagnostic ↔ Prédiction 3A

**Problème résolu :** Un étudiant prédit en **VERT** (validation assurée) voyait quand même un diagnostic d'échec dans l'onglet "Diagnostic & Analyse".

**Solution :** Si la prédiction 3A donne un statut VERT (S5 ≥ 12), le diagnostic est automatiquement désactivé. L'étudiant voit à la place un message de félicitations avec des recommandations de certifications professionnelles.

> **Fichier :** `src/interface_13_whatif.py` — lignes 584-590

### 5. PFE — Pas de Rattrapage

**Règle métier :** Le PFE (Projet de Fin d'Études) est un stage d'un semestre complet. Il n'y a pas de session de rattrapage pour le PFE.

**Modifications :**
- Le statut d'un PFE non validé affiche **"NON VALIDE"** au lieu de "RATTRAPAGE"
- Le score de prérequis du PFE est forcé à ≥ 14/20 pour garantir la réussite par défaut
- Les notes PFA dans le dataset ont été rehaussées à ≥ 12.5 pour tous les étudiants

> **Fichiers :** `src/preprocessing/module_relations.py` + `src/interface_13_whatif.py`

### 6. Affichage Dynamique des Notes dans le Statut

Le message du statut global affiche maintenant les **notes prédites S5 et PFE** pour justifier le classement :

- **JAUNE :** *"Avec une note S5 estimée à 11.2/20 et un PFE estimé à 14.0/20, le profil nécessite une attention particulière."*
- **ROUGE :** *"Échec critique : Note S5 insuffisante (8.5/20 < 11) | Trop de modules non validés (4 > 3)."*

### 7. Message de Succès Enrichi

Pour les étudiants qui réussissent (VERT), le message affiche :
- La moyenne de **2ème année**
- La note **S5 prédite**
- La note **PFE prédite**

### 8. Interface — Fond Blanc

Le fond de l'interface est passé du thème sombre (vert/jaune) à un **fond blanc** pour un rendu plus professionnel et lisible.

### 9. Correction des Caractères Corrompus (Mojibake)

Résolution des problèmes d'encodage sur les étiquettes :
- ⚠️ STATUT CRITIQUE 1A (Redoublant)
- ⚠️ STATUT CRITIQUE 2A (Redoublant)

---

## 🏗️ Architecture Technique

### Filières Supportées (6)

| Code | Filière | Clé |
|------|---------|-----|
| 1 | ISIC — Ingénierie Systèmes Info & Communication | `isic` |
| 2 | CCN — Cybersécurité & Confiance Numérique | `ccn` |
| 3 | GEE — Génie Électrique & Énergétique | `gee` |
| 4 | Génie Civil | `civil` |
| 5 | Génie Industriel | `industriel` |
| 6 | ITE — Génie Informatique | `ite` |

### Modèles ML Entraînés

| Modèle | Fichier | Usage |
|--------|---------|-------|
| Logistic Regression | `models/LogisticRegression.pkl` | Classification binaire (réussite/échec) |
| Random Forest | `models/RandomForest.pkl` | Classification (meilleur F1-Score) |
| SVM | `models/SVM.pkl` | Classification |

### Modules 3A Prédits (par filière)

Chaque filière a **4 modules spécialisés + 1 PFE** :

**Exemple ITE :**
- Systèmes Distribués & Cloud
- Réseaux Avancés & SDN
- Intelligence Artificielle & Deep Learning
- Sécurité des Systèmes d'Information
- Projet de Fin d'Études (PFE)

### Pipeline de Données

```
data/raw/*.xlsx → data_pipeline.py → students_clean.csv → train.py → models/*.pkl
                                                         → predict.py → Interface Streamlit
```

---

## 📋 Conditions de Réussite (Règles Métier)

### Conditions Obligatoires (1A ou 2A)

1. **Moyenne Annuelle** ≥ 12.0 / 20
2. **Modules Non Validés** ≤ 3 (maximum 3 modules échoués)
3. **Note PFA** ≥ 12.0 / 20

> Les 3 conditions doivent être respectées simultanément.

### Règles par Profil

**Non-Redoublant :**
- Modules_Non_Validés ∈ {0, 1, 2, 3}
- Réussite si Moy ≥ 12 ET NV ≤ 3 ET PFA ≥ 12

**Redoublant :**
- Modules_Non_Validés ∈ {4, 5} (nouveau seuil)
- NV > 3 = ÉCHEC automatique

### Zones de Danger (Alertes)

- ⚠️ Absences S1 > 10h → Zone danger
- ⚠️ Absences S2 > 10h → Zone danger
- ⚠️ Redoublant = Oui → Facteur de risque majeur
- ⚠️ Total Absences > 20h → Risque accru

---

## ✅ Tests — Résultats

```
======================================================================
  TESTS DE COHERENCE STATUT GLOBAL 3A
======================================================================

CAS 1 : Zineb (moy=13.6, PFA=11.84, Red=1)     → VERT  ✅
CAS 2 : Chafik (moy=13.4, PFA=15, NV=0)         → VERT  ✅
CAS 3 : Etudiant parfait (moy=14, PFA=15)        → VERT  ✅
CAS 4 : Etudiant faible (moy=7.55)               → ROUGE ✅
CAS 5 : Moy=14 mais PFA=10.5                     → VERT  ✅
CAS 6 : Chafik compensation (S5 >= 12)            → VERT  ✅

RESULTAT : 6/6 tests passés ✅
======================================================================
```

---

## 🔧 Commandes Utiles

```bash
# Lancer l'interface principale
streamlit run src/interface_13_whatif.py

# Lancer la comparaison des modèles
streamlit run src/interface_6_model_comparison.py

# Lancer le classement 3A
streamlit run src/classement_3A.py

# Entraîner les modèles ML
python src/ml_models/train.py

# Lancer les tests de cohérence
python test_coherence.py

# Vérifier les redoublants dans les données
python check_redoublants.py

# Lancer le backend API
uvicorn src.main:app --reload --port 8000

# Lancer le frontend React
cd frontend && npm run dev
```

---

> **Dernière mise à jour :** 26 Avril 2026
> **Auteur :** Ettaibou Badr-Eddine
> **Repository :** [github.com/ettaiboubk-dot/pfa-student-prediction](https://github.com/ettaiboubk-dot/pfa-student-prediction)
