from sqlalchemy.orm import Session
from src.models import User, ReferralCode
from src.schemas import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db:Session, user: UserCreate):
    db_user = User(email= user.email, hashed_password = user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_referral_code(db: Session, user_id: int, code: str, expiry: datetime):
    db_code = ReferralCode(owner_id= user_id, code= code, expiry_date= expiry)
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

def get_referrals_by_user(db: Session, user_id: int):
    return db.query(ReferralCode).filter(ReferralCode.owner_id == user_id).all()