from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

auctions_url = "https://carsandbids.com/past-auctions/"

def get_auctions(url):
    driver.get(url)
    time.sleep(10)
    page = driver.page_source
    return page
    
def get_listing_url(page):
    soup = BeautifulSoup(page, 'html.parser')
    listing_urls = soup.find_all('div', class_='auction-title')
    url_list=[]
    for auction_url in listing_urls:
        url = auction_url.find('a').get('href')
        url_list.append(url)
        
    return url_list
        
        
    
    
get_listing_url(get_auctions(auctions_url))