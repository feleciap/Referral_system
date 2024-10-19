from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from src.database import engine, Base
from src.routers import auth, referral, users
from fastapi.openapi.utils import get_openapi


# Инициализация базы данных
Base.metadata.create_all(bind=engine)

# Инициализация FastAPI приложения
app = FastAPI(
    title= "Referral System API",
    description="API для управления реферальной системой с регистрациейб созданием реферальных кодов, и регистрацией по коду.",
    version="1.0.0"
)

# Разрешение CORS для доступа к API из внешних источников (если необходимо)
origins= [
    "http://localhost",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials= True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение маршрутов (роутеров)
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(referral.router, prefix="/referrals", tags=["Referrals"])

# Кастомизация OpenAPI схемы (Swagger UI)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title= "Referral System API",
        version= "1.0.0",
        description= "API для управления реферальной системой.",
        routes= app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Главная страница для проверки работы API
@app.get("/")
async def root():
    return {"message": "Referral System API is up and running"}
