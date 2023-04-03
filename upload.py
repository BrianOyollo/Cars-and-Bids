import os
import boto3
from datetime import datetime,timedelta
import json


# access keys
aws_access_key_id = os.environ['ACCESS_KEY_ID']
aws_secret_access_key = os.environ['SECRET_ACCESS_KEY']
cars_and_bids_topicarn = os.environ['CARS_AND_BIDS_TOPICARN']


saving_date =  datetime.today().date() - timedelta(days=1)

# s3
s3 = boto3.client(
    's3',
    region_name = 'us-east-1',
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key
)
# sns
sns = boto3.client(
    'sns',
    region_name = 'us-east-1',
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key
)



subject = f'Cars&Bids: Daily Auction Summary'
message = f"""
        Hello,

        Here is the daily auction report for {saving_date}:

            Number of auctions recorded: xx

            Highest bid:$xx (Vehicle: abc)

            Lowest bid:$xx (Vehicle: abc)

        Thank you for your attention
        
        Brian Oyollo
        DE Dept.
    """
no_auctions_message = f"There were no auctions recorded on {saving_date}. Please check again tomorrow."

auctions_file = f'daily_auctions/{saving_date}.json'
urls_file = f'daily_urls/{saving_date}.txt'
try:
    if os.path.isfile(auctions_file):
        # upload files
        s3.upload_file(Filename = f'daily_auctions/{saving_date}.json',Bucket = 'daily-auctions',Key = f'{saving_date}.json')
        s3.upload_file(Filename = f'daily_urls/{saving_date}.txt', Bucket = 'daily-urls', Key = f'{saving_date}.txt')
        
        # send report email
        sns.publish(TopicArn = cars_and_bids_topicarn, Message = message, Subject = subject) 
            
    else:
        sns.publish(TopicArn = cars_and_bids_topicarn, Message = no_auctions_message,Subject = subject)
      
except Exception as e:
    print(e)