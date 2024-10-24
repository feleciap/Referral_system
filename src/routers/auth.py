from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src import crud, schemas, security
from src.dependencies import get_db, get_current_user
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

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
        "access_token": access_token_info["token"],  # Возвращаем токен
        "expires_in": access_token_info["expires_in"],  # Возвращаем время жизни токена в секундах
        "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Маршрут для регистрации нового пользователя."""
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user= user)    
