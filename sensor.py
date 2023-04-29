import airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
from airflow.exceptions import AirflowSensorTimeout
import os


file_path = 'home/brian_oyollo/Documents/projects/demuro/Cars-and-Bids'
def task_failure(context):
    if isinstance(context['exception'], AirflowSensorTimeout):
        with open("dummy_data/failure.txt",'a') as file:

           file.writelines("File not found as of the time:{{ts}}\n")

def print_directory_contents():
    print(os.listdir('dummy_data'))
    
    
with DAG (
    'filesensor_trials',
    default_args = {
        'owner':'BrianOyollo',
        'email':'oyollobrian@gmail.com',
        # 'retries':1,
        # 'retry_delay': timedelta(seconds=100)
    },
    start_date=datetime(2023,3,24),
    schedule=timedelta(minutes=3)
) as dag:
    directory_task = PythonOperator(
        task_id='check_dir_contents',
        python_callable=print_directory_contents
    )
    
    wait_for_file = FileSensor(
        task_id = 'filesensor',
        filepath = f'{file_path}/dummy_data/check.txt',
        poke_interval = 60,
        timeout = 60*2,
        mode = "poke",
        on_failure_callback = task_failure
    )
    
    copy_file = BashOperator(
        task_id = 'copy_file',
        bash_command=f"cp /{file_path}/dummy_data/check.txt /{file_path}/dummy_data/backup/check_{{{{ts}}}}.txt"
    )
    
directory_task >> wait_for_file >> copy_file
    