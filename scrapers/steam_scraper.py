import time
from scrapers.base_scraper import Scraper
from lxml import etree
from web_driver import WebDriver


class SteamScraper(Scraper):
    """
    Scrapes data from the Steam marketplace.
    """

    def __init__(self, web_driver: WebDriver, urls: list[str]):
        super().__init__(web_driver)
        self.urls = urls


    def get_num_pages(self, url: str) -> int:
        """Calculates the number of pages to scrape based on the total number of items."""

        page = self.web_driver.get_page(url, 5)
        num_items = int(page.xpath('//*[@id="searchResults_total"]')[0].text.replace(',', '')) #parses num of items and converts from str '20,000' to int
        if num_items - 10 >= 0:
            return num_items // 10 + 1
        else:
            return 2

    def steam_page_loader(self, current_url: str) -> etree._Element:
        """Loads a Steam marketplace page and handles potential loading errors."""

        while True:
            page = self.web_driver.get_page(current_url, 5)
            error_element = page.xpath('//*[@id="searchResultsRows"]/div/text()')# looking for the "steam market search error"
            element = page.xpath('//*[@id="searchResultsRows"]')
            if not error_element or not element: #if a steam search error or the page is blank
                print('Failed to load the page, refreshing')
                self.web_driver.driver.refresh()
                time.sleep(5)
                continue
            #steam changes opacity of the steam items (items become blur) when it's trying to load a new page, sometimes it might stuck in that position.
            opacity = element[0].attrib.get("style", "").split(";")[0].split(":")[1].strip()
            if 'error' in error_element[0] or opacity == '0.5':
                print('Failed to load the page, refreshing')
                self.web_driver.driver.refresh()
                time.sleep(5)
            else:
                return page

    def scrape(self) -> list[dict]:
        """Scrapes the Steam marketplace for items, iterating through all pages."""
        
        steam_lots = []
        for url in self.urls:
            steam_page_count = self.get_num_pages(url)
            base_url = url.split('#')[0]
            for current_page in range(1, steam_page_count):
                current_url = f'{base_url}#p{current_page}_price_asc'
                page = self.steam_page_loader(current_url)
                for market_listing in page.xpath('//*[@id="searchResultsRows"]/a[contains(@class, "market_listing_row")]'):
                    steam_lots.append(self.extract_item_info(market_listing))
            return steam_lots

    def extract_item_info(self, market_listing: etree._Element) -> dict:
        return {
            'name': market_listing.xpath('.//div[contains(@class, "market_listing_item_name_block")]/span/text()')[0].replace('|', ''),
            'url': market_listing.get('href'),
            'qty': market_listing.xpath('.//span[@class="market_listing_num_listings_qty"]/@data-qty')[0],
            'price': market_listing.xpath('//*[@id="result_0"]/div[1]/div[2]/span[1]/span[1]/text()')[0],
        }