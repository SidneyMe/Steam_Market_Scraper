# Steam Market Scraper

## Overview
The Steam Market Scraper is a Python-based tool designed to scrape data from the Steam Community Market and Steam Folio websites. It collects item information, processes the data, and stores it in various formats including XML, Excel, and an SQLite database.

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/Steam_Market_Scraper.git
    cd Steam_Market_Scraper
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Ensure you have the ChromeDriver executable in the `chromedriver/` directory.

2. Provide the *urls* list in main.py with CS2 url/urls to scrape particular items. If the list stays empty, all CS2 items will be parsed.

3. Run the scraper:
    ```sh
    python main.py
    ```
## Project Structure


```plaintext
Steam_Market_Scraper/
 ├── chromedriver/
 │   ├── chromedriver.exe
 │   ├── LICENSE.chromedriver
 │   └── THIRD_PARTY_NOTICES.chromedriver
 ├── db_creators/
 │   ├── __init__.py
 │   └── sqlite_creator.py
 ├── scrapers/
 │   ├── __init__.py
 │   ├── base_scraper.py
 │   ├── folio_scraper.py
 │   ├── full_steam_scraper.py
 │   └── steam_scraper.py
 ├── output/
 │   ├── steam_items_table.xlsx
 │   └── steam_items.xml
 ├── __pycache__/
 ├── venv/
 ├── data_processor.py
 ├── main.py
 ├── readme.md
 ├── requirements.txt
 ├── scraper_manager.py
 └── web_driver.py
 ```


## Modules
### `web_driver.py`
Manages a headless Chrome WebDriver instance for web scraping.

### `scraper_manager.py`
Manages the scraping process from multiple sources and processes the scraped data.

### `data_processor.py`
Provides methods to generate XML and Excel files from a list of items and to ensure data uniqueness.

### `scrapers/steam_scraper.py`
Scrapes data from the Steam marketplace.

### `scrapers/full_steam_scraper.py`
Scrapes all item data from the Steam Community Market for the game CS:GO.

### `scrapers/folio_scraper.py`
Scrapes sales data from the Steam Folio webpage.

### `db_creators/sqlite_creator.py`
Creates and manages an SQLite database for storing steam items.

## License
This project is licensed under the MIT License. See the [LICENSE](chromedriver/LICENSE.chromedriver) file for details.

## Acknowledgements
- [Selenium](https://www.selenium.dev/)
- [lxml](https://lxml.de/)
- [Pandas](https://pandas.pydata.org/)
- [WebDriver Manager for Python](https://github.com/SergeyPirogov/webdriver_manager)