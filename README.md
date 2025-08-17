# OpenSearch Document Search Application

Функциональность

- Индексация документов с полями title, content и content_type
- Полнотекстовый поиск по полям title и content
- Фильтрация результатов по типу контента
- REST API на FastAPI
- Docker-compose для запуска всего стека

## Запуск приложения

```bash
docker-compose up --build
```

3. Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### GET /search

Поиск документов

Параметры:

- query (string): Поисковый запрос
- content_type (string, optional): Фильтр по типу контента

Пример запроса:

```bash
curl "http://localhost:8000/search?query=python&content_type=documentation"
```

### GET /content-types

Получение списка доступных типов контента

Пример запроса:

```bash
curl "http://localhost:8000/content-types"
```

## Тестовые данные

При первом запуске приложения автоматически создаются тестовые документы разных типов для демонстрации работы поиска.
