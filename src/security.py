from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from src import models, crud
from datetime import datetime, timedelta
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "token")

# Загрузите конфигурацию из переменных окружения
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создает и возвращает новый JWT-токен."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_or_create_access_token(db: AsyncSession, user_id: int):
    """Получает существующий токен пользователя или создает новый."""
    # Проверяем, существует ли токен для пользователя, который еще не истек
    result = await db.execute(
        select(models.UserToken).where(
            models.UserToken.user_id == user_id,
            models.UserToken.expiration > datetime.utcnow()
        )
    )
    
    token_data = result.scalar_one_or_none()
    # Если токен найден и он еще не истек, возвращаем его
    if token_data:
        # return token_data.token
        time_left = token_data.expiration - datetime.utcnow()
        return {"token": token_data.token, "expires_in": time_left.days}


    # Если токен не найден, создаем новый
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)},  
        expires_delta=access_token_expires
    )

    # Сохраняем новый токен в базе данных
    new_token_data = models.UserToken(
        user_id=user_id,
        token=access_token,
        expiration=datetime.utcnow() + access_token_expires
    )
    db.add(new_token_data)
    await db.commit()

    return {"token": access_token, "expires_in": access_token_expires.days}


# def get_or_create_access_token(db: Session, user_id: int):
#     # to_encode = data.copy()
#     # if expires_delta:
#     #     expire = datetime.utcnow() + expires_delta
#     # else:
#     #     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     # to_encode.update({"exp": expire})
#     # return jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
#     token_data = db.query(models.UserToken).filter(
#         models.UserToken.user_id == user_id,
#         models.UserToken.expiration > datetime.utcnow()
#     ).first()

#     if token_data:
#         # Если токен найден и не истек, возвращаем его
#         return token_data.token

#     # Иначе создаем новый токен
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = security.get_or_create_access_token(
#         user_id= user_id, 
#         expires_delta=access_token_expires
#     )

#     # Сохраняем новый токен в базе данных
#     new_token_data = models.UserToken(
#         user_id=user_id,
#         token=access_token,
#         expiration=datetime.utcnow() + access_token_expires
#     )
#     db.add(new_token_data)
#     db.commit()

#     return access_token

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return await crud.get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
