from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv


# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение настроек подключения к базе данных из .env файла
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://feleciap:123@localhost/warehouse")

# Создание движка SQLAlchemy для подключения к базе данных
engine = create_engine(DATABASE_URL)

# Создание базы данных моделей с использованием декларативного стиля
Base = declarative_base()

# Создание фабрики сессий для работы с базой данных
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind= engine)

# Зависимость для получения сессии базы данных для использования в запросах
def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()