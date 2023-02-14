from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json



class CarScrapper:
    def __init__(self,url):
        self.url = url
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options) 
        
    
    def get_live_auction_urls(self): 
        start_time = time.time()
        
        self.driver.get(self.url)
        time.sleep(10)
        # vehicle_urls = self.driver.find_elements(By.XPATH, "//div[@class='auction-title']/a")
        vehicle_urls = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='auction-title']/a")))
        urls = [url.get_attribute('href') for url in vehicle_urls] # might contain duplicates. 
        final_live_auction_urls = list(set(urls)) # convert to set to remove duplicates if any
        
        elapsed_time = time.time() - start_time
        
        print(final_live_auction_urls)
        print(len(final_live_auction_urls))
        print(f"{elapsed_time} seconds")

scraper = CarScrapper("https://carsandbids.com/")
scraper.get_live_auction_urls()
scraper.driver.quit()