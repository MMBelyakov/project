"""
ETL DAG для вашего проекта
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_project',
    default_args=default_args,
    description='ETL пайплайн: API → staging → core → marts',
    schedule_interval='0 0 * * *',  # Каждый день в 00:00
    catchup=False,
    tags=['etl', 'project'],
)

# Запуск ETL
run_etl = BashOperator(
    task_id='run_etl',
    bash_command='cd /opt/airflow && python etl.py',
    dag=dag,
)

# Сообщение об успехе
success_message = BashOperator(
    task_id='success_message',
    bash_command='echo "✅ ETL выполнен успешно! $(date)"',
    dag=dag,
)

run_etl >> success_message