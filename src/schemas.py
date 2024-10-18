from datatime import datatime, timedelta
from pydantic import BaseModel, EmailStr, Field, conint, constr
from typing import List, Optional

# Базовая схема для модели пользователя
class UserBase(BaseModel):
    email: EmailStr

# Схема для создания пользователя (регистрация)
class UserCreate(UserBase):
    password: constr(min_length=6)

# Схема для отображения информации о пользователе (без пароля)
class UserResponse(UserBase):
    id: int
    created_at: datetime

class Config:
    orm_mode = True

# Схема для аутентификации пользователя
class Token(BaseModel):
    access_token: str
    token_type: str

# Схема для валидации данных токена
class TokenData(BaseModel):
    email:Optional[str] = None

# Схема для создания реферального кода
class ReferralCodeCreate(BaseModel):
    code: constr(min_length=5, max_length=10)
    expires_at: datetime = Field(..., description= "Дата и время истечения срока действия реферального кода")

# Схема для отображения реферального кода
class ReferralCodeResponse(BaseModel):
    id: int
    code: str
    expires_at: datetime
    created_at: datetime
    is_active: bool
    owner_id: int

    class Config:
        orm_mode = True

# Схема для получения реферального кода по email
class ReferralByEmailRequest(BaseModel):
    email: EmailStr

# Схема для регистрации по реферальному коду
class RegisterWithReferral(BaseModel):
    referral_code: str
    email: EmailStr
    password: constr(min_length=6)

# Схема для отображения информации о реферале
class ReferralResponse(BaseModel):
    id: int
    email: EmailStr
    referred_by: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True

# Схема для отображения списка рефералов
class ReferralListResponse(BaseModel):
    referrals: List[ReferralResponse]

    class Config:
        orm_mode = True