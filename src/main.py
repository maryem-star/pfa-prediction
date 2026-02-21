from fastapi import FastAPI
from src.api.routes import auth, students, grades, notifications, interventions, import_csv

app = FastAPI(title="PFA Student Prediction API")

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(grades.router)
app.include_router(notifications.router)
app.include_router(interventions.router)
app.include_router(import_csv.router)

@app.get("/")
def root():
    return {"message": "API opérationnelle"}