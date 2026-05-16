# Device Stats Service

Сервис учёта и анализа данных, поступающих с условных устройств. Реализован на
FastAPI с хранением в PostgreSQL и асинхронным расчётом аналитики через Celery
и Redis. Окружение разворачивается одной командой через Docker Compose.

## Архитектура

```
┌────────────┐     HTTP      ┌────────────┐     SQL      ┌────────────┐
│  Клиент    │ ────────────▶ │  FastAPI   │ ───────────▶ │ PostgreSQL │
└────────────┘               │   (api)    │              └────────────┘
                              │            │     broker    ┌────────────┐
                              │            │ ───────────▶ │   Redis    │
                              └─────┬──────┘              └─────┬──────┘
                                    │                            │
                                    │           tasks            │
                                    ▼                            ▼
                              ┌────────────┐              ┌────────────┐
                              │  Celery    │ ◀──────────  │  Очередь   │
                              │   worker   │              └────────────┘
                              └────────────┘
```

- **api** — FastAPI приложение, принимает HTTP-запросы, выполняет CRUD и
  синхронный расчёт статистики.
- **worker** — Celery-воркер, выполняет тяжёлые задачи аналитики асинхронно.
- **postgres** — основное хранилище устройств, пользователей и измерений.
- **redis** — брокер сообщений и backend для результатов Celery.

## Структура проекта

```
app/
├── api/                # HTTP-эндпоинты (users, devices, readings)
├── core/               # Конфигурация приложения
├── db/                 # Подключение к БД, базовая модель
├── models/             # SQLAlchemy ORM модели
├── schemas/            # Pydantic схемы запроса/ответа
├── services/           # Бизнес-логика аналитики
├── tasks/              # Celery-приложение и задачи
└── main.py             # Точка входа FastAPI
```

## Стек

- Python 3.11
- FastAPI + Uvicorn
- SQLAlchemy 2.0 + PostgreSQL 16
- Celery 5 + Redis 7
- Docker, Docker Compose

## Запуск

Требования: установленные Docker и Docker Compose.

```bash
docker compose up --build
```

После запуска доступны:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- OpenAPI: <http://localhost:8000/openapi.json>

Таблицы создаются автоматически при старте сервиса.

## Модель данных

| Таблица   | Поля                                                                 |
|-----------|----------------------------------------------------------------------|
| users     | id (UUID), name, created_at                                          |
| devices   | id (UUID), name, user_id (FK → users, nullable), created_at          |
| readings  | id, device_id (FK → devices), x, y, z, created_at (index)            |

## REST API

### Пользователи

| Метод | Путь                | Описание                  |
|-------|---------------------|---------------------------|
| POST  | `/users`            | Создать пользователя      |
| GET   | `/users`            | Список пользователей      |
| GET   | `/users/{user_id}`  | Получить пользователя     |

### Устройства

| Метод | Путь                    | Описание                                 |
|-------|-------------------------|------------------------------------------|
| POST  | `/devices`              | Создать устройство (можно привязать к user) |
| GET   | `/devices`              | Список устройств                         |
| GET   | `/devices/{device_id}`  | Получить устройство                      |

### Измерения и аналитика

| Метод | Путь                                      | Описание                                       |
|-------|-------------------------------------------|------------------------------------------------|
| POST  | `/devices/{device_id}/readings`           | Записать измерение `{x, y, z}`                 |
| GET   | `/devices/{device_id}/stats`              | Статистика по устройству (синхронно)           |
| POST  | `/devices/{device_id}/stats/async`        | То же асинхронно через Celery                  |
| GET   | `/users/{user_id}/stats`                  | Агрегированная и по-устройству статистика      |
| POST  | `/users/{user_id}/stats/async`            | То же асинхронно через Celery                  |
| GET   | `/tasks/{task_id}`                        | Статус и результат задачи Celery               |

Параметры периода `period_from` и `period_to` принимаются как query-параметры в
формате ISO 8601 (например `2026-01-01T00:00:00`). Если параметры не переданы,
аналитика считается за всё время.

### Результат аналитики

Для каждой из осей `x`, `y`, `z` возвращаются числовые характеристики:

```json
{
  "min": 0.1,
  "max": 9.7,
  "count": 42,
  "sum": 210.5,
  "median": 5.0
}
```

## Примеры запросов

```bash
# Создать пользователя
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Anna"}'

# Создать устройство, привязав к пользователю
curl -X POST http://localhost:8000/devices \
  -H "Content-Type: application/json" \
  -d '{"name": "sensor-1", "user_id": "<USER_UUID>"}'

# Отправить измерение
curl -X POST http://localhost:8000/devices/<DEVICE_UUID>/readings \
  -H "Content-Type: application/json" \
  -d '{"x": 1.2, "y": 3.4, "z": 5.6}'

# Получить статистику по устройству за всё время
curl http://localhost:8000/devices/<DEVICE_UUID>/stats

# Получить статистику за период
curl "http://localhost:8000/devices/<DEVICE_UUID>/stats?period_from=2026-01-01T00:00:00&period_to=2026-12-31T23:59:59"

# Запустить асинхронный расчёт и получить результат
curl -X POST http://localhost:8000/users/<USER_UUID>/stats/async
curl http://localhost:8000/tasks/<TASK_ID>
```

## Асинхронная аналитика (Celery)

Тяжёлые расчёты можно отправлять в Celery через `POST .../stats/async`. Сервис
возвращает идентификатор задачи, а готовый результат запрашивается через
`GET /tasks/{task_id}`. Worker запускается отдельным контейнером и масштабируется
независимо от API.

Пример:

```bash
curl -X POST http://localhost:8000/users/<USER_UUID>/stats/async
# {"task_id": "abc...", "status": "PENDING"}

curl http://localhost:8000/tasks/abc...
# {"task_id": "abc...", "status": "SUCCESS", "result": { ... }}
```

## Нагрузочное тестирование (Locust)

Подробный сценарий и результаты — в [`loadtest/README.md`](loadtest/README.md).

Краткие результаты прогона (50 пользователей, 30 секунд):

| Запрос                      | Запросов | Ошибок | Median, ms | p95, ms |  RPS  |
|-----------------------------|---------:|-------:|-----------:|--------:|------:|
| POST `/devices/:id/readings`|    2 761 |   0    |     6      |   15    |  95.1 |
| GET  `/devices/:id/stats`   |    1 060 |   0    |     4      |   12    |  36.5 |
| GET  `/users/:id/stats`     |      543 |   0    |     6      |   16    |  18.7 |
| **Aggregated**              | **4 464**| **0**  |   **6**    | **16**  |**154**|

Запуск через Docker Compose:

```bash
docker compose up -d
docker compose --profile loadtest up locust
# UI: http://localhost:8089
```

Или headless:

```bash
locust -f locustfile.py --host http://localhost:8000 \
       --headless -u 50 -r 10 -t 30s --csv loadtest/report
```

## Остановка

```bash
docker compose down            # остановить контейнеры
docker compose down -v         # удалить также том с данными PostgreSQL
```
