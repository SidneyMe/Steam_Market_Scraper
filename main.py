from scraper_manager import ScraperManager

if __name__ == '__main__':
    SCRAPE_SALES = False  #regular full scrape of steam takes 45mins, with this on, up to 5h

    #urls to items : https://steamcommunity.com/market/search?category_730_ItemSet%5B%5D=tag_set_op10_characters&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_Tournament%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Type%5B%5D=any&category_730_Weapon%5B%5D=any&appid=730
    urls: list[str] = []  
    scraper_manager = ScraperManager(urls, scrape_sales=SCRAPE_SALES, driver_num=5)
    scraper_manager.run()