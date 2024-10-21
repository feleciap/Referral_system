from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from src import crud, schemas, security
from src.dependencies import get_db, get_current_user
from src.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/token", response_model=schemas.Token)
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
    access_token_expires = timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    access_teken = security.create_access_token(data={"sub": user.email}, expires_delta= access_token_expires)
    return {"access_token": access_teken, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Маршрут для регистрации нового пользователя."""
    db_user = await crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user= user)    

@router.post("/referral_code", response_model=schemas.ReferralCodeResponse)
async def create_referral_code(
    referral_code_data: schemas.ReferralCodeCreate, 
    db: Session = Depends(get_db), 
    current_user: schemas.UserResponse = Depends(get_current_user)):
    """Создание реферального кода."""
    existing_code = await crud.get_active_referral_code(db, current_user.id)
    if existing_code:
        existing_code.is_active = False
        await db.commit()

    new_code = await crud.create_referral_code(db, current_user.id, referral_code_data.code, referral_code_data.expires_at)
    return new_code

@router.delete("/referral-code/{code_id}", response_model=schemas.ReferralCodeResponse)
async def delete_referral_code(
    code_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)):
    """Удаление реферального кода."""
    referral_code = await crud.get_referrals_code_by_id(db, code_id)
    if referral_code is None or referral_code.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Referral code not found or you do not have permission to delete it.")
    
    referral_code.is_active = False
    await db.commit()
    return {"detail": "Referral code deleted successfully."}

