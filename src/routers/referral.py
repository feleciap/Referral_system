from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from src import schemas, crud
from src.models import User, ReferralCode
from src.database import get_db
from logging import getLogger
from typing import Dict, Any

router = APIRouter()

logger = getLogger(__name__)


@router.post("/create_referral/")
async def create_referral(email: str, db: Session = Depends(get_db)):
    try:
        referral_code = await crud.create_referral_code(db, email)
        return {"referral_codes": referral_code}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get_referral_code")
async def get_referral_code(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == email).options(selectinload(User.referral_codes)))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    referral_code_result = await db.execute(
        select(ReferralCode)
        .where(ReferralCode.owner_id == user.id, ReferralCode.is_active == True)
        .order_by(ReferralCode.created_at.desc())
    )
    
    referral_code = referral_code_result.scalars().first()
    
    if not referral_code:
        raise HTTPException(status_code=400, detail="Реферальный код не создан. Пожалуйста, создайте реферальный код.")
    
    return {"referral_code": referral_code.code}


@router.delete("/delete_referral_code/{email}", response_model=schemas.ReferralCodeResponse)
async def delete_referral_code(
    email: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    async with db.begin():
        user_stmt = select(User).filter(User.email == email)
        user_result = await db.execute(user_stmt)
        user = user_result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        stmt = select(ReferralCode).filter(
            ReferralCode.owner_id == user.id,
            ReferralCode.is_active == True
        )
        result = await db.execute(stmt)
        existing_code = result.scalars().first()

        if not existing_code:
            raise HTTPException(status_code=404, detail="Реферальный код не найден")

        existing_code.is_active = False
        
        response_data = {
            "id": existing_code.id,
            "code": existing_code.code,
            "expires_at": existing_code.expiry_date,
            "created_at": existing_code.created_at,
            "is_active": existing_code.is_active,
            "owner_id": existing_code.owner_id
        }
        
        return response_data