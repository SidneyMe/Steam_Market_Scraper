import concurrent.futures
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import pandas as pd


class FolioScraper:
    """
    Scrapes sales from steamfolio
    """
    LOCATORS = {'name' : '//*[@id="item-container"]/div/div/div/div[1]/div/div',
                'sales_w' : '//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[2]/td',
                'sales_m' : '//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[3]/td',
                'sales_y' : '//*[@id="item-container"]/div/div/div/div[2]/div[2]/div/div[2]/div[1]/div/div/table/tbody/tr[4]/td'
                }

    def __init__(self, num_drivers: int, web_drivers: list[webdriver.Chrome]) -> None:
        self.num_drivers = num_drivers
        self.web_drivers = web_drivers

    def get_page(self, driver: webdriver.Chrome,
                 urls: list[str],
                 delay: int,
                 tries: int
                 ) -> list[dict]:

        sales = []
        wait_element = WebDriverWait(driver, delay)

        for url in urls:
            driver.get(url)

            while tries > 0:
                try:
                    element_dct = {}

                    for col, locator in self.LOCATORS.items():
                        element_dct[col] = wait_element.until(EC.visibility_of_element_located((By.XPATH, locator))).text
                    sales.append(element_dct)
                    break

                except TimeoutException:
                    tries -= 1
                    driver.refresh()
                    driver.implicitly_wait(3)
                    print(f'Element not found, retrying... {tries} attempts left')

        return sales

    def executor(self, urls: list[str], delay: int) -> list[dict]:

        results = []
        with concurrent.futures.ThreadPoolExecutor() as _executor:
            futures = [_executor.submit(self.get_page, driver, urls[i::self.num_drivers], delay, 5) for i, driver in enumerate(self.web_drivers)]
            for future in futures:
                result = future.result()
                results.extend(result)

        for res in results:
            res['name'] = res['name'].split('| $')[0].strip()

        return sorted(results, key=lambda name: name['name'])

    def get_folio_urls(self, steam_items: list[dict]) -> list[str]:

        urls = []
        for item in steam_items:
            urls.append(item['href'].replace('https://steamcommunity.com/market/listings/730/', 'https://steamfolio.com/Item?name='))

        return urls

    def re_parse_nones(self, sales: list[dict]) ->  pd.DataFrame:

        sales_df = pd.DataFrame(sales)
        items_to_re_parse = sales_df[sales_df[['sales_w', 'sales_m', 'sales_y']].isna().any(axis=1)]
        
        if items_to_re_parse.empty:
            return sales_df

        try:
            re_parsed_sales = self.executor(items_to_re_parse['url'], delay=2)
            for sale in re_parsed_sales:
                sales_df.loc[sale['name'], ['sales_w', 'sales_m', 'sales_y']] = [sale['sales_w'],
                                                                                 sale['sales_m'],
                                                                                 sale['sales_y']]
        except Exception as e:
            print(f'{sale} generated an exception: {e}')
    
        return sales_df

    def scrape(self, steam_items: list[dict], delay: int) -> pd.DataFrame:
        urls = self.get_folio_urls(steam_items)
        sales = self.executor(urls, delay)
        return self.re_parse_nones(sales)
