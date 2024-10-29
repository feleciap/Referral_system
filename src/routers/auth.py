from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from src.hashing import hash_password, verify_password 
from src import crud, schemas, security
from src.dependencies import get_db, get_current_user
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(
    email: str = Form(...),
    password: str = Form(...),
    referral_code: str = Form(None),
    db: Session = Depends(get_db)
):
    # Проверка, существует ли пользователь с данным email
    db_user = await crud.get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Проверка, существует ли указанный referral_code
    referrer = None
    if referral_code:
        referrer = await crud.get_user_by_referral_code(db, referral_code)
        if not referrer:
            raise HTTPException(status_code=400, detail="Referral code does not exist")
    
    # Хешируем пароль перед сохранением
    hashed_password = hash_password(password)
    
    # Создаем объект пользователя и добавляем referral_code
    user = schemas.UserCreate(email=email, password=hashed_password, referral_code=referral_code)
    
    # Создаем нового пользователя
    new_user = await crud.create_user(db=db, user=user)

    # Если referral_code существует, увеличиваем referral_count у владельца кода
    if referrer:
        if referrer.referral_count is None:
            referrer.referral_count = 0
        referrer.referral_count += 1
        db.add(referrer)
        await db.commit()
    
    return new_user
# @router.post("/register", response_model=schemas.UserResponse)
# async def register_user(
#     email: str = Form(...),
#     password: str = Form(...),
#     referral_code: str = None,
#     db: Session = Depends(get_db)):
    
#     if await crud.get_user_by_email(db, email):
#         raise HTTPException(status_code=400, detail="Email already registered")

#     user = schemas.UserCreate(email=email, password=password)
#     # Создаем нового пользователя
#     new_user = await crud.create_user(db=db, user=user)

#     # Обработка реферального кода, если он предоставлен
#     if referral_code:
#         referrer = await crud.get_user_by_referral_code(db, referral_code)
#         if referrer:
#             # Инициализируем referral_count, если он None
#             if referrer.referral_count is None:
#                 referrer.referral_count = 0
            
#             # Увеличиваем referral_count
#             referrer.referral_count += 1
            
#             # Обновляем информацию о реферале
#             db.add(referrer)
#             await db.commit()  # Подтверждаем изменения

#     return new_user

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)):
    """Маршрут для входа и получения JWT токена с email и паролем."""
    user = await crud.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail= "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_info = await security.get_or_create_access_token(db=db, user_id=user.id)

    return { 
        "access_token": access_token_info["token"],  
        "expires_in": access_token_info["expires_in"], 
        "token_type": "bearer",
        "referral_code": user.referral_code, 
        "referral_count": user.referral_count  
        }