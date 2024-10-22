from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas
from src.dependencies import get_db, get_current_user

router = APIRouter()

@router.get("/users/me", response_model=schemas.UserResponse)
async def read_current_user(current_user: schemas.UserResponse = Depends(get_current_user)):
    """Маршрут для получения данных текущего аутентифицированного пользователя."""
    return current_user

@router.get("/users/{user_id}/referrals", response_model=List[schemas.UserResponse])
async def get_referrals(user_id: int, db: Session = Depends(get_db)):
    """Маршрут для получения списка рефералов пользователя по его ID."""
    referrals = await crud.get_referrals_by_user(db, user_id=user_id)
    if not referrals:
        raise HTTPException(status_code=404, detail="No referrals found")
    return referrals
