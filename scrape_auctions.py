import airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from datetime import datetime,timedelta
import os
import sys

sys.path.append('/home/brian_oyollo/Documents/projects/demuro/Cars-and-Bids/')
from listing import CarScraper


car_scraper = CarScraper("https://carsandbids.com/")


with DAG(
    "cars_and_bids",
    default_args={
        'owner':'Brian Oyollo',
        'email':'oyollobrian@gmail.com',
        "email_on_failure": True,
        "email_on_retry": True,
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        },
    description = 'trial dag',
    schedule = None,
    start_date = datetime(2023,2,27),
    ) as dag:
        task1 = PythonOperator(
                    task_id = 'daily_urls',
                    python_callable = car_scraper.update_past_auction_urls,
                )
        
        task2 = PythonOperator(
            task_id = 'daily_scrape',
            python_callable = car_scraper.daily_scraper,
        )
        
        # task3 = EmailOperator(
        #     task_id = 'daily_auction_data',
        #     to = 'oyollobrian@gmail.com',
        #     subject = f'Auction data for {datetime.today().date()}',
        #     html_content = 'Attached is the latest auction data.',
        #     files = f"daily auctions/{datetime.today().date()}"
        # )
        
        task1 >> task2