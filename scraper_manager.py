import time
import os
import sqlite3
import pandas as pd
from web_driver import WebDriver
from scrapers.steam_scraper import SteamScraper
from scrapers.folio_scraper import FolioScraper
from scrapers.full_steam_scraper import FullSteamScrape
from db_creators.sqlite_creator import SQLiteDatabaseCreator, SqliteMigration
from data_processor import DataProcessor


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


    def __init__(self, steam_urls: list[str], driver_num: int):
        self.steam_urls = steam_urls
        self.driver = WebDriver(driver_num)
        self.web_drivers = self.driver.get_webdriver(driver_num)
        self.data_processor = DataProcessor()
        self.steam_scraper = SteamScraper(self.web_drivers, steam_urls)
        self.steam_full_scraper = FullSteamScrape(driver_num, self.web_drivers)
        self.folio_scraper = FolioScraper(driver_num, self.web_drivers)


    @timer
    def parse(self) -> pd.DataFrame:
        """Scrapes data from the provided Steam URLs or performs a full Steam scrape if no URLs are provided."""

        try:
            if self.steam_urls:
                steam_items = self.steam_scraper.scrape()

            else:
                steam_items = self.steam_full_scraper.scrape()

        except Exception as e:
            print(f'An exception  {e}')

        try:
            folio_sales_df  = self.folio_scraper.scrape(steam_items, 1)

        except Exception as e:
            print(f'An exception  {e}')
            self.output_gen(steam_items)

        finally:
            self.driver.close()

        return self.data_processor.merge_steam_folio(steam_items, folio_sales_df)


    def output_gen(self, steam_items_df: pd.DataFrame) -> None:

        steam_items_df.sort_values(by=['name'])
        print(f"Parsed {len(steam_items_df.index)} items")

        try:
            if os.path.exists('output/steam_items.db'):
                print('Updating data in the existing db')
                sqlite_migrate = SqliteMigration(steam_items_df)
                sqlite_migrate.make_migration()
                print('Data have been updated')

            else:
                print('Creating output folder')
                self.data_processor.create_output_folder()
                print("Creating SQLite database")
                sqlite_creator = SQLiteDatabaseCreator(steam_items_df)
                sqlite_creator.create_db()
                print("Database creation completed")

        except sqlite3.ProgrammingError as sql3_e:
            print(f'Failed to create a db {sql3_e}')

        finally:
            print("Generating XML")
            DataProcessor.generate_xml(steam_items_df)
            print("Creating excel")
            DataProcessor.generate_excel(steam_items_df)


    def run(self) -> None:
        print("Starting run method")
        steam_items = self.data_processor.unique_check(self.parse())
        self.output_gen(steam_items)
