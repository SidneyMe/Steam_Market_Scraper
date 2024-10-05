import time
from web_driver import WebDriver
from scrapers.base_scraper import Scraper


class SteamScraper(Scraper):
    """
    SteamScraper is a class that extends the Scraper class to scrape data from the Steam marketplace.
    Attributes:
        items_list (list): A list to store the scraped items.
    Methods:
        __init__(web_driver: WebDriver):
            Initializes the SteamScraper with a web driver.
        get_num_pages(url):
            Calculates the number of pages to scrape based on the total number of items.
        steam_page_loader(current_url):
            Loads a Steam marketplace page and handles potential loading errors.
        scrape(url):
            Scrapes the Steam marketplace for items, iterating through all pages.
        extract_item_info(market_listing):
            Extracts item information from a market listing element.
    """


    def __init__(self, web_driver: WebDriver):
        super().__init__(web_driver)
        self.items_list = []


    def get_num_pages(self, url):
        page = self.web_driver.get_page(url, 5)
        num_items = int(page.xpath('//*[@id="searchResults_total"]')[0].text.replace(',', ''))
        return (num_items // 10) + (1 if num_items % 10 != 0 else 0) + 1


    def steam_page_loader(self, current_url):
        while True:
            page = self.web_driver.get_page(current_url, 5)
            error_element = page.xpath('//*[@id="searchResultsRows"]/div/text()')
            element = page.xpath('//*[@id="searchResultsRows"]')
            if not error_element or not element:
                print('Failed to load the page, refreshing')
                self.web_driver.driver.refresh()
                time.sleep(5)
                continue
            opacity = element[0].attrib.get("style", "").split(";")[0].split(":")[1].strip()
            if 'error' in error_element[0] or opacity == '0.5':
                print('Failed to load the page, refreshing')
                self.web_driver.driver.refresh()
                time.sleep(5)
            else:
                return page


    def scrape(self, url):
        steam_page_count = self.get_num_pages(url)
        base_url = url.split('#')[0]
        for current_page in range(1, steam_page_count):
            current_url = f'{base_url}#p{current_page}_price_asc'
            page = self.steam_page_loader(current_url)
            for market_listing in page.xpath('//*[@id="searchResultsRows"]/a[contains(@class, "market_listing_row")]'):
                self.items_list.append(self.extract_item_info(market_listing))


    def extract_item_info(self, market_listing):
        return {
            'name': market_listing.xpath('.//div[contains(@class, "market_listing_item_name_block")]/span/text()')[0].replace('|', ''),
            'url': market_listing.get('href'),
            'qty': market_listing.xpath('.//span[@class="market_listing_num_listings_qty"]/@data-qty')[0],
            'price': market_listing.xpath('//*[@id="result_0"]/div[1]/div[2]/span[1]/span[1]/text()')[0],
        }