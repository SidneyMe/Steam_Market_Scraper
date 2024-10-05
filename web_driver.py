import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree

class WebDriver:
    """
    A class to manage a headless Chrome WebDriver instance.
    Methods
    -------
    __init__():
        Initializes the WebDriver with headless Chrome options.
    get_page(url, delay=1):
        Loads a web page and returns its HTML content as an lxml etree object.
    close():
        Closes the WebDriver instance.
    """
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise

    def get_page(self, url, delay=1):
        try:
            self.driver.get(url)
            time.sleep(delay)
            return etree.HTML(self.driver.page_source)
        except Exception as e:
            print(f"Error loading page {url}: {e}")
            return None

    def close(self):
        try:
            self.driver.quit()
        except Exception as ex:
            print(f'Failed closing the driver: {ex}')