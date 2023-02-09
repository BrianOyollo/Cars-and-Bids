from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import json



url = "https://carsandbids.com/auctions/rxM1e8V6/2004-lamborghini-gallardo-coupe"

def get_listing_details(url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    
    
    driver.get(url)
    time.sleep(10)
    page = driver.page_source
    
    soup = BeautifulSoup(page, 'html.parser')
    # title
    div_title = soup.find('div', class_="auction-title")
    title = div_title.find('h1').get_text()
    
    # subtitle
    div_subtitle = soup.find('div', class_="d-md-flex justify-content-between flex-wrap")
    subtitle = div_subtitle.find('h2').get_text()
    
    # quick facts
    quick_facts = soup.find('div', class_='quick-facts')
    quick_facts_dict = {}
    for dl in quick_facts.find_all('dl'):
        dts = dl.find_all('dt')
        dds = dl.find_all('dd')
        
        for dt,dd in zip(dts,dds):
            quick_facts_dict[dt.get_text()] = dd.get_text()
            # print(f"{dt.get_text()}: {dd.get_text()}")
    
    # Doug's take
    dougs_take = soup.select_one("div.dougs-take div.detail-body p").get_text()
    
    # highlights
    highlight_1 = soup.select_one("div.detail-highlights div.detail-body p").get_text()
    highlights = soup.select("div.detail-highlights div.detail-body ul li")
    highlight_list=[]
    for li in highlights:
        highlight_list.append(highlight_1)
        highlight_list.append(li.get_text())

    # equipment
    equipment = [li.get_text() for li in soup.select("div.detail-equipment div.detail-body ul li")]
    print(equipment)
    
    # modifiations
    modifications = [li.get_text() for li in soup.select("div.detail-modifications div.detail-body ul li")]
    
    # flaws
    known_flaws = [li.get_text() for li in soup.select("div.detail-known_flaws div.detail-body ul li")]
    
    # service history
    recent_service_history = [li.get_text() for li in soup.select("div.detail-known_flaws div.detail-body ul li")]
    
    
    
    
    
    
    driver.quit()
get_listing_details(url)