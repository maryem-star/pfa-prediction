from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect
from src.api.routes import (
    auth, students, grades, notifications,
    interventions, import_csv, dashboard, predictions
)
from src.routers import students as students_v2, recommendations
from src.utils.database import engine, Base, SessionLocal
from src.models import user as user_model, student, grade, prediction as pred_model, notification, intervention


def migrate_db():
    """Add missing columns to existing tables (MySQL + SQLite compatible)."""
    inspector = inspect(engine)
    is_mysql = str(engine.url).startswith("mysql")

    migrations = {
        "students": {
            "cne": "VARCHAR(50)" if is_mysql else "TEXT",
            "absences_s1": "FLOAT DEFAULT 0",
            "absences_s2": "FLOAT DEFAULT 0",
            "modules_non_valides": "INT DEFAULT 0",
            "redoublant": "INT DEFAULT 0",
            "photo_url": "VARCHAR(255)" if is_mysql else "TEXT",
        },
        "users": {
            "filiere": "VARCHAR(20)" if is_mysql else "TEXT",
            "student_id": "INT",
        },
        "predictions": {
            "note_predite": "FLOAT",
        },
    }

    with engine.connect() as conn:
        for table_name, columns in migrations.items():
            if table_name not in inspector.get_table_names():
                continue
            existing_cols = {c["name"] for c in inspector.get_columns(table_name)}
            for col_name, col_type in columns.items():
                if col_name not in existing_cols:
                    stmt = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"
                    try:
                        conn.execute(text(stmt))
                        conn.commit()
                        print(f"[MIGRATE] Added {table_name}.{col_name}")
                    except Exception as e:
                        print(f"[MIGRATE] Skip {table_name}.{col_name}: {e}")


def init_db():
    """Create all tables, migrate existing ones, and seed admin user."""
    Base.metadata.create_all(bind=engine)
    migrate_db()
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
                role=RoleEnum.super_admin
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