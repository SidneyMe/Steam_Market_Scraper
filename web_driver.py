from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

class WebDriver:
    """
    Manages the Chrome WebDriver.
    """

    _instance = None

    def __new__(cls, drivers_num: int):
        if cls._instance is None:
            cls._instance = super(WebDriver, cls).__new__(cls)
            cls._instance.init_webdrivers(drivers_num)
        return cls._instance

    def __init__(self, drivers_num: int):
        if not hasattr(self, 'web_drivers'):
            self.init_webdrivers(drivers_num)

    def init_webdrivers(self, drivers_num: int):
        self.wait = WebDriverWait
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        try:
            service = Service(ChromeDriverManager().install())
            self.web_drivers = [webdriver.Chrome(service=service, options=chrome_options) for _ in range(drivers_num)]
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise

    def get_webdriver(self, req_drivers) -> list[webdriver.Chrome]:
        try:
            return self.web_drivers[0:req_drivers]
        except IndexError:
            print('Tried to get more drivers than were created')
        return []

    def close(self):
        try:
            for driver in self.web_drivers:
                driver.close()
        except Exception as ex:
            print(f'Failed closing the driver: {ex}')
