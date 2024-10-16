import time
from scrapers.base_scraper import Scraper
from lxml import etree

class FolioScraper(Scraper):
    """
    A scraper class for extracting sales data from steamfolio webpage using a web driver.
    """

    def folio_page_loader(self, url: str) -> etree._Element:
        """Loads the page until the required elements is rendered by the website"""

        while True:
            page = self.web_driver.get_page(url, 1)
            try:
                if page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0]:
                    return page
            except IndexError:
                print('Failed to load the page, refreshing')
                self.web_driver.driver.refresh()
                time.sleep(5)

    def scrape(self, url: str) -> dict:
        """Extracts sales data (weekly, monthly, yearly) from the loaded webpage"""

        page = self.folio_page_loader(url)
        return {
            'sales_w': page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0],
            'sales_m': page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[3]/td/text()')[0],
            'sales_y': page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[4]/td/text()')[0],
        }