from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'cortex_agent',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def verify_integration():
    print("="*60)
    print("✅ Airflow is successfully triggering this task!")
    print("This means the Scheduler is working.")
    print("="*60)

with DAG(
    '01_cortex_verifier_dag',
    default_args=default_args,
    description='A simple DAG to verify Airflow infrastructure',
    schedule_interval=timedelta(days=1),
    catchup=False
) as dag:

    verify_task = PythonOperator(
        task_id='verify_scheduler',
        python_callable=verify_integration,
    )

    verify_task
