from fastapi import FastAPI, Form
from opensearchpy import OpenSearch, ConnectionError
import random
from typing import List, Dict
import time

app = FastAPI()

def get_opensearch_client(max_retries=5, delay=5):
    for attempt in range(max_retries):
        try:
            client = OpenSearch(
                hosts=['opensearch:9200'],
                http_auth=None,
                use_ssl=False,
                verify_certs=False,
            )
            # Проверяем подключение
            client.info()
            print(f"Successfully connected to OpenSearch after {attempt + 1} attempts")
            return client
        except ConnectionError as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Connection attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)

# Инициализация клиента OpenSearch с повторными попытками
opensearch = None

# Определение индекса
INDEX_NAME = "documents"
INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "content_type": {"type": "keyword"}
        }
    }
}

# Список возможных типов контента
CONTENT_TYPES = ["article", "blog", "news", "documentation"]

@app.on_event("startup")
async def startup_event():
    global opensearch
    # Инициализация клиента с повторными попытками
    opensearch = get_opensearch_client()
    
    # Создание индекса, если он не существует
    if not opensearch.indices.exists(INDEX_NAME):
        opensearch.indices.create(INDEX_NAME, body=INDEX_MAPPING)
        
        # Добавление тестовых документов
        test_docs = [
            {
                "title": "Python Programming Guide",
                "content": "Python is a versatile programming language that's great for beginners and experts alike.",
                "content_type": "documentation"
            },
            {
                "title": "New Features in Python 3.9",
                "content": "Latest Python release brings exciting updates to the language and standard library.",
                "content_type": "news"
            },
            {
                "title": "Best Practices in Web Development",
                "content": "Learn about the essential practices for modern web development.",
                "content_type": "blog"
            },
            {
                "title": "Understanding Machine Learning",
                "content": "A comprehensive guide to machine learning concepts and applications.",
                "content_type": "article"
            }
        ]
        
        for doc in test_docs:
            opensearch.index(
                index=INDEX_NAME,
                body=doc,
                refresh=True
            )

@app.get("/search")
async def search_documents(
    query: str,
    content_type: str = None
) -> List[Dict]:
    # Формирование поискового запроса
    search_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["title", "content"]
                        }
                    }
                ]
            }
        }
    }
    
    # Добавление фильтра по типу контента, если указан
    if content_type:
        search_query["query"]["bool"]["filter"] = [
            {"term": {"content_type": content_type}}
        ]
    
    # Выполнение поиска
    response = opensearch.search(
        index=INDEX_NAME,
        body=search_query
    )
    
    # Форматирование результатов
    results = []
    for hit in response['hits']['hits']:
        source = hit['_source']
        results.append({
            "title": source['title'],
            "snippet": source['content'][:50],
            "content_type": source['content_type']
        })
    
    return results

@app.get("/content-types")
async def get_content_types():
    return CONTENT_TYPES
