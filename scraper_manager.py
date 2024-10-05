import time
from web_driver import WebDriver
from scrapers.steam_scraper import SteamScraper
from scrapers.folio_scraper import FolioScraper
from scrapers.full_steam_scraper import FullSteamScrape
from db_creators.sqlite_creator import SQLiteDatabaseCreator
from data_processor import DataProcessor
import concurrent.futures


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f'Execution time {func.__name__}  {end - start}sec')
        return res
    return wrapper


class ScraperManager:
    """
    ScraperManager is responsible for managing the scraping process from multiple sources and processing the scraped data.
    Attributes:
        steam_urls (list): A list of URLs to scrape from Steam.
        web_driver (WebDriver): An instance of the WebDriver used for web scraping.
        steam_scraper (SteamScraper): An instance of the SteamScraper for scraping individual Steam URLs.
        steam_full_scraper (FullSteamScrape): An instance of the FullSteamScrape for scraping all Steam data.
        folio_scraper (FolioScraper): An instance of the FolioScraper for scraping data from Folio.
    Methods:
        parse():
            Scrapes data from the provided Steam URLs or performs a full Steam scrape if no URLs are provided.
            Uses a ThreadPoolExecutor to concurrently scrape additional data from Folio.
            Returns a list of items with the scraped data.
        run():
            Orchestrates the entire scraping and data processing workflow.
            Parses the data, generates XML and Excel files, and creates an SQLite database with the scraped data.
    """
    def __init__(self, steam_urls):
        self.steam_urls = steam_urls
        self.web_driver = WebDriver()
        self.steam_scraper = SteamScraper(self.web_driver)
        self.steam_full_scraper = FullSteamScrape(self.web_driver)
        self.folio_scraper = FolioScraper(self.web_driver)

    @timer
    def parse(self):
        try:
            if self.steam_urls:
                for url in self.steam_urls:
                    self.steam_scraper.scrape(url)
                    item_list = self.steam_scraper.items_list
            else:
                self.steam_full_scraper.scrape()
                item_list = self.steam_full_scraper.items_list
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                folio_urls = [item['url'].replace('https://steamcommunity.com/market/listings/730/', 'https://steamfolio.com/Item?name=') for item in item_list]
                future_to_url = {executor.submit(self.folio_scraper.scrape, url): url for url in folio_urls}
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        print(f'{url} generated an exception: {exc}')
                    else:
                        index = folio_urls.index(url)
                        item_list[index].update(data)
        finally:
            self.web_driver.close()
        
        return item_list


    def run(self):
        print("Starting run method")
        item_list = self.parse()
        print(f"Parsed {len(item_list)} items")
        
        print("Generating XML")
        DataProcessor.generate_xml(item_list)
        print("Generating Excel")
        DataProcessor.generate_excel(item_list)
        
        print("Creating SQLite database")
        sqlite_creator = SQLiteDatabaseCreator(item_list)
        sqlite_creator.create_db()
        print("Database creation complete")