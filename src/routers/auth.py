from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src import crud, schemas, security
from src.dependencies import get_db
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)):
    """Маршрут для входа в систему и получения JWT токена."""
    user = await crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail= "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_teken = security.create_access_token(data={"sub": user.email}, expires_delta= access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Маршрут для регистрации нового пользователя."""
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user= user)    