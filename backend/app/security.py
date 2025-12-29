# backend/app/security.py

from passlib.context import CryptContext

# Use pbkdf2_sha256 to avoid bcrypt's 72-byte limit and compatibility issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def hash_password(password: str):
    if password is None:
        password = ""
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    if plain is None:
        plain = ""
    return pwd_context.verify(plain, hashed)
