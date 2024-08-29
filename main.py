import concurrent.futures
import time
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import etree
import pandas as pd


class WebDriver:


    def __init__(self):
        chrome_options = Options()
        # Add your chrome options here
        path_to_chromedriver = r'chromedriver/chromedriver.exe'
        service = Service(executable_path=path_to_chromedriver)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)


    def get_page(self, url, delay=1):
        self.driver.get(url)
        time.sleep(delay)
        return etree.HTML(self.driver.page_source)


    def close(self):
        try:
            self.driver.quit()
        except Exception as ex:
            print(f'Failed closing the driver: {ex}')


class Scraper(ABC):


    def __init__(self, web_driver: WebDriver):
        self.web_driver = web_driver


    @abstractmethod
    def scrape(self, url):
        pass


class SteamScraper(Scraper):


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


class FolioScraper(Scraper):


    def folio_page_loader(self, url):
        while True:
            page = self.web_driver.get_page(url)
            try:
                page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0]
                return page
            except IndexError:
                print('Failed to load the page, refreshing')
                self.web_driver.driver.refresh()
                time.sleep(5)


    def scrape(self, url):
        page = self.folio_page_loader(url)
        return {
            'sales_w': page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0],
            'sales_m': page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[3]/td/text()')[0],
            'sales_y': page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[4]/td/text()')[0],
        }


class DataProcessor:


    @staticmethod
    def generate_xml(items, filename='test.xml'):
        root = etree.Element('Items')
        for item in items:
            item_element = etree.SubElement(root, 'Item')
            for key, value in item.items():
                sub_element = etree.SubElement(item_element, key)
                sub_element.text = str(value)
        tree = etree.ElementTree(root)
        with open(filename, 'wb') as f:
            tree.write(f, pretty_print=True, xml_declaration=True, encoding='UTF-8')


    @staticmethod
    def generate_excel(items, filename='steam_items_table.xlsx'):
        df = pd.DataFrame(items)
        df.to_excel(filename, index=False)
        print('Excel has been generated')


class ScraperManager:


    def __init__(self, steam_urls):
        self.steam_urls = steam_urls
        self.web_driver = WebDriver()
        self.steam_scraper = SteamScraper(self.web_driver)
        self.folio_scraper = FolioScraper(self.web_driver)


    def run(self):


        try:
            for url in self.steam_urls:
                self.steam_scraper.scrape(url)
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                folio_urls = [item['url'].replace('https://steamcommunity.com/market/listings/730/', 'https://steamfolio.com/Item?name=') for item in self.steam_scraper.items_list]
                future_to_url = {executor.submit(self.folio_scraper.scrape, url): url for url in folio_urls}
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        print(f'{url} generated an exception: {exc}')
                    else:
                        index = folio_urls.index(url)
                        self.steam_scraper.items_list[index].update(data)
            DataProcessor.generate_xml(self.steam_scraper.items_list)
            DataProcessor.generate_excel(self.steam_scraper.items_list)
        finally:
            self.web_driver.close()


if __name__ == '__main__':
    urls = ['https://steamcommunity.com/market/search?category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_Tournament%5B%5D=any&category_730_TournamentTeam%5B%5D=tag_Team106&category_730_Type%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&appid=730&q=#p1_price_asc']    
    scraper_manager = ScraperManager(urls)
    scraper_manager.run()
