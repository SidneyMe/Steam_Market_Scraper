import os
from lxml import etree
import pandas as pd

class DataProcessor:
    """
    DataProcessor class provides static methods to generate XML and Excel files from a list of items.
    Methods:
        create_output_folder(folder_name='output'):
            creates an output folder if it does not exist.
            Args:
                folder_name (str): The name of the folder to create. Default is 'output'.
        unique_check(list_of_dicts):
            Removes duplicate dictionaries from a list.
            Args:
                list_of_dicts (list): A list of dictionaries.
            Returns:
                list: A list of unique dictionaries
        generate_xml(items, filename='output/steam_items.xml'):
            Generates an XML file from a list of items.
            Args:
                items (list): A list of dictionaries where each dictionary represents an item.
                filename (str): The output file path for the XML file. Default is 'output/steam_items.xml'.
        generate_excel(items, filename='output/steam_items_table.xlsx'):
            Generates an Excel file from a list of items.
            Args:
                items (list): A list of dictionaries where each dictionary represents an item.
                filename (str): The output file path for the Excel file. Default is 'output/steam_items_table.xlsx'.
    """
    def create_output_folder(self, folder_name='output'):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created.")


    @staticmethod
    def unique_check(list_of_dicts):
        return list({d['name']: d for d in list_of_dicts}.values())


    @staticmethod
    def generate_xml(items, filename='output/steam_items.xml'):
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
    def generate_excel(items, filename='output/steam_items_table.xlsx'):
        df = pd.DataFrame(items)
        df.to_excel(filename, index=False)
        print('Excel has been generated')