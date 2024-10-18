from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from src import schemas, crud, auth
from src.database import get_db

router = APIRouter()

@router.post("/create_referral_code")
async def create_referral_code(expiry_days: int, db: Session = Depends(get_db), user: schemas.User = Depends(auth.get_current_user)):
    expiry_date = datetime.utcnow() + timedelta(days= expiry_days)
    code = "####"
    return crud.create_referral_code(db, user.id, code, expiry_date)

@router.get("/get_referrals/{referrer_id}")
async def get_referrals(referrer_id: int, db: Session = Depends(get_db)):
    return crud.get_referrals_by_user(db, referrer_id)