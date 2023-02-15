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
        """
        This method fetches the auction URLs of all the ongoing auctions on the "https://carsandbids.com" website. 
        
        Args:
            self: Instance of the CarsandBidsScraper class.
            
        Returns:
            A tuple consisting of three elements:
            - The list of all auction URLs,
            - The length of the list of auction URLs, and
            - The total elapsed time taken to fetch the auction URLs.
        """
        start_time = time.time()
        
        self.driver.get(self.url)
        vehicle_urls = WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='auction-title']/a")))
        urls = [url.get_attribute('href') for url in vehicle_urls] # might contain duplicates. 
        final_live_auction_urls = list(set(urls)) # convert to set to remove duplicates if any
        
        elapsed_time = time.time() - start_time
        
        return final_live_auction_urls,len(final_live_auction_urls), elapsed_time, 


    def get_past_auctions_urls(self):
        """
        Navigates to the "Past Auctions" page on carsandbids.com and returns a list of URLs for each past auction.
    
        Returns:
        - final_past_auction_urls: a list of unique URLs for each past auction
        - num_urls: the number of URLs in the list
        - elapsed_time: the time elapsed while scraping the URLs
        
        Raises:
        - TimeoutException: if the page or element could not be found within the allotted time (20 seconds)
        - Exception: if there was an error during the scraping process
        """
        start_time = time.time()
            
        final_past_auction_urls = []
        page_num=1
        while True:  
            try:
                self.driver.get(f"https://carsandbids.com/past-auctions/?page={page_num}")
                print(f"Scrapping page {page_num} ...")
                past_auctions_urls = WebDriverWait(self.driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='auction-title']/a")))
                page_urls = [url.get_attribute('href') for url in past_auctions_urls] # might contain duplicates. 
                for final_url in list(set(page_urls)):  # convert to set to remove duplicates
                    final_past_auction_urls.append(final_url)
                   
                next_page_btn = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='arrow next']/button[@class='btn rb btn-link']")))
                time.sleep(5)
                self.driver.execute_script("arguments[0].click();", next_page_btn)
                page_num+=1
            except:
                print("Looks like you got all the auctions.")
                break
    
        elapsed_time = time.time()- start_time
        
        # print(final_past_auction_urls)
        # print(f"{len(final_past_auction_urls)} urls scrapped in {elapsed_time}")
        
        return final_past_auction_urls, len(final_past_auction_urls), elapsed_time
        











scraper = CarScrapper("https://carsandbids.com/")
scraper.get_past_auctions_urls()
scraper.driver.quit()