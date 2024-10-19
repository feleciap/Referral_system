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
    result = db.execute(query)
    return result.scalar_one_or_none() 

# Создать пользователя
def create_user(db:Session, user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(email=user.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Создать реферальный код
def create_referral_code(db: Session, user_id: int, code: str, expiry: datetime):
    db_code = ReferralCode(owner_id= user_id, code= code, expiry_date= expiry)
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

# Получить рефералов по id пользователя
def get_referrals_by_user(db: Session, user_id: int):
    return db.query(ReferralCode).filter(ReferralCode.owner_id == user_id).all()

# Аутентификация пользователя
async def authenticate_user(db: Session, username: str, password: str):
    user = await get_user_by_username(db, username)
    if user is None or not verify_password(password, user.hashed_password): 
        return None
    return user