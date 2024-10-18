from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas
from src.dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Маршрут для регистрации нового пользователя."""
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail= "Email already registered")
    return await crud.create_user(db=db, user=user)

@router.get("/users/me", response_model=schemas.UserResponse)
async def read_current_user(current_user: schemas.UserResponse = Depends(get_current_user)):
    """Маршрут для получения данных текущего аутентифицированного пользователя."""
    return current_user

@router.get("/users/{user_id}/referrals", response_model=List[schemas.UserResponse])
async def get_referrals(user_id: int, db: Session = Depends(get_db)):
    """Маршрут для получения списка рефералов пользователя по его ID."""
    referrals = await crud.get_referrals_by_referrer(db, user_id=user_id)
    if not referrals:
        raise HTTPException(status_code=404, detail="No referrals found")
    return referrals