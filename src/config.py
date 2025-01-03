import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки базы данных для продакшена (PostgreSQL)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Пример использования других переменных
SECRET_KEY = os.getenv("SECRET_KEY", "defaultsecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 43200))