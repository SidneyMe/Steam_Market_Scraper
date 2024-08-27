import concurrent.futures
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import etree
import pandas as pd
import concurrent


def speed_test(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.4f} seconds")
        return result
    return wrapper


class Steam:

 
    def __init__(self, urls, num_drivers=5) -> None:
        self.steam_urls = urls
        self.timer_delay_time = 0
        self.items_list = []
        self.folio_urls = []
        self.drivers = []
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        path_to_chromedriver = r'chromedriver/chromedriver.exe'
        for _ in range(num_drivers):
            service = Service(executable_path=path_to_chromedriver)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.drivers.append(driver)


    def url_processor(self):
        for url in self.steam_urls:
            self.get_all_items(url)


    def sleep(self, sec):
        time.sleep(sec)

    
    def get_page(self, current_page, driver):        
        driver.get(current_page)
        self.sleep(self.timer_delay_time)
        page = etree.HTML(driver.page_source)
        return page


    def get_num_pages(self, url):
        page = self.get_page(url, self.drivers[0])
        num_items = int(page.xpath('//*[@id="searchResults_total"]')[0].text.replace(',', ''))
        num_of_pages = (num_items // 10) + (1 if num_items % 10 != 0 else 0)
        return num_of_pages + 1


    def steam_page_loader(self, current_url, current_page):
        page_loaded = False
        while not page_loaded:
            page = self.get_page(current_url, self.drivers[0])
            error_element = page.xpath('//*[@id="searchResultsRows"]/div/text()')[0]
            element = page.xpath('//*[@id="searchResultsRows"]')[0]
            opacity = element.attrib.get("style", "").split(";")[0].split(":")[1].strip()
            if 'error' in error_element:
                self.drivers[0].refresh()
                self.sleep(5)
                print(f'Failed to load the page {current_page}, refreshing')
            elif opacity == '0.5':
                self.drivers[0].refresh()
                self.sleep(5)
                print(f'Failed to load the page {current_page}, refreshing')
            else:
                page_loaded = True
        return page


    def get_all_items(self, url):
        self.timer_delay_time = 5
        steam_page_count = self.get_num_pages(url)
        base_url = url.split('#')[0]
        for current_page in range(1, steam_page_count):
            current_url = f'{base_url}#p{current_page}_price_asc'
            page = self.steam_page_loader(current_url, current_page)
            for market_listing in page.xpath('//*[@id="searchResultsRows"]/a[contains(@class, "market_listing_row")]'):
                    href = market_listing.get('href')
                    name = market_listing.xpath('.//div[contains(@class, "market_listing_item_name_block")]/span/text()')[0]
                    qty = market_listing.xpath('.//span[@class="market_listing_num_listings_qty"]/@data-qty')[0]
                    price = market_listing.xpath('//*[@id="result_0"]/div[1]/div[2]/span[1]/span[1]/text()')[0]
                    self.items_list.append({
                        'name': name.replace('|', ''),
                        'url': href,
                        'qty': qty,
                        'price' : price,
                    })
                    self.folio_urls.append(href.replace('https://steamcommunity.com/market/listings/730/', 'https://steamfolio.com/Item?name='))


    def folio_page_loader(self, current_url, driver):
        page_loaded = False
        while not page_loaded:
            try:
                page = self.get_page(current_url, driver)
                page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0]
            except IndexError:
                driver.refresh()
                self.sleep(5)
            else:
                page_loaded = True
        return page
    
    
    # def get_sales(self, url):
    #     page = self.folio_page_loader(url)
    #     sales_w = page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0]
    #     sales_m = page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[3]/td/text()')[0]
    #     sales_y = page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[4]/td/text()')[0]
    #     return {
    #                 'sales_w' : sales_w,
    #                 'sales_m' : sales_m,
    #                 'sales_y' : sales_y,         
    #             }

    # @speed_test
    # def feature_to_urls(self):
    #     self.timer_delay_time = 1
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    #         feature_sales = list(executor.map(self.get_sales, self.folio_urls))
            # for i in range(len(self.items_list)):
            #     self.items_list[i].update(feature_sales[i])

    def chuncify(self):
        chunks = []
        prev = 0
        for url in range(0, len(self.folio_urls), 5):
            chunks.append(self.folio_urls[prev:url])
            prev = url
        return chunks
        
    def get_sales(self, url, driver):
        page = self.folio_page_loader(url, driver)
        sales_w = page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td/text()')[0]
        sales_m = page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[3]/td/text()')[0]
        sales_y = page.xpath('//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[4]/td/text()')[0]
        return {
                    'sales_w' : sales_w,
                    'sales_m' : sales_m,
                    'sales_y' : sales_y,         
                }

    @speed_test
    def feature_to_urls(self):
        self.timer_delay_time = 1
        chunks = self.chuncify()
        feature_sales = []
        for urls in chunks:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                feature_sales.append(list(executor.map(self.get_sales, urls, self.drivers)))
        print(feature_sales)


    def generate_xml(self):
        self.url_processor()
        self.feature_to_urls()
        root = etree.Element('Items')
        for item in self.items_list:
            item_element = etree.SubElement(root, 'Item')
            for key, value in item.items():
                sub_element = etree.SubElement(item_element, key)
                sub_element.text = value       
        tree = etree.ElementTree(root)
        with open('test.xml', 'wb') as f:
            tree.write(f, pretty_print=True, xml_declaration=True, encoding='UTF-8')


    def generate_exel(self): 
        df = pd.DataFrame(self.items_list)
        df.to_excel('steam_items_table.xlsx', index=False)
        print('Exel has been generated')


    def close(self):
        try:
            for driver in self.drivers:
                driver.quit()
        except Exception as ex:
            print(f'Failed to close webdriver {ex}')


if __name__ == '__main__':
    
    steam_urls = ['https://steamcommunity.com/market/search?category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_Tournament%5B%5D=any&category_730_TournamentTeam%5B%5D=tag_Team106&category_730_Type%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&appid=730&q=#p1_price_asc']
    s = Steam(steam_urls)
    try:
        s.generate_xml()
        s.generate_exel()
    finally:
        s.close()
