import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import schemas, database

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


# ══════════════════════════════════════════════════════════════════════
# PASSWORD FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def verify_password(
    plain_password,
    hashed_password
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def get_password_hash(password):
    return pwd_context.hash(password)


# ══════════════════════════════════════════════════════════════════════
# JWT TOKEN
# ══════════════════════════════════════════════════════════════════════

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(
            timezone.utc
        ) + expires_delta
    else:
        expire = datetime.now(
            timezone.utc
        ) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# ══════════════════════════════════════════════════════════════════════
# CURRENT USER
# ══════════════════════════════════════════════════════════════════════

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):

    from app import crud

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email: str = payload.get("sub")

        if email is None:
            raise credentials_exception

        token_data = schemas.TokenData(
            email=email
        )

    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(
        db,
        email=token_data.email
    )

    if user is None:
        raise credentials_exception

    return user


# ══════════════════════════════════════════════════════════════════════
# ADMIN USER
# ══════════════════════════════════════════════════════════════════════

def get_current_admin_user(
    current_user: schemas.User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have privileges "
                   "to perform this action"
        )

    return current_user