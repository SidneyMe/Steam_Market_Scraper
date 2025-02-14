# Steam Market Scraper

## Overview
Scrapes data from Steam Community Market and Steam Folio websites. Stores data in formats like XML, Excel, and SQLite database.

### Important note: Full scrape with sales takes 5 hours 😊 and 45 minutes without.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/Steam_Market_Scraper.git
    cd Steam_Market_Scraper
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    venv/bin/activate # Windows
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage


1. Provide the *urls* list in main.py with CS2 url/urls to scrape particular items. If the list stays empty, all items will be parsed.

    Example of a url:
    ```sh 
    https://steamcommunity.com/market/search?category_730_ItemSet%5B%5D=tag_set_op10_characters&category_730_ProPlayer%5B%5D=any&category_730_StickerCapsule%5B%5D=any&category_730_Tournament%5B%5D=any&category_730_TournamentTeam%5B%5D=any&category_730_Type%5B%5D=any&category_730_Weapon%5B%5D=any&appid=730
    ```

2. Set *SCRAPE_SALES* in main.py to True, if you want to scrape weekly, monthly and yearly sales.

3. Run the scraper:
    ```sh
    python main.py
    ```

## License
This project is licensed under the MIT License. See the [LICENSE](chromedriver/LICENSE.chromedriver) file for details.

## Acknowledgements
- [Selenium](https://www.selenium.dev/)
- [lxml](https://lxml.de/)
- [Pandas](https://pandas.pydata.org/)
- [WebDriver Manager for Python](https://github.com/SergeyPirogov/webdriver_manager)