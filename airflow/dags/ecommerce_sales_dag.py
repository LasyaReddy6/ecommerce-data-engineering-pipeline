"""Optional Airflow DAG. Install Airflow separately using its official constraints."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="ecommerce_sales_pipeline",
    description="Run the local e-commerce CSV-to-PostgreSQL ETL pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 8 * * *",
    catchup=False,
    tags=["data-engineering", "portfolio"],
) as dag:
    run_etl = BashOperator(
        task_id="run_etl",
        bash_command="cd {{ dag_run.conf.get('project_root', '/opt/ecommerce-data-engineering-pipeline') }} && python -m src.pipeline",
    )
