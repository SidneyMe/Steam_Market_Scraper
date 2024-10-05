from scraper_manager import ScraperManager

if __name__ == '__main__':
    urls = []    
    scraper_manager = ScraperManager(urls)
    scraper_manager.run()