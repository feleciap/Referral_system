from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from src.hashing import hash_password 
from src import crud, schemas, security
from src.dependencies import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(
    email: str = Form(...),
    password: str = Form(...),
    referral_code: str = Form(None),
    db: Session = Depends(get_db)
):
    db_user = await crud.get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    referrer = None
    if referral_code:
        referrer = await crud.get_user_by_referral_code(db, referral_code)
        if not referrer:
            raise HTTPException(status_code=400, detail="Referral code does not exist")
    
    hashed_password = hash_password(password)
    
    user = schemas.UserCreate(email=email, password=hashed_password, referral_code=referral_code)
    
    new_user = await crud.create_user(db=db, user=user)

    if referrer:
        if referrer.referral_count is None:
            referrer.referral_count = 0
        referrer.referral_count += 1
        db.add(referrer)
        await db.commit()
    
    return new_user


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