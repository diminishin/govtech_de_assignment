from datetime import datetime, timedelta
import pendulum
from airflow import DAG
from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator
from airflow.models import Variable

## Author: Chang Ee Chuan
## Airflow DAG to trigger spark-submit job to run process_datasets.py

local_tz = pendulum.timezone("Asia/Singapore")
default_args = {
    'owner': 'eechuan',
    'depends_on_past': False,
    'start_date': datetime(2022, 12, 3, tzinfo=local_tz),
    'email': ['diminishin@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=1)
}

dag = DAG(dag_id='process_datasets',
          default_args=default_args,
          catchup=False,
          schedule_interval="0 * * * *")

govtech_app_folder=Variable.get("govtech_app_folder_section_1")
arg_list = [govtech_app_folder]

process_datasets= SparkSubmitOperator(task_id='process_datasets',
conn_id='spark_local',
application=f'{govtech_app_folder}/bin/process_datasets.py',
application_args=arg_list,
total_executor_cores=4,
packages="",
executor_cores=2,
executor_memory='5g',
driver_memory='5g',
name='process_datasets',
execution_timeout=timedelta(minutes=10),
dag=dag
)

archive_files= SparkSubmitOperator(task_id='archive_files',
conn_id='spark_local',
application=f'{govtech_app_folder}/bin/archive_files.py',
application_args=arg_list,
total_executor_cores=4,
packages="",
executor_cores=2,
executor_memory='5g',
driver_memory='5g',
name='archive_files',
execution_timeout=timedelta(minutes=10),
dag=dag
)

check_files= SparkSubmitOperator(task_id='check_files',
conn_id='spark_local',
application=f'{govtech_app_folder}/bin/check_files.py',
application_args=arg_list,
total_executor_cores=4,
packages="",
executor_cores=2,
executor_memory='5g',
driver_memory='5g',
name='check_files',
execution_timeout=timedelta(minutes=10),
dag=dag
)

check_files>>process_datasets>>archive_files
