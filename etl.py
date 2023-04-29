import json
import pandas as pd
import os
from sqlalchemy import create_engine
import boto3
from datetime import datetime, timedelta
import numpy as np

def etl(auction_file):
    saving_date =  datetime.today().date() - timedelta(days=1)
    # Extract
    with open(f"/home/brian_oyollo/Documents/projects/demuro/Backup/{auction_file}") as file:
        data = json.load(file)
       
    # ---> flatten json data
    auctions = []
    for key in data.keys():
        auctions.append(data[key])

    # Transform
    
    # ---> add url 
    
    for key in data.keys():
        data[key].update({'url':key})
        
    df = pd.json_normalize(auctions)   
    # ---> add auction_id (from the url)
    df["auction_id"] = df['url'].str.split("/").str[-2]
    
    # ---> remove the newline character ("\n")
    df["auction_quick_facts.Model"] = df["auction_quick_facts.Model"].str.replace("\nSave",'')
    # df["auction_quick_facts.Model"].values
    
    # ---> fix 'sold to' to 'sold', and 'reserve not met, bid to' to 'reserve not met'
    df["auction_stats.auction_status"] = df["auction_stats.auction_status"].str.replace('Reserve not met, bid to','Reserve not met')
    df["auction_stats.auction_status"] = df["auction_stats.auction_status"].str.replace('Sold to','Sold')
    # df["auction_stats.auction_status"].values
    
    # ---> rename and rearrange columns (some auctions didn't have view count)
    if 'auction_stats.view_count' in df.columns:
        df.rename(columns={
            'auction_title':'title',
            'auction_subtitle':'subtitle',
            'auction_equipment':'equipment',
            'known_flaws':'flaws',
            'auction_quick_facts.Make':'make',
            'auction_quick_facts.Model':'model',
            'auction_quick_facts.Mileage':'mileage',
            'auction_quick_facts.VIN':'vin',
            'auction_quick_facts.Title Status':'title_status',
            'auction_quick_facts.Location':'location',
            'auction_quick_facts.Seller':'seller',
            'auction_quick_facts.Engine':'engine',
            'auction_quick_facts.Drivetrain':'drivetrain',
            'auction_quick_facts.Transmission':'transmission',
            'auction_quick_facts.Body Style':'body_style',
            'auction_quick_facts.Exterior Color':'exterior_color',
            'auction_quick_facts.Interior Color':'interior_color',
            'auction_quick_facts.Seller Type':'seller_type',
            'auction_stats.reserve_status':'reserve_status',
            'auction_stats.auction_status':'auction_status',
            'auction_stats.highest_bid_value':'highest_bid',
            'auction_stats.auction_date':'auction_date',
            'auction_stats.view_count':'view_count',
            'auction_stats.bid_count':'bid_count',
            'auction_stats.bids':'bids'   
        }, inplace=True)

        cols_order = [
            'auction_id','title', 'subtitle',
            'make', 'model', 'mileage', 'vin','engine', 'drivetrain','transmission', 'body_style', 'exterior_color', 'interior_color',
            'title_status', 'location', 'seller','seller_type', 'reserve_status', 'auction_status', 'auction_date',
            'view_count', 'bid_count','highest_bid','bids',
            'auction_highlights', 'equipment','modifications', 'flaws', 'services', 'included_items','ownership_history',
            'dougs_take', 'url', 
        ]
        df = df[cols_order]
    else:
        df.rename(columns={
            'auction_title':'title',
            'auction_subtitle':'subtitle',
            'auction_equipment':'equipment',
            'known_flaws':'flaws',
            'auction_quick_facts.Make':'make',
            'auction_quick_facts.Model':'model',
            'auction_quick_facts.Mileage':'mileage',
            'auction_quick_facts.VIN':'vin',
            'auction_quick_facts.Title Status':'title_status',
            'auction_quick_facts.Location':'location',
            'auction_quick_facts.Seller':'seller',
            'auction_quick_facts.Engine':'engine',
            'auction_quick_facts.Drivetrain':'drivetrain',
            'auction_quick_facts.Transmission':'transmission',
            'auction_quick_facts.Body Style':'body_style',
            'auction_quick_facts.Exterior Color':'exterior_color',
            'auction_quick_facts.Interior Color':'interior_color',
            'auction_quick_facts.Seller Type':'seller_type',
            'auction_stats.reserve_status':'reserve_status',
            'auction_stats.auction_status':'auction_status',
            'auction_stats.highest_bid_value':'highest_bid',
            'auction_stats.auction_date':'auction_date',
            # 'auction_stats.view_count':'view_count',
            'auction_stats.bid_count':'bid_count',
            'auction_stats.bids':'bids'   
        }, inplace=True)

        cols_order = [
            'auction_id','title', 'subtitle',
            'make', 'model', 'mileage', 'vin','engine', 'drivetrain','transmission', 'body_style', 'exterior_color', 'interior_color',
            'title_status', 'location', 'seller','seller_type', 'reserve_status', 'auction_status', 'auction_date',
            'bid_count','highest_bid','bids',
            'auction_highlights', 'equipment','modifications', 'flaws', 'services', 'included_items','ownership_history',
            'dougs_take', 'url', 
        ]
        df = df[cols_order]
    # df.head()
    
    # ---> change bid_count, view_count & highest_bid to int
    df['bid_count'] = df['bid_count'].str.replace('[^\d]','', regex=True)
    df['bid_count'] = df['bid_count'].fillna(0).astype(int)
    
    if 'view_count' in df.columns:
        df['view_count'] = df['view_count'].str.replace('[^\d]','', regex=True)
        df['view_count'] = df['view_count'].fillna(0).astype(int)
        
    df['highest_bid'] = df['highest_bid'].str.replace("$",'')
    df['highest_bid'] = df['highest_bid'].str.replace(",",'')
    df['highest_bid'] = df['highest_bid'].fillna(0).astype(int)
    
    # ---> convert auction_date to datetimme
    df['auction_date'] = df['auction_date'].fillna(0)
    df['auction_date'] = pd.to_datetime(df['auction_date'].str.strip()).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # ---> convert mileage to int
    df['mileage'] = df['mileage'].str.replace('[^\d]', '', regex=True)
    df['mileage'] = df['mileage'].replace('', np.nan)
    df['mileage'] = pd.to_numeric(df['mileage'], errors='coerce')
    
    # Load
    
    # ---> load to postgresql
    db_username = os.environ['DB_USERNAME_1']
    db_password = os.environ['DB_PASSWORD_1']
    conn_string = f"postgresql://{db_username}:{db_password}@localhost:5432/carsandbids"
    engine = create_engine(conn_string)
    print(f"----> saving to postgresql")
    df.to_sql('auctions',engine, index=False, if_exists='append')
    
    # ---> save to local storage
    saving_date =  datetime.today().date() - timedelta(days=1)
    print(f"----> saving to local storage")
    df.to_json(f"auction_data/{auction_file.split('.')[0]}.json", orient='records',indent=4)
    df['url'].to_csv(f"auction_data/{auction_file.split('.')[0]}.csv")
    
    
    # ---> load to s3
    # ----> access keys
    aws_access_key_id = os.environ['ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['SECRET_ACCESS_KEY']
    cars_and_bids_topicarn = os.environ['CARS_AND_BIDS_TOPICARN']

    # ----> s3
    s3 = boto3.client(
        's3',
        region_name = 'us-east-1',
        aws_access_key_id = aws_access_key_id,
        aws_secret_access_key = aws_secret_access_key
    )
    print(f"----> uploading to s3")
    s3.upload_file(
        Filename = f"auction_data/{auction_file.split('.')[0]}.json",
        Bucket = 'carsandbids-processed',
        Key = f"{auction_file.split('.')[0]}.json"
    )

    s3.upload_file(
        Filename = f"auction_data/{auction_file.split('.')[0]}.json",
        Bucket = 'carsandbids-processed',
        Key = f"{auction_file.split('.')[0]}.csv"
    )
    

for auction_file in os.listdir('/home/brian_oyollo/Documents/projects/demuro/Backup'):
    print(f"Processing {auction_file}")
    etl(auction_file)