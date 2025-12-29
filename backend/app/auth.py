# backend/app/auth.py

from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from . import crud
from . import security
from .schemas import LoginRequest, SignupRequest

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Signup (JSON body)
@router.post("/auth/signup")
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    from .models import User
    email = payload.email
    password = payload.password
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed = security.hash_password(password)
    username = email.split("@")[0]
    user = crud.create_user(db, username=username, email=email)
    user.hashed_password = hashed
    db.commit()
    db.refresh(user)
    return {"message": "User created", "id": user.id}

# Login (JSON body)
@router.post("/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    from .models import User
    email = payload.email
    password = payload.password
    user = db.query(User).filter(User.email == email).first()
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# OAuth2 scheme and current user dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = crud.get_user(db, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
