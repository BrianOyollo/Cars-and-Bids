import os
import boto3
from datetime import datetime,timedelta
import json


# access keys
aws_access_key_id = os.environ['ACCESS_KEY_ID']
aws_secret_access_key = os.environ['SECRET_ACCESS_KEY']



saving_date =  datetime.today().date() - timedelta(days=1)
project_path = "/home/ec2-user/carsnbids"

# s3
s3 = boto3.client(
    's3',
    region_name = 'us-east-1',
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key
)

# print(s3.list_buckets())

auctions_file = f"{project_path}/daily_auctions/{saving_date}.json"
urls_file = f"{project_path}/daily_urls/{saving_date}.txt"


try:
    if os.path.isfile(auctions_file):
        # upload files  
        print("uploading urls and auction files to cloud....")
        s3.upload_file(Filename = f"{project_path}/daily_auctions/{saving_date}.json",Bucket = 'daily-auctions',Key = f"{saving_date}.json")
        s3.upload_file(Filename = f"{project_path}/daily_urls/{saving_date}.txt", Bucket = 'daily-urls', Key = f"{saving_date}.txt")  

except Exception as e:
    print(e)
