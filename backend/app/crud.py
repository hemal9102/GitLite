from sqlalchemy.orm import Session
from . import models
from typing import Optional

def create_file_meta(db: Session, filename: str, path: str, size: int, content_type: Optional[str], owner_id: Optional[int] = None):
    f = models.FileMeta(filename=filename, path=path, size=size, content_type=content_type, owner_id=owner_id)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f

def get_file(db: Session, file_id: int):
    return db.query(models.FileMeta).filter(models.FileMeta.id == file_id, models.FileMeta.is_deleted == False).first()

def list_files(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.FileMeta).filter(models.FileMeta.is_deleted == False).offset(skip).limit(limit).all()

def soft_delete_file(db: Session, file_id: int):
    f = db.query(models.FileMeta).filter(models.FileMeta.id == file_id).first()
    if f:
        f.is_deleted = True
        db.commit()
    return f

# --- Users CRUD ---

def create_user(db: Session, username: str, email: Optional[str] = None):
    u = models.User(username=username, email=email)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def list_users(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.User).offset(skip).limit(limit).all()

