import sqlite3
from abc import ABC

class SQLiteDB(ABC):

    """Abstract method that creates connections with a db"""

    DB_PATH = 'output/steam_items.db'

    def __init__(self, items_list: list[dict]):
        self.items_list = items_list
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def open_connection(self):
        """Creates connection the the db"""
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cur = self.conn.cursor()

    def close_connection(self):
        """Closes connection with the db if the connection was established"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        self.cur = None
        self.conn = None


class SQLiteDatabaseCreator(SQLiteDB):

    """Creates a sqlite db and inserts items"""

    def sql_script(self) -> str:

        """Returns an sql scrip, which creates a table"""

        return """CREATE TABLE IF NOT EXISTS steam_items(
            id INTEGER PRIMARY KEY,
            name TEXT, url TEXT,
            qty INTEGER,
            price TEXT,
            sales_w INTEGER,
            sales_m INTEGER,
            sales_y INTEGER
            )"""

    def create_db(self):
        self.add_id()
        self.open_connection()
        try:
            self.cur.execute(self.sql_script())
            self.cur.execute("""INSERT INTO 
                             steam_items(id, name, url, qty, price, sales_w, sales_m, sales_y) 
                VALUES (:id, :name, :url, :qty, :price, :sales_w, :sales_m, :sales_y)
                """, self.items_list)
            self.conn.commit()
        finally:
            self.close_connection()

    def add_id(self):

        """Adds an id to each item in the list"""

        for i, item in enumerate(self.items_list):
            item['id'] = i


class SqliteMigration(SQLiteDB):

    """Allows to update generated db"""

    def make_migration(self):
        
        """Updates the existing db. Overwrites old data"""
        
        self.open_connection()
        try:
            for item in self.items_list:
                db_item = self.cur.execute('SELECT * FROM steam_items WHERE name = ?', (item['name'],)).fetchone() #gets an item from the db with the same name of an item
                if not db_item:
                    self.add_new_items(item)
                else:
                    db_item_dict = {
                        'qty': db_item[3],
                        'price': db_item[4],
                        'sales_w': db_item[5]
                    }
                    if item['qty'] != db_item_dict['qty'] or item['price'] != db_item_dict['price'] or item['sales_w'] != db_item_dict['sales_w']:
                        self.cur.execute("""UPDATE steam_items
                                            SET qty = ?, price = ?, sales_w = ?, sales_m = ?, sales_y = ?
                                            WHERE name = ?
                                        """, (item['qty'], item['price'], item['sales_w'], item['sales_m'], item['sales_y'], item['name']))
            self.conn.commit()
        finally:
            self.close_connection()

    def add_new_items(self, new_item: dict):
        """Inserts a new item into the db"""

        last_item = self.cur.execute('SELECT MAX(id) FROM steam_items').fetchone()[0]
        new_item['id'] = int(last_item) + 1
        self.cur.execute("""INSERT INTO steam_items
                (id, name, url, qty, price, sales_w, sales_m, sales_y) 
                VALUES (:id, :name, :url, :qty, :price, :sales_w, :sales_m, :sales_y)""", new_item)
        