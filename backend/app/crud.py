from sqlalchemy.orm import Session
from . import models
from typing import Optional

def create_file_meta(db: Session, filename: str, path: str, size: int, content_type: Optional[str]):
    f = models.FileMeta(filename=filename, path=path, size=size, content_type=content_type)
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
