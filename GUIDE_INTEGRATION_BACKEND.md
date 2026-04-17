# 🚀 Guide d'Intégration du Machine Learning dans le Backend

Salut ! 👋
Si tu es en charge de la partie Backend (FastAPI), ce guide est pour toi.
Nos modèles d'Intelligence Artificielle (Random Forest) ont été entraînés avec succès (Précision > 97%). Ton rôle maintenant est simplement de les **charger** et de les **appeler** quand un étudiant a besoin d'une prédiction (calcul de risque : Vert, Jaune ou Rouge).

Voici les étapes simples à suivre pour intégrer cela proprement dans le projet !

---

## Étape 1 : Vérifier les fichiers d'Intelligence Artificielle

Assure-toi que le dossier `models/` à la racine de ce dossier contient bien ces trois fichiers générés par l'entraînement :
- `RandomForest.pkl` (L'algorithme IA entraîné)
- `scaler.pkl` (L'outil pour mettre les notes à la bonne échelle pour l'IA)
- `feature_names.pkl` (La liste et l'ordre exact des moyennes attendues par l'IA)

> 💡 **Info** : Ces fichiers contiennent "le cerveau" pré-entraîné. Tu n'as pas besoin de les modifier ni de relancer l'entraînement.

## Étape 2 : Où mettre le code de prédiction ?

Pour garder le code propre (Architecture MVC / Hexagonale), ne mets pas directement l'IA dans tes routes (`routes/`). 
Utilise ou crée un service dédié au Machine Learning. Par exemple : `src/services/prediction_service.py` ou `src/ml_models/predict.py`.

## Étape 3 : Charger l'IA (Une seule fois au démarrage)

Le chargement d'un modèle IA prend un peu de temps. **Il faut donc le charger une seule fois au lancement du serveur FastAPI**, et non à chaque requête web.

```python
import joblib
import numpy as np

# A mettre idealement dans un bloc "on_startup" de FastAPI ou via un Singleton
class MLService:
    def __init__(self):
        # On charge nos modèles depuis le disque
        self.model = joblib.load('models/RandomForest.pkl')
        self.scaler = joblib.load('models/scaler.pkl')
        self.feature_names = joblib.load('models/feature_names.pkl')
        print("✅ Modèles IA chargés et prêts !")
        
ml_service = MLService() # L'instance prête à être utilisée
```

## Étape 4 : Faire une prédiction pour un étudiant

Voici la fonction pour prendre les notes d'un étudiant depuis la base de données (MySQL) et lui calculer sa couleur de risque.

```python
def predict_student_risk(notes_etudiant: list[float]) -> dict:
    \"\"\"
    Exemple: notes_etudiant = [12, 15, 10, 9, 13, 14, 11] (les 7 matières)
    \"\"\"
    # 1. Mise à l'échelle (pour que l'IA puisse lire les notes correctement)
    features_transformees = ml_service.scaler.transform([notes_etudiant])
    
    # 2. On demande à l'IA la probabilité (la "chance" de réussir)
    probabilite = ml_service.model.predict_proba(features_transformees)[0].max()
    pourcentage = round(probabilite * 100, 2)
    
    # 3. On déduit la couleur de risque (Rouge = Danger, Jaune = Rattrapage, Vert = Succès)
    couleur = "ROUGE"
    if probabilite >= 0.60:
        couleur = "VERT"
    elif probabilite >= 0.40:
        couleur = "JAUNE"
        
    return {
        "status_couleur": couleur,
        "probabilite_succes_pourcent": pourcentage
    }
```

## Étape 5 : L'utiliser dans tes Routes (Endpoints)

Maintenant, tu peux utiliser cette fonction facilement dans n'importe quel Endpoint FastAPI lorsque le Frontend te demande une prédiction.

```python
from fastapi import APIRouter
# Importe ton service ici

router = APIRouter()

@router.get("/students/{student_id}/prediction")
def get_prediction(student_id: int):
    # 1. Cherche l'étudiant et ses notes dans ta base SQL
    notes = database.get_student_grades(student_id) 
    
    # 2. Utilise le service ML pour deviner son avenir !
    resultat = predict_student_risk(notes)
    
    # 3. Renvoie ça proprement au Front-End Angular/React
    return resultat
```

---
**C'est tout !** 🚀
Si tout fonctionne bien, l'API renverra un JSON comme celui-ci au frontend :
```json
{
  "status_couleur": "VERT",
  "probabilite_succes_pourcent": 85.5
}
```
Bon dev ! 💻
