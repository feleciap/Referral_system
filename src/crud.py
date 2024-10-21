from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import text
from sqlalchemy.future import select
from src import models
from src.models import User, ReferralCode
from src.schemas import UserCreate
from datetime import datetime
from src.hashing import hash_password, verify_password
import bcrypt

# Получить пользователя по email
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalar_one_or_none()

# Получить пользователя по username (асинхронно)
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).filter(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none() 

# Создать пользователя
async def create_user(db: AsyncSession, user: UserCreate):
    existing_user= await get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(email=user.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Создать реферальный код
async def create_referral_code(db: AsyncSession, user_id: int, code: str, expiry: datetime):
    db_code = ReferralCode(owner_id= user_id, code= code, expiry_date= expiry)
    db.add(db_code)
    await db.commit()
    await db.refresh(db_code)
    return db_code

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

# Получить активный реферальный код по id пользователя
async def get_active_referral_code(db: AsyncSession, user_id: int):
    result = await db.execute(select(ReferralCode).filter(ReferralCode.owner_id == user_id, ReferralCode.is_active == True))
    return result.scalar_one_or_none()

# Создать реферальный код
async def create_referral_code(db: AsyncSession, user_id: int, code: str, expiry: datetime):
    existing_code = await db.execute(select(ReferralCode).filter(ReferralCode.owner_id == user_id, ReferralCode.expiry_date > datetime.utcnow()))
    if existing_code.scalar_one_or_none() is not None:
        raise ValueError("У вас уже есть активный реферальный код")

    db_code = ReferralCode(owner_id=user_id, code=code, expiry_date=expiry)
    db.add(db_code)
    await db.commit()
    await db.refresh(db_code)
    return db_code

# Получить реферальный код по id
async def get_referral_code_by_id(db: AsyncSession, code_id: int):
    return await db.execute(select(ReferralCode).filter(ReferralCode.id == code_id)).scalar_one_or_none()