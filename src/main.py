from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import (
    auth, students, grades, notifications,
    interventions, import_csv, dashboard, predictions
)
from src.routers import students as students_v2, recommendations

app = FastAPI(title="PFA Student Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Anciens routers
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(grades.router)
app.include_router(notifications.router)
app.include_router(interventions.router)
app.include_router(import_csv.router)
app.include_router(dashboard.router)
app.include_router(predictions.router)

# Nouveaux routers avec rôles
app.include_router(students_v2.router)
app.include_router(recommendations.router)


@app.get("/")
def root():
    return {"message": "API opérationnelle"}