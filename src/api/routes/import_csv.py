from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.student import Student
from src.models.grade import Grade
from src.auth.dependencies import get_current_user
import pandas as pd
import io

router = APIRouter(prefix="/import", tags=["Import"])

@router.post("/students/{filiere}")
def import_students(
    filiere: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    contents = file.file.read()
    df = pd.read_excel(io.BytesIO(contents), header=None, skiprows=4)

    # Colonnes: 0=CNE, 1=Nom, 2=Prénom
    imported = 0
    errors = []

    for _, row in df.iterrows():
        try:
            cne = str(row[0]).strip()
            nom = str(row[1]).strip()
            prenom = str(row[2]).strip()

            if not cne or cne == 'nan' or cne == 'CNE':
                continue

            # Vérifier si étudiant existe déjà
            existing = db.query(Student).filter(Student.email == f"{cne}@pfa.com").first()
            if existing:
                continue

            student = Student(
                nom=nom,
                prenom=prenom,
                email=f"{cne}@pfa.com",
                filiere=filiere,
                annee="1",
                semestre="S1"
            )
            db.add(student)
            db.commit()
            db.refresh(student)

            # Importer les notes S1 (colonnes 4 à 10)
            matieres_s1 = [
                "Matiere_1", "Matiere_2", "Matiere_3",
                "Matiere_4", "Matiere_5", "Anglais", "Francais"
            ]
            for i, matiere in enumerate(matieres_s1):
                try:
                    note = float(row[4 + i])
                    if pd.notna(note):
                        grade = Grade(
                            student_id=student.id,
                            matiere=matiere,
                            note=note,
                            semestre="S1",
                            annee_academique="2024-2025"
                        )
                        db.add(grade)
                except:
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

@router.get("/status")
def import_status(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total = db.query(Student).count()
    par_filiere = {}
    for filiere in ["CCN", "Génie Civil", "Génie Industriel", "ISIC"]:
        count = db.query(Student).filter(Student.filiere == filiere).count()
        par_filiere[filiere] = count
    return {"total_etudiants": total, "par_filiere": par_filiere}