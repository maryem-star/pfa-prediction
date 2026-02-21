 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.models.notification import Notification
from src.auth.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/notifications", tags=["Notifications"])

class NotificationCreate(BaseModel):
    user_id: int
    titre: str
    message: str
    niveau: Optional[str] = "info"

@router.get("/")
def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Notification).filter(Notification.user_id == current_user.id).all()

@router.post("/")
def create_notification(data: NotificationCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notif = Notification(**data.model_dump())
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

@router.put("/{notif_id}/lu")
def mark_as_read(notif_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    notif.lu = True
    db.commit()
    return {"message": "Notification marquée comme lue"}