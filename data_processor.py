import os
from lxml import etree
import pandas as pd

class DataProcessor:
    """
    DataProcessor class provides static methods to generate XML and Excel files from a list of items.
    """

    @staticmethod
    def create_output_folder(folder_name: str ='output'):
        """Creates an output folder if it does not exist."""

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created.")


    @staticmethod
    def unique_check(steam_items_df: pd.DataFrame) -> pd.DataFrame:
        """Removes duplicate dictionaries from a list."""

        return steam_items_df.drop_duplicates(subset=['name'])


    @staticmethod
    def generate_xml(steam_items_df: pd.DataFrame, filepath: str ='output/steam_items'):
        """Generates an XML file from a list of items."""

        steam_items_df.to_xml(path_or_buffer=filepath, encoding='UTF-8', pretty_print=True)


    @staticmethod
    def generate_excel(items: list[dict], filename: str ='output/steam_items_table.xlsx'):
        """Generates an Excel file from a list of items."""

        df = pd.DataFrame(items)
        df.to_excel(filename, index=False)
        print('Excel has been generated')


    @staticmethod
    def merge_steam_folio(steam_items: list[dict], sales_df: pd.DataFrame) -> pd.DataFrame:

        steam_items_df = pd.DataFrame(steam_items)
        return steam_items_df.merge(sales_df, how='inner', on='name')