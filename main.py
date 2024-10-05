from scraper_manager import ScraperManager

if __name__ == '__main__':
    urls = ['https://steamcommunity.com/market/search?category_730_ItemSet%5B%5D=any&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_Tournament%5B%5D=any&category_730_TournamentTeam%5B%5D=tag_Team106&category_730_Type%5B%5D=any&category_730_Weapon%5B%5D=any&category_730_StickerCategory%5B%5D=tag_TeamLogo&category_730_StickerCategory%5B%5D=tag_Tournament&appid=730&q=#p1_price_asc']    
    scraper_manager = ScraperManager(urls)
    scraper_manager.run()