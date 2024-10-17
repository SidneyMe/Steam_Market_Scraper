import time
import os
import concurrent.futures
from web_driver import WebDriver
from scrapers.steam_scraper import SteamScraper
from scrapers.folio_scraper import FolioScraper
from scrapers.full_steam_scraper import FullSteamScrape
from db_creators.sqlite_creator import SQLiteDatabaseCreator, SqliteMigration
from data_processor import DataProcessor
import pandas as pd

def timer(func):
    """Times the execution time of the parser"""
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f'Execution time {func.__name__}  {end - start}sec')
        return res
    return wrapper


class ScraperManager:
    """
    Managing the scraping process from multiple sources and processing the scraped data.
    """

    def __init__(self, steam_urls: list[str]):
        self.steam_urls = steam_urls
        self.web_driver = WebDriver()
        self.data_processor = DataProcessor()
        self.steam_scraper = SteamScraper(self.web_driver, steam_urls)
        self.steam_full_scraper = FullSteamScrape(self.web_driver)
        self.folio_scraper = FolioScraper(self.web_driver)

    @timer
    def parse(self) -> list[dict]:
        """Scrapes data from the provided Steam URLs or performs a full Steam scrape if no URLs are provided."""

        try:
            if self.steam_urls:
                for url in self.steam_urls:
                    steam_items = self.steam_scraper.scrape()
            else:
                steam_items = self.steam_full_scraper.scrape()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                folio_urls = self.folio_scraper.get_folio_urls(steam_items)
                future_to_url = {executor.submit(self.folio_scraper.scrape, url): url for url in folio_urls}
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        print(f'{url} generated an exception: {exc}')
                    else:
                        index = folio_urls.index(url)
                        steam_items[index].update(data)
            steam_items = self.re_parse_nones(steam_items)
        except Exception:
            self.output_gen(steam_items)
        finally:
            self.web_driver.close()
        return steam_items

    def re_parse_nones(self, steam_items: list[dict]) -> list[dict]:
        """Re-parses items with missing sales data by scraping again from Folio"""

        steam_items_df = pd.DataFrame(steam_items)
        item_list_res = steam_items_df.to_dict(orient='records')
        for key, item in enumerate(item_list_res):
            if pd.isna(item['sales_w']) or pd.isna(item['sales_m']) or pd.isna(item['sales_y']):
                try:
                    print(f"Reparsing for item: {item['name']}")
                    scraped_data = self.folio_scraper.scrape(item['url'].replace('https://steamcommunity.com/market/listings/730/', 'https://steamfolio.com/Item?name='))
                except Exception:
                    print(f"An exception has accrued. The parsing data for {item["name"]} will be replaced with 0's")
                    scraped_data = {'sales_w' : 0, 'sales_m' : 0, 'sales_y' : 0}
                finally:
                    item_list_res[key]['sales_w'] = scraped_data['sales_w']
                    item_list_res[key]['sales_m'] = scraped_data['sales_m']
                    item_list_res[key]['sales_y'] = scraped_data['sales_y']

        return item_list_res

    def output_gen(self, steam_items):
        steam_items.sort(key=lambda item: item['name'])
        print(f"Parsed {len(steam_items)} items")
        if os.path.exists('output/steam_items.db'):
            print('Updating data in the existing db')
            sqlite_migrate = SqliteMigration(steam_items)
            sqlite_migrate.make_migration()
            print('Data have been updated')
        else:
            print("Creating SQLite database")
            sqlite_creator = SQLiteDatabaseCreator(steam_items)
            sqlite_creator.create_db()
            print("Database creation completed")
        self.data_processor.create_output_folder()

        print("Generating XML")
        DataProcessor.generate_xml(steam_items) 
        print("Creating excel")
        DataProcessor.generate_excel(steam_items)

    def run(self):
        print("Starting run method")
        steam_items = DataProcessor.unique_check(self.parse())
        self.output_gen(steam_items)
