from scraper_manager import ScraperManager

if __name__ == '__main__':
    urls = []
    scraper_manager = ScraperManager(urls, driver_num=5)
    scraper_manager.run()