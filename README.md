# Search Queries 

Менеджер поисковых запросов с сервер-сайд сортировкой и пагинацией.

## Стек

| Слой       | Технология                                |
|------------|-------------------------------------------|
| Backend    | FastAPI + SQLAlchemy 2 + SQLite           |
| Frontend   | React 18 + Vite (FSD-структура)           |
| БД         | SQLite                                    |

---

## Быстрый старт

### Backend

```bash
cd backend
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

При старте автоматически создаётся БД и засевается **10 000 записей**.
API доступно на `http://localhost:8000`. Документация: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Открыть `http://localhost:5173`.

---

## API

| Метод    | URL                     | Описание                          |
|----------|-------------------------|-----------------------------------|
| `GET`    | `/api/queries`          | Список с пагинацией и сортировкой |
| `POST`   | `/api/queries`          | Создать запрос                    |
| `PUT`    | `/api/queries/{id}`     | Обновить запрос                   |
| `DELETE` | `/api/queries/{id}`     | Удалить один запрос               |
| `DELETE` | `/api/queries`          | Групповое удаление (body: {ids})  |

### Query params для GET /api/queries

| Параметр    | По умолчанию   | Описание                      |
|-------------|----------------|-------------------------------|
| `page`      | `1`            | Номер страницы                |
| `page_size` | `50`           | Строк на страницу (10–200)    |
| `sort_by`   | `created_at`   | Поле для сортировки           |
| `sort_dir`  | `desc`         | `asc` или `desc`              |

---

## Структура проекта

```
project/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── utils.py
│   ├── domain/
│   │   └── search_query/
│   │       ├── model.py
│   │       ├── schemas.py
│   │       ├── repository.py
│   │       └── service.py
│   ├── api/
│   │   └── v1/
│   │       └── routes/
│   │           └── search_queries.py
│   ├── infrastructure/
│   │   └── seeder.py
│   └── tests/
│       ├── conftest.py
│       └── make_query/
│           ├── test_model.py
│           ├── test_repository.py
│           ├── test_service.py
│           ├── test_schemas.py
│           ├── test_routes.py
│           └── test_seeder.py
├── frontend/
│   └── src/
│       ├── app/
│       │   └── App.jsx
│       ├── features/
│       │   └── search-queries/
│       │       ├── api/
│       │       │   └── queriesApi.ts
│       │       ├── components/
│       │       │   ├── QueriesPage.tsx
│       │       │   ├── QueriesTable.tsx
│       │       │   └── QueriesModal.tsx
│       │       └── hooks/
│       │           └── useQueries.ts
│       └── shared/
│           └── ui/
│               ├── Modal.tsx
│               └── Pagination.tsx
```

### Ключевые решения

- **Производительность**: клиент никогда не получает все данные. Сортировка и пагинация выполняются на уровне SQL (`ORDER BY` + `LIMIT/OFFSET`). SQLAlchemy генерирует единственный эффективный запрос.
- **Просроченные дедлайны**: проверяются на фронтенде (`deadline < new Date()`). Строки подсвечиваются янтарным цветом с иконкой ⚠.
- **Групповое удаление**: чекбоксы в каждой строке + «Выбрать всё на странице». На бэкенде - один запрос `DELETE ... WHERE id IN (...)`.
- **FSD (Feature-Sliced Design)**: фича `search-queries` полностью инкапсулирует API, хук и компоненты. Shared UI (`Modal`, `Pagination`) вынесен отдельно.
- **Seeder**: при старте проверяет количество записей и засевает только недостающие батчами по 2000 (`bulk_save_objects`).
- **UTC Синхронизация**: В бд сохраняется не локальное время а общее время по utc(проверка на дедлайны отрабатывает корректно)
- **DDD (Domain Driven Design)**: Проект построен по принципам DDD: бизнес-логика изолирована в domain, API обрабатывает запросы, core содержит конфигурацию, infrastructure отвечает за генерацию данных, а tests покрывают все слои.
 
---
