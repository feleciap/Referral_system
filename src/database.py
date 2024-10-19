# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# import os
# from dotenv import load_dotenv


# # Загрузка переменных окружения из .env файла
# load_dotenv()

# # Получение настроек подключения к базе данных из .env файла
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://feleciap:123@localhost/warehouse")

# # Создание движка SQLAlchemy для подключения к базе данных
# engine = create_async_engine(DATABASE_URL, echo=True)

# # Создание базы данных моделей с использованием декларативного стиля
# Base = declarative_base()

# # Создание фабрики сессий для работы с базой данных
# SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine, class_=AsyncSession)

# # Зависимость для получения сессии базы данных для использования в запросах
# async def get_db():
#     database = SessionLocal()
#     try:
#         yield database
#     finally:
#         await database.close()
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Строка подключения с асинхронным драйвером asyncpg
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://feleciap:123@localhost/warehouse")

# Создание асинхронного движка SQLAlchemy для подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание базы данных моделей с использованием декларативного стиля
Base = declarative_base()

# Создание асинхронной фабрики сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Зависимость для получения асинхронной сессии базы данных для использования в запросах
async def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        await database.close()  # Асинхронное закрытие сессии
