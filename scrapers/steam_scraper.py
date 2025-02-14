import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver


class SteamScraper:
    """
    Scrapes data from the Steam marketplace.
    """

    LOCATORS = {
                #xpath
                'items_num': '//*[@id="searchResults_total"]',
                'ban': '//*[@id="mainContents"]/h2',
                #class
                'item_name': 'market_listing_item_name',
                'qty': 'market_listing_num_listings_qty',
                'price': 'normal_price',
                'href': 'market_listing_row_link',
                'active_table': 'market_listing_table_active',
                }


    def __init__(self, web_drivers: list[webdriver.Chrome], urls: list[str]):
        self.web_driver = web_drivers[0]
        self.urls = urls
        self.wait = WebDriverWait


    def page_loader(self, current_url: str) -> bool:
        """Loads a Steam marketplace page and handles potential loading errors."""

        wait = self.wait(self.web_driver, 5)

        while True:
            try:
                self.web_driver.get(current_url)
                time.sleep(13)
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, self.LOCATORS['active_table'])))
                return True

            except TimeoutException:
                try:
                    self.web_driver.refresh()

                    if wait.until(EC.text_to_be_present_in_element((By.XPATH, self.LOCATORS['ban']), text_='Error')):
                        print("You've been banned")
                        time.sleep(300) #steam banns for 5min
                        self.web_driver.refresh()

                except TimeoutException:
                    continue


    def get_num_pages(self, url: str) -> dict[str, int]:
        """Scrapes number of items and calculates number of pages"""

        if not self.page_loader(url):
            self.get_num_pages(url)

        #gets num of items and converts from str '20,000' to int
        num_items = int(self.wait(self.web_driver, 3).until(EC.visibility_of_element_located((By.XPATH, self.LOCATORS['items_num']))).text.replace(',', ''))

        if num_items - 10 >= 0:
            return {'num_pages': num_items // 10 + 1,
                    'num_items': num_items} 
        else:
            return {'num_pages': 2,
                    'num_items': num_items}


    def scrape(self) -> list[dict]:
        """Scrapes the Steam marketplace for items, iterating through all pages."""
        steam_lots = []
        for url in self.urls:
            steam_page_count, item_num = self.get_num_pages(url).values()
            base_url = url.split('#')[0]

            for current_page in range(1, steam_page_count + 1):
                current_url = f'{base_url}#p{current_page}_price_asc'

                if self.page_loader(current_url):
                    steam_items = self.web_driver.find_elements(By.CLASS_NAME, self.LOCATORS['href'])

                    for steam_item in steam_items:
                        splitted = steam_item.text.splitlines()
                        steam_lots.append({
                            'name': splitted[3],
                            'qty': splitted[0],
                            'price': splitted [2],
                            'href': steam_item.get_attribute('href')
                        })

        return steam_lots
