from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from src.database import SessionLocal
from src import crud, schemas, security
from src.config import SECRET_KEY, ALGORITHM
from src.security import oauth2_scheme

oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get the DB session
def get_db():
    """Функция для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get the current user from the token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Функция для получения текущего пользователя по токену."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"www-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user
