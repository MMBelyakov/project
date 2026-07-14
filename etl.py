import requests
import psycopg2
import json

BASE_URL = "https://jsonplaceholder.typicode.com"

DB_CONFIG = {
    "host": "localhost",   # скрипт бежит на Windows, поэтому localhost (порт проброшен)
    "port": 5432,
    "dbname": "dwh",
    "user": "dwh",
    "password": "dwh",
}


def extract(endpoint: str) -> list[dict]:
    """Забираем данные из API как есть."""
    response = requests.get(f"{BASE_URL}/{endpoint}", timeout=10)
    response.raise_for_status()
    return response.json()


def load_to_staging(endpoint: str, records: list[dict]) -> None:
    """Кладём сырой JSON в staging.<endpoint> без разбора полей."""
    conn = psycopg2.connect(**DB_CONFIG)
    with conn, conn.cursor() as cur:
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
            [(json.dumps(r),) for r in records],
        )
    conn.close()


def run(endpoint: str) -> None:
    records = extract(endpoint)
    load_to_staging(endpoint, records)
    print(f"{endpoint}: загружено {len(records)} записей")


def run_sql_file(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    with psycopg2.connect(**DB_CONFIG) as conn, conn.cursor() as cur:
        cur.execute(sql)


def transform() -> None:
    run_sql_file("sql/core.sql")
    print("core: пересобран")

    run_sql_file("sql/marts.sql")
    print("marts: пересобраны")

if __name__ == "__main__":
    for endpoint in ["users", "posts", "comments"]:
        run(endpoint)
    transform()