from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 7, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=15),
    "max_active_tasks": 20,
}

dag = DAG(
    dag_id="data_crawling_dag",
    default_args=default_args,
    description="A DAG to run data crawling steps",
    schedule_interval=timedelta(days=30),
)

# Define the paths for the CLI and the commands
cli_path = "/opt/airflow/"

step_crawling_auctions = BashOperator(
    cwd=cli_path,
    task_id="step_crawling_auctions",
    bash_command='python -m src datacrawl step-crawling-auctions -t 1 --seller sothebys --start-date "2024-04-01" --crawling-mode new',
    dag=dag,
)

step_crawling_items = BashOperator(
    cwd=cli_path,
    task_id="step_crawling_items",
    bash_command="python -m src datacrawl step-crawling-items -t 1 --seller sothebys --crawling-mode new",
    dag=dag,
)

step_crawling_detailed = BashOperator(
    cwd=cli_path,
    task_id="step_crawling_detailed",
    bash_command="python -m src datacrawl step-crawling-detailed -t 1 --seller sothebys -sqs 50 --crawling-mode new",
    dag=dag,
)

step_crawling_pictures = BashOperator(
    cwd=cli_path,
    task_id="step_crawling_pictures",
    bash_command="python -m src datacrawl step-crawling-pictures -t 5 --seller sothebys",
    dag=dag,
)

# Define task dependencies
(
    step_crawling_auctions
    >> step_crawling_items
    >> step_crawling_detailed
    >> step_crawling_pictures
)
