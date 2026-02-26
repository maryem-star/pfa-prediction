from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, students, grades, notifications, interventions, import_csv, dashboard, predictions

app = FastAPI(title="PFA Student Prediction API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(grades.router)
app.include_router(notifications.router)
app.include_router(interventions.router)
app.include_router(import_csv.router)
app.include_router(dashboard.router)
app.include_router(predictions.router)

@app.get("/")
def root():
    return {"message": "API opérationnelle"}