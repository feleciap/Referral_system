from passlib.context import CryptContext


# Создаем объект CryptContext для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для создания хеша пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Функция для проверки пароля с хешем
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)