# Referral System API

API для управления системой реферальных кодов с использованием FastAPI, JWT-аутентификации и базы данных PostgreSQL.

## Оглавление
- [Описание проекта](#описание-проекта)
- [Стек технологий](#стек-технологий)
- [Установка и запуск](#установка-и-запуск)
- [Настройка переменных окружения](#настройка-переменных-окружения)
- [Маршруты API](#маршруты-api)
- [Примеры запросов](#примеры-запросов)

## Описание проекта

Этот проект представляет собой систему реферальных кодов, которая позволяет пользователям регистрироваться и получать доступ к API. Пользователи могут делиться реферальными кодами, приглашать новых пользователей и отслеживать количество приглашенных ими людей.

## Стек технологий

- **Backend**: FastAPI
- **База данных**: PostgreSQL
- **Аутентификация**: JWT (JSON Web Token)
- **Миграции базы данных**: Alembic
- **Контейнеризация**: Docker

## Установка и запуск

### Клонирование репозитория

```bash
git clone git@github.com:feleciap/Referral_system.git
cd referral_system