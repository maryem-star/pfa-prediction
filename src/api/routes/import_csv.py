from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.student import Student
from src.models.grade import Grade
from src.auth.dependencies import get_current_user
import pandas as pd
import io

router = APIRouter(prefix="/import", tags=["Import"])

FILIERE_MAP = {
    "genie_industriel": "GI",
    "genie_civil": "GC",
    "isic": "ISIC",
    "ccn": "CCN",
    "ccn_cybersec": "CCN",
    "ite": "2ITE",
    "ite_genie_info": "2ITE",
    "gee": "G2E",
    "gee_genie_electrique": "G2E",
}

@router.post("/students/{filiere}")
def import_students(
    filiere: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    contents = file.file.read()

    if file.filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents), header=None, skiprows=4)
        df.columns = ["CNE", "Nom", "Prenom"] + [f"col_{i}" for i in range(3, len(df.columns))]

    imported = 0
    errors = []

    for _, row in df.iterrows():
        try:
            cne = str(row.get("CNE", row.iloc[0]) if "CNE" in df.columns else row.iloc[0]).strip()
            nom = str(row.get("Nom", row.iloc[1]) if "Nom" in df.columns else row.iloc[1]).strip()
            prenom = str(row.get("Prenom", row.iloc[2]) if "Prenom" in df.columns else row.iloc[2]).strip()

            if not cne or cne == "nan" or cne == "CNE":
                continue

            existing = db.query(Student).filter(Student.cne == cne).first()
            if existing:
                continue

            student = Student(
                nom=nom,
                prenom=prenom,
                cne=cne,
                email=f"{cne}@ensa.ma",
                filiere=filiere,
                annee="1",
                semestre="S1"
            )
            db.add(student)
            db.commit()
            db.refresh(student)

            # Import S1 grades
            s1_fields = [
                ("Module_S1_1", "Mathematiques_1"),
                ("Module_S1_2", "Algorithmique_Prog"),
                ("Module_S1_3", "Architecture_Ord"),
                ("Module_S1_4", "Electronique_Num"),
                ("Module_S1_5", "Reseaux_Info_1"),
                ("Anglais_Tech_1", "Anglais_Tech_1"),
                ("Francais_Pro_1", "Francais_Pro_1"),
            ]
            for col_name, matiere in s1_fields:
                try:
                    val = row.get(col_name)
                    if val is None:
                        val = row.get(matiere)
                    if pd.notna(val):
                        grade = Grade(
                            student_id=student.id,
                            matiere=matiere,
                            note=float(val),
                            semestre="S1",
                            annee_academique="2024-2025"
                        )
                        db.add(grade)
                except Exception:
                    pass

            # Import S2 grades
            s2_fields = [
                ("Module_S2_1", "Mathematiques_2"),
                ("Module_S2_2", "Structures_Donnees"),
                ("Module_S2_3", "Systemes_Exploitation"),
                ("Module_S2_4", "Bases_Donnees"),
                ("Module_S2_5", "Reseaux_Info_2"),
                ("Anglais_Tech_2", "Anglais_Tech_2"),
                ("Francais_Pro_2", "Francais_Pro_2"),
                ("PFA_2", "PFA_2"),
            ]
            for col_name, matiere in s2_fields:
                try:
                    val = row.get(col_name)
                    if val is None:
                        val = row.get(matiere)
                    if pd.notna(val):
                        grade = Grade(
                            student_id=student.id,
                            matiere=matiere,
                            note=float(val),
                            semestre="S2",
                            annee_academique="2024-2025"
                        )
                        db.add(grade)
                except Exception:
                    pass

            db.commit()
            imported += 1

        except Exception as e:
            errors.append(str(e))
            continue

    return {
        "message": f"{imported} étudiants importés avec succès",
        "filiere": filiere,
        "errors": errors[:5] if errors else []
    }


@router.post("/seed")
def seed_from_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Import all students from data/processed/students_clean.csv into the database."""
    import os

    csv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))),
        "data", "processed", "students_clean.csv"
    )
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Fichier students_clean.csv introuvable")

    df = pd.read_csv(csv_path)
    imported = 0
    skipped = 0

    for _, row in df.iterrows():
        cne = str(row.get("CNE", "")).strip()
        if not cne or cne == "nan":
            continue

        existing = db.query(Student).filter(Student.cne == cne).first()
        if existing:
            skipped += 1
            continue

        filiere_raw = str(row.get("Filiere", "")).strip()
        filiere = FILIERE_MAP.get(filiere_raw, filiere_raw.upper() if filiere_raw else "ISIC")

        abs_s1 = float(row.get("Absences_S1", 0) or 0)
        abs_s2 = float(row.get("Absences_S2", 0) or 0)
        mnv = int(row.get("Modules_Non_Valides", 0) or 0)
        red = int(row.get("Redoublant", 0) or 0)

        student = Student(
            nom=str(row.get("Nom", "")).strip(),
            prenom=str(row.get("Prenom", "")).strip(),
            cne=cne,
            email=f"{cne}@ensa.ma",
            filiere=filiere,
            annee="1",
            semestre="S1",
            absences_s1=abs_s1,
            absences_s2=abs_s2,
            modules_non_valides=mnv,
            redoublant=red,
        )
        db.add(student)
        db.commit()
        db.refresh(student)

        # S1 grades
        s1_modules = {
            "Module_S1_1": "Mathematiques_1",
            "Module_S1_2": "Algorithmique_Prog",
            "Module_S1_3": "Architecture_Ord",
            "Module_S1_4": "Electronique_Num",
            "Module_S1_5": "Reseaux_Info_1",
            "Anglais_Tech_1": "Anglais_Tech_1",
            "Francais_Pro_1": "Francais_Pro_1",
        }
        for csv_col, matiere in s1_modules.items():
            try:
                val = row.get(csv_col)
                if pd.notna(val):
                    db.add(Grade(
                        student_id=student.id,
                        matiere=matiere,
                        note=float(val),
                        semestre="S1",
                        annee_academique="2024-2025"
                    ))
            except Exception:
                pass

        # S2 grades
        s2_modules = {
            "Module_S2_1": "Mathematiques_2",
            "Module_S2_2": "Structures_Donnees",
            "Module_S2_3": "Systemes_Exploitation",
            "Module_S2_4": "Bases_Donnees",
            "Module_S2_5": "Reseaux_Info_2",
            "Anglais_Tech_2": "Anglais_Tech_2",
            "Francais_Pro_2": "Francais_Pro_2",
            "PFA_2": "PFA_2",
        }
        for csv_col, matiere in s2_modules.items():
            try:
                val = row.get(csv_col)
                if pd.notna(val):
                    db.add(Grade(
                        student_id=student.id,
                        matiere=matiere,
                        note=float(val),
                        semestre="S2",
                        annee_academique="2024-2025"
                    ))
            except Exception:
                pass

        db.commit()
        imported += 1

    return {
        "message": f"{imported} étudiants importés, {skipped} déjà existants",
        "total_imported": imported,
        "total_skipped": skipped,
    }


@router.get("/status")
def import_status(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total = db.query(Student).count()
    par_filiere = {}
    for filiere in ["ISIC", "CCN", "2ITE", "GC", "GI", "G2E"]:
        count = db.query(Student).filter(Student.filiere == filiere).count()
        par_filiere[filiere] = count
    return {"total_etudiants": total, "par_filiere": par_filiere}
