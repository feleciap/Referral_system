from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from datetime import datetime, timedelta
from src import schemas, crud, security
from src.models import User 
from src.database import get_db
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

router = APIRouter()

@router.post("/create_referral_code")
async def create_referral_code(
    referral_code_data: schemas.ReferralCodeCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(security.get_current_user)):
    
    existing_code = await crud.get_active_referral_code(db, current_user.id)
    if existing_code:
        raise HTTPException(status_code=400, detail="У вас уже есть активный реферальный код")
    
    expiry_date = referral_code_data.expiry_date or datetime.utcnow() + timedelta(days=30)
    if expiry_date <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Неправильный срок годности")
    
    new_code = await crud.create_referral_code(db=db, user_id=current_user.id, code=referral_code_data.code, expiry=expiry_date)
    return new_code


@router.post("/get_referral_code")
async def get_referral_code(email: str, db: AsyncSession = Depends(get_db)):
    # Найдите пользователя по email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Подготовка сообщения для отправки email
    message = MessageSchema(
        subject="Ваш реферальный код",
        recipients=[email],
        body=f"Ваш реферальный код: {user.referral_code}",
        subtype="html"
    )
    
    # Отправка email
    fm = FastMail(conf)
    await fm.send_message(message)
    
    return {"detail": "Referral code sent to your email"}

@router.delete("/delete_referral_code", response_model=schemas.ReferralCodeResponse)
async def delete_referral_code(current_user: schemas.UserResponse = Depends(security.get_current_user), db: Session = Depends(get_db)):
    deleted_code = await crud.delete_active_referral_code(db, current_user.id)
    if not deleted_code:
        raise HTTPException(status_code=404, detail="У вас нет активного реферального кода")
    return {"detail": "Реферальный код успешно удалён"}
