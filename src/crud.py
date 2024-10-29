from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from fastapi import Depends, HTTPException
from fastapi_mail import FastMail, MessageSchema
from sqlalchemy import select
from src.models import User, ReferralCode
from src.schemas import UserCreate, ReferralCodeResponse
from src.database import get_db
from datetime import datetime
from src.hashing import hash_password, verify_password
import bcrypt
import random
import string

# Получить пользователя по email
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_referral_code(db: AsyncSession, referral_code: str):
    result = await db.execute(select(User).filter(User.referral_code == referral_code))
    user = result.scalars().first()
    
    # Если пользователь не найден, возвращаем объект с пустым referral_code
    if user is None:
        return User(referral_code="")  # Или возвращайте любой другой подходящий объект
    
    return user

# Создать пользователя
async def create_user(db: AsyncSession, user: UserCreate):
    existing_user= await get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Пользователь с таким email уже существует")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(email=user.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Создать реферальный код
async def create_referral_code(db: AsyncSession, email: str):
    # Поиск пользователя по email
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    
    if user is None:
        raise ValueError("Пользователь с таким email не найден")

    # Проверка, есть ли у пользователя активный реферальный код
    existing_code = await db.execute(
        select(ReferralCode).filter(ReferralCode.owner_id == user.id, ReferralCode.is_active == True)
    )
    referral_code = existing_code.scalars().first()

    if referral_code:
        # Если активный реферальный код уже существует, возвращаем его
        return referral_code.code

    # Генерация нового реферального кода, если его нет
    referral_code_str = generate_referral_code(user.email)

    # Создание нового объекта ReferralCode и присвоение пользователю
    referral_code = ReferralCode(code=referral_code_str, owner=user)
    
    # Добавляем новый реферальный код в базу данных
    db.add(referral_code)
    await db.commit()
    await db.refresh(referral_code)
    
    return referral_code_str


# Удалить реферальный код
async def delete_referral_code(db_session, email):
    async with db_session() as session:
        referral_code = await session.execute(
            select(ReferralCode).where(ReferralCode.email == email)
        )
        existing_code = referral_code.scalars().first()
        if existing_code:
            await session.delete(existing_code)
            await session.commit()
            return {"message": "Referral code deleted successfully"}
        else:
            return {"message": "Referral code not found"}


# Получить рефералов по id пользователя
async def get_referrals_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(ReferralCode).filter(ReferralCode.owner_id ==user_id))
    return result.scalars().all()

# Аутентификация пользователя
async def authenticate_user(db: Session, email: str, password: str):
    user = await get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password): 
        return None
    return user

# # Получить активный реферальный код по id пользователя
# async def get_active_referral_code(db: AsyncSession, user_id: int):
#     result = await db.execute(select(ReferralCode).filter(ReferralCode.owner_id == user_id, ReferralCode.is_active == True))
#     return result.scalar_one_or_none()

# Получить реферальный код по id
async def get_referral_code_by_id(db: AsyncSession, code_id: int):
    result = await db.execute(select(ReferralCode).filter(ReferralCode.id == code_id))
    return result.scalar_one_or_none()

# Генерация реферального кода
def generate_referral_code(identifier: str, length: int = 8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def get_referral_code(db: AsyncSession, code_id: int):
    result = await db.execute(select(ReferralCode).filter_by(id=code_id))
    return result.scalars().first()