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
        "retry_delay": timedelta(minutes=5),
        },
    description = 'Scrape daily auctions and update the URLs list',
    schedule = "@daily",
    start_date = datetime(2023,3,3),
    ) as dag:
        task1 = PythonOperator(
                    task_id = 'update_daily_urls',
                    python_callable = car_scraper.update_past_auction_urls,
                    templates_dict={
                        'urls_file_path':"{{ds}}"
                    }
                )
        
        task2 = PythonOperator(
            task_id = 'scrape_daily_auctions',
            python_callable = car_scraper.daily_scraper,
            templates_dict={
                "auctions_file_path":"{{ds}}"
            }
        )
        
        # task3 = EmailOperator(
        #     task_id = 'daily_auction_data',
        #     to = 'oyollobrian@gmail.com',
        #     subject = f'Auction data for {datetime.today().date()}',
        #     html_content = 'Attached is the latest auction data.',
        #     files = f"daily auctions/{datetime.today().date()}"
        # )
        
        task1 >> task2