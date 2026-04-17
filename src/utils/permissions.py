from fastapi import Depends, HTTPException, status
from src.models.user import RoleEnum, ROLE_FILIERES
from src.auth.dependencies import get_current_user

def get_filieres_autorisees(user) -> list | None:
    return ROLE_FILIERES.get(user.role, [])

def verifier_acces_filiere(filiere: str, user) -> bool:
    autorisees = get_filieres_autorisees(user)
    if autorisees is None:
        return True
    return filiere in autorisees

def require_roles(*roles: RoleEnum):
    def checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôles requis : {[r.value for r in roles]}"
            )
        return current_user
    return checker

def require_not_etudiant(current_user=Depends(get_current_user)):
    if current_user.role == RoleEnum.etudiant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Les étudiants n'ont pas accès à cette ressource."
        )
    return current_user