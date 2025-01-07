import urllib.parse
import time
import json
from lxml import etree
from selenium import webdriver
from web_driver import WebDriver

class FullSteamScrape:
    """
    Scrapes all items' data from the Steam Community Market for CS2
    """

    STEAM_URL = 'https://steamcommunity.com/market/search/render/?appid=730&norender=1'

    def __init__(self, num_drivers, web_drivers: list[webdriver.Chrome]):
        self.driver = WebDriver(num_drivers)
        self.web_driver = web_drivers[0]
        self.max_retries: int = 5
        self.retry_delay: int = 5

    def get_page(self) -> dict:
        self.web_driver.get(self.STEAM_URL)
        time.sleep(13)
        page = etree.HTML(self.web_driver.page_source)
        page_json = page.xpath('/html/body/pre/text()')[0]
        self.STEAM_URL = self.STEAM_URL.split('&start=')[0]
        return json.loads(page_json)

    def page_loader(self, page_num: int) -> list[dict]:
        """Loads a specific page of results from the Steam Community Market, retrying up to a specified number of times if necessary."""

        for attempt in range(self.max_retries):
            try:
                self.STEAM_URL = f'{self.STEAM_URL}&start={page_num}&count=100'
                page_json = self.get_page()
                if 'results' in page_json and page_json['results']:
                    return page_json['results']
                else:
                    raise TypeError("Results key not found or empty. Reloading")
            except (TypeError, json.JSONDecodeError) as e:
                print(f"Error occurred (Attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Skipping this page.")
        return []


    def scrape(self) -> list[dict]:
        steam_items = []
        try:
            num_items = self.get_page()['total_count']
        except(KeyError, json.JSONDecodeError):
            num_items = 21552 # value last seen by me
        for page in range(0, num_items, 100):
            print(f'Working with page {(page+1)//100}')
            results = self.page_loader(page)
            if results is None:
                continue
            for item in results:
                steam_items.append(self.extract_items_info(item))
        return steam_items

    def encode_url(self, item_name: str) -> str:
        """Encodes a name of an item to standard URL encoding"""

        return f'https://steamcommunity.com/market/listings/730/{urllib.parse.quote(item_name)}'

    def extract_items_info(self, item: dict) -> dict:
        return {
                    'name' : item['name'],
                    'href' : self.encode_url(item['name']),
                    'qty' : item['sell_listings'],
                    'price' : item['sell_price_text'],
                }