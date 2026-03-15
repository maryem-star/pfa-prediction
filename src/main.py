from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import auth, students, grades, notifications, interventions, import_csv, dashboard, predictions
from src.utils.database import engine, Base, SessionLocal
from src.models import user as user_model, student, grade, prediction as pred_model, notification, intervention


def init_db():
    """Crée toutes les tables et l'utilisateur admin au démarrage."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from src.models.user import User, RoleEnum
        from passlib.context import CryptContext
        existing = db.query(User).filter(User.email == "admin@pfa.com").first()
        if not existing:
            pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin = User(
                nom="Admin", prenom="PFA",
                email="admin@pfa.com",
                hashed_password=pwd.hash("admin123"),
                role=RoleEnum.admin
            )
            db.add(admin)
            db.commit()
            print("[STARTUP] Admin user created: admin@pfa.com / admin123")
        else:
            print("[STARTUP] Admin user already exists.")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="PFA Student Prediction API", lifespan=lifespan)

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
