from app.core.config import settings
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import hashlib, secrets
from jose import jwt
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ---------- simple password hashing ----------
def _hash(password: str, salt: str = None):
    if not salt:
        salt = secrets.token_hex(16)
    return hashlib.sha256((password + salt).encode()).hexdigest(), salt

# ---------- get users collection ----------
def _get_users(request: Request):
    return request.app.state.db["users"]

# ---------- Pydantic models ----------
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ---------- dependency ----------
async def get_current_user(token: str = Depends(oauth2_scheme), request: Request = None):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except:
        raise HTTPException(401, "Invalid token")
    users = _get_users(request)
    user = await users.find_one({"email": payload["sub"]})
    if not user:
        raise HTTPException(401, "User not found")
    user["_id"] = str(user["_id"])
    return user

# ---------- register ----------
@router.post("/register")
async def register(data: UserCreate, request: Request):
    users = _get_users(request)
    if await users.find_one({"email": data.email}):
        raise HTTPException(400, "Email already registered")
    hashed, salt = _hash(data.password)
    now = datetime.utcnow()
    doc = {
        "email": data.email,
        "username": data.username,
        "hashed_password": hashed,
        "salt": salt,
        "full_name": data.full_name or "",
        "streak": 0,
        "daily_card_limit": 20,
        "target_retention": 0.9,
        "created_at": now,
        "updated_at": now
    }
    result = await users.insert_one(doc)
    token = jwt.encode(
        {"sub": data.email, "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"_id": str(result.inserted_id), "email": data.email, "username": data.username}
    }

# ---------- login ----------
@router.post("/login")
async def login(data: UserLogin, request: Request):
    users = _get_users(request)
    user = await users.find_one({"email": data.email})
    if not user:
        raise HTTPException(401, "Invalid email or password")
    # handle users without salt (old data) – but we deleted them, so this is safe
    if "salt" not in user:
        raise HTTPException(401, "User record corrupted. Please register again.")
    hashed, _ = _hash(data.password, user["salt"])
    if hashed != user["hashed_password"]:
        raise HTTPException(401, "Invalid email or password")
    token = jwt.encode(
        {"sub": data.email, "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"_id": str(user["_id"]), "email": user["email"], "username": user["username"]}
    }

# ---------- get current user ----------
@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user