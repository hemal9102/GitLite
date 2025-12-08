from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from . import crud
from . import models
from .database import engine, get_db, Base

# create tables (for simple demo; for real apps use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="File Directory API")

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.post("/files/", status_code=201)
async def upload_file(uploaded_file: UploadFile = File(...), db: Session = Depends(get_db)):
    # save to disk
    file_path = os.path.join(STORAGE_DIR, uploaded_file.filename)
    # ensure unique filename (simple approach)
    if os.path.exists(file_path):
        base, ext = os.path.splitext(uploaded_file.filename)
        i = 1
        while os.path.exists(os.path.join(STORAGE_DIR, f"{base}_{i}{ext}")):
            i += 1
        file_path = os.path.join(STORAGE_DIR, f"{base}_{i}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    size = os.path.getsize(file_path)
    record = crud.create_file_meta(db, filename=os.path.basename(file_path), path=file_path, size=size, content_type=uploaded_file.content_type)
    return {"id": record.id, "filename": record.filename}

@app.get("/files/")
def list_files(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return crud.list_files(db, skip=skip, limit=limit)

@app.get("/files/{file_id}")
def get_file_meta(file_id: int, db: Session = Depends(get_db)):
    f = crud.get_file(db, file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return {"id": f.id, "filename": f.filename, "size": f.size, "path": f.path, "created_at": f.created_at}

@app.delete("/files/{file_id}")
def delete_file(file_id: int, db: Session = Depends(get_db)):
    f = crud.soft_delete_file(db, file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    # optionally delete file from disk:
    try:
        if os.path.exists(f.path):
            os.remove(f.path)
    except Exception:
        pass
    return {"deleted": True}
