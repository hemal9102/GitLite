from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from . import crud
from . import models
from .database import engine, get_db, Base, SessionLocal
from .auth import router as auth_router, get_current_user
from . import security

# create tables (for simple demo; for real apps use Alembic)
Base.metadata.create_all(bind=engine)

# --- create default admin user when env provided (useful for docker) ---
def _create_default_admin_if_missing():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_email or not admin_password:
        return
    from .models import User

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == admin_email).first():
            return
        username = admin_email.split("@")[0]
        user = crud.create_user(db, username=username, email=admin_email)
        user.hashed_password = security.hash_password(admin_password)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

_create_default_admin_if_missing()

app = FastAPI(title="File Directory API")

# Configure CORS (make origins configurable via ALLOW_ORIGINS env var)
# ALLOW_ORIGINS can be a comma-separated list, or '*' to allow all origins.
allow_origins_env = os.getenv("ALLOW_ORIGINS")
if allow_origins_env:
    if allow_origins_env.strip() == "*":
        allow_origins = ["*"]
    else:
        allow_origins = [o.strip() for o in allow_origins_env.split(",") if o.strip()]
else:
    # sensible defaults for local development
    allow_origins = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8080",
        "https://hemal9102.github.io"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# mount auth router
app.include_router(auth_router)

# Serve frontend assets under /static and serve index.html at root
FRONTEND_CANDIDATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
REPO_ROOT_CANDIDATE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = None
if os.path.isdir(FRONTEND_CANDIDATE):
    FRONTEND_DIR = FRONTEND_CANDIDATE
elif os.path.isfile(os.path.join(REPO_ROOT_CANDIDATE, "index.html")):
    FRONTEND_DIR = REPO_ROOT_CANDIDATE

if FRONTEND_DIR and os.path.isdir(FRONTEND_DIR):
    # mount static assets at /static to avoid overshadowing API routes
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="frontend_static")

    # serve index.html at root
    @app.get("/", include_in_schema=False)
    def serve_index():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Index not found")

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)

@app.post("/files/", status_code=201)
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user), db: Session = Depends(get_db)):
    # save to disk
    file_path = os.path.join(STORAGE_DIR, file.filename)
    # ensure unique filename (simple approach)
    if os.path.exists(file_path):
        base, ext = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(os.path.join(STORAGE_DIR, f"{base}_{i}{ext}")):
            i += 1
        file_path = os.path.join(STORAGE_DIR, f"{base}_{i}{ext}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    size = os.path.getsize(file_path)
    record = crud.create_file_meta(db, filename=os.path.basename(file_path), path=file_path, size=size, content_type=file.content_type, owner_id=user.id)
    return {"id": record.id, "filename": record.filename, "owner_id": record.owner_id}

@app.get("/files/")
def list_files(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.FileMeta).filter(models.FileMeta.owner_id == user.id, models.FileMeta.is_deleted == False).all()

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

# Serve file download
@app.get("/files/download/{file_id}")
def download_file(file_id: int, db: Session = Depends(get_db)):
    f = crud.get_file(db, file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.exists(f.path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return FileResponse(f.path, media_type='application/octet-stream', filename=f.filename)

# --- Users endpoints (kept for admin use) ---
@app.post("/users/", status_code=201)
def create_user(username: str = Form(...), email: str | None = Form(None), db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    u = crud.create_user(db, username=username, email=email)
    return {"id": u.id, "username": u.username}

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = crud.get_user(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": u.id, "username": u.username, "email": u.email}

@app.get("/users/")
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    users = crud.list_users(db, skip=skip, limit=limit)
    return users
