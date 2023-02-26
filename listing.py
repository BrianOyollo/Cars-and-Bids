from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json



class CarScrapper:
    def __init__(self,url):
        self.url = url
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options) 
        
    # get urls of live auctions
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

    # get urls of all auctions (from Nov. 2020)
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
                print(f"scraping page {page_num}...")
                past_auctions_urls = WebDriverWait(self.driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='auction-title']/a")))
                page_urls = [url.get_attribute('href') for url in past_auctions_urls]
                for final_url in page_urls:
                    final_past_auction_urls.append(final_url)
                   
                next_page_btn = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='arrow next']/button[@class='btn rb btn-link']")))
                time.sleep(5)
                self.driver.execute_script("arguments[0].click();", next_page_btn)
                page_num+=1
            except:
                print("Looks like you got all the auctions.")
                break
    
        elapsed_time = time.time()- start_time
        print(f"{page_num} pages scrapped in {round(elapsed_time,2)}")
        
        
        with open('auction_urls.txt', 'w') as obj:
            print(f"Writing urls to file...")
            for url in final_past_auction_urls:
                obj.writelines(f"{url}\n")
                
            #   
    
    # save urls of new auctions & update the overall list of auction URLs
    def update_past_auction_urls(self):
        with open('auction_urls_copy.txt', 'r') as obj:
            print("Reading previous URLs...")
            old_urls = obj.readlines()

        daily_urls = []
        
        page=1
        while True and page <= 2:
            try:
                self.driver.get(f"https://carsandbids.com/past-auctions/?page={page}")
                print(f"scraping page {page}...")
                vehicle_urls = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//div[@class='auction-title']/a")))
                
                urls = [url.get_attribute('href') for url in vehicle_urls]
                for final_url in urls:
                    daily_urls.append(final_url)
                    
                next_page_btn = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='arrow next']/button[@class='btn rb btn-link']")))
                
                time.sleep(5)
                self.driver.execute_script("arguments[0].click();", next_page_btn)
                page+=1
            except Exception as e:
                print(e)
                break
        
        
        with open(f'daily urls/{datetime.today().date()}.txt','w') as file:
            print("Saving daily auction urls...")
            for url in daily_urls:
                if f"{url}\n" not in old_urls:
                    file.writelines(f"{url}\n")
            
            
        for index, url in enumerate(daily_urls):
            if url not in old_urls:
                old_urls.insert(index,url.strip())        

        with open('auction_urls_copy.txt','w') as obj:
            print('Updating URLs...')
            for url in old_urls:
                obj.writelines(f"{url.strip()}\n")
             
    # scrape
    def scrap_auction_details(self,urls):
                
        def load_auction_page(url):
            try:
                self.driver.get(url.strip('\n'))
            except Exception as e:
                print(f"Oops, something went wrong while loading {url}")
                print(e)
                
            return self.driver
                
        def get_auction_title(driver):
            try:    
                auction_title = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='auction-title ']/h1"))).text
            except Exception as e:
                print("Error getting auction title")
                auction_title = None

            return auction_title

        def get_auction_subtitle(driver):
            try:    
                auction_subtitle = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='d-md-flex justify-content-between flex-wrap']/h2"))).text
            except Exception as e:
                print("Error getting auction sub-title")
                auction_subtitle = None
            
            return auction_subtitle
                
        def get_quick_facts(driver):
            quick_facts = {}
            try:
                auction_quick_facts_dt = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='quick-facts']/dl/dt")))
                auction_quick_facts_dd = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='quick-facts']/dl/dd")))
            except Exception as e:
                print("Error getting auction quick-facts")
                auction_quick_facts_dt = []
                auction_quick_facts_dd = []    
                
            for dt,dd in zip(auction_quick_facts_dt, auction_quick_facts_dd):
                quick_facts[dt.text]=dd.text
                
            return quick_facts

        def get_dougs_take(driver):
            try:
                dougs_take = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='detail-section dougs-take']/div[@class='detail-body']/p"))).text
            except Exception as e:
                print("Error getting Doug's take")
                dougs_take = None
            
            return dougs_take
                
        def get_auction_highlights(driver):
            try:
                auction_highlights = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='detail-section detail-highlights']/div[@class='detail-body']/ul/li")))
                highlights = [highlight.text for highlight in auction_highlights]
            except Exception as e:
                print("Error getting auction's highlights")
                highlights = []
                
            return highlights
        
        def get_auction_equiment(driver):
            try:
                auction_equipment = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='detail-section detail-equipment']/div[@class='detail-body']/ul/li")))
                equipment = [equipment.text for equipment in auction_equipment]
            except Exception as e:
                print("Error getting auction's equipment")
                equipment = []
                
            return equipment

        def get_auction_modifications(driver):
            try:
                auction_modifications = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='detail-section detail-modifications']/div[@class='detail-body']/ul/li")))
                modifications = [modification.text for modification in auction_modifications]
            except Exception as e:
                print("Error getting auction's modifications")
                modifications = []
                
            return modifications

        def get_known_flaws(driver):
            try:
                auction_known_flaws = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='detail-section detail-known_flaws']/div[@class='detail-body']/ul/li")))
                known_flaws = [flaw.text for flaw in auction_known_flaws]
            except Exception as e:
                print("Error getting auction's known flaws")
                known_flaws = []
                
            return known_flaws

        def get_service_history(driver):
            try:
                auction_service_history = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='detail-section detail-recent_service_history']/div[@class='detail-body']/ul/li")))
                services = [service_history.text for service_history in auction_service_history]
            except Exception as e:
                print("Error getting auction's service history")
                services = []
                
            return services

        def get_included_items(driver):
            try:
                other_included_items = WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='detail-section detail-other_items']/div[@class='detail-body']/ul/li")))
                included_items = [item.text for item in other_included_items]
            except Exception as e:
                print("Error getting auction's included items")
                included_items = []
                
            return included_items    

        def get_ownership_hostory(driver):
            try:
                ownership_history = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='detail-section detail-ownership_history']/div[@class='detail-body']/p")))
                ownership_history = ownership_history.text
            except Exception as e:
                print("Error getting auction's ownership history")
                ownership_history = None
            
            return ownership_history

        def get_auction_stats(driver):
            auction_stats = {}
            try:
                reserve_status = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='auction-subheading ']/h3/span"))).text
                auction_status = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//div[@class='current-bid ended d-flex flex-column flex-shrink-1 ']/div[@class='d-flex bidder']/h4"))).text
                highest_bid_value = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//span[@class='bid-value']"))).text
                auction_date = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='stats']/li/div[@class='td end-icon']"))).text
                bid_count = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='stats']/li/div[@class='td bid-icon']"))).text
                view_count = WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH, "//ul[@class='stats']/li/div[@class='td views-icon']"))).text
                # scroll_pause_time = 5 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
                # screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
                # i = 1

                while True:
                    try:
                    # scroll one screen height each time
                    # driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
                    # i += 1
                    # time.sleep(scroll_pause_time)
                    # # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
                    # scroll_height = driver.execute_script("return document.body.scrollHeight;")
                    # # Break the loop when the height we need to scroll to is larger than the total scroll height
                        load_more = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//li[@class='load-more']/button[@class='btn btn-secondary btn-block']")))
                        driver.execute_script("arguments[0].click();", load_more)
                        time.sleep(5)
                    except Exception as e:
                        break
                    # if (screen_height) * i > scroll_height:
                    #     break 
                    
                    
                    
                bids = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='content']/dl[@class='placed-bid ']/dd[@class='bid-value']")))
                bid_list=[bid.text for bid in bids]
            except Exception as e:
                print("Error getting auction's stats")
                reserve_status = None
                auction_status = None
                highest_bid_value = None
                auction_date = None
                bid_count = None
                view_count = None
                bid_list = []
                
            auction_stats = {
                'reserve_status':reserve_status,
                'auction_status':auction_status,
                'highest_bid_value':highest_bid_value,
                'auction_date':auction_date,
                'view_count':view_count,
                'bid_count':bid_count,
                'bids':bid_list,
            }
            
            return auction_stats    
            
        auction_details = {}       
        for url in urls:
            print(f"scraping {url}")
        
            driver = load_auction_page(url.strip('\n'))
            auction_title = get_auction_title(driver)
            auction_subtitle = get_auction_subtitle(driver)
            auction_quick_facts = get_quick_facts(driver)
            dougs_take = get_dougs_take(driver)
            auction_highlights = get_auction_highlights(driver)
            auction_equipment = get_auction_equiment(driver)
            auction_modifications = get_auction_modifications(driver)
            auction_known_flaws = get_known_flaws(driver)
            auction_services = get_service_history(driver)
            auction_included_items = get_included_items(driver)
            auction_ownership_history = get_ownership_hostory(driver)
            auction_stats = get_auction_stats(driver)
            
            auction_details[url.strip('\n')] = {  
                'auction_title':auction_title,
                'auction_subtitle':auction_subtitle,
                'auction_quick_facts':auction_quick_facts,
                "dougs_take":dougs_take,
                'auction_highlights':auction_highlights,
                'auction_equipment':auction_equipment,
                'modifications':auction_modifications,
                'known_flaws':auction_known_flaws,
                'services':auction_services,
                'included_items':auction_included_items,
                'ownership_history':auction_ownership_history,
                'auction_stats':auction_stats
            }
            
            
        return auction_details
   
    def scrap_dump_in_chunks(self,chunk_size):
        with open('auction_urls.txt', 'r') as obj:
            print("Reading auction urls...")
            auction_urls = obj.readlines()
        
        for index in range(0, len(auction_urls),chunk_size):
            batch_urls = auction_urls[index:index+chunk_size]
            batch_name = f"{index+1}-{(index+chunk_size)}"
            auctions = self.scrap_auction_details(batch_urls)        
            with open(f"auctions{batch_name}.json", 'w') as obj:
                json.dump(auctions, obj, indent=4)
            
scrapper = CarScrapper("https://carsandbids.com/")

# scrapper.get_past_auctions_urls()
scrapper.update_past_auction_urls()
# scrapper.scrap_dump_in_chunks(1000)

scrapper.driver.quit()