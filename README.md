# Soul

Soul — это веб-приложение на Django для познания себя самому и скрепления пар с помощью вопросов, которые сами редко задаём в обычной жизни.

## Возможности

- Регистрация и авторизация пользователей.
- Просмотр и редактирование профиля.
- Загрузка фотографии профиля.
- Поиск пользователей.
- Создание пары и отправка приглашений.
- Работа с вопросами.
- Получение уведомлений.
- Периодическая отправка вопросов через Celery.
- Использование Redis как брокера сообщений.
- Настройка расписания уведомлений по московскому времени.

## Технологии

- Python
- Django
- Celery
- Redis
- SQLite
- HTML
- CSS

## Структура проекта

```text
soul/
├── accounts/          # Пользователи, профили и уведомления
├── couples/           # Пары и приглашения
├── notifications/     # Модель и обработка уведомлений
├── questions/         # Вопросы и периодические задачи
├── soul/              # Настройки и конфигурация Django
├── static/            # CSS и изображения
├── manage.py
├── run_local.py       # Локальный запуск приложения
├── requirements.txt
├── .gitignore
└── README.md
```

## Установка

### Требования

Перед установкой должны быть доступны:

- Python 3.12 или новее.
- Redis.
- Git.

### Клонирование проекта

```bash
git clone [https://github.com/D0roy/soul.git](https://github.com/D0roy/soul.git)
cd soul
```

### Создание виртуального окружения

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Если PowerShell блокирует запуск скриптов:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Установка зависимостей

```powershell
python -m pip install -r requirements.txt
```

## Настройка базы данных

Примените миграции:

```powershell
python manage.py migrate
```

При необходимости создайте администратора:

```powershell
python manage.py createsuperuser
```

## Запуск Redis

Redis должен быть запущен до запуска Celery.

Проверить подключение можно командой:

```powershell
redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

## Запуск приложения

Для запуска Django, Celery Worker и Celery Beat выполните:

```powershell
python run_local.py
```

После запуска приложение будет доступно по адресу:

```text
http://127.0.0.1:8000
```

Также можно открыть:

```text
http://localhost:8000
```

Остановить приложение:

```text
Ctrl+C
```

## Запуск вручную

Если требуется запускать процессы отдельно:

```powershell
python manage.py runserver
```

В отдельном окне PowerShell:

```powershell
celery -A soul worker --loglevel=info --pool=solo
```

Ещё в одном окне:

```powershell
celery -A soul beat --loglevel=info
```

## Расписание уведомлений

Celery Beat запускает периодическую задачу:

```text
questions.tasks.send_scheduled_questions
```

Часовой пояс приложения:

```text
Europe/Moscow
```

Уведомления могут создаваться по расписанию:

```text
10:00 по Москве
15:00 по Москве
20:00 по Москве
```

## Проверка проекта

Проверка Django:

```powershell
python manage.py check
```

Проверка миграций:

```powershell
python manage.py makemigrations --check
```

## Важные файлы

- `soul/settings.py` — настройки Django.
- `soul/celery.py` — конфигурация Celery.
- `questions/tasks.py` — периодические задачи.
- `run_local.py` — запуск приложения.
- `requirements.txt` — зависимости проекта.
- `.gitignore` — файлы, которые не загружаются в GitHub.

## Безопасность

Не добавляйте в GitHub:

- файл `.env`;
- реальные пароли;
- токены;
- API-ключи;
- базу данных с личными данными;
- пользовательские изображения из папки `media`.

Для секретных настроек рекомендуется использовать переменные окружения.

## Статус проекта

Проект находится в разработке и предназначен для локального запуска.