# Referral System API

API для управления системой реферальных кодов с использованием FastAPI, JWT-аутентификации и базы данных PostgreSQL.

## Оглавление
- [Описание проекта](#описание-проекта)
- [Стек технологий](#стек-технологий)
- [Установка и запуск](#установка-и-запуск)
- [Настройка переменных окружения](#настройка-переменных-окружения)
- [Конечные точки API](#конечные-точки-api)

## Описание проекта

Этот проект представляет собой систему реферальных кодов, которая позволяет пользователям регистрироваться и получать доступ к API. Пользователи могут делиться реферальными кодами, приглашать новых пользователей и отслеживать количество приглашенных ими людей.

## Стек технологий

- **Backend**: FastAPI
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (JSON Web Token)
- **Миграции базы данных**: Alembic

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone git@github.com:feleciap/Referral_system.git
cd referral_system
```

### 2. Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  
venv\Scripts\activate # На Windows
```

### 3. Установите зависимости:

```bash
pip install -r requirements.txt
```


### 4. Настройте базу данных:

 `Для PostgreSQL создайте базу данных и обновите строку подключения в database.py`

 ## Настройка переменных окружения

* Создайте файл .env в корне проекта и добавьте следующие переменные окружения:

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/your_database
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```
* Примечание: Замените username, password, и your_database на соответствующие данные вашей базы данных PostgreSQL.

## Запуск приложения

### 1. Запустите PostgreSQL (либо локально, либо через Docker).

### 2. Примените миграции для базы данных:

```bash
alembic upgrade head
```

### 3. Запустите сервер FastAPI:

```bash
uvicorn main:app --reload
```

### 4. Доступ к документации API:

* Swagger UI: http://localhost:8000/docs

* ReDoc: http://localhost:8000/redoc

## Конечные точки API

* POST /auth/register - Регистрация нового пользователя

* POST /auth/login - Получение JWT-токена (вход в систему)

* POST /referrals/create_referral - Создание реферального кода

* GET /referrals/get_referral_code - Получение реферального кода по электронной почте

* DELETE /referrals/delete_referral_code/{email} - Удаление активного реферального кода