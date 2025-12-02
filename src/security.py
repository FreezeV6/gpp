import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import List
from fastapi import HTTPException, Depends, Header

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(user_id: int, username: str, email: str, roles: List[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "roles": roles,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": now
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token wygasł")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token")


async def get_current_user(authorization: str = Header(None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=403, detail="Authorization header jest wymagany")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except (ValueError, IndexError):
        raise HTTPException(status_code=403, detail="Invalid Authorization header format")

    payload = verify_token(token)
    return payload


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if "ROLE_ADMIN" not in current_user.get("roles", []):
        raise HTTPException(status_code=403, detail="Brak dostępu - wymagana rola ROLE_ADMIN")
    return current_user

