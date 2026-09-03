import requests
import psycopg2
import json

# Конфигурация
BASE_URL = "https://jsonplaceholder.typicode.com"
DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "dbname": "dwh",
    "user": "dwh",
    "password": "dwh",
}
ENDPOINTS = ["users", "posts"]  # Без comments


# ========== ETL ФУНКЦИИ ==========
def extract(endpoint):
    """Извлекает данные из API."""
    response = requests.get(f"{BASE_URL}/{endpoint}", timeout=30)
    response.raise_for_status()
    return response.json()


def load(endpoint, data):
    """Загружает данные в staging."""
    with psycopg2.connect(**DB_CONFIG) as conn, conn.cursor() as cur:
        cur.execute(f"""
            CREATE SCHEMA IF NOT EXISTS staging;
            CREATE TABLE IF NOT EXISTS staging.{endpoint} (
                raw         jsonb,
                _loaded_at  timestamp DEFAULT now(),
                _source     text DEFAULT 'jsonplaceholder'
            );
        """)
        cur.executemany(
            f"INSERT INTO staging.{endpoint} (raw) VALUES (%s)",
            [(json.dumps(r),) for r in data]
        )


def run_sql(filepath):
    """Выполняет SQL-файл."""
    with open(filepath, encoding="utf-8") as f:
        with psycopg2.connect(**DB_CONFIG) as conn, conn.cursor() as cur:
            cur.execute(f.read())


def transform():
    """Запускает трансформацию."""
    run_sql("sql/core.sql")
    print("core: пересобран")
    run_sql("sql/marts.sql")
    print("marts: пересобраны")


# ========== ТОЧКА ВХОДА ==========
if __name__ == "__main__":
    # Загрузка данных
    for endpoint in ENDPOINTS:
        data = extract(endpoint)
        load(endpoint, data)
        print(f"{endpoint}: загружено {len(data)} записей")
    
    # Трансформация
    transform()