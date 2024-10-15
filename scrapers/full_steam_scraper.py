import urllib.parse
import time
import json
from scrapers.base_scraper import Scraper
from web_driver import WebDriver

class FullSteamScrape(Scraper):
    """
    Scrapes items' data from the Steam Community Market for CS2
    """

    def __init__(self, web_driver: WebDriver):
        super().__init__(web_driver)
        self.items_list: list = []
        self.url = 'https://steamcommunity.com/market/search/render/?appid=730&norender=1'
        self.max_retries: int = 5
        self.retry_delay: int = 5

    def get_json(self) -> list[dict]:
        """Fetches the JSON data from the Steam Community Market"""
     
        page = self.web_driver.get_page(self.url, 13)
        page_json = page.xpath('/html/body/pre/text()')[0]
        self.url = self.url.split('&start=')[0]
        return json.loads(page_json)

    def page_loader(self, page_num: int) -> list[dict]:
        """Loads a specific page of results from the Steam Community Market, retrying up to a specified number of times if necessary."""

        for attempt in range(self.max_retries):
            try:
                self.url = f'{self.url}&start={page_num}&count=100'
                page_json = self.get_json()
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
                    return None

    def scrape(self):
        try:
            num_pages = self.get_json()['total_count']
        except(KeyError, json.JSONDecodeError):
            num_pages = 21552 # value last seen by me
        for i in range(0, num_pages, 100):
            print(f'Working with page {(i+1)//100}')
            results = self.page_loader(i)
            if results is None:
                continue
            for item in results:
                self.items_list.append(self.extract_items_info(item))

    def encode_url(self, item_name: str) -> str:
        """Encodes a name of an item to standard URL encoding"""

        return f'https://steamcommunity.com/market/listings/730/{urllib.parse.quote(item_name)}'

    def extract_items_info(self, item: dict) -> dict:
        return {
                    'name' : item['name'],
                    'url' : self.encode_url(item['name']),
                    'qty' : item['sell_listings'],
                    'price' : item['sell_price_text'],
                }