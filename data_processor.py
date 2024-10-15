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
    def unique_check(list_of_dicts: list[dict]) -> list[dict]:
        """Removes duplicate dictionaries from a list."""

        return list({d['name']: d for d in list_of_dicts}.values())


    @staticmethod
    def generate_xml(items: list[dict], filename: str ='output/steam_items.xml'):
        """Generates an XML file from a list of items."""

        root = etree.Element('Items')
        for item in items:
            item_element = etree.SubElement(root, 'Item')
            for key, value in item.items():
                sub_element = etree.SubElement(item_element, key)
                sub_element.text = str(value)
        tree = etree.ElementTree(root)
        with open(filename, 'wb') as f:
            tree.write(f, pretty_print=True, xml_declaration=True, encoding='UTF-8')


    @staticmethod
    def generate_excel(items: list[dict], filename: str ='output/steam_items_table.xlsx'):
        """Generates an Excel file from a list of items."""

        df = pd.DataFrame(items)
        df.to_excel(filename, index=False)
        print('Excel has been generated')