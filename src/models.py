from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.database import Base

class User(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key= True, index= True)
    username = Column(String, unique= True, index= True)
    email = Column(String, unique= True, index= True, nullable= False)
    hashed_password = Column(String, nullable= False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    referral_code = relationship("ReferralCode", back_populates="owner")

class ReferralCode(Base):
    __tablename__ = 'referral_codes'

    id = Column(Integer, primary_key= True, index= True)
    code = Column(String, unique= True, nullable= False)
    expiry_date = Column(DateTime, nullable= False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable= False)
    owner = relationship("User", back_populates= "referral_code")