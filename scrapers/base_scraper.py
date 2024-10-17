from abc import ABC, abstractmethod
from web_driver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

class Scraper(ABC):
    """
    A base class for web scrapers that defines the basic structure and requirements for a scraper.
    Attributes:
        web_driver (WebDriver): The web driver instance used to interact with web pages.
    Methods:
        scrape(url):
            Abstract method that must be implemented by subclasses to define the scraping logic for a given URL.
    """


    def __init__(self, web_driver: WebDriver):
        self.web_driver = web_driver
        self.wait = WebDriverWait

    @abstractmethod
    def scrape(self):
        pass