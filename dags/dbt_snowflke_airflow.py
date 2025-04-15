from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable


PROJECT_DIR = Variable.get("dbt_project_dir") #"/Users/user/Documents/learningProg/dataengineering/de_dbt_snowflake_airflow/snowflake" # Path to dbt project created after dbt init
PROFILES_DIR = Variable.get("dbt_profiles_dir") #"~/.dbt/profiles.yml" # Path to your dbt profiles.yml file
# Path to your dbt executable got with the command => which dbt
dbt_path = Variable.get("dbt_executable_path") #"/Users/user/Documents/learningProg/dataengineering/de_dbt_snowflake_airflow/airflow-env/bin/dbt"

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    'dbt_snowflake_pipeline',
    default_args=default_args,
    description='A simple DBT pipeline with Airflow to run dbt commands on Snowflake',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 4, 15),
    catchup=False,
    tags=['dbt', 'snowflake'],
) as dag:
    # dag to signify the start of the pipeline
    start = EmptyOperator(task_id='start')

    with TaskGroup("dbt_tasks", tooltip="DBT Tasks") as dbt_tasks:
        # Task to run dbt debug
        dbt_debug = BashOperator(
            task_id='dbt_debug',
            bash_command=f'{dbt_path} debug --project-dir {PROJECT_DIR}',
            env={
                "DBT_PROFILES_DIR": "/Users/user/.dbt"
            }
        )

        # Task to run dbt run
        dbt_run = BashOperator(
            task_id='dbt_run',
            bash_command=f'{dbt_path} run --project-dir {PROJECT_DIR} --select airflow', #this run models under the airflow folder in models folder
            env={
                "DBT_PROFILES_DIR": "/Users/user/.dbt"
            }
        )

        # Task to run dbt test
        dbt_test = BashOperator(
            task_id='dbt_test',
            bash_command=f'{dbt_path} test --project-dir {PROJECT_DIR} --select airflow',
            env={
                "DBT_PROFILES_DIR": "/Users/user/.dbt"
            }
        )

        dbt_debug >> dbt_run >> dbt_test

    # dag to signify the end of the pipeline
    end = EmptyOperator(task_id='end')

    start >> dbt_tasks >> end

